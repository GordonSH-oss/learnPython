# 01 从 C 到现代 C++

## 学习目标

- 使用 C++20 编译、链接并运行程序
- 区分 C++ 标准库、命名空间和语言特性
- 理解 C++ 与 C 的兼容边界
- 建立“资源由对象管理”的学习方向

## 第一个程序

```cpp
#include <iostream>

int main() {
    std::cout << "Hello, modern C++!\n";
}
```

```bash
clang++ -std=c++20 -Wall -Wextra -Wpedantic \
  examples/01_hello.cpp -o build/examples/01_hello
./build/examples/01_hello
```

使用 `clang++` 而不是 `clang`，因为驱动程序会自动链接 C++ 标准库。源文件通常使用 `.cpp`。

## 命名空间

`std::cout` 中的 `std` 是标准库命名空间。命名空间解决大型程序中的名称冲突：

```cpp
namespace geometry {
double area(double radius);
}
```

头文件中不要写 `using namespace std;`，它会把大量名称注入所有包含者。局部作用域可使用精确声明：

```cpp
using std::cout;
```

## C++ 不是严格超集

大量 C 代码可以按 C++ 编译，但两种语言具有不同规则：

- C++ 对 `void *` 转换更严格。
- 字符串字面量是 `const char[]`。
- C++ 有函数重载、引用、类、模板和异常。
- 某些 C99/C11 特性在不同 C++ 标准中形式不同。

不要把 `.c` 文件批量改名为 `.cpp` 并假定语义完全不变。C 与 C++ 模块之间应建立明确接口。

## 标准库是语言实践的一部分

现代 C++ 通常使用：

- `std::string` 管理字符串
- `std::vector` 管理动态连续数组
- `std::filesystem::path` 管理路径
- `std::thread` 管理线程对象
- `std::unique_ptr` 表达独占动态所有权

这些类型把资源生命周期绑定到对象析构，减少手写 cleanup。

## 编译阶段

C++ 同样经历预处理、编译、汇编和链接。模板通常需要在使用点看到定义，因此经常放在头文件；普通函数仍应采用声明与定义分离。

名称修饰使重载函数具有不同链接符号。需要向 C 暴露稳定符号时使用 `extern "C"`，第 15 章会详细说明。

## 检查点

1. 为什么应使用 `clang++` 链接 C++ 程序？
2. `std::` 解决什么问题？
3. 为什么不能把 C++ 当作完全兼容的 C 超集？

## 动手练习

1. 运行示例并查看退出状态。
2. 分别用 `clang` 和 `clang++` 链接，观察标准库符号错误。
3. 创建自己的命名空间并定义两个同名函数。

