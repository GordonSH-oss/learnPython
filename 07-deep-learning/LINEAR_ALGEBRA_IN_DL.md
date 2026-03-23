# 线性代数在深度学习中的应用

线性代数是深度学习的核心数学基础，几乎每个神经网络操作都涉及线性代数。

## 🎯 核心用途概览

### 1. 数据表示
- **向量** - 表示单个样本的特征
- **矩阵** - 表示批量数据
- **张量** - 表示高维数据（图像、视频等）

### 2. 神经网络计算
- **矩阵乘法** - 神经网络的核心运算
- **权重矩阵** - 存储网络参数
- **偏置向量** - 调整输出

### 3. 模型训练
- **梯度** - 优化方向
- **反向传播** - 链式法则 + 矩阵求导
- **批量处理** - 矩阵并行计算

---

## 📊 详细应用场景

### 1️⃣ 数据表示和组织

#### 向量表示单个样本
```python
import numpy as np
import torch

# 一张 28x28 的灰度图像
image = torch.randn(28, 28)  # 2D 矩阵

# 展平成向量用于全连接层
image_vector = image.view(-1)  # 784 维向量
print(f"图像向量形状: {image_vector.shape}")  # [784]

# 一个句子的词嵌入
sentence = torch.randn(10, 300)  # 10 个词，每个词 300 维
print(f"句子表示: {sentence.shape}")  # [10, 300]
```

#### 矩阵表示批量数据
```python
# Batch 处理：一次处理多个样本
batch_size = 32
features = 784

# 32 张图像，每张展平成 784 维
batch_images = torch.randn(batch_size, features)
print(f"批量图像: {batch_images.shape}")  # [32, 784]

# 好处：GPU 并行计算，加速训练
```

#### 张量表示高维数据
```python
# RGB 图像：高 × 宽 × 通道
rgb_image = torch.randn(3, 224, 224)  # [通道, 高, 宽]
print(f"RGB 图像: {rgb_image.shape}")

# 批量 RGB 图像
batch_rgb = torch.randn(32, 3, 224, 224)  # [批量, 通道, 高, 宽]
print(f"批量 RGB: {batch_rgb.shape}")

# 视频：批量 × 通道 × 时间 × 高 × 宽
video = torch.randn(8, 3, 30, 224, 224)  # 8 个视频，每个 30 帧
print(f"视频数据: {video.shape}")
```

---

### 2️⃣ 全连接层（最基础的应用）

#### 数学原理
```
输入: x (n 维向量)
权重: W (m × n 矩阵)
偏置: b (m 维向量)
输出: y = Wx + b (m 维向量)
```

#### PyTorch 实现
```python
import torch
import torch.nn as nn

# 全连接层
input_dim = 784   # 输入维度（28x28 图像展平）
output_dim = 128  # 输出维度

fc = nn.Linear(input_dim, output_dim)
# 内部有两个参数：
# - weight: [output_dim, input_dim] = [128, 784]
# - bias:   [output_dim] = [128]

# 单个样本
x = torch.randn(784)
y = fc(x)
print(f"输入: {x.shape}, 输出: {y.shape}")  # [784] -> [128]

# 批量处理
batch_x = torch.randn(32, 784)
batch_y = fc(batch_x)
print(f"批量输入: {batch_x.shape}, 批量输出: {batch_y.shape}")  # [32, 784] -> [32, 128]
```

#### 矩阵乘法详解
```python
# 手动实现全连接层
input_size = 3
output_size = 2
batch_size = 4

# 权重矩阵 W: [output_size, input_size]
W = torch.tensor([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])

# 偏置向量 b: [output_size]
b = torch.tensor([0.1, 0.2])

# 批量输入 X: [batch_size, input_size]
X = torch.randn(batch_size, input_size)

# 前向传播: Y = XW^T + b
# X @ W.T 的形状: [4, 3] @ [3, 2] = [4, 2]
Y = X @ W.T + b
print(f"输出形状: {Y.shape}")  # [4, 2]

# 等价于 PyTorch 的实现
fc = nn.Linear(input_size, output_size)
fc.weight.data = W
fc.bias.data = b
Y_pytorch = fc(X)
print(f"PyTorch 输出: {Y_pytorch.shape}")
```

---

### 3️⃣ 卷积神经网络（CNN）

#### 卷积 = 矩阵运算
```python
# 卷积可以看作是特殊的矩阵乘法
conv = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3)

# 输入图像: [batch, channels, height, width]
image = torch.randn(1, 3, 224, 224)
output = conv(image)
print(f"卷积输出: {output.shape}")  # [1, 64, 222, 222]

# 卷积核本质上是小矩阵（3x3, 5x5 等）
# 在图像上滑动，进行矩阵运算
```

#### 全局平均池化 = 矩阵平均
```python
# 全局平均池化将特征图压缩成向量
gap = nn.AdaptiveAvgPool2d((1, 1))

feature_map = torch.randn(1, 512, 7, 7)  # [batch, channels, H, W]
pooled = gap(feature_map)
print(f"池化后: {pooled.shape}")  # [1, 512, 1, 1]

# 展平成向量
vector = pooled.view(pooled.size(0), -1)
print(f"向量: {vector.shape}")  # [1, 512]
```

---

### 4️⃣ 注意力机制（Attention）

#### 自注意力 = 矩阵乘法的艺术
```python
# 简化的自注意力实现
seq_len = 10     # 序列长度
d_model = 512    # 特征维度
batch_size = 2

# Query, Key, Value 都是矩阵
Q = torch.randn(batch_size, seq_len, d_model)
K = torch.randn(batch_size, seq_len, d_model)
V = torch.randn(batch_size, seq_len, d_model)

# 注意力分数 = Q @ K^T
scores = torch.matmul(Q, K.transpose(-2, -1))  # [2, 10, 10]
scores = scores / (d_model ** 0.5)  # 缩放

# 注意力权重 = softmax(scores)
attention_weights = torch.softmax(scores, dim=-1)

# 输出 = 注意力权重 @ V
output = torch.matmul(attention_weights, V)  # [2, 10, 512]

print(f"注意力输出: {output.shape}")
```

---

### 5️⃣ 反向传播（梯度计算）

#### 链式法则 + 矩阵求导
```python
# 简单的神经网络
x = torch.randn(1, 10, requires_grad=True)
W1 = torch.randn(20, 10, requires_grad=True)
b1 = torch.randn(20, requires_grad=True)
W2 = torch.randn(1, 20, requires_grad=True)
b2 = torch.randn(1, requires_grad=True)

# 前向传播
h = torch.relu(x @ W1.T + b1)  # [1, 20]
y = h @ W2.T + b2               # [1, 1]

# 损失
loss = (y - 1) ** 2

# 反向传播（自动计算梯度）
loss.backward()

print(f"W1 的梯度形状: {W1.grad.shape}")  # [20, 10]
print(f"b1 的梯度形状: {b1.grad.shape}")  # [20]

# 梯度的计算涉及大量矩阵求导
# PyTorch 自动完成，但底层都是线性代数
```

---

### 6️⃣ 批归一化（Batch Normalization）

#### 统计量计算 = 向量运算
```python
batch_norm = nn.BatchNorm1d(128)

# 批量数据
x = torch.randn(32, 128)  # [batch_size, features]

# 批归一化计算每个特征的均值和方差
# mean: [128]
# var:  [128]
normalized = batch_norm(x)

print(f"归一化后: {normalized.shape}")  # [32, 128]

# 本质上是向量的均值、方差计算和标准化
# mean = sum(x, dim=0) / batch_size
# var = sum((x - mean)^2, dim=0) / batch_size
# normalized = (x - mean) / sqrt(var + eps)
```

---

### 7️⃣ 嵌入层（Embedding）

#### 查表 = 矩阵索引
```python
# 词嵌入
vocab_size = 10000
embedding_dim = 300

embedding = nn.Embedding(vocab_size, embedding_dim)
# 内部是一个矩阵: [vocab_size, embedding_dim] = [10000, 300]

# 输入是词的索引
word_ids = torch.tensor([5, 100, 234, 9])  # 4 个词的 ID
word_vectors = embedding(word_ids)
print(f"词向量: {word_vectors.shape}")  # [4, 300]

# 本质上是从嵌入矩阵中查找对应行
# word_vectors[i] = embedding.weight[word_ids[i]]
```

---

### 8️⃣ 损失函数计算

#### 向量范数和距离
```python
# L2 损失（均方误差）
pred = torch.randn(32, 10)
target = torch.randn(32, 10)

# 方法1：手动计算
mse = torch.mean((pred - target) ** 2)

# 方法2：使用内置函数
mse_loss = nn.MSELoss()
loss = mse_loss(pred, target)

print(f"MSE Loss: {loss.item()}")

# 余弦相似度
cos_sim = nn.CosineSimilarity(dim=1)
similarity = cos_sim(pred, target)
print(f"余弦相似度: {similarity.shape}")  # [32]

# 这些都是向量/矩阵的范数和内积运算
```

---

### 9️⃣ 矩阵分解（高级应用）

#### SVD 用于降维和压缩
```python
# 奇异值分解（SVD）
weight_matrix = torch.randn(1000, 500)

# SVD 分解
U, S, V = torch.svd(weight_matrix)
print(f"U: {U.shape}, S: {S.shape}, V: {V.shape}")
# U: [1000, 1000], S: [500], V: [500, 500]

# 低秩近似（压缩模型）
k = 100  # 保留前 100 个奇异值
compressed = U[:, :k] @ torch.diag(S[:k]) @ V[:, :k].T
print(f"压缩后: {compressed.shape}")  # [1000, 500]

# 应用：模型压缩、加速推理
```

---

### 🔟 优化算法

#### 梯度下降 = 向量运算
```python
# 梯度下降更新规则
W = torch.randn(100, 50)
grad_W = torch.randn(100, 50)
learning_rate = 0.01

# 参数更新（向量运算）
W = W - learning_rate * grad_W

# Adam 优化器（涉及更复杂的向量运算）
# m = β1 * m + (1 - β1) * grad     # 一阶矩估计
# v = β2 * v + (1 - β2) * grad^2   # 二阶矩估计
# W = W - lr * m / (sqrt(v) + eps)  # 参数更新
```

---

## 🎓 需要掌握的线性代数概念

### 基础概念
1. ✅ **向量** - 一维数组
2. ✅ **矩阵** - 二维数组
3. ✅ **张量** - 多维数组
4. ✅ **转置** - 行列互换
5. ✅ **点积** - 向量内积

### 核心运算
6. ✅ **矩阵乘法** - 神经网络的基础
7. ✅ **逐元素乘法** - Hadamard 乘积
8. ✅ **矩阵求导** - 反向传播
9. ✅ **特征值/特征向量** - PCA、正则化
10. ✅ **范数** - L1/L2 正则化

### 高级概念
11. ✅ **奇异值分解 (SVD)** - 模型压缩
12. ✅ **特征分解** - 协方差矩阵
13. ✅ **正交矩阵** - 初始化、归一化
14. ✅ **秩** - 模型容量
15. ✅ **条件数** - 训练稳定性

---

## 📊 实际例子：完整的神经网络

```python
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    """展示线性代数应用的简单网络"""
    def __init__(self):
        super().__init__()
        # 1. 线性变换（矩阵乘法）
        self.fc1 = nn.Linear(784, 256)  # W1: [256, 784]
        self.fc2 = nn.Linear(256, 128)  # W2: [128, 256]
        self.fc3 = nn.Linear(128, 10)   # W3: [10, 128]
        
        # 2. 批归一化（向量统计）
        self.bn1 = nn.BatchNorm1d(256)
        self.bn2 = nn.BatchNorm1d(128)
        
    def forward(self, x):
        # x: [batch_size, 784]
        
        # 线性变换 + 激活
        x = self.fc1(x)        # [batch, 784] @ [784, 256]^T -> [batch, 256]
        x = self.bn1(x)        # 向量标准化
        x = torch.relu(x)      # 逐元素激活
        
        x = self.fc2(x)        # [batch, 256] @ [256, 128]^T -> [batch, 128]
        x = self.bn2(x)
        x = torch.relu(x)
        
        x = self.fc3(x)        # [batch, 128] @ [128, 10]^T -> [batch, 10]
        return x

# 创建模型
model = SimpleNet()

# 输入数据
batch_images = torch.randn(32, 784)

# 前向传播（全是矩阵运算）
output = model(batch_images)
print(f"输出: {output.shape}")  # [32, 10]

# 计算参数总数
total_params = sum(p.numel() for p in model.parameters())
print(f"总参数量: {total_params:,}")
```

---

## 💡 为什么线性代数如此重要？

### 1. 高效计算
- GPU 对矩阵运算高度优化
- 批量处理 = 一次矩阵乘法
- 比循环快 100-1000 倍

### 2. 并行化
```python
# 慢：循环处理（串行）
for i in range(batch_size):
    output[i] = W @ x[i] + b

# 快：矩阵运算（并行）
output = X @ W.T + b  # 一次完成所有样本
```

### 3. 数学优雅
- 简洁的数学表达
- 易于理论分析
- 便于推导和优化

### 4. 硬件友好
- GPU/TPU 专门为矩阵运算设计
- 充分利用硬件加速

---

## 📚 学习资源

### 推荐书籍
1. 《Deep Learning》(Goodfellow) - 第2章：线性代数
2. 《动手学深度学习》- 附录：线性代数
3. 《线性代数及其应用》(Strang)

### 在线课程
1. 3Blue1Brown - 线性代数的本质
2. MIT 18.06 - 线性代数
3. Fast.ai - 计算线性代数

### 实践建议
1. 手写矩阵运算加深理解
2. 用 NumPy/PyTorch 实践
3. 可视化矩阵变换
4. 理解几何意义

---

## 🎯 总结

线性代数在深度学习中**无处不在**：

| 应用 | 线性代数操作 |
|-----|-------------|
| 数据表示 | 向量、矩阵、张量 |
| 全连接层 | 矩阵乘法 |
| 卷积层 | 特殊矩阵运算 |
| 注意力机制 | Q、K、V 矩阵乘法 |
| 批归一化 | 向量统计量 |
| 反向传播 | 矩阵求导、链式法则 |
| 优化器 | 向量更新 |
| 损失函数 | 向量范数、距离 |
| 模型压缩 | SVD、低秩分解 |
| 正则化 | 矩阵范数 |

**掌握线性代数 = 理解深度学习的本质！** 🚀
