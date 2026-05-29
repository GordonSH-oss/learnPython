"""Text and Markdown chunking helpers.

Run:
    python 06-tools-and-tests/chunking.py
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size chunks with optional overlap."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
    return chunks


@dataclass(frozen=True)
class DocumentStructure:
    headers: list[dict[str, Any]]
    code_blocks: list[dict[str, int]]
    tables: list[dict[str, int]]
    lists: list[dict[str, Any]]
    paragraphs: list[dict[str, int]]
    total_lines: int


class DocumentAnalyzer:
    """Analyze Markdown structure for better chunking decisions."""

    def __init__(self) -> None:
        self.header_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
        self.table_pattern = re.compile(r"^\|.+\|")
        self.list_item_pattern = re.compile(r"^[\s]*[-*+]\s+|^\s*\d+\.\s+")

    def analyze_document_structure(self, content: str) -> DocumentStructure:
        lines = content.split("\n")
        structure: dict[str, Any] = {
            "headers": [],
            "code_blocks": [],
            "tables": [],
            "lists": [],
            "paragraphs": [],
            "total_lines": len(lines),
        }

        in_code_block = False
        in_table = False
        current_list: dict[str, Any] | None = None
        current_paragraph: dict[str, int] | None = None

        for i, line in enumerate(lines):
            header_match = self.header_pattern.match(line)
            if header_match:
                if current_paragraph is not None:
                    current_paragraph["end"] = i - 1
                    structure["paragraphs"].append(current_paragraph)
                    current_paragraph = None
                structure["headers"].append(
                    {"line": i, "level": len(header_match.group(1)), "text": header_match.group(2).strip()}
                )
                continue

            if line.strip().startswith("```"):
                if current_paragraph is not None:
                    current_paragraph["end"] = i - 1
                    structure["paragraphs"].append(current_paragraph)
                    current_paragraph = None
                if not in_code_block:
                    code_start = i
                    in_code_block = True
                else:
                    structure["code_blocks"].append({"start": code_start, "end": i})
                    in_code_block = False
                continue
            if in_code_block:
                continue

            if self.table_pattern.match(line):
                if current_paragraph is not None:
                    current_paragraph["end"] = i - 1
                    structure["paragraphs"].append(current_paragraph)
                    current_paragraph = None
                if not in_table:
                    table_start = i
                    in_table = True
                continue
            if in_table and not line.strip():
                structure["tables"].append({"start": table_start, "end": i - 1})
                in_table = False
                continue

            if self.list_item_pattern.match(line):
                if current_paragraph is not None:
                    current_paragraph["end"] = i - 1
                    structure["paragraphs"].append(current_paragraph)
                    current_paragraph = None
                if current_list is None:
                    current_list = {"start": i, "items": []}
                current_list["items"].append(i)
                continue
            if current_list and not line.startswith(" "):
                current_list["end"] = i - 1
                structure["lists"].append(current_list)
                current_list = None

            if line.strip():
                if current_paragraph is None:
                    current_paragraph = {"start": i, "end": i}
                else:
                    current_paragraph["end"] = i
            elif current_paragraph is not None:
                structure["paragraphs"].append(current_paragraph)
                current_paragraph = None

        if in_table:
            structure["tables"].append({"start": table_start, "end": len(lines) - 1})
        if current_list:
            current_list["end"] = len(lines) - 1
            structure["lists"].append(current_list)
        if current_paragraph:
            structure["paragraphs"].append(current_paragraph)

        return DocumentStructure(**structure)

    def _analyze_document_structure(self, content: str) -> dict[str, Any]:
        """Backward-compatible wrapper for older notes."""

        return self.analyze_document_structure(content).__dict__


def main() -> None:
    text = "Python makes small tools pleasant. " * 20
    print(chunk_text(text, chunk_size=80, overlap=10))


if __name__ == "__main__":
    main()
