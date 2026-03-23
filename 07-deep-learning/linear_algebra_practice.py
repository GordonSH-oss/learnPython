"""
线性代数在深度学习中的实践
Linear Algebra in Deep Learning - Practical Examples

配套文档: LINEAR_ALGEBRA_IN_DL.md
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple


def separator(title: str):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


# ============================================================================
# 案例 1: 数据表示 - 从图像到向量
# ============================================================================
def case1_data_representation():
    separator("案例 1: 数据表示")
    
    # 1.1 单张灰度图像
    image = torch.randn(28, 28)
    print(f"原始图像形状: {image.shape}")
    
    # 展平成向量
    image_vector = image.view(-1)
    print(f"展平后向量: {image_vector.shape}")
    print(f"向量维度: {image_vector.numel()}")
    
    # 1.2 批量图像处理
    batch_size = 32
    batch_images = torch.randn(batch_size, 28, 28)
    print(f"\n批量图像形状: {batch_images.shape}")
    
    # 展平批量图像
    batch_vectors = batch_images.view(batch_size, -1)
    print(f"批量向量形状: {batch_vectors.shape}")
    
    # 1.3 RGB 图像（3通道）
    rgb_image = torch.randn(3, 224, 224)
    print(f"\nRGB 图像形状: {rgb_image.shape} (C, H, W)")
    
    # 批量 RGB 图像
    batch_rgb = torch.randn(32, 3, 224, 224)
    print(f"批量 RGB 形状: {batch_rgb.shape} (N, C, H, W)")
    
    # 1.4 视频数据（时间维度）
    video = torch.randn(8, 3, 30, 224, 224)
    print(f"\n视频数据形状: {video.shape} (N, C, T, H, W)")
    print(f"  - 8 个视频样本")
    print(f"  - 3 个颜色通道 (RGB)")
    print(f"  - 30 帧")
    print(f"  - 224x224 分辨率")


# ============================================================================
# 案例 2: 矩阵乘法 - 全连接层的核心
# ============================================================================
def case2_matrix_multiplication():
    separator("案例 2: 矩阵乘法")
    
    # 2.1 手动实现全连接层
    input_size = 3
    output_size = 2
    batch_size = 4
    
    # 权重矩阵 W: [output_size, input_size]
    W = torch.tensor([[1.0, 2.0, 3.0],
                      [4.0, 5.0, 6.0]])
    print(f"权重矩阵 W 形状: {W.shape}")
    print(f"W = \n{W}")
    
    # 偏置向量 b: [output_size]
    b = torch.tensor([0.1, 0.2])
    print(f"\n偏置向量 b: {b}")
    
    # 批量输入 X: [batch_size, input_size]
    X = torch.randn(batch_size, input_size)
    print(f"\n输入矩阵 X 形状: {X.shape}")
    print(f"X = \n{X}")
    
    # 前向传播: Y = XW^T + b
    Y = X @ W.T + b
    print(f"\n输出 Y 形状: {Y.shape}")
    print(f"Y = XW^T + b = \n{Y}")
    
    # 2.2 使用 PyTorch 的 Linear 层
    fc = nn.Linear(input_size, output_size)
    fc.weight.data = W
    fc.bias.data = b
    
    Y_pytorch = fc(X)
    print(f"\nPyTorch Linear 层输出:\n{Y_pytorch}")
    
    # 验证两种方法结果相同
    print(f"\n手动计算和 PyTorch 是否一致: {torch.allclose(Y, Y_pytorch)}")
    
    # 2.3 矩阵乘法的维度规则
    print(f"\n矩阵乘法维度规则:")
    print(f"  X @ W.T = [{batch_size}, {input_size}] @ [{input_size}, {output_size}]")
    print(f"         = [{batch_size}, {output_size}]")


# ============================================================================
# 案例 3: 多层神经网络 - 矩阵链式乘法
# ============================================================================
def case3_multi_layer_network():
    separator("案例 3: 多层神经网络")
    
    class SimpleNet(nn.Module):
        def __init__(self, input_dim, hidden_dims, output_dim):
            super().__init__()
            self.layers = nn.ModuleList()
            
            # 构建多层
            dims = [input_dim] + hidden_dims + [output_dim]
            for i in range(len(dims) - 1):
                self.layers.append(nn.Linear(dims[i], dims[i+1]))
            
        def forward(self, x, verbose=False):
            if verbose:
                print(f"输入形状: {x.shape}")
            
            for i, layer in enumerate(self.layers):
                x = layer(x)
                if verbose:
                    print(f"第 {i+1} 层后: {x.shape}")
                
                # 最后一层不加激活
                if i < len(self.layers) - 1:
                    x = torch.relu(x)
            
            return x
    
    # 创建网络: 784 -> 256 -> 128 -> 64 -> 10
    model = SimpleNet(
        input_dim=784,
        hidden_dims=[256, 128, 64],
        output_dim=10
    )
    
    print(f"网络结构:")
    for i, layer in enumerate(model.layers):
        print(f"  第 {i+1} 层: {layer.in_features} -> {layer.out_features}")
    
    # 前向传播
    batch_size = 32
    x = torch.randn(batch_size, 784)
    
    print(f"\n前向传播过程:")
    y = model(x, verbose=True)
    
    # 计算参数量
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n总参数量: {total_params:,}")
    
    # 每层参数量
    print(f"\n每层参数量:")
    for i, layer in enumerate(model.layers):
        layer_params = layer.weight.numel() + layer.bias.numel()
        print(f"  第 {i+1} 层: {layer_params:,} 参数")


# ============================================================================
# 案例 4: 注意力机制 - Q、K、V 矩阵乘法
# ============================================================================
def case4_attention_mechanism():
    separator("案例 4: 注意力机制")
    
    def scaled_dot_product_attention(Q, K, V, verbose=False):
        """
        缩放点积注意力
        
        Args:
            Q: Query [batch, seq_len, d_model]
            K: Key   [batch, seq_len, d_model]
            V: Value [batch, seq_len, d_model]
        
        Returns:
            output: [batch, seq_len, d_model]
            attention_weights: [batch, seq_len, seq_len]
        """
        d_k = Q.size(-1)
        
        # 1. 计算注意力分数 Q @ K^T
        scores = torch.matmul(Q, K.transpose(-2, -1))
        if verbose:
            print(f"Q @ K^T 形状: {scores.shape}")
        
        # 2. 缩放
        scores = scores / (d_k ** 0.5)
        
        # 3. Softmax 得到注意力权重
        attention_weights = torch.softmax(scores, dim=-1)
        if verbose:
            print(f"注意力权重形状: {attention_weights.shape}")
            print(f"权重和 (应该=1): {attention_weights.sum(dim=-1)[0, 0]:.4f}")
        
        # 4. 加权求和 attention_weights @ V
        output = torch.matmul(attention_weights, V)
        if verbose:
            print(f"输出形状: {output.shape}")
        
        return output, attention_weights
    
    # 创建 Q, K, V
    batch_size = 2
    seq_len = 10
    d_model = 512
    
    Q = torch.randn(batch_size, seq_len, d_model)
    K = torch.randn(batch_size, seq_len, d_model)
    V = torch.randn(batch_size, seq_len, d_model)
    
    print(f"Q 形状: {Q.shape}")
    print(f"K 形状: {K.shape}")
    print(f"V 形状: {V.shape}")
    
    print(f"\n计算注意力:")
    output, attention_weights = scaled_dot_product_attention(Q, K, V, verbose=True)
    
    # 可视化注意力权重（第一个样本的前5个词）
    print(f"\n注意力权重矩阵（前5x5）:")
    print(attention_weights[0, :5, :5])
    print(f"  - 每行表示一个词对所有词的注意力分布")
    print(f"  - 每行和为 1")


# ============================================================================
# 案例 5: 卷积 = 矩阵运算
# ============================================================================
def case5_convolution_as_matrix():
    separator("案例 5: 卷积作为矩阵运算")
    
    # 5.1 卷积层
    conv = nn.Conv2d(
        in_channels=3,
        out_channels=64,
        kernel_size=3,
        padding=1
    )
    
    # 输入图像
    image = torch.randn(1, 3, 224, 224)
    print(f"输入图像: {image.shape} (N, C, H, W)")
    
    # 卷积操作
    output = conv(image)
    print(f"卷积输出: {output.shape}")
    
    # 卷积核参数
    print(f"\n卷积核参数:")
    print(f"  权重形状: {conv.weight.shape} (out_ch, in_ch, kH, kW)")
    print(f"  偏置形状: {conv.bias.shape}")
    print(f"  总参数: {conv.weight.numel() + conv.bias.numel():,}")
    
    # 5.2 im2col: 将卷积转换为矩阵乘法
    print(f"\n卷积可以转换为矩阵乘法 (im2col 算法):")
    print(f"  - 将图像展开成列矩阵")
    print(f"  - 卷积核展开成行矩阵")
    print(f"  - 执行矩阵乘法")
    print(f"  - 这就是为什么 GPU 对卷积如此高效！")
    
    # 5.3 深度可分离卷积
    depthwise = nn.Conv2d(64, 64, 3, padding=1, groups=64)
    pointwise = nn.Conv2d(64, 128, 1)
    
    x = torch.randn(1, 64, 56, 56)
    y = pointwise(depthwise(x))
    
    print(f"\n深度可分离卷积:")
    print(f"  输入: {x.shape}")
    print(f"  -> Depthwise: {depthwise(x).shape}")
    print(f"  -> Pointwise: {y.shape}")
    
    # 参数对比
    standard_conv = nn.Conv2d(64, 128, 3, padding=1)
    standard_params = standard_conv.weight.numel() + standard_conv.bias.numel()
    separable_params = (depthwise.weight.numel() + depthwise.bias.numel() + 
                       pointwise.weight.numel() + pointwise.bias.numel())
    
    print(f"\n参数量对比:")
    print(f"  标准卷积: {standard_params:,}")
    print(f"  可分离卷积: {separable_params:,}")
    print(f"  节省: {(1 - separable_params/standard_params)*100:.1f}%")


# ============================================================================
# 案例 6: 批归一化 - 向量统计
# ============================================================================
def case6_batch_normalization():
    separator("案例 6: 批归一化")
    
    # 创建批归一化层
    batch_norm = nn.BatchNorm1d(128)
    
    # 批量数据
    batch_size = 32
    features = 128
    x = torch.randn(batch_size, features)
    
    print(f"输入形状: {x.shape}")
    print(f"输入均值: {x.mean().item():.4f}")
    print(f"输入标准差: {x.std().item():.4f}")
    
    # 批归一化
    normalized = batch_norm(x)
    
    print(f"\n归一化后:")
    print(f"输出形状: {normalized.shape}")
    print(f"输出均值: {normalized.mean().item():.4f} (接近 0)")
    print(f"输出标准差: {normalized.std().item():.4f} (接近 1)")
    
    # 手动实现批归一化
    print(f"\n手动实现批归一化:")
    eps = 1e-5
    
    # 计算均值和方差（沿 batch 维度）
    mean = x.mean(dim=0, keepdim=True)  # [1, 128]
    var = x.var(dim=0, keepdim=True, unbiased=False)  # [1, 128]
    
    print(f"  均值形状: {mean.shape}")
    print(f"  方差形状: {var.shape}")
    
    # 标准化
    normalized_manual = (x - mean) / torch.sqrt(var + eps)
    
    print(f"  手动归一化均值: {normalized_manual.mean().item():.4f}")
    print(f"  手动归一化标准差: {normalized_manual.std().item():.4f}")


# ============================================================================
# 案例 7: 梯度计算 - 矩阵求导
# ============================================================================
def case7_gradient_computation():
    separator("案例 7: 梯度计算")
    
    print("简单的两层网络:")
    
    # 输入
    x = torch.randn(1, 10, requires_grad=True)
    print(f"输入 x 形状: {x.shape}")
    
    # 权重（需要梯度）
    W1 = torch.randn(20, 10, requires_grad=True)
    b1 = torch.randn(20, requires_grad=True)
    W2 = torch.randn(1, 20, requires_grad=True)
    b2 = torch.randn(1, requires_grad=True)
    
    print(f"W1 形状: {W1.shape}")
    print(f"W2 形状: {W2.shape}")
    
    # 前向传播
    h = torch.relu(x @ W1.T + b1)  # [1, 20]
    y = h @ W2.T + b2              # [1, 1]
    
    print(f"\n前向传播:")
    print(f"  隐藏层 h: {h.shape}")
    print(f"  输出 y: {y.shape}, 值: {y.item():.4f}")
    
    # 损失
    target = torch.tensor([[1.0]])
    loss = (y - target) ** 2
    print(f"  损失: {loss.item():.4f}")
    
    # 反向传播
    loss.backward()
    
    print(f"\n反向传播 - 梯度形状:")
    print(f"  ∂L/∂W1: {W1.grad.shape}")
    print(f"  ∂L/∂b1: {b1.grad.shape}")
    print(f"  ∂L/∂W2: {W2.grad.shape}")
    print(f"  ∂L/∂b2: {b2.grad.shape}")
    
    # 梯度统计
    print(f"\n梯度统计:")
    print(f"  W1 梯度均值: {W1.grad.mean().item():.6f}")
    print(f"  W1 梯度标准差: {W1.grad.std().item():.6f}")
    print(f"  W2 梯度均值: {W2.grad.mean().item():.6f}")
    print(f"  W2 梯度标准差: {W2.grad.std().item():.6f}")


# ============================================================================
# 案例 8: 矩阵分解 - SVD
# ============================================================================
def case8_matrix_decomposition():
    separator("案例 8: 矩阵分解 (SVD)")
    
    # 创建一个权重矩阵
    m, n = 1000, 500
    W = torch.randn(m, n)
    
    print(f"原始权重矩阵: {W.shape}")
    print(f"参数量: {W.numel():,}")
    
    # SVD 分解
    U, S, V = torch.svd(W)
    
    print(f"\nSVD 分解:")
    print(f"  U: {U.shape}")
    print(f"  S: {S.shape} (奇异值)")
    print(f"  V: {V.shape}")
    
    # 奇异值分布
    print(f"\n奇异值统计:")
    print(f"  最大奇异值: {S[0].item():.4f}")
    print(f"  最小奇异值: {S[-1].item():.4f}")
    print(f"  前10个奇异值占比: {S[:10].sum() / S.sum() * 100:.2f}%")
    print(f"  前50个奇异值占比: {S[:50].sum() / S.sum() * 100:.2f}%")
    
    # 低秩近似
    ranks = [10, 50, 100, 200]
    print(f"\n低秩近似:")
    
    for k in ranks:
        # 重构矩阵
        W_approx = U[:, :k] @ torch.diag(S[:k]) @ V[:, :k].T
        
        # 近似误差
        error = torch.norm(W - W_approx) / torch.norm(W)
        
        # 参数量
        compressed_params = k * (m + n)
        compression_ratio = compressed_params / W.numel()
        
        print(f"  秩 {k:3d}: 误差={error*100:.2f}%, "
              f"参数={compressed_params:,} ({compression_ratio*100:.1f}%)")


# ============================================================================
# 案例 9: 嵌入层 - 矩阵索引
# ============================================================================
def case9_embedding_layer():
    separator("案例 9: 嵌入层")
    
    # 词汇表大小和嵌入维度
    vocab_size = 10000
    embedding_dim = 300
    
    # 创建嵌入层
    embedding = nn.Embedding(vocab_size, embedding_dim)
    
    print(f"嵌入层参数:")
    print(f"  词汇表大小: {vocab_size:,}")
    print(f"  嵌入维度: {embedding_dim}")
    print(f"  参数矩阵形状: {embedding.weight.shape}")
    print(f"  总参数: {embedding.weight.numel():,}")
    
    # 输入词的索引
    word_ids = torch.tensor([5, 100, 234, 9, 5678])
    print(f"\n输入词 ID: {word_ids}")
    
    # 查找词向量
    word_vectors = embedding(word_ids)
    print(f"词向量形状: {word_vectors.shape}")
    
    # 本质上是矩阵索引
    print(f"\n嵌入层 = 矩阵查表:")
    print(f"  word_vectors[i] = embedding.weight[word_ids[i]]")
    
    # 验证
    manual_lookup = embedding.weight[word_ids]
    print(f"  手动查表结果相同: {torch.allclose(word_vectors, manual_lookup)}")
    
    # 批量句子
    batch_size = 32
    seq_len = 20
    batch_sentences = torch.randint(0, vocab_size, (batch_size, seq_len))
    
    batch_embeddings = embedding(batch_sentences)
    print(f"\n批量嵌入:")
    print(f"  输入形状: {batch_sentences.shape} (batch, seq_len)")
    print(f"  输出形状: {batch_embeddings.shape} (batch, seq_len, embed_dim)")


# ============================================================================
# 案例 10: 损失函数 - 向量运算
# ============================================================================
def case10_loss_functions():
    separator("案例 10: 损失函数")
    
    batch_size = 32
    num_classes = 10
    
    # 模拟预测和真实标签
    predictions = torch.randn(batch_size, num_classes)
    targets = torch.randint(0, num_classes, (batch_size,))
    
    print(f"预测形状: {predictions.shape}")
    print(f"目标形状: {targets.shape}")
    
    # 10.1 交叉熵损失
    ce_loss = nn.CrossEntropyLoss()
    loss_ce = ce_loss(predictions, targets)
    print(f"\n交叉熵损失: {loss_ce.item():.4f}")
    
    # 10.2 MSE 损失
    pred_reg = torch.randn(batch_size, 1)
    target_reg = torch.randn(batch_size, 1)
    
    mse_loss = nn.MSELoss()
    loss_mse = mse_loss(pred_reg, target_reg)
    print(f"MSE 损失: {loss_mse.item():.4f}")
    
    # 手动计算 MSE
    loss_mse_manual = torch.mean((pred_reg - target_reg) ** 2)
    print(f"手动计算 MSE: {loss_mse_manual.item():.4f}")
    
    # 10.3 余弦相似度
    emb1 = torch.randn(batch_size, 128)
    emb2 = torch.randn(batch_size, 128)
    
    cos_sim = nn.CosineSimilarity(dim=1)
    similarity = cos_sim(emb1, emb2)
    
    print(f"\n余弦相似度:")
    print(f"  输出形状: {similarity.shape}")
    print(f"  平均相似度: {similarity.mean().item():.4f}")
    print(f"  最大相似度: {similarity.max().item():.4f}")
    print(f"  最小相似度: {similarity.min().item():.4f}")
    
    # 手动计算余弦相似度
    dot_product = (emb1 * emb2).sum(dim=1)
    norm1 = torch.norm(emb1, dim=1)
    norm2 = torch.norm(emb2, dim=1)
    cos_sim_manual = dot_product / (norm1 * norm2)
    
    print(f"  手动计算相似度: {cos_sim_manual.mean().item():.4f}")


# ============================================================================
# 主函数
# ============================================================================
def main():
    """运行所有案例"""
    print("="*60)
    print("  线性代数在深度学习中的实践")
    print("  Linear Algebra in Deep Learning")
    print("="*60)
    
    # 运行所有案例
    case1_data_representation()
    case2_matrix_multiplication()
    case3_multi_layer_network()
    case4_attention_mechanism()
    case5_convolution_as_matrix()
    case6_batch_normalization()
    case7_gradient_computation()
    case8_matrix_decomposition()
    case9_embedding_layer()
    case10_loss_functions()
    
    print("\n" + "="*60)
    print("  所有案例运行完成！")
    print("="*60)
    
    print("\n💡 关键要点:")
    print("1. 数据表示: 向量、矩阵、张量")
    print("2. 神经网络 = 矩阵乘法 + 非线性激活")
    print("3. 注意力机制 = Q·K^T·V 矩阵运算")
    print("4. 卷积 = 特殊的矩阵运算（im2col）")
    print("5. 批归一化 = 向量统计量")
    print("6. 反向传播 = 矩阵求导链式法则")
    print("7. SVD = 模型压缩和低秩近似")
    print("8. 嵌入 = 矩阵查表")
    print("9. 损失函数 = 向量范数和距离")
    print("10. GPU 加速 = 高效矩阵运算")


if __name__ == "__main__":
    main()
