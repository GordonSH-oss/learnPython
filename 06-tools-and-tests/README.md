# 工具和测试

各种工具脚本和测试文件。

## 测试文件

### test.py
通用测试文件，用于临时测试和实验。

### test_import.py
测试 Python 模块导入机制。

**学习要点：**
- 模块搜索路径
- 相对导入 vs 绝对导入
- `__init__.py` 的作用
- `sys.path` 管理

## 工具脚本

### add.py
简单的加法计算工具。

### analyze_md.py
Markdown 文件分析工具。

**功能：**
- 解析 Markdown 文件结构
- 提取标题和内容
- 生成结构化输出

### chunking.py 和 use_chunking.py
文本分块工具，常用于：
- 长文本处理
- 向量数据库数据准备
- NLP 预处理

**核心概念：**
- 固定大小分块
- 重叠分块
- 语义分块

## 数据文件

### objectname.md
大型文档文件，可能用于测试文本处理工具。

### structure_output.json
结构化数据输出，可能是 `analyze_md.py` 的输出结果。

### test.txt
简单的文本测试文件。

### test.yaml
YAML 配置文件测试。

## 使用示例

### 文本分块
```python
from chunking import chunk_text

text = "很长的文本..."
chunks = chunk_text(text, chunk_size=500, overlap=50)
```

### Markdown 分析
```python
from analyze_md import analyze_markdown

result = analyze_markdown("document.md")
print(result)
```

## 测试最佳实践

### 1. 使用 unittest
```python
import unittest

class TestAdd(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(add(2, 3), 5)

if __name__ == '__main__':
    unittest.main()
```

### 2. 使用 pytest
```python
def test_addition():
    assert add(2, 3) == 5
```

### 3. 测试覆盖率
```bash
# 安装 pytest 和 coverage
pip install pytest pytest-cov

# 运行测试并查看覆盖率
pytest --cov=. tests/
```

## 调试技巧

### 使用 pdb
```python
import pdb

def my_function():
    x = 10
    pdb.set_trace()  # 设置断点
    return x * 2
```

### 使用 logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

## 常用测试工具

### pytest
```bash
pip install pytest

# 运行所有测试
pytest

# 运行特定文件
pytest test_add.py

# 显示详细输出
pytest -v
```

### unittest (内置)
```bash
# 运行单个测试文件
python -m unittest test_add.py

# 运行所有测试
python -m unittest discover
```

### doctest (内置)
```python
def add(a, b):
    """
    >>> add(2, 3)
    5
    >>> add(-1, 1)
    0
    """
    return a + b

if __name__ == "__main__":
    import doctest
    doctest.testmod()
```

## 性能分析

### 使用 timeit
```python
import timeit

# 测试代码执行时间
time = timeit.timeit('sum(range(100))', number=10000)
print(f"执行时间: {time}秒")
```

### 使用 cProfile
```bash
# 分析程序性能
python -m cProfile -s cumulative your_script.py
```

## 扩展阅读

- [pytest 文档](https://docs.pytest.org/)
- [unittest 文档](https://docs.python.org/3/library/unittest.html)
- [Python 调试技巧](https://realpython.com/python-debugging-pdb/)
- [测试驱动开发 (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)
