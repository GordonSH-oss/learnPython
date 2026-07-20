"""Build the optional Cython example with ``make cython``."""

from Cython.Build import cythonize
from setuptools import Extension, setup


setup(
    name="using-c-cython-example",
    version="1.0.0",
    ext_modules=cythonize(
        [Extension("cython_example", ["cython_example.pyx"])],
        compiler_directives={"language_level": "3"},
    ),
)
