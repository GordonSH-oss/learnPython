from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("torch")
nbformat = pytest.importorskip("nbformat")
NotebookClient = pytest.importorskip("nbclient").NotebookClient

PYTORCH_ROOT = Path(__file__).parents[1]

# The dataset lesson intentionally downloads MNIST. It is covered by the data-loader
# unit tests and kept out of the offline notebook execution gate.
OFFLINE_NOTEBOOKS = [
    path
    for path in sorted((PYTORCH_ROOT / "notebooks").glob("*.ipynb"))
    if not path.name.startswith("04-")
]


@pytest.mark.parametrize("path", OFFLINE_NOTEBOOKS, ids=lambda path: path.stem)
def test_notebook_executes_offline(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(notebook, timeout=120, kernel_name="python3", resources={"metadata": {"path": str(PYTORCH_ROOT)}})
    client.execute()
