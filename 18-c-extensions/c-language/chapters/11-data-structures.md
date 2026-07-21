# 11 数据结构与函数指针

## 学习目标

完成本章后，你应该能够：

- 实现具有清晰所有权的单链表
- 比较动态数组和链表的时间、空间与缓存成本
- 使用函数指针和上下文参数传递行为
- 设计插入、删除和销毁操作的失败契约

## 先运行示例

```bash
make build/examples/11_linked_list
./build/examples/11_linked_list
```

## 链表的结构

```c
typedef struct Node {
    int value;
    struct Node *next;
} Node;
```

链表通过指针表达节点关系：

```text
head
  |
  v
[10 | next] -> [20 | next] -> [30 | NULL]
```

链表对象通常拥有从 `head` 可达的所有节点。只要这个所有权约定成立，销毁函数就可以沿链释放每个节点。

## 插入与失败

```c
#include <stdbool.h>
#include <stdlib.h>

bool push_front(Node **head, int value) {
    if (head == NULL) {
        return false;
    }

    Node *node = malloc(sizeof *node);
    if (node == NULL) {
        return false;
    }

    node->value = value;
    node->next = *head;
    *head = node;
    return true;
}
```

只有分配成功后才修改 `head`，所以失败时原链表保持不变。`Node **` 允许函数更新调用者保存的头指针。

## 删除节点

删除第一个匹配节点需要同时处理头节点和中间节点：

```c
bool remove_first(Node **head, int target) {
    if (head == NULL) return false;

    Node **link = head;
    while (*link != NULL) {
        if ((*link)->value == target) {
            Node *removed = *link;
            *link = removed->next;
            free(removed);
            return true;
        }
        link = &(*link)->next;
    }
    return false;
}
```

这里 `link` 始终指向“当前节点由哪个指针引用”，因此不需要为删除头节点写独立分支。

## 正确销毁

```c
void destroy_list(Node **head) {
    if (head == NULL) return;

    Node *node = *head;
    while (node != NULL) {
        Node *next = node->next;
        free(node);
        node = next;
    }
    *head = NULL;
}
```

必须在 `free(node)` 前保存 `next`，否则会从已经释放的节点读取指针。

## 动态数组还是链表

| 特性 | 动态数组 | 单链表 |
| --- | --- | --- |
| 按索引访问 | O(1) | O(n) |
| 已知位置插入 | 可能移动元素 | 已有前驱位置时 O(1) |
| 额外空间 | 容量余量 | 每节点一个指针和分配开销 |
| 缓存局部性 | 好 | 通常较差 |
| 分配次数 | 批量扩容 | 通常每节点一次 |

链表不是“更高级的数组”。现代机器上，动态数组常因连续内存和较少分配而更快。只有操作模式确实适合节点结构时才选择链表。

## 函数指针与上下文

```c
typedef bool (*Predicate)(int value, void *context);

size_t count_if(const Node *head, Predicate predicate, void *context) {
    size_t count = 0;
    for (const Node *node = head; node != NULL; node = node->next) {
        if (predicate(node->value, context)) {
            ++count;
        }
    }
    return count;
}
```

函数指针描述行为，`void *context` 携带调用者状态。相比依赖全局变量，这种接口可以同时支持多个独立配置，也更容易测试。

调用者必须保证回调和上下文在遍历期间有效，并遵守接口关于修改链表、线程和错误处理的约定。

## 迭代时修改结构

回调若删除当前节点，普通的 `node = node->next` 遍历可能访问已释放内存。接口应明确：

- 遍历期间完全禁止结构修改；或
- 提供专门的可变迭代器；或
- 由遍历函数自己完成筛选和删除。

不要把这项约束留给调用者猜测。

## 常见错误

- 分配失败后仍修改链表状态
- 删除头节点时忘记更新 `head`
- 释放节点后读取 `next`
- 丢失头指针导致整条链泄漏
- 销毁后未清空拥有者保存的指针
- 回调依赖隐藏全局状态
- 遍历期间无协议地修改链表

## 检查点

1. 为什么 `push_front` 接收 `Node **`？
2. 为什么链表插入 O(1) 不代表它一定比数组快？
3. 回调上下文由谁拥有、必须存活多久？

## 动手练习

1. 扩展 `examples/11_linked_list.c`，实现删除第一个匹配节点。
2. 使用函数指针统计偶数节点，并改成“统计大于指定阈值”的上下文回调。
3. 用 sanitizer 测试空链表、单节点、删除头部、删除尾部和不存在的值。
