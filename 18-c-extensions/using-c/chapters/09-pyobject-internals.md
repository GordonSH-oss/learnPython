# 09 CPython 对象模型：PyObject 内部结构

## 学习目标

理解 CPython 中所有 Python 对象的底层表示，掌握 `PyObject`、`PyVarObject`、`PyTypeObject` 的关系，能阅读和操作 `PyListObject`、`PyLongObject` 等具体类型的 C 结构，并在扩展代码中正确使用相关 API。

## 一切皆 PyObject

CPython 中每个 Python 对象在 C 层都是一块以 `PyObject` 开头的内存：

```c
typedef struct _object {
    Py_ssize_t ob_refcnt;   // 引用计数
    PyTypeObject *ob_type;  // 指向类型对象
} PyObject;
```

两个字段的职责：

| 字段 | 作用 |
| --- | --- |
| `ob_refcnt` | 跟踪有多少指针引用此对象，降到 0 时释放 |
| `ob_type` | 指向类型对象，决定对象支持哪些操作 |

所有对象类型——整数、列表、字典、自定义类——的 C 结构体都以 `PyObject` 为首部。这让 Python/C API 可以用 `PyObject *` 统一传递任意对象，再通过 `ob_type` 判断实际类型。

### PyObject_HEAD 和 PyObject_VAR_HEAD 宏

阅读 CPython 源码时，你不会直接看到 `ob_refcnt` 和 `ob_type` 字段声明，而是看到宏：

```c
// 固定大小对象使用
typedef struct {
    PyObject_HEAD           // 展开为 ob_refcnt + ob_type
    double ob_fval;
} PyFloatObject;

// 变长对象使用
typedef struct {
    PyObject_VAR_HEAD       // 展开为 ob_refcnt + ob_type + ob_size
    PyObject *ob_item[1];
} PyTupleObject;
```

在 CPython 3.12+ 中，`PyObject_HEAD` 实际展开为嵌入的 `PyObject ob_base;`，这意味着访问引用计数要通过 `op->ob_base.ob_refcnt`（但通常使用 `Py_REFCNT(op)` 宏）。了解这一点有助于阅读源码时不被宏迷惑。

```text
PyObject *obj
┌──────────────────┐
│ ob_refcnt = 3    │  ← 有 3 个地方引用此对象
│ ob_type = &Type  │  ← 指向 PyLong_Type / PyList_Type / ...
├──────────────────┤
│ 类型特有数据...   │  ← 紧跟在 PyObject 之后
└──────────────────┘
```

## PyVarObject：变长对象

列表、元组、字节串等长度可变的对象多一个字段：

```c
typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size;  // 当前元素个数
} PyVarObject;
```

`ob_size` 记录对象当前包含多少个元素（不是分配的内存大小）。`PyList_GET_SIZE(op)` 宏直接读取这个字段，不做类型检查，适合性能关键路径。

继承关系：

```text
PyObject          ← int, float, module, function ...
  └── PyVarObject ← list, tuple, bytes, str ...
```

## PyTypeObject：类型本身也是对象

每个 `ob_type` 指向的 `PyTypeObject` 定义了该类型的行为——方法槽、内存布局、分配释放策略：

```c
typedef struct _typeobject {
    PyVarObject ob_base;        // 类型对象本身是变长对象
    const char *tp_name;        // "list", "int", ...
    Py_ssize_t tp_basicsize;    // 实例的固定大小
    Py_ssize_t tp_itemsize;     // 每个元素的大小（变长时）

    // 方法槽（选取关键的几个）
    destructor tp_dealloc;      // 释放
    reprfunc tp_repr;           // repr()
    PySequenceMethods *tp_as_sequence;  // 序列协议
    PyMappingMethods *tp_as_mapping;    // 映射协议
    // ... 还有几十个槽
} PyTypeObject;
```

`type(obj)` 在 C 层就是读取 `obj->ob_type`。`isinstance(obj, list)` 检查 `ob_type` 是否是 `PyList_Type` 或其子类。

## PyLongObject：整数的内部表示

Python 3 的整数可以任意大。CPython 用数组存储，每个"数字"占 30 位（64 位平台）：

```c
struct _longobject {
    PyVarObject ob_base;
    digit ob_digit[1];  // 柔性数组，实际长度由 ob_size 决定
};
```

- `ob_size` 的绝对值是 `ob_digit` 数组的长度
- `ob_size` 为负表示负数，为 0 表示整数 0
- 小整数（-5 到 256）被预分配缓存，`PyLong_FromLong(42)` 不会每次分配新内存

```text
Python: n = 123456789

C 层 PyLongObject:
┌────────────────────┐
│ ob_refcnt = 1      │
│ ob_type = &PyLong_Type │
│ ob_size = 1        │  ← 1 个 digit 就够
│ ob_digit[0] = 123456789 │
└────────────────────┘

Python: n = 2**60

C 层 PyLongObject:
┌────────────────────┐
│ ob_refcnt = 1      │
│ ob_type = &PyLong_Type │
│ ob_size = 2        │  ← 需要 2 个 digit
│ ob_digit[0] = ...  │
│ ob_digit[1] = ...  │
└────────────────────┘
```

在扩展代码中操作整数不需要直接碰 `ob_digit`，使用 API：

```c
// Python int → C
long val = PyLong_AsLong(obj);
long long big = PyLong_AsLongLong(obj);

// C → Python int
PyObject *result = PyLong_FromLong(42);
PyObject *big_result = PyLong_FromLongLong(total);
```

## PyFloatObject：最简单的固定大小对象

浮点数是固定大小对象的典型——结构体只多一个 `double`：

```c
typedef struct {
    PyObject ob_base;
    double ob_fval;
} PyFloatObject;
```

没有 `ob_size`，不是 `PyVarObject`。每个 float 对象固定占 `sizeof(PyObject) + sizeof(double)` = 24 字节（64 位平台）。

```c
// C → Python float
PyObject *f = PyFloat_FromDouble(3.14);

// Python float → C
double val = PyFloat_AsDouble(f);
// 或跳过类型检查直接读取（仅在已确认类型后使用）
double val2 = PyFloat_AS_DOUBLE(f);
```

与 PyLongObject 对比：float 大小固定、精度有限（IEEE 754 double）；int 变长、精度无限。

## PyTupleObject：不可变的紧凑容器

元组和列表很像，但不可变，结构更紧凑：

```c
typedef struct {
    PyVarObject ob_base;
    PyObject *ob_item[1];  // 柔性数组，元素直接内嵌
} PyTupleObject;
```

与 `PyListObject` 的关键区别：

| | PyListObject | PyTupleObject |
| --- | --- | --- |
| 元素存储 | 间接指针 `ob_item` → 堆上数组 | 元素直接嵌在结构体末尾 |
| `allocated` 字段 | 有（支持增长） | 无（大小固定） |
| 可变性 | 可 append/insert/del | 创建后不可修改 |
| 内存分配 | 对象 + 独立数组 | 单次分配 |

```text
PyTupleObject (3 elements)
┌──────────────────────┐
│ ob_refcnt = 1        │
│ ob_type = &PyTuple_Type│
│ ob_size = 3          │
│ ob_item[0] ──────────┼──→ PyObject (元素 0)
│ ob_item[1] ──────────┼──→ PyObject (元素 1)
│ ob_item[2] ──────────┼──→ PyObject (元素 2)
└──────────────────────┘
    ↑ 全部在一块连续内存中
```

C 扩展中操作元组：

```c
// 创建并填充（SET_ITEM 偷取引用，和 list 一样）
PyObject *tup = PyTuple_New(3);
PyTuple_SET_ITEM(tup, 0, PyLong_FromLong(1));
PyTuple_SET_ITEM(tup, 1, PyLong_FromLong(2));
PyTuple_SET_ITEM(tup, 2, PyLong_FromLong(3));

// 读取（借用引用）
PyObject *elem = PyTuple_GET_ITEM(tup, 0);

// 长度
Py_ssize_t len = PyTuple_GET_SIZE(tup);
```

元组创建后不应再调用 `SET_ITEM`——这只用于初始化阶段。CPython 内部对空元组和单元素元组有缓存优化。

## PyListObject：列表的内部结构

这是实际使用中最常操作的容器类型：

```c
typedef struct {
    PyVarObject ob_base;
    PyObject **ob_item;   // 指向 PyObject* 数组的指针
    Py_ssize_t allocated; // 已分配槽位数（≥ ob_size）
} PyListObject;
```

关键设计：

```text
PyListObject
┌──────────────────────┐
│ ob_refcnt = 1        │
│ ob_type = &PyList_Type│
│ ob_size = 3          │  ← 当前 3 个元素
│ ob_item ─────────────┼──→ ┌─────────────┐
│ allocated = 4        │    │ PyObject *[0]│ → 指向 "hello"
└──────────────────────┘    │ PyObject *[1]│ → 指向 42
                            │ PyObject *[2]│ → 指向 [1,2]
                            │ (空槽)       │
                            └─────────────┘
```

`ob_item` 是一个动态数组，存放指向各元素的指针。`allocated` 记录已分配容量，`ob_size` 是实际使用量。append 时若 `ob_size == allocated`，按约 1.125 倍增长重新分配。

### 在 C 扩展中操作列表

```c
// 创建
PyObject *lst = PyList_New(0);          // 空列表
PyObject *lst3 = PyList_New(3);         // 预分配 3 个槽位（元素为 NULL，必须逐个设置）

// 追加元素（会增加 item 的引用计数）
PyObject *item = PyLong_FromLong(42);
PyList_Append(lst, item);
Py_DECREF(item);  // Append 已经 INCREF，我们释放自己的引用

// 读取元素（借用引用，不需要 DECREF）
PyObject *elem = PyList_GetItem(lst, 0);  // 借用引用
// PyList_GET_ITEM(lst, 0) 是无检查版本，跳过边界和类型检查

// 设置元素（偷取引用——不会 INCREF，会 DECREF 旧元素）
PyObject *new_val = PyUnicode_FromString("hello");
PyList_SetItem(lst3, 0, new_val);  // 偷取 new_val 的引用，不要再 DECREF

// 长度
Py_ssize_t len = PyList_Size(lst);       // 带类型检查
Py_ssize_t len2 = PyList_GET_SIZE(lst);  // 宏，无检查
```

引用所有权的关键区别：

| API | 引用语义 |
| --- | --- |
| `PyList_Append(list, item)` | 增加 `item` 引用计数 |
| `PyList_SetItem(list, i, item)` | **偷取** `item` 引用，不增加 |
| `PyList_GetItem(list, i)` | 返回**借用**引用 |
| `PyList_GET_ITEM(list, i)` | 返回**借用**引用，无检查 |

`SetItem` 偷取引用的设计是为了方便连续填充新建列表：

```c
PyObject *lst = PyList_New(3);
PyList_SET_ITEM(lst, 0, PyLong_FromLong(1));  // 直接偷取，无需额外 DECREF
PyList_SET_ITEM(lst, 1, PyLong_FromLong(2));
PyList_SET_ITEM(lst, 2, PyLong_FromLong(3));
```

## PyDictObject 和 PyUnicodeObject 简述

### 字典

```c
typedef struct {
    PyObject_HEAD
    Py_ssize_t ma_used;       // 已存储键值对数量
    PyDictKeysObject *ma_keys; // 哈希表结构
    PyObject **ma_values;      // split-table 模式的值数组
} PyDictObject;
```

字典使用紧凑哈希表（compact dict），插入顺序即迭代顺序。C 层 API：

```c
PyObject *d = PyDict_New();
PyDict_SetItemString(d, "key", value);  // INCREF value
PyObject *v = PyDict_GetItemString(d, "key");  // 借用引用
```

### 字符串

CPython 3 的字符串根据最大码点选择编码：

```c
typedef struct {
    PyObject_HEAD
    Py_ssize_t length;
    Py_hash_t hash;       // 缓存的哈希值，-1 表示未计算
    struct { ... } state; // kind: 1=Latin1, 2=UCS2, 4=UCS4
    // 数据紧跟在结构体后面
} PyUnicodeObject;  // 简化表示
```

纯 ASCII 字符串每字符 1 字节；含中文则每字符 2 或 4 字节。

## 类型检查与类型转换

在 C 扩展中收到 `PyObject *` 后，操作前必须确认类型：

```c
if (!PyList_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "expected a list");
    return NULL;
}
// 现在可以安全使用 PyList_* API
Py_ssize_t len = PyList_GET_SIZE(obj);
```

常用检查宏：

| 宏 | 检查 |
| --- | --- |
| `PyList_Check(op)` | 是否为 list 或其子类 |
| `PyList_CheckExact(op)` | 是否恰好是 list（不含子类） |
| `PyLong_Check(op)` | 是否为 int |
| `PyUnicode_Check(op)` | 是否为 str |
| `PyDict_Check(op)` | 是否为 dict |

`Check` 和 `CheckExact` 的区别：当你依赖内部结构布局时用 `CheckExact`；当你只需要对象支持某个协议时用 `Check`。

## 引用计数实战

理解 PyObject 后，引用计数的规则更具体了：

```c
PyObject *build_pair(long a, long b) {
    PyObject *lst = PyList_New(2);
    if (lst == NULL) return NULL;

    PyObject *oa = PyLong_FromLong(a);
    if (oa == NULL) {
        Py_DECREF(lst);
        return NULL;
    }

    PyObject *ob = PyLong_FromLong(b);
    if (ob == NULL) {
        Py_DECREF(oa);
        Py_DECREF(lst);
        return NULL;
    }

    // SET_ITEM 偷取引用，所以不需要 DECREF oa/ob
    PyList_SET_ITEM(lst, 0, oa);
    PyList_SET_ITEM(lst, 1, ob);
    return lst;  // 调用者拥有 lst 的新引用
}
```

失败路径必须清理已创建的对象。每条路径画出哪些对象需要释放：

```text
成功路径: lst(转交) oa(被偷) ob(被偷) → 无需 DECREF
oa 失败: lst(需释放)
ob 失败: oa(需释放) lst(需释放)
```

## 对象生命周期全貌

```text
1. 分配: tp_alloc (通常 PyObject_Malloc + 设置 ob_refcnt=1, ob_type)
2. 初始化: tp_init 或工厂函数填充类型特有数据
3. 使用中: ob_refcnt 随引用增减变化
4. ob_refcnt → 0: tp_dealloc 被调用
5. 释放: tp_free (通常 PyObject_Free)
```

循环引用（如列表包含自身）不会被引用计数回收，由分代垃圾收集器处理。支持循环引用的类型必须实现 `tp_traverse` 和 `tp_clear`。

## 调试技巧：在 lldb/gdb 中观察 PyObject

扩展崩溃时，能在调试器中检查 PyObject 状态非常有用。

### _PyObject_Dump

CPython 内置了调试辅助函数，在 lldb 断点中直接调用：

```text
(lldb) expr (void)_PyObject_Dump(obj)
object  : 0x100a04f90
type    : list
refcount: 1
address : 0x100a04f90
[0, 1, 2]
```

### 手动检查字段

```text
(lldb) p obj->ob_type->tp_name
(const char *) "list"

(lldb) p ((PyVarObject *)obj)->ob_size
(Py_ssize_t) 3

(lldb) p ((PyListObject *)obj)->ob_item[0]->ob_type->tp_name
(const char *) "int"

(lldb) p ((PyFloatObject *)obj)->ob_fval
(double) 3.14
```

### 使用 CPython 的 gdb/lldb 辅助脚本

CPython 源码自带 `Tools/gdb/libpython.py`（gdb）和 `Tools/lldb/libpython.py`（lldb），加载后可以直接 `py-print` 显示 Python 层面的值：

```text
(gdb) py-print obj
$1 = [0, 1, 2]
```

### 构建带调试符号的扩展

```bash
# 编译时加 -g，不优化
gcc -g -O0 -shared -fPIC -I$(python3-config --includes) \
    mymodule.c -o mymodule.so

# 或使用 Python debug build
python3-dbg -c "import mymodule"
```

Python debug build（`--with-pydebug`）会启用额外检查：引用计数断言、内存填充 0xCD 检测 use-after-free、以及 `sys.getrefcount` 的准确性验证。

## 动手练习

1. 在 CPython 源码中找到 `Include/cpython/listobject.h`，确认 `PyListObject` 的字段与本章描述一致。注意 CPython 3.12+ 的字段可能因 free-threading 有新增。

2. 写一个 C 扩展函数 `make_range_list(n)`，返回 `[0, 1, 2, ..., n-1]`。使用 `PyList_New(n)` + `PyList_SET_ITEM` 模式，确保每条失败路径正确清理。

3. 用 `sys.getsizeof` 观察不同大小整数的内存占用差异，验证小整数缓存（`a is b` 对比）。

4. 写一个函数接受 `PyObject *`，打印其 `ob_refcnt` 和 `ob_type->tp_name`，在不同上下文调用它观察引用计数变化。

5. 阅读 `PyList_Append` 的源码实现（`Objects/listobject.c`），画出它在容量不足时的增长策略和引用计数操作。

6. 写一个扩展函数，接受一个 list 参数，返回一个 tuple，元素相同但顺序逆转。对比 `PyList_GetItem`（借用）与 `PyTuple_SET_ITEM`（偷取）的引用处理——中间需要 `Py_INCREF`。

7. 编译带 `-g -O0` 的扩展，用 lldb 断点在你的 C 函数入口处停下，用 `_PyObject_Dump` 查看传入参数，观察 `ob_refcnt` 在函数前后的变化。
