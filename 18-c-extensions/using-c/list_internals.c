/*
 * list_internals.c — CPython list 内部实现注释版
 *
 * 从 Objects/listobject.c 提取的关键实现，展示：
 * - list 的内存布局
 * - append 的 O(1) 均摊复杂度如何实现
 * - 扩容策略
 *
 * 对应源码: Include/cpython/listobject.h, Objects/listobject.c
 */

/* ============================================================
 * 1. list 的内存布局
 * ============================================================ */

typedef struct {
    PyObject_VAR_HEAD          /* 包含 ob_refcnt, ob_type, ob_size */
    PyObject **ob_item;        /* 指向元素数组的指针。
                                  list 就是一个 PyObject* 的数组！ */
    Py_ssize_t allocated;      /* 数组实际分配的容量（>= ob_size）*/
} PyListObject;

/*
 * 关键区别：
 *   ob_size = 当前元素个数（你 len() 看到的）
 *   allocated = 底层数组的容量（通常比 ob_size 大）
 *
 * 这就是为什么 append 不是每次都要 realloc。
 */


/* ============================================================
 * 2. 扩容策略 — list_resize()
 * ============================================================ */

static int
list_resize(PyListObject *self, Py_ssize_t newsize)
{
    Py_ssize_t new_allocated;
    PyObject **items;

    Py_ssize_t allocated = self->allocated;

    /* 如果新大小在已分配空间的一半到全部之间，直接改 ob_size 就行 */
    if (allocated >= newsize && newsize >= (allocated >> 1)) {
        self->ob_size = newsize;
        return 0;
    }

    /* 核心扩容公式: new = newsize + newsize/8 + 小常数
     * 这给出约 12.5% 的过分配，是 O(1) 均摊的关键 */
    new_allocated = (newsize >> 3) + (newsize < 9 ? 3 : 6);
    new_allocated += newsize;

    items = (PyObject **)PyMem_Realloc(
        self->ob_item,
        new_allocated * sizeof(PyObject *)
    );
    if (items == NULL) return -1;

    self->ob_item = items;
    self->ob_size = newsize;
    self->allocated = new_allocated;
    return 0;
}

/*
 * 扩容序列举例（实际容量）:
 *   0 → 4 → 8 → 16 → 25 → 35 → 46 → 58 → 72 → 88 ...
 *
 * 对比 Java ArrayList 的 1.5x 策略和 C++ vector 的 2x 策略，
 * CPython 选择了更保守的 ~1.125x，节省内存。
 */
