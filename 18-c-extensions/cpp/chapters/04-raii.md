# 04 RAII 与资源生命周期

## 学习目标

- 理解 RAII 如何统一成功和异常路径清理
- 使用析构函数释放非内存资源
- 优先使用标准 RAII 类型
- 设计不可复制或可移动的资源封装

## RAII 心智模型

RAII（Resource Acquisition Is Initialization）把资源获取绑定到对象初始化，把释放绑定到析构：

```text
构造成功 -> 对象拥有资源 -> 离开作用域 -> 析构释放
```

无论函数正常返回还是抛出异常，已构造的局部对象都会按逆序析构。

## 文件资源示例

```cpp
class File {
public:
    explicit File(const char* path)
        : handle_(std::fopen(path, "rb")) {
        if (handle_ == nullptr) {
            throw std::system_error(errno, std::generic_category(), "fopen");
        }
    }

    ~File() {
        if (handle_ != nullptr) std::fclose(handle_);
    }

    File(const File&) = delete;
    File& operator=(const File&) = delete;

private:
    std::FILE* handle_;
};
```

构造失败时对象未完成，不会调用其析构；已经完成构造的其他局部对象仍会清理。

## 优先使用现成 RAII 类型

- `std::vector` 管理动态数组
- `std::string` 管理字符存储
- `std::fstream` 管理文件流
- `std::unique_ptr` 管理独占动态对象
- `std::lock_guard`/`std::scoped_lock` 管理 mutex
- `std::jthread` 管理线程 join

只有标准库没有表达某种资源时，才编写自定义 RAII wrapper，例如 socket、数据库句柄或第三方库 context。

## 析构函数规则

析构函数通常不应抛异常。栈展开期间再次抛出会导致 `std::terminate`。无法可靠报告的关闭错误应通过显式 `close()` 操作处理，析构作为最后兜底。

## Scope guard

简单一次性清理有时可用智能指针加自定义 deleter，或项目中的 scope-exit 工具。关键不是一定创建类，而是让每个成功获取立即对应一个自动清理对象。

## 常见错误

- 获取多个资源后用多条 return 手工清理
- 析构函数抛异常
- 资源 wrapper 可复制导致重复关闭
- 构造函数先获取资源，后续失败却未交给 RAII 成员
- 使用裸 owning pointer 表达所有权

## 动手练习

1. 为 POSIX fd 实现只移动、不可复制的 wrapper。
2. 故意在获取两个资源后抛异常，验证析构顺序。
3. 用 `std::lock_guard` 替换手工 lock/unlock。

