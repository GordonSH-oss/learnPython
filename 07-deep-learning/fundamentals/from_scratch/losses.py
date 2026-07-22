"""Numerically stable losses and their analytic gradients."""

from __future__ import annotations

import numpy as np


def softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=1, keepdims=True)


class CrossEntropyLoss:
    def __init__(self) -> None:
        self.probabilities: np.ndarray | None = None
        self.targets: np.ndarray | None = None

    def forward(self, logits: np.ndarray, targets: np.ndarray) -> float:
        if logits.ndim != 2 or targets.shape != (len(logits),):
            raise ValueError("logits must be 2D and targets must contain one class index per row")
        self.probabilities = softmax(logits)
        self.targets = targets.astype(int, copy=False)
        chosen = self.probabilities[np.arange(len(logits)), self.targets]
        return float(-np.log(np.clip(chosen, 1e-12, 1.0)).mean())

    def backward(self) -> np.ndarray:
        if self.probabilities is None or self.targets is None:
            raise RuntimeError("forward must be called before backward")
        gradient = self.probabilities.copy()
        gradient[np.arange(len(gradient)), self.targets] -= 1.0
        return gradient / len(gradient)


class MSELoss:
    def __init__(self) -> None:
        self.difference: np.ndarray | None = None

    def forward(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        self.difference = predictions - targets
        return float(np.mean(self.difference**2))

    def backward(self) -> np.ndarray:
        if self.difference is None:
            raise RuntimeError("forward must be called before backward")
        return 2.0 * self.difference / self.difference.size
