# CPython 源码阅读指南

## CPython 是什么？

CPython 是 Python 的官方实现，用 C 语言编写。当你运行 `python xxx.py` 时，
实际在运行的就是 CPython 解释器。理解它的源码能让你：

- 真正明白 Python 的语义（为什么 list 比 tuple 慢？为什么 dict 查找是 O(1)？）
- 理解 GIL、引用计数、垃圾回收
- 写出更高效的 Python 代码
- 具备给 CPython 贡献代码的能力

## 获取源码

```bash
git clone https://github.com/python/cpython.git
cd cpython
git checkout v3.12.0  # 选一个稳定版本
```

## 目录结构

```
cpython/
├── Include/          # 公开的 C 头文件（PyObject, PyListObject 等）
│   ├── object.h      # PyObject 基础定义
│   ├── listobject.h  # list 类型声明
│   └── dictobject.h  # dict 类型声明
├── Objects/          # 内建对象的实现（最重要！）
│   ├── object.c      # 引用计数、通用对象操作
│   ├── listobject.c  # list 的全部实现
│   ├── dictobject.c  # dict 的全部实现
│   ├── longobject.c  # int 的实现（Python 3 的 int 是大整数）
│   └── typeobject.c  # type 和类机制
├── Python/           # 解释器核心
│   ├── ceval.c       # 字节码执行循环（巨大但核心）
│   ├── compile.c     # AST → 字节码编译器
│   └── import.c      # import 机制
├── Modules/          # 标准库的 C 实现
│   ├── _io/          # io 模块
│   ├── _json.c       # json 的 C 加速
│   └── mathmodule.c  # math 模块
├── Parser/           # 语法解析器
└── Lib/              # 标准库的 Python 实现
```

## 核心概念 1：PyObject — 万物之源

Python 中所有值都是对象，在 C 层面都是 `PyObject *` 指针。

```c
// Include/object.h（简化版）
typedef struct _object {
    Py_ssize_t ob_refcnt;    // 引用计数
    PyTypeObject *ob_type;   // 类型指针（指向 int、str、list 等类型对象）
} PyObject;
```

**关键洞察：**
- 每个 Python 对象的内存开头都是这个结构
- `ob_refcnt` 降到 0 时对象被释放
- `ob_type` 决定了对象支持的操作（加减乘除、索引、迭代等）

变长对象多一个字段：

```c
typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size;      // 元素个数
} PyVarObject;
```

`list`、`tuple`、`str` 都是 `PyVarObject`。

## 核心概念 2：引用计数

```c
// Include/object.h
#define Py_INCREF(op)  (++(op)->ob_refcnt)
#define Py_DECREF(op)  do { \
    if (--(op)->ob_refcnt == 0) \
        _Py_Dealloc(op);       \
} while (0)
```

在 C 扩展中必须正确管理引用计数，否则会内存泄漏或崩溃：
- 接收"借用引用"：不需要 DECREF
- 接收"新引用"：用完后必须 DECREF
- 返回值给 Python：返回"新引用"

## 核心概念 3：类型对象

```c
// 每种类型都有一个 PyTypeObject，定义了该类型的全部行为
PyTypeObject PyList_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "list",                          // tp_name
    sizeof(PyListObject),            // tp_basicsize
    ...
    (reprfunc)list_repr,             // tp_repr   → repr(x)
    &list_as_sequence,               // tp_as_sequence → x[i], len(x)
    &list_as_mapping,                // tp_as_mapping  → x[k]
    ...
    list_methods,                    // tp_methods → x.append(), x.sort()
};
```

当你写 `my_list.append(1)` 时，CPython 会：
1. 通过 `my_list->ob_type` 找到 `PyList_Type`
2. 在 `tp_methods` 表中查找 `"append"`
3. 调用对应的 C 函数 `list_append()`

## 实战：阅读 list.append 的实现

打开 `Objects/listobject.c`，搜索 `list_append`：

```c
static PyObject *
list_append(PyListObject *self, PyObject *object)
{
    if (app1(self, object) == 0)   // 核心逻辑在 app1()
        Py_RETURN_NONE;
    return NULL;
}

static int
app1(PyListObject *self, PyObject *v)
{
    Py_ssize_t n = PyList_GET_SIZE(self);

    // 检查是否需要扩容
    if (list_resize(self, n + 1) < 0)
        return -1;

    // 增加引用计数，存入数组
    Py_INCREF(v);
    self->ob_item[n] = v;
    return 0;
}
```

**你能看出：**
- `list` 底层是一个 C 数组（`ob_item`）
- `append` 可能触发 `list_resize`（类似 C++ vector 的扩容）
- 新元素直接放到数组末尾，所以是 O(1) 均摊

## 实战：阅读 dict 的实现

`Objects/dictobject.c` 是 Python 中最精妙的实现之一。

```c
// Include/cpython/dictobject.h（简化）
typedef struct {
    PyObject_HEAD
    Py_ssize_t ma_used;        // 已存储的键值对数量
    PyDictKeysObject *ma_keys; // 键数组（compact dict since 3.6）
    PyObject **ma_values;      // 值数组
} PyDictObject;
```

dict 使用开放地址法哈希表，Python 3.6+ 使用紧凑布局保证插入顺序。

## 实战：字节码执行循环

`Python/ceval.c` 中的 `_PyEval_EvalFrameDefault` 是 Python 的心脏：

```c
// 极度简化版
for (;;) {
    opcode = NEXTOP();     // 取下一条字节码
    switch (opcode) {
        case LOAD_FAST:     // 加载局部变量
            value = GETLOCAL(oparg);
            PUSH(value);
            break;
        case BINARY_ADD:    // a + b
            right = POP();
            left = TOP();
            result = PyNumber_Add(left, right);
            SET_TOP(result);
            break;
        case CALL_FUNCTION: // 函数调用
            ...
            break;
    }
}
```

用 `dis` 模块可以查看任何 Python 函数的字节码：

```python
import dis
def foo(a, b):
    return a + b

dis.dis(foo)
# LOAD_FAST  0 (a)
# LOAD_FAST  1 (b)
# BINARY_ADD
# RETURN_VALUE
```

## 推荐阅读顺序

| 阶段 | 文件 | 你会学到 |
|------|------|---------|
| 1 | `Include/object.h` | PyObject 结构、引用计数宏 |
| 2 | `Objects/listobject.c` | 动态数组实现、扩容策略 |
| 3 | `Objects/longobject.c` | 大整数如何存储和运算 |
| 4 | `Objects/dictobject.c` | 哈希表、开放地址法、紧凑布局 |
| 5 | `Python/ceval.c` | 字节码执行、栈帧、GIL |
| 6 | `Objects/typeobject.c` | 类继承、MRO、描述符协议 |
| 7 | `Modules/gcmodule.c` | 分代垃圾回收、循环引用检测 |

## 阅读技巧

1. **从你熟悉的 Python 行为出发** — 比如想知道 `list.sort()` 用什么算法？
   搜索 `list_sort` → 发现是 TimSort
2. **用 `dis` 模块找入口** — 反汇编代码看到字节码名称，
   然后到 `ceval.c` 搜索对应的 case
3. **忽略宏展开** — 先理解逻辑，不要深入每一个宏定义
4. **关注数据结构** — 先看 `.h` 文件里的 struct 定义，
   再看 `.c` 文件里的操作函数
5. **用 IDE 的跳转功能** — VSCode + clangd 可以跳转到定义

## 工具

```bash
# 编译 debug 版 CPython（可以 gdb 调试）
./configure --with-pydebug
make -j4

# 反汇编 Python 代码查看字节码
python -m dis your_script.py
```
