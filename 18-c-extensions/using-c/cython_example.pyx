# cython_example.pyx — Cython 示例
#
# Cython 让你用类 Python 语法写 C 性能的代码。
# 它会把 .pyx 文件编译成 C，再编译成共享库。
#
# 编译: python setup_cython.py build_ext --inplace
# 安装 Cython: pip install cython

"""
对比三种方式计算素数筛：
1. 纯 Python
2. Cython 无类型声明（略有加速）
3. Cython 有类型声明（大幅加速）
"""


# ============================================================
# 方式 1: 纯 Python 风格（Cython 仍会编译它，有一定加速）
# ============================================================

def primes_python_style(int n):
    """埃拉托斯特尼筛法 — 无 C 类型声明版本"""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    result = []
    for i in range(2, n + 1):
        if sieve[i]:
            result.append(i)
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return result


# ============================================================
# 方式 2: 使用 cdef 声明 C 类型（关键加速手段）
# ============================================================

def primes_cython(int n):
    """埃拉托斯特尼筛法 — 使用 C 类型声明"""
    cdef int i, j
    cdef list result = []

    # 用 bytearray 代替 list[bool]，内存更紧凑
    cdef bytearray sieve = bytearray(b'\x01') * (n + 1)
    sieve[0] = 0
    sieve[1] = 0

    for i in range(2, n + 1):
        if sieve[i]:
            result.append(i)
            for j in range(i * i, n + 1, i):
                sieve[j] = 0
    return result
