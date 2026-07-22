from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_all_notebooks_are_valid_and_have_teaching_sections() -> None:
    notebooks = sorted((ROOT / "pytorch/notebooks").glob("*.ipynb"))
    assert len(notebooks) == 13
    required = ("学习目标", "概念模型", "检查点", "试一试", "常见错误")
    for path in notebooks:
        notebook = json.loads(path.read_text())
        text = "".join("".join(cell["source"]) for cell in notebook["cells"])
        assert notebook["nbformat"] == 4
        assert all(section in text for section in required)


def test_fundamentals_do_not_import_torch() -> None:
    for path in (ROOT / "fundamentals").glob("*"):
        if path.suffix in {".py", ".md"}:
            assert "import torch" not in path.read_text().lower()
