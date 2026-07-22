# 深度学习学习路线

本目录把“框架无关的原理”和“PyTorch 工程实践”分开。建议先建立数学与训练直觉，再进入 PyTorch 的数据、模型、训练、调试和部署流程。

## 目录

- [`fundamentals/`](fundamentals/README.md)：线性代数、梯度下降和神经网络计算的框架无关基础。
- [`pytorch/`](pytorch/README.md)：以 Notebook 为主的 PyTorch 完整课程，所有导入 `torch` 或 `torchvision` 的内容都在这里。

## 推荐顺序

1. 阅读 `fundamentals/linear_algebra.md`，运行 NumPy 练习。
2. 按编号学习 `pytorch/notebooks/` 中的 13 节课。
3. 使用 `pytorch/examples/` 重复运行训练任务，修改参数观察行为。
4. 运行测试，确认训练循环、检查点和模型形状符合预期。

## 环境

```bash
python -m pip install -r requirements/ai.txt
jupyter lab 07-deep-learning/pytorch/notebooks
```

PyTorch 基线为 2.2+。所有示例支持 CPU；可用时也支持 CUDA 或 Apple MPS。MNIST、CIFAR-10 和预训练权重会在首次使用时下载。

## 学完后应能做到

- 根据张量形状预测全连接、卷积、循环网络和 Attention 的数据流。
- 正确划分训练、验证、测试集并解释 `train()`、`eval()` 和梯度上下文。
- 编写可恢复的训练任务，保存检查点并加载推理模型。
- 识别过拟合、设备不一致、梯度缺失、数据泄漏和显存问题。
- 使用迁移学习、混合精度，并导出可复现的推理模型。
