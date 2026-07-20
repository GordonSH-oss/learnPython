"""Legacy setuptools entry point; the tutorial uses ``make extension`` by default."""

from setuptools import Extension, setup


setup(
    name="using-c-mymath",
    version="1.0.0",
    ext_modules=[Extension("mymath", ["mymath_module.c"])],
)
