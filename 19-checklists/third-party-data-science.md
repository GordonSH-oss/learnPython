# 第三方库：数据科学

## NumPy

- [ ] 我理解 ndarray 的形状、dtype、轴和广播。
- [ ] 我会使用索引切片、向量化运算、`reshape`、`mean`、`where`。

安装：`python -m pip install numpy`（仓库基线 `numpy>=1.26`）。

```python
import numpy as np

x = np.array([[1, 2], [3, 4]], dtype=np.float64)
print(x.mean(axis=0), x * 2)
```

常见坑：切片可能是视图而非副本；形状不匹配会触发广播错误或意外广播；Python 循环通常比向量化慢。

自查：`axis=0` 聚合哪一维？什么时候必须 `.copy()`？

练习：标准化一个二维特征矩阵，并验证每列均值接近 0。

仓库关联：[NumPy 线性层练习](../07-deep-learning/fundamentals/notebooks/03-numpy-and-linear-layers.ipynb)。

## pandas

- [ ] 我能区分 Series、DataFrame、索引和缺失值。
- [ ] 我会使用 `read_csv`、`loc`、`assign`、`groupby`、`merge`、`fillna` 和 `to_csv`。

安装：`python -m pip install pandas`（仓库基线 `pandas>=2.2`）。

```python
import pandas as pd

df = pd.DataFrame({"team": ["A", "A", "B"], "score": [2, 4, 5]})
print(df.groupby("team", as_index=False)["score"].mean())
```

常见坑：链式赋值可能不修改原表；索引对齐会改变赋值结果；连接前要检查键重复和缺失值。

自查：`loc` 与 `iloc` 的区别是什么？为什么聚合前要确认数据粒度？

练习：清洗一个含缺失值的 CSV，按类别聚合，再与维表合并并检查行数变化。

仓库关联：[pandas 工作流](../13-data-science/pandas_workflow.py)。

## Matplotlib

- [ ] 我知道 Figure、Axes 和绘图对象的关系。
- [ ] 我会使用面向对象接口、标签、图例、布局和保存图片。

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9], label="score")
ax.set(xlabel="step", ylabel="value")
ax.legend()
fig.savefig("plot.png", dpi=150, bbox_inches="tight")
```

常见坑：脚本中要显式保存或 `show`；图例和坐标轴标签不可省；批量绘图要关闭 Figure 以避免内存增长。

自查：为什么推荐 `fig, ax = plt.subplots()`？如何保证图表可复现？

练习：从 pandas 聚合结果生成带标题、单位和误差说明的图表。

仓库关联：`requirements/data.txt` 和深度学习 notebooks。

## scikit-learn

- [ ] 我理解 estimator、fit、transform、predict 和 pipeline。
- [ ] 我会划分训练/验证数据、避免数据泄漏、选择指标并保存预处理流程。

安装：`python -m pip install scikit-learn`（仓库基线 `scikit-learn>=1.4`）。

```python
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

model = make_pipeline(StandardScaler(), LinearRegression())
model.fit([[1], [2], [3]], [2, 4, 6])
print(model.predict([[4]]))
```

常见坑：不能先用全量数据拟合预处理器；训练集和测试集要隔离；指标必须符合任务目标。

自查：为什么预处理应放进 Pipeline？交叉验证如何避免泄漏？

练习：为分类数据构建带标准化的 pipeline，报告准确率和混淆矩阵。

仓库关联：扩展主题；可结合 [深度学习基础](../07-deep-learning/fundamentals/README.md)。

