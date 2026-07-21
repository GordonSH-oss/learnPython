#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <limits.h>
#include <stdint.h>
#include <string.h>

static PyObject *mymath_sum_squares(PyObject *module, PyObject *argument) {
    (void)module;
    long long limit = PyLong_AsLongLong(argument);
    if (limit == -1 && PyErr_Occurred()) {
        return NULL;
    }
    if (limit < 0) {
        PyErr_SetString(PyExc_ValueError, "limit must be non-negative");
        return NULL;
    }
    if (limit > INT32_MAX) {
        PyErr_SetString(PyExc_OverflowError, "limit exceeds INT32_MAX");
        return NULL;
    }

    int overflowed = 0;
    int64_t total = 0;
    Py_BEGIN_ALLOW_THREADS
    for (int64_t value = 1; value <= limit; ++value) {
        int64_t square = value * value;
        if (total > INT64_MAX - square) {
            overflowed = 1;
            break;
        }
        total += square;
    }
    Py_END_ALLOW_THREADS

    if (overflowed) {
        PyErr_SetString(PyExc_OverflowError,
                        "result does not fit in a signed 64-bit integer");
        return NULL;
    }
    return PyLong_FromLongLong(total);
}

static PyObject *mymath_count_byte(PyObject *module, PyObject *args) {
    (void)module;
    const char *data;
    const char *needle;
    Py_ssize_t data_length;
    Py_ssize_t needle_length;

    if (!PyArg_ParseTuple(args, "y#y#", &data, &data_length,
                          &needle, &needle_length)) {
        return NULL;
    }
    if (needle_length != 1) {
        PyErr_SetString(PyExc_ValueError,
                        "needle must contain exactly one byte");
        return NULL;
    }

    Py_ssize_t count = 0;
    for (Py_ssize_t index = 0; index < data_length; ++index) {
        if (data[index] == needle[0]) {
            ++count;
        }
    }
    return PyLong_FromSsize_t(count);
}

static PyObject *mymath_sum_doubles_buffer(PyObject *module, PyObject *argument) {
    (void)module;
    Py_buffer view;
    if (PyObject_GetBuffer(argument, &view,
                           PyBUF_FORMAT | PyBUF_C_CONTIGUOUS) < 0) {
        return NULL;
    }

    PyObject *result = NULL;
    if (view.ndim != 1 || view.itemsize != (Py_ssize_t)sizeof(double) ||
        view.format == NULL || strcmp(view.format, "d") != 0 ||
        view.len % (Py_ssize_t)sizeof(double) != 0) {
        PyErr_SetString(PyExc_TypeError,
                        "values must be a one-dimensional contiguous "
                        "native-double buffer");
        goto cleanup;
    }

    const double *values = view.buf;
    Py_ssize_t length = view.len / (Py_ssize_t)sizeof(double);
    double total = 0.0;
    for (Py_ssize_t index = 0; index < length; ++index) {
        total += values[index];
    }
    result = PyFloat_FromDouble(total);

cleanup:
    PyBuffer_Release(&view);
    return result;
}

static PyMethodDef mymath_methods[] = {
    {
        "sum_squares",
        mymath_sum_squares,
        METH_O,
        PyDoc_STR("sum_squares(limit, /) -> int\n"
                  "Return 1**2 + ... + limit**2 using a C loop."),
    },
    {
        "count_byte",
        mymath_count_byte,
        METH_VARARGS,
        PyDoc_STR("count_byte(data, needle, /) -> int\n"
                  "Count a one-byte needle in a bytes-like object."),
    },
    {
        "sum_doubles_buffer",
        mymath_sum_doubles_buffer,
        METH_O,
        PyDoc_STR("sum_doubles_buffer(values, /) -> float\n"
                  "Sum a contiguous native-double buffer without copying."),
    },
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef mymath_module = {
    PyModuleDef_HEAD_INIT,
    "mymath",
    "Small examples for learning the Python/C API.",
    0,
    mymath_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

PyMODINIT_FUNC PyInit_mymath(void) {
    return PyModule_Create(&mymath_module);
}
