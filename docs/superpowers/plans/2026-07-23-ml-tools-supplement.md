# ML Tools Supplement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 26 new sections (22-47) to the PyTorch prerequisites notebook covering the full ML/LLM training tool ecosystem.

**Architecture:** Append cells to the existing Jupyter notebook using NotebookEdit. Each section is a markdown cell (table + explanation) followed by one or more code cells with runnable examples.

**Tech Stack:** Jupyter Notebook, Python, PyTorch, NumPy, Pandas, Matplotlib, Seaborn, scikit-learn, tqdm, torchvision, torchmetrics, Hugging Face (transformers, datasets, tokenizers), PEFT, TensorBoard, wandb, PyTorch Lightning, Accelerate, DeepSpeed, Optuna, ONNX, einops, timm, bitsandbytes

## Global Constraints

- All new sections append after the existing Section 21 (cell id `40a58dea`)
- Follow existing format: markdown cell with `## N. Title` + table, then code cell with examples
- Code cells must be runnable without downloading large datasets (use synthetic/toy data)
- Tools requiring special hardware get "(简介)" suffix and descriptive text only where code can't run locally
- Chinese language for all markdown explanations, matching existing notebook style

---

### Task 1: Data Processing & Visualization (Sections 22-25)

**Files:**
- Modify: `07-deep-learning/pytorch/notebooks/00-prerequites.ipynb` (append cells after section 21)

**Interfaces:**
- Consumes: Nothing (independent)
- Produces: Sections 22-25 in notebook

- [ ] **Step 1: Add Section 22 - NumPy markdown cell**

Insert after cell `40a58dea`:

```markdown
## 22. NumPy：数组计算与 PyTorch 互操作

NumPy 是 Python 科学计算的基石。PyTorch 张量与 NumPy 数组可以零拷贝互转（CPU 上共享内存）。

| 工具 | 用途 |
| --- | --- |
| `np.array(data)` | 创建数组 |
| `np.zeros / ones / arange / linspace` | 常用创建方式 |
| `np.reshape / concatenate / stack` | 形状变换与拼接 |
| `np.mean / std / sum / max / argmax` | 统计与聚合 |
| `np.random.randn / randint / shuffle` | 随机数 |
| `torch.from_numpy(arr)` | NumPy → Tensor（共享内存） |
| `tensor.numpy()` | Tensor → NumPy（仅 CPU） |
| `np.save / np.load` | 保存和加载数组文件 |
```

- [ ] **Step 2: Add Section 22 - NumPy code cell**

```python
import numpy as np

# 创建数组
a = np.array([[1, 2, 3], [4, 5, 6]])
print("NumPy array:\n", a)
print("shape:", a.shape, "dtype:", a.dtype)

# 统计运算
print("mean:", np.mean(a), "max:", np.max(a), "argmax:", np.argmax(a))

# 与 PyTorch 互转（共享内存）
t = torch.from_numpy(a)
print("\nTensor from NumPy:", t)
print("Shares memory:", t.data_ptr() == a.__array_interface__['data'][0])

# 修改 numpy 会影响 tensor（共享内存）
a[0, 0] = 999
print("After modifying NumPy, tensor:", t)

# Tensor → NumPy（仅 CPU tensor）
b = torch.randn(2, 3)
b_np = b.numpy()
print("\nNumPy from Tensor:", b_np)
```

- [ ] **Step 3: Add Section 23 - Pandas markdown cell**

```markdown
## 23. Pandas：表格数据处理

Pandas 是数据分析的首选库，擅长处理表格数据、时间序列和特征工程。

| 工具 | 用途 |
| --- | --- |
| `pd.DataFrame(data)` | 创建表格 |
| `pd.read_csv / read_excel` | 读取文件 |
| `df.head() / info() / describe()` | 快速查看数据 |
| `df.dropna() / fillna()` | 处理缺失值 |
| `df[column] / df.loc[] / df.iloc[]` | 索引和选择 |
| `df.groupby().agg()` | 分组聚合 |
| `df.apply() / map()` | 应用函数 |
| `df.values` | 转为 NumPy 数组 |
| `torch.tensor(df.values)` | DataFrame → Tensor |
```

