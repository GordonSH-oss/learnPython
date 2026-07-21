/*
 * list_internals.c — CPython list 内部实现注释版
 *
 * 概念伪代码，展示：
 * - list 的内存布局
 * - append 的 O(1) 均摊复杂度如何实现
 * - 扩容策略
 *
 * 精确布局和扩容算法必须查看目标 CPython tag 的
 * Include/cpython/listobject.h 与 Objects/listobject.c。
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

    /* 伪代码：选择大于 newsize 的容量并检查溢出。
     * 精确公式、对齐和是否过分配属于版本敏感实现细节。 */
    new_allocated = choose_capacity_for_current_version(newsize);

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
 * 稳定结论：list 使用动态引用数组，append 通常具有均摊 O(1) 复杂度。
 * 不要把某个版本观察到的容量序列写进扩展 ABI 或业务逻辑。
 */
