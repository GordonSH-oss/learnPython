"""
setup_cython.py — 编译 Cython 扩展

使用方法：
    pip install cython
    python setup_cython.py build_ext --inplace

编译后可以 import cython_example
"""

from setuptools import setup
from Cython.Build import cythonize

setup(
    name="cython_example",
    ext_modules=cythonize("cython_example.pyx"),
)
