# 深度学习基础原理

这里不依赖 PyTorch，目标是先理解数组形状、线性变换、激活函数、损失和梯度下降，再学习框架如何自动完成这些工作。

## 学习材料

- `linear_algebra.md`：从样本、批次和参数矩阵理解神经网络计算。
- `linear_algebra_practice.py`：仅使用 NumPy 实现线性层、softmax、数值梯度和梯度下降。

## 运行

```bash
python -m pip install -r requirements/data.txt
python 07-deep-learning/fundamentals/linear_algebra_practice.py
```

## 检查点

运行后应看到矩阵乘法的输出形状、softmax 每行概率和接近 1，以及线性回归损失持续下降。
