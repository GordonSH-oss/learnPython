"""Compact models used across lessons."""

from __future__ import annotations

import math

import torch
from torch import nn


class ImageClassifier(nn.Module):
    def __init__(self, channels: int = 1, num_classes: int = 10, dropout: float = 0.0) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(channels, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(nn.Flatten(), nn.Dropout(dropout), nn.Linear(32 * 4 * 4, num_classes))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(inputs))


class SequenceClassifier(nn.Module):
    def __init__(self, input_size: int = 1, hidden_size: int = 32, num_classes: int = 2) -> None:
        super().__init__()
        self.rnn = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.output = nn.Linear(hidden_size, num_classes)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        _, (hidden, _) = self.rnn(inputs)
        return self.output(hidden[-1])


class ScaledDotProductAttention(nn.Module):
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        scores = query @ key.transpose(-2, -1) / math.sqrt(query.shape[-1])
        if mask is not None:
            scores = scores.masked_fill(~mask, float("-inf"))
        weights = scores.softmax(dim=-1)
        return weights @ value, weights
