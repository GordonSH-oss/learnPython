# 14 `filesystem`、流与序列化边界

## 学习目标

- 使用 `std::filesystem::path` 处理路径
- 遍历目录并处理 `std::error_code`
- 正确检查流状态和关闭错误边界
- 避免直接序列化对象内存布局

## 路径不是字符串拼接

```cpp
std::filesystem::path root{"/tmp"};
auto file = root / "report.txt";
```

path 处理平台分隔符和编码边界。展示给用户时可调用 `.string()`，但跨平台 Unicode 转换需要按平台测试。

## 错误处理

filesystem 同时提供抛异常和接收 `std::error_code` 的重载：

```cpp
std::error_code error;
auto size = std::filesystem::file_size(path, error);
if (error) { /* handle */ }
```

批量目录扫描通常适合 error_code，以便记录单项失败并继续；初始化关键配置可能更适合异常。

## 文件流

```cpp
std::ifstream input{path, std::ios::binary};
if (!input) throw std::runtime_error("open failed");
```

读取循环后区分 EOF 与其他失败。输出析构会关闭文件，但需要报告提交错误时应显式 flush/close 并检查状态。

## 序列化

不能直接把任意 C++ 对象 `write(sizeof object)` 到文件。对象可能包含指针、padding、虚表、平台字节序和非平凡不变量。序列化格式应明确字段、宽度、版本和编码。

## 常见错误

- 用字符串加 `/` 拼路径
- 递归遍历中未处理权限错误和符号链接循环
- 只检查打开，不检查读取/写入完成
- 直接序列化 string/vector 对象内存
- 临时文件与目标文件不在同一文件系统却假定 rename 原子

## 动手练习

1. 统计目录中的普通文件大小。
2. 同时实现异常版和 error_code 版接口。
3. 设计带版本号的二进制记录格式。

