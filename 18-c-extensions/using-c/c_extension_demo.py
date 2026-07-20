"""
c_extension_demo.py — 演示 C 扩展模块的使用和性能对比

运行前先编译:
    python setup_mymath.py build_ext --inplace
"""

import time

try:
    import mymath
except ImportError:
    print("mymath 模块未编译，请先运行:")
    print("  python setup_mymath.py build_ext --inplace")
    exit(1)

# ============================================================
# 1. 基本使用
# ============================================================

print("=== C 扩展模块 mymath ===")
print(f"fibonacci(10) = {mymath.fibonacci(10)}")
print(f"fibonacci(50) = {mymath.fibonacci(50)}")
print(f"is_prime(97) = {mymath.is_prime(97)}")
print(f"is_prime(100) = {mymath.is_prime(100)}")
print(f"power(2, 20) = {mymath.power(2, 20)}")

# ============================================================
# 2. 性能对比: 斐波那契
# ============================================================

def py_fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print("\n=== 性能对比: fibonacci(100000) ===")

start = time.perf_counter()
for _ in range(100):
    py_fibonacci(1000)
py_time = time.perf_counter() - start

start = time.perf_counter()
for _ in range(100):
    mymath.fibonacci(1000)
c_time = time.perf_counter() - start

print(f"Python: {py_time:.4f}s")
print(f"C 扩展: {c_time:.4f}s")
print(f"加速比: {py_time / c_time:.1f}x")
