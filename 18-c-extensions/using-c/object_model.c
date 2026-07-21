/*
 * object_model.c — CPython 对象模型注释版
 *
 * 这不是可编译代码，也不是任何 CPython 版本的精确头文件。
 * 它只展示传统对象模型的概念关系。字段布局、引用计数实现和宏会随
 * CPython 版本、debug/free-threaded 等构建选项变化。
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
    Py_ssize_t ob_refcnt;    /* 概念上的引用管理状态。扩展必须使用
                                Py_INCREF/Py_DECREF 等公开 API，不能直接修改。 */

    PyTypeObject *ob_type;   /* 概念上的类型指针。type(x) 的完整实现还涉及
                                公开 API、类型对象和版本相关机制。 */
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
 * 下列宏是历史教学伪代码，不是当前 CPython 的可复制定义。
 * immortal objects 和 free-threaded 构建会改变内部细节。
 */

/* 概念：获得一个强引用时使用公开 Py_INCREF API。 */
#define Py_INCREF(op)  (++(op)->ob_refcnt)

/* 概念：释放拥有的强引用时使用公开 Py_DECREF API。 */
#define Py_DECREF(op)  do {           \
    if (--(op)->ob_refcnt == 0)       \
        _Py_Dealloc(op);   /* 引用归零，立即释放 */ \
} while (0)

/*
 * 例子：Python 代码 a = [1, 2, 3]
 *
 * C 层面发生了什么：
 * 更稳定的描述是：a 和 b 各自持有引用；删除名称会释放对应引用。
 * 对象何时析构还可能受到其他引用、容器、循环 GC 和实现优化影响。
 */
