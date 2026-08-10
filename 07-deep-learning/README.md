# 深度学习学习路线

本目录把“框架无关的原理”和“PyTorch 工程实践”分开。建议先建立数学与训练直觉，再进入 PyTorch 的数据、模型、训练、调试和部署流程。

## 目录

- [`fundamentals/`](fundamentals/README.md)：10 节从纯 Python 到 NumPy 的手写 MLP 课程，覆盖反向传播、优化、验证和调试。
- [`pytorch/`](pytorch/README.md)：以 Notebook 为主的 PyTorch 完整课程，所有导入 `torch` 或 `torchvision` 的内容都在这里。
- [`pytorch/tutorials/`](pytorch/tutorials/README.md)：PyTorch 官方 Tutorials Git 仓库的本地副本，用于完成基础课程后的查漏补缺和专题进阶。

## 推荐顺序

1. 按编号完成 `fundamentals/notebooks/` 中的 10 节手写神经网络课程。
2. 使用 `fundamentals/linear_algebra.md` 和练习脚本巩固矩阵与数值梯度。
3. 按 [`pytorch/README.md`](pytorch/README.md) 中的 canonical learning path 学习框架课程。
4. 使用 `pytorch/examples/` 重复运行训练任务，修改参数观察行为。
5. 完成 `pytorch/tutorials/beginner_source/basics/` 中的官方基础教程，对照自编课程查漏补缺。
6. 从官方 Tutorials 中选择一个应用方向和一个工程方向深入学习，并把示例改造成自己的小项目。
7. 运行两套测试，确认手写梯度、训练收敛、框架训练循环和模型形状符合预期。

## PyTorch 官方 Tutorials 学习计划

`pytorch/tutorials/` 是完整的官方文档源码仓库，不适合按目录逐文件阅读。先完成本仓库的 Notebook 主线，再按以下顺序使用它。

### 1. 基础复习（必修）

按顺序学习 [`beginner_source/basics/`](pytorch/tutorials/beginner_source/basics/)：

```text
tensorqs -> data -> transforms -> buildmodel -> autogradqs
         -> optimization -> saveloadrun -> quickstart
```

这一阶段以“能独立重写”为完成标准，而不是只运行代码。完成后，应能从空文件写出 Dataset、DataLoader、`nn.Module`、训练循环以及模型保存和加载流程。

### 2. 综合项目（必修一项）

- 计算机视觉：`beginner_source/blitz/cifar10_tutorial.py`、`beginner_source/transfer_learning_tutorial.py`。
- NLP：`beginner_source/nlp/` 或 `intermediate_source/seq2seq_translation_tutorial.py`。
- 生成模型：`beginner_source/dcgan_faces_tutorial.py`。
- 强化学习：`intermediate_source/reinforcement_q_learning.py` 或 `intermediate_source/reinforcement_ppo.py`。

不要只照抄官方示例：至少更换一次数据集、模型结构或训练配置，并记录验证指标、失败实验和改动结论。

### 3. 工程专题（必修一项）

- 性能分析：`beginner_source/profiler.py`、`intermediate_source/tensorboard_tutorial.rst`。
- 编译优化：`intermediate_source/torch_compile_tutorial.py`，再按需阅读 `recipes_source/` 中的 `torch.compile` 内容。
- 模型导出：`beginner_source/onnx/`、`intermediate_source/torch_export_tutorial.py`。
- 分布式训练：先读 `beginner_source/dist_overview.rst`，再进入 DDP、FSDP 或 Tensor Parallel 专题。

`advanced_source/`、`recipes_source/` 和 `unstable_source/` 不作为连续课程；遇到具体项目需求时再检索。尤其是 `unstable_source/`，其中 API 和运行条件可能变化，不纳入基础阶段的完成标准。

## 环境

```bash
python -m pip install -r requirements/data.txt
jupyter lab 07-deep-learning/pytorch/notebooks
```

完成 fundamentals 只需 NumPy、Matplotlib 和 Jupyter。进入 PyTorch 部分前，再安装 `requirements/ai.txt`；PyTorch 基线为 2.2+。所有框架示例支持 CPU，可用时也支持 CUDA 或 Apple MPS。MNIST、CIFAR-10 和预训练权重会在首次使用时下载。

## 学完后应能做到

- 根据张量形状预测全连接、卷积、循环网络和 Attention 的数据流。
- 不依赖自动求导实现 MLP 的前向传播、反向传播、优化和梯度检查。
- 正确划分训练、验证、测试集并解释 `train()`、`eval()` 和梯度上下文。
- 编写可恢复的训练任务，保存检查点并加载推理模型。
- 识别过拟合、设备不一致、梯度缺失、数据泄漏和显存问题。
- 使用迁移学习、混合精度，并导出可复现的推理模型。
