"""Training policies that are independent from model architecture."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EarlyStopping:
    patience: int = 3
    mode: str = "max"
    best: float | None = None
    stale_epochs: int = 0

    def update(self, value: float) -> tuple[bool, bool]:
        improved = self.best is None or (value > self.best if self.mode == "max" else value < self.best)
        if improved:
            self.best = value
            self.stale_epochs = 0
        else:
            self.stale_epochs += 1
        return improved, self.stale_epochs >= self.patience
