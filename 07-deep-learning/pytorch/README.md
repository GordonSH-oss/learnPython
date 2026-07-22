# PyTorch 深度学习课程

本课程面向掌握 Python 基础的学习者。Notebook 用来建立概念和调试直觉，`common/` 保存可复用实现，`examples/` 提供可从终端重复运行的任务。

## 安装与启动

从仓库根目录运行：

```bash
python -m pip install -r requirements/ai.txt
jupyter lab 07-deep-learning/pytorch/notebooks
```

首次使用 MNIST、CIFAR-10 或预训练 ResNet 时需要网络。数据保存在 `data/`，检查点和导出模型保存在 `artifacts/`，两者都不会提交到 Git。

## 课程路线

| 课程 | 核心问题 | 对应实现 |
| --- | --- | --- |
| 01 张量与设备 | shape、dtype、广播、CPU/CUDA/MPS | `common/runtime.py` |
| 02 自动微分 | 计算图、叶子张量、梯度累积 | Notebook |
| 03 神经网络 | 模块、参数、logits | `common/models.py` |
| 04 数据加载 | 数据划分、批次、增强 | `common/data.py` |
| 05 训练与验证 | 模式、指标、检查点 | `common/engine.py`、`common/checkpoint.py` |
| 06 线性回归 | 损失和梯度下降 | `examples/linear_regression.py` |
| 07 CNN MNIST | 卷积形状和分类训练 | `examples/train_image_classifier.py` |
| 08 正则化 | Dropout、AdamW、增强、早停 | 图像训练示例 |
| 09 迁移学习 | 冻结、替换分类头、解冻 | `examples/transfer_learning.py` |
| 10 RNN/LSTM | 时间步与隐藏状态 | `examples/rnn_sequences.py` |
| 11 Attention | Q/K/V、缩放和 mask | `examples/attention_demo.py` |
| 12 混合精度 | autocast、梯度缩放、CUDA 条件执行 | `examples/mixed_precision.py` |
| 13 模型导出 | TorchScript 与输出一致性 | `examples/export_model.py` |

## 常用命令

所有训练入口接受 `--dataset`、`--data-dir`、`--epochs`、`--batch-size`、`--device`、`--output-dir` 和 `--quick`。某些示例不使用其中全部参数，但保持统一接口以便切换实验。

```bash
python 07-deep-learning/pytorch/examples/linear_regression.py --quick --epochs 20
python 07-deep-learning/pytorch/examples/train_image_classifier.py --dataset mnist --quick --epochs 1
python 07-deep-learning/pytorch/examples/train_image_classifier.py --dataset cifar10 --quick --epochs 1
python 07-deep-learning/pytorch/examples/rnn_sequences.py --quick --epochs 3
python 07-deep-learning/pytorch/examples/attention_demo.py --quick
python 07-deep-learning/pytorch/examples/transfer_learning.py --quick
python 07-deep-learning/pytorch/examples/mixed_precision.py --quick
python 07-deep-learning/pytorch/examples/export_model.py --quick
pytest 07-deep-learning/pytorch/tests
```

`--quick` 只缩小真实数据子集或合成任务规模。图像训练不会在下载失败时自动替换成随机数据。

## 数据边界

- 训练集用于梯度更新，可以打乱并应用随机增强。
- 验证集用于选择模型、早停和超参数比较，不参与梯度更新。
- 测试集只用于最终评估，不应用训练时随机增强。

## 调试顺序

1. 打印输入、标签和 logits 的 shape、dtype、device。
2. 检查训练使用 `model.train()`，评估使用 `model.eval()` 和 `inference_mode()`。
3. 检查参数梯度是否为 `None`、是否全零或出现非有限值。
4. 同时观察训练与验证曲线，防止把过拟合误判为“训练成功”。
5. CUDA 显存不足时减小 batch size，并确认没有保存带计算图的历史张量。
