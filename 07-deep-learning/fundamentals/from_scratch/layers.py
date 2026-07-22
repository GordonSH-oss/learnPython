"""Layers with explicit forward and backward passes."""

from __future__ import annotations

import numpy as np


class Linear:
    def __init__(self, input_features: int, output_features: int, seed: int = 0) -> None:
        rng = np.random.default_rng(seed)
        scale = np.sqrt(2.0 / input_features)
        self.weight = rng.normal(0.0, scale, (input_features, output_features))
        self.bias = np.zeros(output_features)
        self.grad_weight = np.zeros_like(self.weight)
        self.grad_bias = np.zeros_like(self.bias)
        self.inputs: np.ndarray | None = None

    def forward(self, inputs: np.ndarray, training: bool = True) -> np.ndarray:
        del training
        if inputs.ndim != 2 or inputs.shape[1] != self.weight.shape[0]:
            raise ValueError(f"expected inputs shaped (batch, {self.weight.shape[0]}), got {inputs.shape}")
        self.inputs = inputs
        return inputs @ self.weight + self.bias

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        if self.inputs is None:
            raise RuntimeError("forward must be called before backward")
        self.grad_weight[...] = self.inputs.T @ grad_output
        self.grad_bias[...] = grad_output.sum(axis=0)
        return grad_output @ self.weight.T

    def parameters(self) -> list[tuple[np.ndarray, np.ndarray]]:
        return [(self.weight, self.grad_weight), (self.bias, self.grad_bias)]


class ReLU:
    def __init__(self) -> None:
        self.mask: np.ndarray | None = None

    def forward(self, inputs: np.ndarray, training: bool = True) -> np.ndarray:
        del training
        self.mask = inputs > 0
        return np.maximum(inputs, 0)

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        if self.mask is None:
            raise RuntimeError("forward must be called before backward")
        return grad_output * self.mask

    def parameters(self) -> list[tuple[np.ndarray, np.ndarray]]:
        return []


class Sigmoid:
    def __init__(self) -> None:
        self.output: np.ndarray | None = None

    def forward(self, inputs: np.ndarray, training: bool = True) -> np.ndarray:
        del training
        positive = inputs >= 0
        output = np.empty_like(inputs, dtype=float)
        output[positive] = 1.0 / (1.0 + np.exp(-inputs[positive]))
        exponentials = np.exp(inputs[~positive])
        output[~positive] = exponentials / (1.0 + exponentials)
        self.output = output
        return output

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        if self.output is None:
            raise RuntimeError("forward must be called before backward")
        return grad_output * self.output * (1.0 - self.output)

    def parameters(self) -> list[tuple[np.ndarray, np.ndarray]]:
        return []


class Dropout:
    def __init__(self, probability: float = 0.5, seed: int = 0) -> None:
        if not 0 <= probability < 1:
            raise ValueError("probability must be in [0, 1)")
        self.probability = probability
        self.rng = np.random.default_rng(seed)
        self.mask: np.ndarray | None = None

    def forward(self, inputs: np.ndarray, training: bool = True) -> np.ndarray:
        if not training or self.probability == 0:
            self.mask = None
            return inputs
        keep_probability = 1.0 - self.probability
        self.mask = (self.rng.random(inputs.shape) < keep_probability) / keep_probability
        return inputs * self.mask

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        return grad_output if self.mask is None else grad_output * self.mask

    def parameters(self) -> list[tuple[np.ndarray, np.ndarray]]:
        return []
