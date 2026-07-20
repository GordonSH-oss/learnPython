/*
 * mymath_module.c — Python C 扩展模块示例
 *
 * 展示 Python/C API 的标准用法：
 * - 解析 Python 参数
 * - 返回 Python 对象
 * - 注册模块方法
 * - 异常处理
 *
 * 编译: python setup_mymath.py build_ext --inplace
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* ============================================================
 * 函数实现
 * ============================================================ */

/* 斐波那契数列（演示纯 C 计算的加速） */
static PyObject *mymath_fibonacci(PyObject *self, PyObject *args) {
    int n;

    /* 解析参数：i = int */
    if (!PyArg_ParseTuple(args, "i", &n))
        return NULL;

    if (n < 0) {
        PyErr_SetString(PyExc_ValueError, "n must be non-negative");
        return NULL;
    }

    long long a = 0, b = 1;
    for (int i = 0; i < n; i++) {
        long long temp = a + b;
        a = b;
        b = temp;
    }

    return PyLong_FromLongLong(a);
}

/* 判断素数 */
static PyObject *mymath_is_prime(PyObject *self, PyObject *args) {
    long long n;

    if (!PyArg_ParseTuple(args, "L", &n))
        return NULL;

    if (n < 2)
        Py_RETURN_FALSE;

    for (long long i = 2; i * i <= n; i++) {
        if (n % i == 0)
            Py_RETURN_FALSE;
    }

    Py_RETURN_TRUE;
}

/* 快速幂 */
static PyObject *mymath_power(PyObject *self, PyObject *args) {
    long long base, exp;

    if (!PyArg_ParseTuple(args, "LL", &base, &exp))
        return NULL;

    if (exp < 0) {
        PyErr_SetString(PyExc_ValueError, "exponent must be non-negative");
        return NULL;
    }

    long long result = 1;
    while (exp > 0) {
        if (exp % 2 == 1)
            result *= base;
        base *= base;
        exp /= 2;
    }

    return PyLong_FromLongLong(result);
}

/* ============================================================
 * 模块方法表
 * ============================================================ */

static PyMethodDef MyMathMethods[] = {
    {"fibonacci", mymath_fibonacci, METH_VARARGS,
     "fibonacci(n) -> int\n\nReturn the n-th Fibonacci number."},
    {"is_prime", mymath_is_prime, METH_VARARGS,
     "is_prime(n) -> bool\n\nReturn True if n is a prime number."},
    {"power", mymath_power, METH_VARARGS,
     "power(base, exp) -> int\n\nFast exponentiation using binary method."},
    {NULL, NULL, 0, NULL}
};

/* ============================================================
 * 模块定义
 * ============================================================ */

static struct PyModuleDef mymathmodule = {
    PyModuleDef_HEAD_INIT,
    "mymath",
    "A sample C extension module for math operations.",
    -1,
    MyMathMethods
};

/* 模块初始化函数 — 函数名必须是 PyInit_<模块名> */
PyMODINIT_FUNC PyInit_mymath(void) {
    return PyModule_Create(&mymathmodule);
}
