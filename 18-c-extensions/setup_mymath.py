"""
setup_mymath.py — 编译 C 扩展模块

使用方法：
    python setup_mymath.py build_ext --inplace

编译完成后会生成 mymath.cpython-*.so（或 .pyd），可以直接 import mymath
"""

from setuptools import setup, Extension

mymath_ext = Extension(
    "mymath",
    sources=["mymath_module.c"],
)

setup(
    name="mymath",
    version="1.0",
    description="Sample C extension module",
    ext_modules=[mymath_ext],
)
