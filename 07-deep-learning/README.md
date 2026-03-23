# PyTorch 深度学习

这个目录包含 PyTorch 深度学习的学习材料，从基础到进阶。

## 📚 学习路径

### 阶段 0: 数学基础（重要！）
0. **LINEAR_ALGEBRA_IN_DL.md** + **linear_algebra_practice.py** - 线性代数在深度学习中的应用

### 阶段 1: PyTorch 基础
1. **pytorch_basics.py** - PyTorch 基础概念
2. **tensors.py** - 张量操作
3. **autograd.py** - 自动微分

### 阶段 2: 神经网络基础
4. **neural_networks.py** - 构建神经网络
5. **training_loop.py** - 训练循环
6. **datasets_dataloaders.py** - 数据加载

### 阶段 3: 实战项目
7. **linear_regression.py** - 线性回归
8. **image_classification.py** - 图像分类
9. **cnn_mnist.py** - CNN 手写数字识别
10. **transfer_learning.py** - 迁移学习

## 🎯 内容概览

### 数学基础（必读！）
- **向量、矩阵、张量** - 数据表示
- **矩阵乘法** - 神经网络的核心
- **梯度和求导** - 反向传播原理
- **线性代数应用** - 注意力、卷积、SVD 等
- **10个实践案例** - 从数据表示到损失函数

### PyTorch 基础
- Tensor 张量
- 自动求导 Autograd
- GPU 加速
- 数据类型转换

### 神经网络
- 全连接网络
- 卷积神经网络 (CNN)
- 循环神经网络 (RNN)
- 激活函数
- 损失函数
- 优化器

### 实战技巧
- 数据预处理
- 模型训练
- 模型评估
- 模型保存和加载
- 超参数调优
- 过拟合处理

## 🚀 快速开始

### 环境安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装 PyTorch (CPU 版本)
pip install torch torchvision torchaudio

# 或者安装 GPU 版本 (需要 CUDA)
# 访问 https://pytorch.org/ 获取安装命令
```

### 验证安装

```python
import torch
print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")
```

## 📖 推荐学习顺序

### 初学者（从数学基础开始！）
1. **先读** `LINEAR_ALGEBRA_IN_DL.md` - 理解线性代数的重要性
2. **运行** `linear_algebra_practice.py` - 实践 10 个核心案例
3. 从 `pytorch_basics.py` 开始学习 PyTorch
4. 学习 `tensors.py` 理解张量操作
5. 学习 `autograd.py` 理解自动微分
6. 实践 `linear_regression.py` 第一个项目

### 进阶学习者
1. 学习 `neural_networks.py` 构建网络
2. 学习 `training_loop.py` 训练流程
3. 实践 `cnn_mnist.py` CNN 项目
4. 学习 `transfer_learning.py` 迁移学习

## 🎓 学习资源

### 官方资源
- [PyTorch 官方文档](https://pytorch.org/docs/)
- [PyTorch 教程](https://pytorch.org/tutorials/)
- [PyTorch 示例](https://github.com/pytorch/examples)

### 推荐课程
- [Deep Learning with PyTorch](https://pytorch.org/deep-learning-with-pytorch)
- [Fast.ai](https://www.fast.ai/)
- [吴恩达深度学习课程](https://www.coursera.org/specializations/deep-learning)

### 推荐书籍
- 《深度学习入门：基于Python的理论与实现》
- 《动手学深度学习》(Dive into Deep Learning)
- 《Python深度学习》(Deep Learning with Python)

## 📊 项目结构

```
07-deep-learning/
├── README.md                       # 本文件
├── LINEAR_ALGEBRA_IN_DL.md         # 线性代数理论指南 ⭐️ 必读
├── linear_algebra_practice.py      # 线性代数实践（10个案例）⭐️
├── pytorch_basics.py               # PyTorch 基础
├── tensors.py                      # 张量操作
├── autograd.py                     # 自动微分
├── neural_networks.py              # 神经网络
├── training_loop.py                # 训练循环
├── datasets_dataloaders.py         # 数据加载
├── linear_regression.py            # 线性回归项目
├── image_classification.py         # 图像分类
├── cnn_mnist.py                    # CNN 手写数字识别
├── transfer_learning.py            # 迁移学习
└── models/                         # 保存的模型
    └── .gitkeep
```

## 💡 学习建议

### 1. 动手实践
- 每个示例都要自己运行一遍
- 尝试修改参数观察结果
- 自己写代码实现类似功能

### 2. 理解原理
- 不要只记住 API
- 理解背后的数学原理
- 理解为什么这样设计

### 3. 循序渐进
- 从简单的例子开始
- 逐步增加复杂度
- 不要跳跃式学习

### 4. 查阅文档
- 遇到不懂的 API 查文档
- 学会阅读官方文档
- 参考官方示例

### 5. 做笔记
- 记录重要概念
- 记录遇到的问题
- 记录解决方案

## ⚠️ 注意事项

### 硬件要求
- **CPU**: 任何现代 CPU 都可以学习
- **内存**: 建议至少 8GB RAM
- **GPU**: 可选，但能加速训练（NVIDIA GPU + CUDA）
- **存储**: 建议至少 10GB 空闲空间

### 软件要求
- Python 3.8+
- PyTorch 1.9+
- NumPy
- Matplotlib (用于可视化)
- Jupyter Notebook (可选)

### 常见问题

**Q: 必须有 GPU 才能学习 PyTorch 吗？**
A: 不需要。CPU 足够学习基础知识，GPU 只是加速训练。

**Q: PyTorch 和 TensorFlow 选哪个？**
A: PyTorch 更 Pythonic，更易学习和调试。两者都很好，选一个深入学习即可。

**Q: 需要先学习深度学习理论吗？**
A: 建议理论和实践结合，先学基础理论，再通过代码实践加深理解。

**Q: 学习需要多长时间？**
A: 基础知识 1-2 周，深入学习需要 2-3 个月，精通需要持续实践。

## 🎯 学习目标

### 基础目标
- [ ] **理解线性代数在深度学习中的应用（必须！）**
- [ ] 理解 Tensor 张量操作
- [ ] 掌握自动求导机制
- [ ] 能够构建简单的神经网络
- [ ] 完成线性回归项目

### 进阶目标
- [ ] 理解 CNN 原理和实现
- [ ] 完成图像分类项目
- [ ] 理解 RNN/LSTM 原理
- [ ] 掌握迁移学习

### 高级目标
- [ ] 能够阅读和实现论文
- [ ] 能够自己设计网络架构
- [ ] 能够调试和优化模型
- [ ] 能够部署模型到生产环境

## 🔧 调试技巧

### 1. 检查张量形状
```python
print(f"Shape: {tensor.shape}")
print(f"Size: {tensor.size()}")
```

### 2. 检查梯度
```python
print(f"Requires grad: {tensor.requires_grad}")
print(f"Gradient: {tensor.grad}")
```

### 3. 使用断言
```python
assert tensor.shape == (batch_size, features), "Shape mismatch!"
```

### 4. 可视化
```python
import matplotlib.pyplot as plt
plt.imshow(image)
plt.show()
```

## 📈 学习进度跟踪

建议在学习过程中记录：
- 学习日期
- 完成的章节
- 遇到的问题
- 解决方案
- 心得体会

## 🎉 开始学习

**重要提示：先从数学基础开始！**

```bash
cd 07-deep-learning

# 第一步：阅读线性代数指南
# 推荐使用 Markdown 阅读器或 VSCode 打开
open LINEAR_ALGEBRA_IN_DL.md

# 第二步：运行线性代数实践案例
python linear_algebra_practice.py

# 第三步：开始 PyTorch 学习
python pytorch_basics.py
```

Good luck! 🚀
