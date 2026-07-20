"""Demonstrate the native ``mymath`` extension built by ``make extension``."""

import mymath


def main() -> None:
    print("module:", mymath.__file__)
    print("sum_squares(10) =", mymath.sum_squares(10))
    print("count_byte(b'banana', b'a') =", mymath.count_byte(b"banana", b"a"))

    try:
        mymath.sum_squares(-1)
    except ValueError as error:
        print("expected error:", error)


if __name__ == "__main__":
    main()
