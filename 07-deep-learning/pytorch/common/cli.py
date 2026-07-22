"""Shared command-line options for training examples."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainConfig:
    dataset: str
    data_dir: Path
    epochs: int
    batch_size: int
    device: str
    output_dir: Path
    quick: bool
    resume: Path | None
    seed: int
    patience: int


def parse_train_config(default_dataset: str, description: str) -> TrainConfig:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--dataset", default=default_dataset)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parents[1] / "data")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda", "mps"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parents[1] / "artifacts")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--patience", type=int, default=3)
    args = parser.parse_args()
    return TrainConfig(**vars(args))
