from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("torchvision")

PYTORCH_ROOT = Path(__file__).parents[1]
EXAMPLES = PYTORCH_ROOT / "examples"


@pytest.mark.parametrize(
    ("script", "arguments", "expected"),
    [
        ("linear_regression.py", ["--quick", "--epochs", "2"], "learned y"),
        ("rnn_sequences.py", ["--quick", "--epochs", "1"], "val_acc"),
        ("attention_demo.py", ["--quick"], "future attention mass"),
        ("mixed_precision.py", ["--quick", "--device", "cpu"], "AMP training is skipped"),
        ("export_model.py", ["--quick"], "max output difference"),
    ],
)
def test_offline_example_smoke(tmp_path: Path, script: str, arguments: list[str], expected: str) -> None:
    command = [
        sys.executable,
        str(EXAMPLES / script),
        *arguments,
        "--output-dir",
        str(tmp_path),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True, timeout=120)
    assert expected in completed.stdout


@pytest.mark.parametrize("script", sorted(EXAMPLES.glob("*.py")))
def test_every_example_exposes_unified_cli(script: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(script), "--help"], check=True, capture_output=True, text=True, timeout=30
    )
    for option in ("--dataset", "--data-dir", "--epochs", "--batch-size", "--device", "--output-dir", "--quick"):
        assert option in completed.stdout
