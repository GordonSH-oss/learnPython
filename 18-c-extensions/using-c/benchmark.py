"""Compare equivalent Python, ctypes, and Python/C API implementations."""

from __future__ import annotations

import statistics
import time
from array import array
from collections.abc import Callable

import mymath

from ctypes_demo import (
    sum_doubles as ctypes_sum_doubles_copy,
    sum_doubles_buffer as ctypes_sum_doubles_buffer,
    sum_squares as ctypes_sum_squares,
)


LIMIT = 1_000_000
REPEATS = 7
BUFFER_LENGTH = 250_000


def python_sum_squares(limit: int) -> int:
    total = 0
    for value in range(1, limit + 1):
        total += value * value
    return total


def median_seconds(function: Callable[[int], int], argument: int) -> float:
    function(argument)  # warm up import-time and first-call effects
    samples = []
    for _ in range(REPEATS):
        started = time.perf_counter_ns()
        function(argument)
        samples.append((time.perf_counter_ns() - started) / 1_000_000_000)
    return statistics.median(samples)


def median_call(function: Callable[[], object]) -> float:
    function()
    samples = []
    for _ in range(REPEATS):
        started = time.perf_counter_ns()
        function()
        samples.append((time.perf_counter_ns() - started) / 1_000_000_000)
    return statistics.median(samples)


def python_sum_doubles(values: array[float]) -> float:
    total = 0.0
    for value in values:
        total += value
    return total


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

    values = array("d", (index * 0.25 for index in range(BUFFER_LENGTH)))
    expected_buffer_sum = python_sum_doubles(values)
    buffer_implementations: dict[str, Callable[[], float]] = {
        "Python loop": lambda: python_sum_doubles(values),
        "ctypes copy": lambda: ctypes_sum_doubles_copy(values),
        "ctypes buffer": lambda: ctypes_sum_doubles_buffer(values),
        "C API buffer": lambda: mymath.sum_doubles_buffer(values),
    }
    for name, function in buffer_implementations.items():
        actual = function()
        if actual != expected_buffer_sum:
            raise AssertionError(f"{name} returned {actual}, expected {expected_buffer_sum}")

    buffer_timings = {
        name: median_call(function)
        for name, function in buffer_implementations.items()
    }
    buffer_baseline = buffer_timings["Python loop"]
    print(f"\nsum {BUFFER_LENGTH:,} native doubles; median of {REPEATS} runs")
    print(f"{'implementation':<18} {'seconds':>10} {'speedup':>10}")
    for name, seconds in buffer_timings.items():
        print(f"{name:<18} {seconds:>10.6f} {buffer_baseline / seconds:>9.1f}x")


if __name__ == "__main__":
    main()
