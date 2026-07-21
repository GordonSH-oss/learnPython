"""Load the arithmetic C ABI and expose small Python wrappers."""

from __future__ import annotations

import ctypes
import os
import platform
from array import array
from pathlib import Path
from typing import Iterable


def _library_path() -> Path:
    build = Path(os.environ.get("USING_C_BUILD", Path(__file__).parent / "build"))
    name = "libarithmetic.dylib" if platform.system() == "Darwin" else "libarithmetic.so"
    return build / name


def _load_library() -> ctypes.CDLL:
    path = _library_path()
    if not path.exists():
        raise RuntimeError(f"shared library not found: {path}; run `make ctypes`")

    library = ctypes.CDLL(path)
    int32_pointer = ctypes.POINTER(ctypes.c_int32)
    int64_pointer = ctypes.POINTER(ctypes.c_int64)
    double_pointer = ctypes.POINTER(ctypes.c_double)

    library.add_int32.argtypes = [ctypes.c_int32, ctypes.c_int32, int32_pointer]
    library.add_int32.restype = ctypes.c_int
    library.sum_squares.argtypes = [ctypes.c_int32, int64_pointer]
    library.sum_squares.restype = ctypes.c_int
    library.sum_doubles.argtypes = [double_pointer, ctypes.c_size_t, double_pointer]
    library.sum_doubles.restype = ctypes.c_int
    library.count_byte.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char]
    library.count_byte.restype = ctypes.c_size_t
    return library


LIB = _load_library()


def _require_int32(value: int, name: str) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    if not -(2**31) <= value < 2**31:
        raise OverflowError(f"{name} does not fit in a signed 32-bit integer")
    return value


def add_int32(left: int, right: int) -> int:
    left = _require_int32(left, "left")
    right = _require_int32(right, "right")
    result = ctypes.c_int32()
    status = LIB.add_int32(left, right, ctypes.byref(result))
    if status == -2:
        raise OverflowError("32-bit signed addition overflowed")
    if status != 0:
        raise RuntimeError(f"add_int32 failed with status {status}")
    return result.value


def sum_squares(limit: int) -> int:
    limit = _require_int32(limit, "limit")
    result = ctypes.c_int64()
    status = LIB.sum_squares(limit, ctypes.byref(result))
    if status == -1:
        raise ValueError("limit must be a non-negative 32-bit integer")
    if status == -2:
        raise OverflowError("result does not fit in a signed 64-bit integer")
    return result.value


def sum_doubles(values: Iterable[float]) -> float:
    """Copy an iterable into a temporary C array, then sum it."""
    data = [float(value) for value in values]
    array_type = ctypes.c_double * len(data)
    c_values = array_type(*data)
    result = ctypes.c_double()
    status = LIB.sum_doubles(c_values, len(data), ctypes.byref(result))
    if status != 0:
        raise RuntimeError(f"sum_doubles failed with status {status}")
    return result.value


def sum_doubles_buffer(values: object) -> float:
    """Sum a writable, C-contiguous native-double buffer without copying it."""
    view = memoryview(values)
    if view.ndim != 1 or not view.c_contiguous:
        raise ValueError("values must be a one-dimensional C-contiguous buffer")
    if view.format != "d" or view.itemsize != ctypes.sizeof(ctypes.c_double):
        raise TypeError("values must expose native C doubles (format 'd')")
    if view.readonly:
        raise TypeError("ctypes.from_buffer requires a writable buffer")

    length = view.nbytes // view.itemsize
    result = ctypes.c_double()
    if length == 0:
        pointer = None
    else:
        array_type = ctypes.c_double * length
        pointer = array_type.from_buffer(view)
    status = LIB.sum_doubles(pointer, length, ctypes.byref(result))
    if status != 0:
        raise RuntimeError(f"sum_doubles failed with status {status}")
    return result.value


def count_byte(data: bytes, needle: bytes) -> int:
    if not isinstance(data, bytes) or not isinstance(needle, bytes):
        raise TypeError("data and needle must be bytes")
    if len(needle) != 1:
        raise ValueError("needle must contain exactly one byte")
    return LIB.count_byte(data, len(data), needle)


if __name__ == "__main__":
    print("add_int32(3, 5) =", add_int32(3, 5))
    print("sum_squares(10) =", sum_squares(10))
    print("sum_doubles([1, 2, 3.5]) =", sum_doubles([1, 2, 3.5]))
    print(
        "sum_doubles_buffer(array('d', [1, 2, 3.5])) =",
        sum_doubles_buffer(array("d", [1, 2, 3.5])),
    )
    print("count_byte(b'banana', b'a') =", count_byte(b"banana", b"a"))
