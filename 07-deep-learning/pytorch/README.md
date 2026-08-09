# PyTorch 深度学习课程

本课程面向掌握 Python 基础的学习者。每个 Notebook 包含概念模型、多个实验、底层机制、检查点、练习和专项调试建议；`common/` 保存可复用实现，`examples/` 提供可从终端重复运行的任务。

## 安装与启动

从仓库根目录运行：

```bash
python -m pip install -r requirements/ai.txt
jupyter lab 07-deep-learning/pytorch/notebooks
```

首次使用 MNIST、CIFAR-10 或预训练 ResNet 时需要网络。数据保存在 `data/`，检查点和导出模型保存在 `artifacts/`，两者都不会提交到 Git。

## 如何使用课程

课程共有 30 个 Notebook，但文件编号不是严格的学习顺序。请使用下面的 canonical learning path；`00-prerequites.ipynb` 只用于环境检查和工具查询，不属于必读主线，也不建议从头到尾顺序阅读。

### Canonical Learning Path

```text
01 -> 02 -> 25 -> 03 -> 29 -> 06 -> 04 -> 18 -> 05 -> 15 -> 22
   -> 07 -> 08 -> 16 -> 17
   -> 10 -> 11 -> 14 -> 26
   -> 09 -> 12 -> 21 -> 19 -> 20 -> 23 -> 13 -> 24 -> 27 -> 28
```

- `25` 是 `02` 的深入案例：自定义梯度与 `gradcheck`。
- `29` 必须在训练循环前学习，用于确定模型输出、标签和 loss 契约。
- `18` 必须在真实数据项目之前学习，避免预处理和数据泄漏问题。
- `26` 是 Attention/Encoder 之后的生成模型拓展。
- `27`、`28` 放在最后，分别需要分布式运行环境和 PyTorch 2.x。

### 阶段 1：PyTorch 核心基础（必修）

| Notebook | 核心能力 | 阶段产出 |
| --- | --- | --- |
| 01 张量与设备 | shape、dtype、广播、view、device | 能预测常见 Tensor 操作结果 |
| 02 自动微分 | 计算图、叶子节点、梯度累积 | 能解释和检查简单梯度 |
| 25 自定义 Autograd | Function、backward、gradcheck | 能验证自定义梯度 |
| 03 神经网络 | Module、参数注册、logits、buffer | 能独立定义两层模型 |
| 29 任务契约 | 回归、二分类、多分类、多标签 | 能正确匹配输出、标签和 loss |
| 06 线性回归 | 参数更新和损失曲线 | 完成第一个最小训练任务 |
| 04、18 数据管道 | Dataset、DataLoader、预处理、泄漏 | 能构建可靠的数据边界 |
| 05 训练与验证 | train/eval、指标、checkpoint | 能写完整训练验证循环 |

阶段验收：独立完成一个合成数据分类任务，包含 Dataset、模型、训练、验证、最佳 checkpoint 和推理。

### 阶段 2：模型与项目实践（必修一条，其他选修）

| Notebook | 方向 | 建议 |
| --- | --- | --- |
| 07、08、16 | CNN、正则化、图像分类项目 | 计算机视觉主线必修 |
| 09 | 迁移学习 | 图像方向进阶 |
| 10 | RNN/LSTM | 序列模型基础 |
| 11、14 | Attention、Transformer Encoder | NLP/Transformer 主线必修 |
| 26 | Decoder-only Transformer 与生成 | 生成模型进阶 |

阶段验收：完成 CNN 图像分类或 Transformer 文本分类项目，提交训练曲线、测试指标、错误样本和推理示例。

### 阶段 3：训练与工程能力（推荐必修）

| Notebook | 核心能力 |
| --- | --- |
| 12、21、22 | AMP、Profiler、梯度累积与裁剪 |
| 15 | shape、dtype、device、梯度和 loss 调试 |
| 17、18 | 评估指标、推理、预处理和数据泄漏 |
| 19、20 | 实验配置、日志和测试 |
| 23 | 阅读与修改 PyTorch 项目代码 |
| 13、24 | 模型导出与部署契约 |

阶段验收：从 checkpoint 恢复训练，定位一个人为制造的训练问题，并为模型编写 shape、参数更新和保存加载测试。

### 阶段 4：PyTorch 进阶机制（按需学习）

| Notebook | 核心能力 | 环境要求 |
| --- | --- | --- |
| 25 | 自定义 Autograd、`gradcheck` | CPU 可完成 |
| 27 | DDP、rank、world size、DistributedSampler | 多进程/多 GPU 环境完成全部练习 |
| 28 | `torch.compile`、graph break | PyTorch 2.x |

### 内容分类

- 参考索引：`00`
- 基础机制：`01`、`02`、`03`、`04`、`06`、`25`、`29`
- 模型结构：`07`、`08`、`09`、`10`、`11`、`14`、`26`
- 训练工程：`05`、`15`、`18`、`19`、`20`、`21`、`22`、`23`
- 部署与系统：`12`、`13`、`24`、`27`、`28`
- 综合项目：`16`、`17`

需要查询 NumPy、Pandas、torchvision、Hugging Face、LoRA 或其他生态工具时，再按需阅读 `00-prerequites.ipynb` 对应章节。

### 分类验收

- 基础机制：手算 shape 和广播，验证一阶/二阶导，正确匹配 loss 与标签。
- 模型结构：独立实现 MLP，解释 CNN shape，构造 Attention mask，并完成一次 Encoder 分类或 Decoder 生成。
- 训练工程：手写训练/验证循环，恢复 checkpoint，修复至少三类训练错误，并保存配置和指标。
- 部署与系统：完成导出 round-trip，定义推理契约，理解 DDP 数据分片，并比较 eager/compiled 输出。
- 综合项目：从预处理开始完成真实数据项目，输出曲线、测试指标、错误分析和推理结果。

## 完成标准

完成 Notebook 不等于掌握。满足以下条件后，可以认为具备较扎实的 PyTorch 中级工程能力：

1. 不复制完整模板，独立完成一个真实数据项目。
2. 能解释模型中主要 Tensor 的 shape 和 device。
3. 能实现训练、验证、测试、checkpoint、恢复训练和推理。
4. 能通过小 batch 过拟合、梯度检查和有限值检查定位训练问题。
5. 能比较至少两组实验并保存配置、指标和模型版本。
6. 能阅读一个新的 PyTorch 项目，找到数据、模型、loss、优化器和训练入口。
7. 遇到陌生 API 时能阅读官方文档并写最小验证代码。

## 常用命令

所有训练入口接受 `--dataset`、`--data-dir`、`--epochs`、`--batch-size`、`--device`、`--output-dir`、`--quick`、`--resume`、`--seed` 和 `--patience`。某些演示不使用其中全部参数，但保持统一接口以便切换实验。

```bash
python 07-deep-learning/pytorch/examples/linear_regression.py --quick --epochs 20
python 07-deep-learning/pytorch/examples/linear_regression.py --epochs 40 --resume 07-deep-learning/pytorch/artifacts/linear_regression.pt
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

图像分类和迁移学习始终根据验证指标保存最佳检查点，并在最终测试前重新加载它。恢复训练会同时恢复模型、优化器以及可用的调度器状态。

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
