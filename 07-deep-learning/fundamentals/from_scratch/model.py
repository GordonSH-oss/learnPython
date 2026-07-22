"""A sequential multi-layer perceptron."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from .layers import Dropout, Linear, ReLU


class MLP:
    def __init__(
        self,
        input_features: int,
        hidden_features: Iterable[int],
        output_features: int,
        dropout: float = 0.0,
        seed: int = 0,
    ) -> None:
        sizes = [input_features, *hidden_features, output_features]
        self.layers: list[object] = []
        for index, (fan_in, fan_out) in enumerate(zip(sizes, sizes[1:])):
            self.layers.append(Linear(fan_in, fan_out, seed + index))
            if index < len(sizes) - 2:
                self.layers.append(ReLU())
                if dropout:
                    self.layers.append(Dropout(dropout, seed + 100 + index))

    def forward(self, inputs: np.ndarray, training: bool = True) -> np.ndarray:
        output = inputs
        for layer in self.layers:
            output = layer.forward(output, training=training)  # type: ignore[attr-defined]
        return output

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        gradient = grad_output
        for layer in reversed(self.layers):
            gradient = layer.backward(gradient)  # type: ignore[attr-defined]
        return gradient

    def parameters(self) -> list[tuple[np.ndarray, np.ndarray]]:
        parameters: list[tuple[np.ndarray, np.ndarray]] = []
        for layer in self.layers:
            parameters.extend(layer.parameters())  # type: ignore[attr-defined]
        return parameters

    def predict(self, inputs: np.ndarray) -> np.ndarray:
        return self.forward(inputs, training=False).argmax(axis=1)
