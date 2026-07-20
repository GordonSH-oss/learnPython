"""Contract tests shared by the ctypes and Python/C API examples."""

import unittest

import mymath

import ctypes_demo


class CtypesTests(unittest.TestCase):
    def test_add_and_overflow(self):
        self.assertEqual(ctypes_demo.add_int32(20, 22), 42)
        with self.assertRaises(OverflowError):
            ctypes_demo.add_int32(2**31 - 1, 1)
        with self.assertRaises(OverflowError):
            ctypes_demo.add_int32(2**32, 0)
        with self.assertRaises(TypeError):
            ctypes_demo.add_int32("20", 22)

    def test_sum_squares(self):
        self.assertEqual(ctypes_demo.sum_squares(10), 385)
        with self.assertRaises(ValueError):
            ctypes_demo.sum_squares(-1)
        with self.assertRaises(OverflowError):
            ctypes_demo.sum_squares(2**31)

    def test_array_and_embedded_nul(self):
        self.assertAlmostEqual(ctypes_demo.sum_doubles([1, 2.5, -0.5]), 3.0)
        self.assertEqual(ctypes_demo.count_byte(b"a\x00a", b"a"), 2)


class PythonCApiTests(unittest.TestCase):
    def test_sum_squares(self):
        self.assertEqual(mymath.sum_squares(10), 385)
        with self.assertRaises(ValueError):
            mymath.sum_squares(-1)
        with self.assertRaises(TypeError):
            mymath.sum_squares("10")

    def test_count_byte(self):
        self.assertEqual(mymath.count_byte(b"a\x00a", b"a"), 2)
        with self.assertRaises(ValueError):
            mymath.count_byte(b"abc", b"ab")


if __name__ == "__main__":
    unittest.main()
