"""Framework-independent deep-learning math exercises using NumPy."""

from __future__ import annotations

import numpy as np


def stable_softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=1, keepdims=True)


def numerical_gradient(function, value: np.ndarray, epsilon: float = 1e-5) -> np.ndarray:
    gradient = np.zeros_like(value, dtype=float)
    for index in np.ndindex(value.shape):
        original = value[index]
        value[index] = original + epsilon
        positive = function(value)
        value[index] = original - epsilon
        negative = function(value)
        value[index] = original
        gradient[index] = (positive - negative) / (2 * epsilon)
    return gradient


def fit_linear_regression(steps: int = 200, learning_rate: float = 0.1) -> tuple[float, float, list[float]]:
    x = np.linspace(-1, 1, 100).reshape(-1, 1)
    y = 3 * x + 2
    weight = np.zeros((1, 1))
    bias = np.zeros((1,))
    losses: list[float] = []

    for _ in range(steps):
        prediction = x @ weight + bias
        error = prediction - y
        losses.append(float(np.mean(error**2)))
        weight -= learning_rate * (2 / len(x)) * x.T @ error
        bias -= learning_rate * 2 * error.mean(axis=0)

    return float(weight.item()), float(bias.item()), losses


def main() -> None:
    batch = np.array([[1.0, 2.0], [3.0, 4.0]])
    weight = np.array([[0.5, -1.0, 2.0], [1.5, 0.0, -0.5]])
    output = batch @ weight
    probabilities = stable_softmax(output)

    quadratic = lambda value: float(np.sum(value**2))
    gradient = numerical_gradient(quadratic, np.array([1.0, 2.0]))
    learned_weight, learned_bias, losses = fit_linear_regression()

    print("linear output shape:", output.shape)
    print("softmax row sums:", probabilities.sum(axis=1))
    print("gradient of sum(x^2):", gradient)
    print(f"learned y = {learned_weight:.2f}x + {learned_bias:.2f}")
    print(f"loss: {losses[0]:.4f} -> {losses[-1]:.6f}")


if __name__ == "__main__":
    main()
