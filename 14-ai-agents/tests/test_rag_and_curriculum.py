import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]


def load_rag():
    spec = importlib.util.spec_from_file_location("rag_pipeline", ROOT / "rag_pipeline.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_rag_ranks_matches_and_refuses_without_evidence():
    rag = load_rag()
    chunks = [rag.Chunk("python.md", "Python Agent tool memory"), rag.Chunk("sql.md", "SQL transaction")]
    matches = rag.retrieve("Python tool", chunks, top_k=2)
    assert matches[0][0].source == "python.md"
    assert rag.retrieve("unrelated", chunks) == []
    assert "没有在本地资料" in rag.build_answer("unrelated", [])


def test_curriculum_has_fourteen_linked_lessons():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"\(guides/(\d{2}-[^)]+\.md)\)", readme)
    assert len(links) == 14
    assert len(set(links)) == 14
    for link in links:
        path = ROOT / "guides" / link
        assert path.exists(), link
        content = path.read_text(encoding="utf-8")
        assert "## 学习目标" in content
        assert "## 常见错误" in content or "## 常见错误与生产注意" in content


def test_online_examples_skip_without_credentials(monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    path = ROOT / "examples" / "framework_openai_agents.py"
    spec = importlib.util.spec_from_file_location("framework_openai_agents", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    module.main()
    assert "SKIP" in capsys.readouterr().out
