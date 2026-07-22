"""Mini-batch training utilities."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np

from .losses import CrossEntropyLoss
from .model import MLP
from .optim import SGD


def accuracy(predictions: np.ndarray, targets: np.ndarray) -> float:
    return float(np.mean(predictions == targets))


def iterate_minibatches(
    features: np.ndarray, labels: np.ndarray, batch_size: int, seed: int
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    indices = np.random.default_rng(seed).permutation(len(features))
    for start in range(0, len(indices), batch_size):
        batch = indices[start : start + batch_size]
        yield features[batch], labels[batch]


def train_classifier(
    model: MLP,
    features: np.ndarray,
    labels: np.ndarray,
    optimizer: SGD,
    epochs: int = 100,
    batch_size: int = 32,
    seed: int = 0,
) -> dict[str, list[float]]:
    history = {"loss": [], "accuracy": []}
    loss_function = CrossEntropyLoss()
    for epoch in range(epochs):
        for batch_features, batch_labels in iterate_minibatches(features, labels, batch_size, seed + epoch):
            logits = model.forward(batch_features, training=True)
            loss_function.forward(logits, batch_labels)
            model.backward(loss_function.backward())
            optimizer.step()
            optimizer.zero_grad()
        logits = model.forward(features, training=False)
        history["loss"].append(loss_function.forward(logits, labels))
        history["accuracy"].append(accuracy(logits.argmax(axis=1), labels))
    return history
