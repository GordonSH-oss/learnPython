"""
PyTorch 基础入门

这是 PyTorch 深度学习的第一课，介绍最基础的概念和操作
"""

print("=" * 60)
print("欢迎来到 PyTorch 深度学习！")
print("=" * 60)

# ============================================================
# 检查环境
# ============================================================
print("\n" + "=" * 60)
print("1. 检查 PyTorch 环境")
print("=" * 60)

try:
    import torch
    import numpy as np
    
    print(f"✅ PyTorch 版本: {torch.__version__}")
    print(f"✅ CUDA 是否可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✅ CUDA 版本: {torch.version.cuda}")
        print(f"✅ GPU 设备: {torch.cuda.get_device_name(0)}")
    else:
        print("ℹ️  运行在 CPU 模式（学习基础知识足够）")
    
except ImportError as e:
    print("❌ PyTorch 未安装")
    print("\n安装命令:")
    print("  pip install torch torchvision torchaudio")
    print("\n或访问 https://pytorch.org/ 获取适合你系统的安装命令")
    exit(1)


# ============================================================
# 案例 1: 什么是 Tensor（张量）？
# ============================================================
print("\n" + "=" * 60)
print("2. 什么是 Tensor（张量）？")
print("=" * 60)

print("""
Tensor 是 PyTorch 的核心数据结构，类似于 NumPy 的 ndarray
但 Tensor 可以：
  • 在 GPU 上运行以加速计算
  • 自动计算梯度（用于训练神经网络）
  
简单理解：
  • 0 维 Tensor = 标量（一个数）
  • 1 维 Tensor = 向量（一维数组）
  • 2 维 Tensor = 矩阵（二维数组）
  • 3 维及以上 = 高维张量
""")

# 创建不同维度的 Tensor
scalar = torch.tensor(3.14)           # 0 维
vector = torch.tensor([1, 2, 3])       # 1 维
matrix = torch.tensor([[1, 2],         # 2 维
                        [3, 4]])
tensor_3d = torch.tensor([[[1, 2],     # 3 维
                           [3, 4]],
                          [[5, 6],
                           [7, 8]]])

print(f"标量 (0维): {scalar}, shape: {scalar.shape}")
print(f"向量 (1维): {vector}, shape: {vector.shape}")
print(f"矩阵 (2维):\n{matrix}\nshape: {matrix.shape}")
print(f"3维张量 shape: {tensor_3d.shape}")


# ============================================================
# 案例 2: 创建 Tensor 的多种方式
# ============================================================
print("\n" + "=" * 60)
print("3. 创建 Tensor 的多种方式")
print("=" * 60)

# 从数据创建
print("从列表创建:")
t1 = torch.tensor([1, 2, 3, 4, 5])
print(f"  {t1}")

# 从 NumPy 数组创建
print("\n从 NumPy 数组创建:")
np_array = np.array([1, 2, 3, 4, 5])
t2 = torch.from_numpy(np_array)
print(f"  {t2}")

# 创建全零张量
print("\n全零张量:")
zeros = torch.zeros(3, 4)  # 3行4列
print(f"  shape: {zeros.shape}\n{zeros}")

# 创建全一张量
print("\n全一张量:")
ones = torch.ones(2, 3)  # 2行3列
print(f"  shape: {ones.shape}\n{ones}")

# 创建随机张量
print("\n随机张量 (0-1 均匀分布):")
rand = torch.rand(2, 3)
print(f"  {rand}")

# 创建正态分布随机张量
print("\n随机张量 (正态分布):")
randn = torch.randn(2, 3)
print(f"  {randn}")

# 创建指定范围的张量
print("\n指定范围 (类似 range):")
arange = torch.arange(0, 10, 2)  # 从0到10，步长2
print(f"  {arange}")

# 创建等间隔张量
print("\n等间隔张量:")
linspace = torch.linspace(0, 10, 5)  # 从0到10，分成5份
print(f"  {linspace}")


# ============================================================
# 案例 3: Tensor 的基本属性
# ============================================================
print("\n" + "=" * 60)
print("4. Tensor 的基本属性")
print("=" * 60)

t = torch.randn(3, 4)
print(f"Tensor:\n{t}\n")
print(f"形状 (shape): {t.shape}")
print(f"维度 (ndim): {t.ndim}")
print(f"元素总数 (numel): {t.numel()}")
print(f"数据类型 (dtype): {t.dtype}")
print(f"设备 (device): {t.device}")
print(f"是否需要梯度 (requires_grad): {t.requires_grad}")


# ============================================================
# 案例 4: Tensor 的基本操作
# ============================================================
print("\n" + "=" * 60)
print("5. Tensor 的基本操作")
print("=" * 60)

a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

print(f"a = {a}")
print(f"b = {b}\n")

# 加法
print(f"加法: a + b = {a + b}")
print(f"加法: torch.add(a, b) = {torch.add(a, b)}")

# 减法
print(f"\n减法: a - b = {a - b}")

# 乘法（逐元素）
print(f"\n乘法: a * b = {a * b}")

# 除法
print(f"\n除法: a / b = {a / b}")

# 矩阵乘法
print("\n矩阵乘法:")
m1 = torch.tensor([[1, 2],
                   [3, 4]])
m2 = torch.tensor([[5, 6],
                   [7, 8]])
print(f"m1 @ m2 =\n{m1 @ m2}")
print(f"torch.matmul(m1, m2) =\n{torch.matmul(m1, m2)}")


# ============================================================
# 案例 5: 改变 Tensor 形状
# ============================================================
print("\n" + "=" * 60)
print("6. 改变 Tensor 形状")
print("=" * 60)

original = torch.arange(12)
print(f"原始张量: {original}, shape: {original.shape}")

# reshape - 返回新张量
reshaped = original.reshape(3, 4)
print(f"\nreshape(3, 4):\n{reshaped}")

# view - 返回视图（共享内存）
viewed = original.view(2, 6)
print(f"\nview(2, 6):\n{viewed}")

# -1 自动推断维度
auto = original.reshape(3, -1)  # 3行，列数自动推断
print(f"\nreshape(3, -1):\n{auto}")

# 转置
matrix = torch.tensor([[1, 2, 3],
                       [4, 5, 6]])
print(f"\n原始矩阵:\n{matrix}")
print(f"转置后:\n{matrix.t()}")


# ============================================================
# 案例 6: 索引和切片
# ============================================================
print("\n" + "=" * 60)
print("7. 索引和切片（类似 NumPy）")
print("=" * 60)

t = torch.arange(12).reshape(3, 4)
print(f"张量:\n{t}\n")

print(f"第0行: {t[0]}")
print(f"第1行第2列: {t[1, 2]}")
print(f"前2行: \n{t[:2]}")
print(f"第1列: {t[:, 1]}")
print(f"最后一行: {t[-1]}")


# ============================================================
# 案例 7: GPU 加速
# ============================================================
print("\n" + "=" * 60)
print("8. GPU 加速（如果可用）")
print("=" * 60)

# 检查 GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")

# 创建张量并移动到设备
t_cpu = torch.randn(3, 3)
print(f"\nCPU 张量:\n{t_cpu}")
print(f"设备: {t_cpu.device}")

if torch.cuda.is_available():
    t_gpu = t_cpu.to(device)  # 移动到 GPU
    print(f"\nGPU 张量:\n{t_gpu}")
    print(f"设备: {t_gpu.device}")
    
    # GPU 上的计算
    result = t_gpu + t_gpu
    print(f"\nGPU 计算结果:\n{result}")
    
    # 移回 CPU
    result_cpu = result.cpu()
    print(f"\n移回 CPU:\n{result_cpu}")
else:
    print("\n没有 GPU，使用 CPU 进行计算")


# ============================================================
# 案例 8: Tensor 与 NumPy 的转换
# ============================================================
print("\n" + "=" * 60)
print("9. Tensor 与 NumPy 的转换")
print("=" * 60)

# Tensor → NumPy
t = torch.tensor([1, 2, 3, 4, 5])
n = t.numpy()
print(f"Tensor: {t}")
print(f"NumPy:  {n}")
print(f"类型:   {type(n)}")

# NumPy → Tensor
n2 = np.array([6, 7, 8, 9, 10])
t2 = torch.from_numpy(n2)
print(f"\nNumPy:  {n2}")
print(f"Tensor: {t2}")
print(f"类型:   {type(t2)}")

print("\n⚠️  注意：它们共享内存，修改一个会影响另一个")
t[0] = 100
print(f"修改 Tensor 后: t={t}, n={n}")


# ============================================================
# 案例 9: 常用的聚合操作
# ============================================================
print("\n" + "=" * 60)
print("10. 常用的聚合操作")
print("=" * 60)

t = torch.tensor([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])

print(f"张量:\n{t}\n")
print(f"求和: {t.sum()}")
print(f"均值: {t.mean()}")
print(f"最大值: {t.max()}")
print(f"最小值: {t.min()}")
print(f"标准差: {t.std()}")

print(f"\n按列求和: {t.sum(dim=0)}")  # 沿着第0维（行）
print(f"按行求和: {t.sum(dim=1)}")    # 沿着第1维（列）


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("PyTorch 基础总结")
print("=" * 60)
print("""
🎯 你已经学会了:
1. ✅ PyTorch 环境检查
2. ✅ Tensor 的概念和重要性
3. ✅ 创建 Tensor 的多种方式
4. ✅ Tensor 的基本属性
5. ✅ Tensor 的基本运算
6. ✅ 改变 Tensor 形状
7. ✅ 索引和切片
8. ✅ GPU 加速
9. ✅ Tensor 与 NumPy 转换
10. ✅ 聚合操作

📚 下一步学习:
• tensors.py - 深入学习 Tensor 操作
• autograd.py - 学习自动微分（核心！）
• neural_networks.py - 构建第一个神经网络

💡 练习建议:
1. 尝试创建不同形状的 Tensor
2. 练习各种运算操作
3. 理解 CPU 和 GPU 的区别
4. 熟悉 Tensor 的形状变换

🎉 恭喜完成第一课！继续加油！
""")
