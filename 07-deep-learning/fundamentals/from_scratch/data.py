"""Deterministic synthetic data for offline experiments."""

from __future__ import annotations

import numpy as np


def make_spiral(samples_per_class: int = 100, classes: int = 3, noise: float = 0.2, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    features = np.zeros((samples_per_class * classes, 2), dtype=float)
    labels = np.zeros(samples_per_class * classes, dtype=int)
    for class_index in range(classes):
        rows = slice(class_index * samples_per_class, (class_index + 1) * samples_per_class)
        radius = np.linspace(0.05, 1.0, samples_per_class)
        angle = np.linspace(class_index * 4, (class_index + 1) * 4, samples_per_class)
        angle += rng.normal(0.0, noise, samples_per_class)
        features[rows] = np.column_stack((radius * np.sin(angle), radius * np.cos(angle)))
        labels[rows] = class_index
    return features, labels


def train_validation_split(
    features: np.ndarray, labels: np.ndarray, validation_fraction: float = 0.2, seed: int = 0
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be between 0 and 1")
    indices = np.random.default_rng(seed).permutation(len(features))
    validation_size = max(1, int(len(features) * validation_fraction))
    validation_indices, train_indices = indices[:validation_size], indices[validation_size:]
    return features[train_indices], features[validation_indices], labels[train_indices], labels[validation_indices]
