# 数据分析和机器学习基础

数据分析模块关注“把原始数据变成模型或业务判断能使用的特征”。它是深度学习和 AI 应用工程之前的基础层。

## 学习目标

- 会用 pandas 读取、清洗、聚合数据。
- 理解缺失值、异常值、类型转换和特征工程。
- 会用简单模型建立基线，而不是一开始就上深度学习。
- 知道训练集、验证集、测试集的边界。

## 本目录文件

- `pandas_workflow.py`：构造一份内存数据，演示清洗、聚合和简单特征生成。

## 推荐命令

```bash
python -m pip install -r requirements/data.txt
python 13-data-science/pandas_workflow.py
```

## 学习路线

1. 先学 `Series` 和 `DataFrame`。
2. 再学读取 CSV/JSON、缺失值处理和类型转换。
3. 接着学 groupby、merge、pivot。
4. 最后用 scikit-learn 建一个基线模型。

## 练习

1. 增加一列 `channel`，按渠道统计收入。
2. 把异常订单过滤规则改成“金额必须在 0 到 1000 之间”。
3. 将结果保存为 CSV。
