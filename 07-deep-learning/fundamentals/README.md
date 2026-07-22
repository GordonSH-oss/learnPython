# 深度学习基础：从零手写神经网络

这套课程面向已经掌握 Python 基础的学习者。前两课使用纯 Python 标量和列表建立计算直觉，之后只使用 NumPy 完成矩阵计算；神经网络层、损失、反向传播、优化器和训练循环全部自行实现。

这里不使用任何深度学习框架、自动微分或现成神经网络 API。目标是完整理解一个多层感知机从前向传播到训练、验证和调试的全过程，再进入 PyTorch 课程。

## Notebook 课程

| 课程 | 核心问题 |
| --- | --- |
| 01 标量、向量与神经元 | 特征、权重、偏置和批量前向计算 |
| 02 导数与链式法则 | 局部导数如何沿计算图传播 |
| 03 NumPy 与线性层 | shape、广播和 Linear 的 forward/backward |
| 04 激活函数与损失 | ReLU、Sigmoid、Softmax、MSE 和交叉熵 |
| 05 反向传播 | 如何串联每一层的解析梯度 |
| 06 完整 MLP | 组合层、枚举参数并完成预测 |
| 07 优化与训练循环 | SGD、Momentum、mini-batch 和学习曲线 |
| 08 验证与泛化 | 数据划分、L2、Dropout 和早停 |
| 09 梯度检查与调试 | 有限差分、shape 和梯度诊断 |
| 10 综合项目 | 从零训练螺旋数据多分类器并绘制决策边界 |

`from_scratch/` 保存课程共用的 NumPy 实现。每个 Notebook 都可以按顺序独立运行，不需要下载数据或访问网络。

## 补充材料

- `linear_algebra.md`：从样本、批次和参数矩阵理解神经网络计算。
- `linear_algebra_practice.py`：使用 NumPy 实现 softmax、数值梯度和线性回归。

## 运行

```bash
python -m pip install -r requirements/data.txt
jupyter lab 07-deep-learning/fundamentals/notebooks
```

也可以运行原有练习和测试：

```bash
python 07-deep-learning/fundamentals/linear_algebra_practice.py
pytest 07-deep-learning/fundamentals/tests
```

## 学完后应能做到

- 根据输入和参数 shape 写出全连接层的前向与反向计算。
- 解释链式法则、反向传播、损失函数和优化器之间的职责边界。
- 从零实现 Linear、激活函数、交叉熵、MLP、SGD、Momentum 和 Dropout。
- 使用有限差分验证解析梯度，并按固定顺序排查训练问题。
- 正确划分训练集和验证集，识别过拟合并绘制学习曲线与决策边界。

CNN、RNN 和 Attention 的工程实现放在后续 PyTorch 课程中，本目录聚焦完整掌握 MLP 主线。
