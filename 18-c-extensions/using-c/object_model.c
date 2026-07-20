/*
 * object_model.c — CPython 对象模型注释版
 *
 * 这不是可编译的代码，而是从 CPython 源码中提取的关键片段加注释。
 * 用于帮助理解 Python 对象在 C 层面的表示。
 *
 * 对应源码: Include/object.h, Objects/object.c
 */

/* ============================================================
 * 1. 所有 Python 对象的基础结构
 * ============================================================
 *
 * 无论是 int、str、list 还是自定义类的实例，
 * 在内存中开头都是这个结构。
 */

typedef struct _object {
    Py_ssize_t ob_refcnt;    /* 引用计数。每次有变量指向这个对象就 +1,
                                变量删除或离开作用域就 -1,
                                到 0 时立即释放内存。 */

    PyTypeObject *ob_type;   /* 类型指针。指向一个描述"这是什么类型"的对象。
                                Python 中 type(x) 就是读这个字段。 */
} PyObject;


/* ============================================================
 * 2. 变长对象（list, tuple, str 等）
 * ============================================================ */

typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size;      /* 当前元素个数。len(x) 就是读这个字段。
                                所以 len() 是 O(1) 的！ */
} PyVarObject;


/* ============================================================
 * 3. 引用计数的核心操作
 * ============================================================
 *
 * 这就是 Python "不需要手动 malloc/free" 的秘密。
 */

/* 增加引用 — 当一个新变量指向此对象时调用 */
#define Py_INCREF(op)  (++(op)->ob_refcnt)

/* 减少引用 — 当变量不再需要此对象时调用 */
#define Py_DECREF(op)  do {           \
    if (--(op)->ob_refcnt == 0)       \
        _Py_Dealloc(op);   /* 引用归零，立即释放 */ \
} while (0)

/*
 * 例子：Python 代码 a = [1, 2, 3]
 *
 * C 层面发生了什么：
 * 1. 创建 PyListObject, ob_refcnt = 1（变量 a 持有）
 * 2. 如果 b = a，则 Py_INCREF(list), ob_refcnt = 2
 * 3. del a → Py_DECREF(list), ob_refcnt = 1（还没释放）
 * 4. del b → Py_DECREF(list), ob_refcnt = 0 → 释放内存
 */
