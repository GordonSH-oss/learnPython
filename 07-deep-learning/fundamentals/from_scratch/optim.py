"""Optimizers that update explicit parameter/gradient pairs."""

from __future__ import annotations

import numpy as np


Parameter = tuple[np.ndarray, np.ndarray]


class SGD:
    def __init__(self, parameters: list[Parameter], learning_rate: float = 0.1, weight_decay: float = 0.0) -> None:
        self.parameters = parameters
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay

    def step(self) -> None:
        for parameter, gradient in self.parameters:
            parameter -= self.learning_rate * (gradient + self.weight_decay * parameter)

    def zero_grad(self) -> None:
        for _, gradient in self.parameters:
            gradient.fill(0.0)


class Momentum(SGD):
    def __init__(
        self,
        parameters: list[Parameter],
        learning_rate: float = 0.1,
        momentum: float = 0.9,
        weight_decay: float = 0.0,
    ) -> None:
        super().__init__(parameters, learning_rate, weight_decay)
        self.momentum = momentum
        self.velocities = [np.zeros_like(parameter) for parameter, _ in parameters]

    def step(self) -> None:
        for velocity, (parameter, gradient) in zip(self.velocities, self.parameters):
            velocity *= self.momentum
            velocity += gradient + self.weight_decay * parameter
            parameter -= self.learning_rate * velocity
