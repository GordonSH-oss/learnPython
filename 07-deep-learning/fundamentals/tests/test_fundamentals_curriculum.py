from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_course_contains_ten_valid_notebooks_with_teaching_sections() -> None:
    notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
    assert len(notebooks) == 10
    required = ("学习目标", "概念模型", "逐步实现", "检查点", "试一试", "常见错误")
    for path in notebooks:
        notebook = json.loads(path.read_text())
        text = "".join("".join(cell["source"]) for cell in notebook["cells"])
        assert notebook["nbformat"] == 4
        assert all(section in text for section in required)


def test_fundamentals_do_not_use_deep_learning_frameworks() -> None:
    forbidden = ("import torch", "import tensorflow", "import jax", "autograd")
    for path in ROOT.rglob("*"):
        if "tests" not in path.parts and path.suffix in {".py", ".md", ".ipynb"}:
            text = path.read_text().lower()
            assert not any(token in text for token in forbidden), path
