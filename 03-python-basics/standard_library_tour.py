"""A compact tour of standard-library tools used across this repo.

Run:
    python 03-python-basics/standard_library_tour.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import islice
import json
from pathlib import Path
import re


@lru_cache(maxsize=128)
def normalize_word(word: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", word.lower())


def word_counts(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    by_first_letter: defaultdict[str, list[str]] = defaultdict(list)
    for raw_word in re.findall(r"[A-Za-z0-9_]+", text):
        word = normalize_word(raw_word)
        counts[word] += 1
        by_first_letter[word[:1]].append(word)
    sample_groups = {key: len(words) for key, words in islice(by_first_letter.items(), 2)}
    print("sample group sizes:", sample_groups)
    return counts


def main() -> None:
    path = Path("README.md")
    data = {"file": str(path), "top_words": word_counts(path.read_text(encoding="utf-8")).most_common(5)}
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
