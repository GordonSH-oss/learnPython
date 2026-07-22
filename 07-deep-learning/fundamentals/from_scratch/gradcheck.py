"""Finite-difference checks for explicit gradients."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def gradient_check(
    function: Callable[[], float], parameter: np.ndarray, analytic_gradient: np.ndarray, epsilon: float = 1e-5
) -> float:
    numerical = np.zeros_like(parameter, dtype=float)
    for index in np.ndindex(parameter.shape):
        original = parameter[index]
        parameter[index] = original + epsilon
        positive = function()
        parameter[index] = original - epsilon
        negative = function()
        parameter[index] = original
        numerical[index] = (positive - negative) / (2 * epsilon)
    denominator = np.maximum(1e-8, np.abs(numerical) + np.abs(analytic_gradient))
    return float(np.max(np.abs(numerical - analytic_gradient) / denominator))
