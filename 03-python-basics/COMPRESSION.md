# Python 压缩模块教程：gzip、bz2、lzma、zlib

## 目标

学完这篇教程后，你应该能判断：

- `gzip`、`bz2`、`lzma`、`zlib` 分别适合什么场景。
- 如何压缩和解压 `bytes` 数据。
- 如何读写 `.gz`、`.bz2`、`.xz` 文件。
- 为什么不要把自己的脚本命名为 `compression.py`。

配套示例文件：[bz2_compression.py](./bz2_compression.py)

运行：

```bash
python 03-python-basics/bz2_compression.py
```

## 先建立一个心智模型

压缩通常有两层概念：

| 概念 | 说明 | 例子 |
|------|------|------|
| 压缩算法 | 负责把数据变小 | DEFLATE、bzip2、LZMA |
| 文件格式或容器 | 负责在压缩数据外面加元数据 | `.gz`、`.bz2`、`.xz`、`.zip`、`.tar.gz` |

所以：

- `zlib` 主要暴露 DEFLATE 压缩能力，常用于协议、内存数据和底层压缩流。
- `gzip` 使用 DEFLATE，但有 gzip 文件头和校验信息，常见扩展名是 `.gz`。
- `bz2` 使用 bzip2 算法，常见扩展名是 `.bz2`。
- `lzma` 使用 LZMA/LZMA2 算法，常见扩展名是 `.xz`。

## 核心对比

| 模块 | 常见扩展名 | 压缩率 | 速度 | 兼容性 | 典型场景 |
|------|------------|--------|------|--------|----------|
| `gzip` | `.gz` | 中等 | 快 | 很好 | 日志、HTTP、通用单文件压缩 |
| `zlib` | 通常不是用户文件扩展名 | 中等 | 快 | 偏底层 | 网络协议、内存数据、嵌入式压缩流 |
| `bz2` | `.bz2` | 通常高于 gzip | 慢 | 一般 | 文本归档、需要更高压缩率但不追求速度 |
| `lzma` | `.xz`、`.lzma` | 通常最高 | 慢，内存占用较高 | 较好 | 软件包、长期归档、大文件压缩 |

经验规则：

- 想要通用、快、兼容性好：选 `gzip`。
- 想要最高压缩率，能接受更慢：选 `lzma`。
- 想压缩协议或内存里的二进制片段：选 `zlib`。
- 需要 `.bz2` 格式或在文本数据上获得比 gzip 更好的压缩率：选 `bz2`。

注意：压缩率高度依赖数据内容。重复度、文件大小、文本或二进制结构都会影响结果。配套示例的输出只是一个可观察样本，不是所有数据的固定排名。

## 压缩和解压 bytes

四个模块都支持“一次性压缩 bytes”的写法：

```python
import bz2
import gzip
import lzma
import zlib

data = b"hello hello hello" * 100

gz_data = gzip.compress(data, compresslevel=6, mtime=0)
bz2_data = bz2.compress(data, compresslevel=9)
xz_data = lzma.compress(data, preset=6)
zlib_data = zlib.compress(data, level=6)

print(gzip.decompress(gz_data) == data)
print(bz2.decompress(bz2_data) == data)
print(lzma.decompress(xz_data) == data)
print(zlib.decompress(zlib_data) == data)
```

### 压缩等级

| 模块 | 参数 | 范围 | 含义 |
|------|------|------|------|
| `gzip` | `compresslevel` | `0` 到 `9` | 越大压缩率通常越高，但越慢 |
| `zlib` | `level` | `0` 到 `9` | 越大压缩率通常越高，但越慢 |
| `bz2` | `compresslevel` | `1` 到 `9` | 越大压缩率通常越高，但越慢 |
| `lzma` | `preset` | `0` 到 `9` | 越大压缩率通常越高，但更慢、更耗内存 |

不要盲目使用最高等级。真实项目里通常要在压缩率、CPU 时间、内存占用之间取平衡。

## 压缩文件

`gzip`、`bz2`、`lzma` 都提供了类似 `open()` 的文件 API，适合处理大文件：

```python
import bz2
import gzip
import lzma

data = b"example data" * 1000

with gzip.open("sample.txt.gz", "wb", compresslevel=6) as file:
    file.write(data)

with bz2.open("sample.txt.bz2", "wb", compresslevel=9) as file:
    file.write(data)

with lzma.open("sample.txt.xz", "wb", preset=6) as file:
    file.write(data)
```

读取时也一样：

```python
with gzip.open("sample.txt.gz", "rb") as file:
    restored = file.read()
```

如果是文本，可以使用文本模式：

```python
with gzip.open("sample.txt.gz", "wt", encoding="utf-8") as file:
    file.write("你好，gzip\n")

with gzip.open("sample.txt.gz", "rt", encoding="utf-8") as file:
    print(file.read())
```

## zlib 的定位

`zlib` 没有 `zlib.open()` 这种高级文件 API。它更像底层工具，适合处理内存数据或流式压缩：

```python
import zlib

compressor = zlib.compressobj(level=6)
parts = []

for chunk in [b"hello ", b"hello ", b"hello"]:
    parts.append(compressor.compress(chunk))

parts.append(compressor.flush())
compressed = b"".join(parts)

print(zlib.decompress(compressed))
```

`gzip` 和 `zlib` 都使用 DEFLATE，但二进制格式不一样：

- `gzip.compress(...)` 产生 gzip 格式数据。
- `zlib.compress(...)` 产生 zlib 格式数据。
- 两者不能直接互相用对方的 `decompress()` 解压。

## 什么时候需要 zipfile 或 tarfile？

`gzip`、`bz2`、`lzma` 通常压缩的是一个字节流。它们本身不负责“多个文件打包”。

如果你要把多个文件放进一个归档文件：

- 用 `zipfile` 创建 `.zip`，它既是归档格式，也可以对每个文件做压缩。
- 用 `tarfile` 创建 `.tar`、`.tar.gz`、`.tar.bz2`、`.tar.xz`。其中 `tar` 负责打包多个文件，`gzip`/`bz2`/`xz` 负责压缩整个 tar 流。

## 常见坑

### 不要命名为 compression.py

在 Python 3.14 中，标准库 `bz2` 会导入标准库包 `compression._common`。

如果你的脚本叫 `compression.py`，运行时 Python 会优先在当前目录找模块，于是把你的脚本误当成标准库 `compression` 包，导致循环导入：

```text
AttributeError: partially initialized module 'bz2' has no attribute 'compress'
```

避免方式：

- 不要把脚本命名为 `compression.py`。
- 可以使用 `bz2_compression.py`、`compression_examples.py`、`compression_tutorial.py` 这类名字。

### 小文件不一定变小

压缩格式会有文件头、校验信息、字典等额外开销。非常小的数据压缩后可能更大。

### 不要无上限解压不可信数据

压缩数据可能很小，但解压后非常大。处理不可信输入时，要限制解压后的大小，避免内存被耗尽。

## 选择建议

| 需求 | 推荐 |
|------|------|
| 日志文件、接口响应、通用兼容 | `gzip` |
| 长期归档、追求更高压缩率 | `lzma` |
| 协议层、内存数据、底层流 | `zlib` |
| 需要 `.bz2` 或文本压缩率优先 | `bz2` |
| 多文件打包 | `zipfile` 或 `tarfile` |

## 小练习

1. 把 [bz2_compression.py](./bz2_compression.py) 里的 `DATA` 重复次数从 `100` 改成 `1`，观察小数据压缩率。
2. 把 `gzip` 的 `compresslevel` 从 `6` 改成 `1` 和 `9`，比较压缩大小。
3. 把 `lzma` 的 `preset` 从 `6` 改成 `9`，观察文件大小和运行速度。
4. 试着用 `gzip.decompress()` 解压 `zlib.compress()` 的结果，看看错误信息。
