"""Demonstrate the native ``mymath`` extension built by ``make extension``."""

from array import array

import mymath


def main() -> None:
    print("module:", mymath.__file__)
    print("sum_squares(10) =", mymath.sum_squares(10))
    print("count_byte(b'banana', b'a') =", mymath.count_byte(b"banana", b"a"))
    print(
        "sum_doubles_buffer(array('d', [1, 2, 3.5])) =",
        mymath.sum_doubles_buffer(array("d", [1, 2, 3.5])),
    )

    try:
        mymath.sum_squares(-1)
    except ValueError as error:
        print("expected error:", error)


if __name__ == "__main__":
    main()
