"""Compare equivalent Python, ctypes, and Python/C API implementations."""

from __future__ import annotations

import statistics
import time
from collections.abc import Callable

import mymath

from ctypes_demo import sum_squares as ctypes_sum_squares


LIMIT = 1_000_000
REPEATS = 7


def python_sum_squares(limit: int) -> int:
    total = 0
    for value in range(1, limit + 1):
        total += value * value
    return total


def median_seconds(function: Callable[[int], int], argument: int) -> float:
    samples = []
    for _ in range(REPEATS):
        started = time.perf_counter_ns()
        function(argument)
        samples.append((time.perf_counter_ns() - started) / 1_000_000_000)
    return statistics.median(samples)


def main() -> None:
    implementations = {
        "Python loop": python_sum_squares,
        "ctypes": ctypes_sum_squares,
        "Python/C API": mymath.sum_squares,
    }
    expected = python_sum_squares(LIMIT)
    for name, function in implementations.items():
        actual = function(LIMIT)
        if actual != expected:
            raise AssertionError(f"{name} returned {actual}, expected {expected}")

    timings = {
        name: median_seconds(function, LIMIT)
        for name, function in implementations.items()
    }
    baseline = timings["Python loop"]
    print(f"sum of squares from 1 through {LIMIT:,}; median of {REPEATS} runs")
    print(f"{'implementation':<18} {'seconds':>10} {'speedup':>10}")
    for name, seconds in timings.items():
        print(f"{name:<18} {seconds:>10.6f} {baseline / seconds:>9.1f}x")


if __name__ == "__main__":
    main()
