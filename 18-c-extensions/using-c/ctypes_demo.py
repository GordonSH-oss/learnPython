"""
ctypes_demo.py — 用 ctypes 调用 C 共享库

ctypes 是 Python 标准库，不需要安装任何额外依赖。
适合调用已有的 C 库，或者快速实验 C 函数。

运行前先编译：
    macOS:  gcc -shared -o libarithmetic.dylib arithmetic.c
    Linux:  gcc -shared -fPIC -o libarithmetic.so arithmetic.c
"""

import ctypes
import time
import platform
import os

# ============================================================
# 1. 加载共享库
# ============================================================

lib_dir = os.path.dirname(os.path.abspath(__file__))

if platform.system() == "Darwin":
    lib_path = os.path.join(lib_dir, "libarithmetic.dylib")
else:
    lib_path = os.path.join(lib_dir, "libarithmetic.so")

if not os.path.exists(lib_path):
    print(f"共享库不存在: {lib_path}")
    print("请先编译: gcc -shared -o libarithmetic.dylib arithmetic.c")
    exit(1)

lib = ctypes.CDLL(lib_path)

# ============================================================
# 2. 声明函数签名（参数类型和返回类型）
# ============================================================

# int add(int a, int b)
lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
lib.add.restype = ctypes.c_int

# double divide(double a, double b)
lib.divide.argtypes = [ctypes.c_double, ctypes.c_double]
lib.divide.restype = ctypes.c_double

# long long sum_of_squares(int n)
lib.sum_of_squares.argtypes = [ctypes.c_int]
lib.sum_of_squares.restype = ctypes.c_longlong

# double array_sum(double *arr, int length)
lib.array_sum.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]
lib.array_sum.restype = ctypes.c_double

# int count_char(const char *s, char c)
lib.count_char.argtypes = [ctypes.c_char_p, ctypes.c_char]
lib.count_char.restype = ctypes.c_int

# ============================================================
# 3. 调用 C 函数
# ============================================================

print("=== 基本调用 ===")
print(f"add(3, 5) = {lib.add(3, 5)}")
print(f"divide(10.0, 3.0) = {lib.divide(10.0, 3.0):.4f}")
print(f"divide(1.0, 0.0) = {lib.divide(1.0, 0.0)}")

print("\n=== 字符串参数 ===")
text = b"hello world, hello python"
count = lib.count_char(text, b'l')
print(f"count_char('hello world, hello python', 'l') = {count}")

# ============================================================
# 4. 传递数组（指针）
# ============================================================

print("\n=== 数组传递 ===")
data = [1.0, 2.0, 3.0, 4.0, 5.0]
ArrayType = ctypes.c_double * len(data)
c_array = ArrayType(*data)
result = lib.array_sum(c_array, len(data))
print(f"array_sum([1,2,3,4,5]) = {result}")

# ============================================================
# 5. 性能对比：Python vs C
# ============================================================

print("\n=== 性能对比: sum_of_squares(10_000_000) ===")

N = 10_000_000

# Python 版本
start = time.perf_counter()
py_result = sum(i * i for i in range(1, N + 1))
py_time = time.perf_counter() - start

# C 版本
start = time.perf_counter()
c_result = lib.sum_of_squares(N)
c_time = time.perf_counter() - start

print(f"Python: {py_result}, 耗时 {py_time:.4f}s")
print(f"C:      {c_result}, 耗时 {c_time:.4f}s")
print(f"加速比: {py_time / c_time:.1f}x")

if py_result != c_result:
    print("\n⚠️  注意: C 结果与 Python 不同！")
    print("   原因: C 的 long long 是 64 位，大数会溢出。")
    print("   Python 的 int 是任意精度的，不会溢出。")
    print("   这正是理解 C 和 Python 差异的好例子。")
