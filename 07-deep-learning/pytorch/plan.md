# PyTorch 学习计划

这份计划面向已经掌握 Python、基础线性代数和导数概念的学习者，目标是通过持续编码和两个小项目，建立完整的 PyTorch 模型开发、训练、验证、推理和调试能力。

## 学习目标

完成计划后，你应该能够：

1. 熟练操作 Tensor，并判断常见广播和维度变换的结果。
2. 理解 Autograd 计算图、梯度累积和梯度截断等核心机制。
3. 使用 `nn.Module` 独立实现 MLP、CNN 和简单 Transformer Encoder。
4. 编写包含训练、验证、测试、checkpoint 和推理的完整流程。
5. 使用 Dataset 和 DataLoader 组织真实数据。
6. 排查 shape、device、dtype、梯度和 loss 异常等常见问题。
7. 阅读并修改结构清晰的 PyTorch 项目代码。

本计划不包含手写 CUDA 算子、分布式训练和大模型算子开发。

## 开始前

### 前置知识

- Python：函数、类、迭代器、列表和字典等基础知识。
- NumPy：数组、索引、切片和矩阵运算。
- 数学：向量、矩阵乘法、导数、链式法则和基础概率。

### 环境要求

- Python 3.10 或更高版本。
- PyTorch 2.x。
- 能运行 Jupyter Notebook 或 Python 脚本。
- 没有 GPU 也可以完成计划；代码应同时兼容 CPU、CUDA 和 Apple Silicon MPS。

建议第一天记录 Python、PyTorch 和设备信息，并运行一次 Tensor 运算，确认环境可用。

### 时间安排

- 标准进度：6 周，工作日每天 1.5-2 小时，周末每天 3-4 小时。
- 加速进度：前 4 周完成基础和 CNN 项目，第 5-6 周继续学习 Transformer 和工程实践。
- 每次学习建议分配：20% 阅读和理解，60% 编码，20% 复盘和记录。

不要把“完全不查资料”作为熟练标准。真正的目标是能独立拆解问题、阅读报错和官方文档，并完成实现。

## 第 1 周：Tensor 与 Autograd

### 本周目标

掌握 Tensor、索引、广播和自动求导，能够手算关键 shape 和简单梯度。

### Day 1-2：Tensor 基础

- 创建 Tensor，理解 shape、dtype 和 device。
- NumPy 与 Tensor 互转，理解共享内存可能带来的影响。
- CPU、CUDA 和 MPS 之间的设备切换。
- 使用 `reshape`、`view`、`squeeze`、`unsqueeze`、`transpose` 和 `permute`。
- 使用 `cat` 和 `stack`，解释两者输出 shape 的区别。
- 比较 `view`、`reshape` 和 `contiguous()`。
- 比较 `clone()`、`detach()` 和 `detach().clone()`。

### Day 3-4：索引与广播

- 整数索引、切片、花式索引和布尔掩码。
- 理解整数索引会消除维度，而切片通常保留维度。
- 根据输入 shape 判断能否广播，并计算输出 shape。
- 理解 `expand` 不复制数据，以及广播维度的梯度会在反向传播时求和。
- 了解原地操作可能对 Autograd 造成的影响。

### Day 5-7：Autograd

- `requires_grad`、叶子节点、中间节点和 `grad_fn`。
- 计算图如何建立，以及一次 `backward()` 后图的默认生命周期。
- 标量 loss 的 `backward()`；非标量输出需要显式传入外部梯度。
- 梯度累积以及为什么需要清空梯度。
- `torch.autograd.grad()`、一阶导数和简单二阶导数。
- `detach()`、`torch.no_grad()` 和 `torch.inference_mode()` 的使用场景。
- 使用 `retain_grad()` 检查中间 Tensor 的梯度。

### 本周作业

1. 完成 5 道广播和输出 shape 推演题。
2. 完成 3 道 Autograd 梯度计算题，并手算结果进行对照。
3. 只使用 Tensor 和 Autograd 实现线性回归 `y = wx + b`。
4. 再手动写出线性回归参数的梯度更新，与 Autograd 结果比较。

### 验收标准

- 能解释一段 Tensor 代码中每一步的 shape。
- 能说明叶子 Tensor 的梯度存放在哪里。
- 能解释梯度为什么会累积。
- 能正确选择 `reshape`、`detach` 和 `no_grad`。

## 第 2 周：`nn.Module` 与模型结构

### 本周目标

理解参数注册和模块组合机制，能够独立定义、保存和加载模型。

### Day 8-9：`nn.Module` 基础

- `__init__()`、`forward()` 和通过 `model(x)` 调用模型的过程。
- `parameters()`、`named_parameters()`、`state_dict()`。
- 参数、普通 Tensor 和 buffer 的区别；了解 `register_buffer()`。
- `model.train()` 和 `model.eval()` 对 Dropout、BatchNorm 的影响。
- `Sequential`、`ModuleList` 和 `ModuleDict` 的区别。

### Day 10-11：常用层和损失函数

- `nn.Linear`、`nn.Embedding` 的输入输出和参数 shape。
- ReLU、Sigmoid、Tanh 等常见激活函数。
- `nn.ReLU()` 与 `torch.nn.functional.relu()` 的区别。
- `MSELoss`、`BCEWithLogitsLoss` 和 `CrossEntropyLoss`。
- 理解 `CrossEntropyLoss` 接收 logits，标签通常为 `torch.long` 类型的类别索引。
- 理解二分类的一维 logits 与两类 logits 两种常见写法。

### Day 12-14：模型实现与持久化

- 实现两层 MLP。
- 使用统一的 `device` 将模型和数据移动到相同设备。
- 查看参数名称、shape 和参数量。
- 保存和加载 `state_dict`。
- 保存包含模型、优化器、epoch 和指标的 checkpoint。
- 从 checkpoint 恢复训练，并编写独立推理函数。

### 本周作业

1. 使用 `nn.Module` 重写线性回归。
2. 实现一个两层多分类网络。
3. 保存模型，重新创建模型并加载参数，验证加载前后的输出一致。
4. 人为遗漏一个模块注册，观察并解释 `state_dict` 或参数列表的变化。

### 验收标准

- 能独立实现一个自定义 `nn.Module`。
- 能解释 `ModuleList` 为什么不同于普通 Python list。
- 能说明训练模式和评估模式的差异。
- 能正确保存、加载模型并恢复训练。

## 第 3 周：数据管道与完整训练循环

### 本周目标

完成从数据集到训练、验证和测试的闭环，并形成可复用的训练函数。

### Day 15-17：Dataset 与 DataLoader

- 使用 `TensorDataset`。
- 实现自定义 Dataset 的 `__len__()` 和 `__getitem__()`。
- 理解 `batch_size`、`shuffle`、`drop_last` 和 `num_workers`。
- 检查一个 batch 中数据和标签的 shape、dtype、device。
- 正确划分训练集、验证集和测试集，避免数据泄漏。
- 了解 `collate_fn`、`pin_memory` 和 `non_blocking` 的用途。

### Day 18-20：训练、验证与测试

完整训练流程至少包含：

```python
for epoch in range(num_epochs):
    model.train()
    for x, y in train_loader:
        x = x.to(device)
        y = y.to(device)

        optimizer.zero_grad(set_to_none=True)
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.inference_mode():
        for x, y in val_loader:
            # 累计验证 loss 和指标
            ...
```

- 正确累计整个 epoch 的 loss，避免直接平均 batch loss 带来的误差。
- 计算分类准确率，并区分 loss 和业务指标。
- 使用 SGD 和 Adam，理解学习率与 weight decay 的基本作用。
- 使用一种学习率调度器，明确它应该在 batch 后还是 epoch 后调用。
- 根据验证集指标保存最佳 checkpoint。
- 训练完成后只在测试集上进行最终评估。

### Day 21：训练调试

- 先尝试让模型过拟合一个很小的 batch，验证训练链路正确。
- 检查输入、标签、logits 和 loss 的 shape 与 dtype。
- 检查模型和数据是否位于同一 device。
- 检查梯度是 `None`、全零、过大，还是包含 NaN/Inf。
- 排查 loss 不下降：数据、标签、损失函数、学习率、模型容量和参数更新。
- 使用固定随机种子提高实验可复现性，并理解完全确定性可能影响性能。

### 本周作业

使用模拟数据完成一个二分类或多分类任务，提交：

- Dataset 和 DataLoader。
- `train_one_epoch()`、`evaluate()` 和 `predict()`。
- 训练 loss、验证 loss 和验证指标。
- 最佳 checkpoint 保存与加载。
- 测试集最终结果。
- 一次小 batch 过拟合实验。

### 验收标准

- 能不照抄模板写出训练和验证主流程。
- 能解释 `zero_grad()`、`backward()` 和 `step()` 的调用顺序。
- 能恢复中断的训练。
- loss 异常时能按固定清单逐项排查。

## 第 4 周：CNN 图像分类项目

### 本周目标

完成第一个可复现的小型项目，将前 3 周的知识串成完整工程流程。

### Day 22-24：CNN 基础

- 理解 `Conv2d` 输入的 NCHW 格式。
- 根据 kernel、stride、padding 和 dilation 计算输出空间尺寸。
- 使用池化、BatchNorm、Dropout 和全连接分类头。
- 使用自适应池化减少对固定输入尺寸的依赖。
- 了解图像归一化和训练集数据增强的基本作用。

### Day 25-28：完成项目

推荐使用 MNIST、Fashion-MNIST 或 CIFAR-10。项目必须包含：

1. 数据下载、预处理和数据集划分。
2. CNN 模型和参数量统计。
3. 训练、验证、最佳模型保存和测试。
4. loss 与准确率曲线。
5. 单张或一个 batch 的推理示例。
6. 错误分类样本分析。
7. README 或实验记录：环境、模型、超参数、结果和已知问题。

建议至少进行一次对照实验，例如改变学习率、模型宽度、BatchNorm 或数据增强，并说明结果差异。

### 验收标准

- 项目可以从头运行，而不是只能在已有 Notebook 状态中运行。
- 加载最佳 checkpoint 后可以单独执行推理。
- 能解释 CNN 中各层的输入输出 shape。
- 能结合训练和验证曲线判断明显的过拟合或欠拟合。

## 第 5 周：Attention 与简单 Transformer

### 本周目标

理解 Self-Attention 的数据流，实现并训练一个简单 Transformer Encoder 分类模型。

### Day 29-31：Attention 基础

- 理解 token embedding 和位置编码。
- 理解 Query、Key、Value 的含义和 shape。
- 手动实现 scaled dot-product attention。
- 理解缩放因子、softmax 维度和 attention 权重。
- 理解 padding mask 与 causal mask 的区别。

### Day 32-35：Transformer Encoder

- 学习多头注意力中的 head 拆分和维度变换。
- 理解残差连接、LayerNorm 和前馈网络。
- 使用 `nn.MultiheadAttention` 或 `nn.TransformerEncoderLayer`。
- 实现简单文本分类模型：Embedding、位置编码、Encoder 和分类头。
- 检查 batch-first 设置、mask shape 和 padding 位置。

### 本周作业

1. 给定 batch、序列长度、head 数和 embedding 维度，写出 Attention 各阶段 shape。
2. 实现一个可运行的 scaled dot-product attention。
3. 在小型或模拟文本数据上训练 Transformer Encoder 分类模型。
4. 保存模型并对新输入执行推理。

### 验收标准

- 能解释 Attention 中矩阵乘法和 softmax 的维度。
- 能区分 padding mask 和 causal mask。
- 能排查常见的 mask、batch 和序列维度错误。
- 能独立搭建简单 Transformer Encoder，而不要求从零实现所有内部算子。

## 第 6 周：工程实践与综合巩固

### 本周目标

提高训练稳定性、可维护性和代码阅读能力，完成一次综合复盘。

### Day 36-38：训练稳定性与性能

- 使用梯度裁剪，并观察裁剪前后的梯度范数。
- 使用自动混合精度；根据设备选择适用的 autocast 和 GradScaler 用法。
- 了解训练与推理阶段的显存来源。
- 避免意外保存计算图，例如错误累计带梯度的 loss Tensor。
- 初步学习 profiler 或计时方法，定位明显性能瓶颈。

### Day 39-40：代码组织

- 将数据、模型、训练、评估和配置拆分成清晰模块。
- 统一随机种子、设备选择和日志记录。
- 通过配置集中管理超参数，避免散落的魔法数字。
- 保存运行配置、最佳指标和 checkpoint。
- 为关键函数添加最小单元测试或 shape 测试。

### Day 41-42：阅读与复现

- 选择一个规模较小的 PyTorch 开源项目或官方示例。
- 找到数据入口、模型入口、loss、优化器和训练主循环。
- 修改一个模型参数或训练配置，并成功运行。
- 写一页复盘：代码结构、学到的模式、遇到的问题和下一步方向。

### 综合验收

在不复制完整现成项目的前提下，独立完成以下任务：

1. 从数据到推理实现一个分类项目。
2. 使用 train、validation、test 三个数据阶段。
3. 保存最佳模型并恢复中断训练。
4. 输出训练曲线和最终指标。
5. 定位一个人为制造的 shape、device 或梯度问题。
6. 解释 MLP、CNN 或 Transformer 中主要 Tensor 的 shape 变化。
7. 阅读官方文档解决一个计划中没有直接给出答案的问题。

达到这些标准，可以认为已经具备较扎实的 PyTorch 入门和小型项目实践能力，但仍需要通过更多真实项目积累熟练度。

## 调试检查清单

遇到问题时，按以下顺序检查：

1. 打印输入、标签、模型输出的 shape、dtype 和 device。
2. 确认任务、模型最后一层、标签格式和损失函数相匹配。
3. 用一个小 batch 尝试过拟合。
4. 确认参数出现在 `named_parameters()` 中，并且优化器接收了这些参数。
5. 检查关键参数的 `grad` 是否为 `None`、零、NaN 或 Inf。
6. 确认训练阶段调用 `train()`，验证和推理阶段调用 `eval()`。
7. 检查学习率、数据归一化和标签是否正确。
8. 将复杂流程缩小为最小可复现示例。

## 可选拓展

完成核心计划后，再根据方向选择：

- 概率模型：`torch.distributions`、`rsample()` 和变分自编码器。
- 计算机视觉：迁移学习、检测、分割和更强的数据增强。
- NLP：子词分词、语言模型、causal mask 和 Hugging Face Transformers。
- 性能工程：`torch.compile`、profiling、量化和分布式训练。
- 部署：TorchScript、ONNX 或服务化推理。

## 学习原则

1. 至少 60% 的时间用于写代码和调试。
2. 示例可以参考，但关键训练循环和模型至少要自己重新实现一次。
3. 每周保留代码、实验结果和问题记录，不只保留阅读笔记。
4. 报错时先分析 shape、dtype、device 和梯度，再搜索解决方案。
5. 优先阅读 PyTorch 官方教程和 API 文档，养成基于文档验证结论的习惯。
