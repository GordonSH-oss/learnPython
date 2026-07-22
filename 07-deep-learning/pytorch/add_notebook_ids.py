"""Add deterministic cell IDs required by modern nbformat."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    for path in sorted(Path(__file__).with_name("notebooks").glob("*.ipynb")):
        notebook = json.loads(path.read_text())
        prefix = path.stem[:2]
        for index, cell in enumerate(notebook["cells"], start=1):
            cell["id"] = f"lesson-{prefix}-cell-{index:02d}"
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
