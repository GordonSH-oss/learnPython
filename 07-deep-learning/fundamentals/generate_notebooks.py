"""Generate the framework-free course notebooks in a consistent format."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).parent
OUTPUT = ROOT / "notebooks"


def markdown(text: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(text).strip().splitlines(keepends=True)}


def code(text: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(text).strip().splitlines(keepends=True),
    }


SETUP = """
from pathlib import Path
import sys

course_dir = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd() / "07-deep-learning/fundamentals"
sys.path.insert(0, str(course_dir.resolve()))
"""


COURSES: list[tuple[str, str, str, str, list[dict[str, object]], str, str, str]] = [
    (
        "01-scalars-vectors-and-neurons.ipynb",
        "标量、向量与神经元",
        "用纯 Python 解释特征、权重、偏置和批量前向计算。",
        "神经元计算加权和 `z = x·w + b`。一层网络只是同时计算多个神经元；批次则是重复处理多个样本。",
        [
            code("""
def dot(left, right):
    if len(left) != len(right):
        raise ValueError("两个向量必须等长")
    return sum(a * b for a, b in zip(left, right))

def neuron(inputs, weights, bias):
    return dot(inputs, weights) + bias

sample = [1.5, -2.0, 0.5]
print("单个神经元输出:", neuron(sample, [0.2, -0.4, 1.0], 0.1))
"""),
            code("""
def dense_layer(batch, weights, biases):
    return [[neuron(sample, column, bias) for column, bias in zip(weights, biases)] for sample in batch]

batch = [[1.0, 2.0], [-1.0, 3.0], [0.5, 0.5]]
# 每个内部列表是一位输出神经元的权重。
outputs = dense_layer(batch, [[0.5, -0.2], [-1.0, 0.8], [0.3, 0.3]], [0.0, 0.1, -0.1])
print(outputs)
assert len(outputs) == 3 and len(outputs[0]) == 3
"""),
        ],
        "输入有 2 个特征、输出有 3 个神经元时，需要 6 个权重和 3 个偏置；输出 shape 是 `(batch, 3)`。",
        "增加一个输入特征，先在纸上写出所有权重需要如何变化，再修改代码。",
        "把样本数误当成特征数；权重向量长度与输入不一致；忘记每个输出神经元都有自己的偏置。",
    ),
    (
        "02-derivatives-and-chain-rule.ipynb",
        "导数与链式法则",
        "用纯 Python 计算局部导数，并沿简单计算图传播梯度。",
        "反向传播把输出对损失的影响从右向左传递。链式法则把路径上的局部导数相乘，分支汇合处则相加。",
        [
            code("""
def square(x):
    return x * x

def central_difference(function, x, epsilon=1e-5):
    return (function(x + epsilon) - function(x - epsilon)) / (2 * epsilon)

x = 3.0
analytic = 2 * x
numeric = central_difference(square, x)
print(analytic, numeric)
assert abs(analytic - numeric) < 1e-8
"""),
            code("""
# y = (x*w + b)^2，手工应用链式法则。
x, w, b = 2.0, -3.0, 1.0
z = x * w + b
y = z ** 2
dy_dz = 2 * z
dy_dw = dy_dz * x
dy_db = dy_dz
dy_dx = dy_dz * w
print({"y": y, "dy/dw": dy_dw, "dy/db": dy_db, "dy/dx": dy_dx})
"""),
        ],
        "前向阶段保存 `z`，反向阶段才能复用它计算 `2z`；梯度描述敏感度，不是参数更新本身。",
        "把平方损失替换为 `(prediction-target)**2`，推导 prediction 的梯度并用数值差分验证。",
        "更新参数后才计算梯度；漏掉链式法则中的某一项；把梯度方向和梯度下降方向混为一谈。",
    ),
    (
        "03-numpy-and-linear-layers.ipynb",
        "NumPy 与线性层",
        "从列表计算切换到批量矩阵运算，并实现带缓存的 Linear 层。",
        "`X @ W + b` 同时处理整个批次。`X:(N,D)`、`W:(D,H)`、`b:(H,)`，输出为 `(N,H)`。",
        [code(SETUP + """
import numpy as np
from from_scratch import Linear

x = np.array([[1.0, 2.0], [-1.0, 3.0], [0.5, 0.5]])
layer = Linear(2, 4, seed=3)
y = layer.forward(x)
print("X, W, b, Y:", x.shape, layer.weight.shape, layer.bias.shape, y.shape)
assert y.shape == (3, 4)
"""), code("""
grad_output = np.ones_like(y) / y.size
grad_input = layer.backward(grad_output)
print("dX, dW, db:", grad_input.shape, layer.grad_weight.shape, layer.grad_bias.shape)
assert grad_input.shape == x.shape
""")],
        "偏置利用广播加到每一行；反向传播分别得到输入、权重和偏置的梯度，shape 必须与对应对象一致。",
        "故意传入 `(3, 3)` 输入，阅读错误信息；再创建匹配的新 Linear 层。",
        "交换 batch 和 feature 维；依赖广播掩盖 shape 错误；没有先 forward 就调用 backward。",
    ),
    (
        "04-activations-and-losses.ipynb",
        "激活函数与损失",
        "实现并比较 ReLU、Sigmoid、Softmax、MSE 和交叉熵。",
        "激活函数提供非线性；logits 是未归一化分数；Softmax 与交叉熵合并求导可得到稳定且简洁的梯度。",
        [code(SETUP + """
import numpy as np
from from_scratch import CrossEntropyLoss, MSELoss, ReLU, Sigmoid, softmax

values = np.array([[-1000.0, 0.0, 1000.0], [-2.0, 0.0, 2.0]])
print("ReLU:\n", ReLU().forward(values))
print("Sigmoid:\n", Sigmoid().forward(values))
probabilities = softmax(values)
print("Softmax row sums:", probabilities.sum(axis=1))
"""), code("""
logits = np.array([[2.0, 0.5, -1.0], [-1.0, 0.0, 3.0]])
targets = np.array([0, 2])
criterion = CrossEntropyLoss()
print("cross entropy:", criterion.forward(logits, targets))
print("gradient:\n", criterion.backward())

mse = MSELoss()
print("mse:", mse.forward(np.array([1.5, 2.0]), np.array([1.0, 3.0])))
""")],
        "稳定 Softmax 先减去每行最大值。分类训练向交叉熵传 logits，不要先手工 Softmax 再重复归一化。",
        "把正确类别的 logit 从 2 提高到 5，观察损失和对应梯度如何变化。",
        "直接对巨大 logits 求指数；用 MSE 处理类别索引；对整个批次只计算一个 Softmax 分母。",
    ),
    (
        "05-backpropagation.ipynb",
        "反向传播",
        "串联 Linear、ReLU 与交叉熵，完成一次完整的前向和反向传播。",
        "每层只需要知道自己的输入和上游梯度。反向传播按前向的相反顺序调用，各层把梯度交给前一层。",
        [code(SETUP + """
import numpy as np
from from_scratch import CrossEntropyLoss, Linear, ReLU

x = np.array([[0.2, -0.4], [1.0, 0.3], [-0.5, 0.8]])
y = np.array([0, 1, 0])
layer1, activation, layer2 = Linear(2, 4, 1), ReLU(), Linear(4, 2, 2)

hidden = layer1.forward(x)
activated = activation.forward(hidden)
logits = layer2.forward(activated)
loss_fn = CrossEntropyLoss()
loss = loss_fn.forward(logits, y)
print("loss:", loss)
"""), code("""
gradient = loss_fn.backward()
gradient = layer2.backward(gradient)
gradient = activation.backward(gradient)
gradient = layer1.backward(gradient)
print("dX shape:", gradient.shape)
print("first layer gradient norm:", np.linalg.norm(layer1.grad_weight))
assert gradient.shape == x.shape
""")],
        "梯度流向为 loss → logits → hidden → inputs；每个可训练层同时保存参数梯度，供优化器更新。",
        "交换两个 backward 调用，预测会出现哪一种 shape 错误，再恢复正确顺序。",
        "反向顺序与前向相同；用更新后的权重继续传播旧梯度；批次损失求均值后又重复除以 batch size。",
    ),
    (
        "06-building-an-mlp.ipynb",
        "完整 MLP",
        "把层组合成可复用模型，统一管理前向传播、反向传播、参数和预测。",
        "MLP 是顺序层的组合。训练返回 logits 并缓存中间结果；预测关闭随机层，取最大 logit 对应的类别。",
        [code(SETUP + """
import numpy as np
from from_scratch import CrossEntropyLoss, MLP

model = MLP(2, [8, 8], 3, seed=10)
x = np.array([[0.1, 0.2], [-0.4, 0.8], [0.9, -0.2]])
y = np.array([0, 1, 2])
logits = model.forward(x)
criterion = CrossEntropyLoss()
loss = criterion.forward(logits, y)
model.backward(criterion.backward())
print("logits shape:", logits.shape, "loss:", loss)
"""), code("""
parameters = model.parameters()
print("parameter tensors:", len(parameters))
for index, (parameter, gradient) in enumerate(parameters):
    print(index, parameter.shape, gradient.shape)
assert all(parameter.shape == gradient.shape for parameter, gradient in parameters)
""")],
        "两层隐藏层意味着三个 Linear 层；ReLU 没有可训练参数；参数枚举让优化器无需了解模型内部结构。",
        "把隐藏层改为 `[16]` 或 `[16, 8, 4]`，计算并验证参数张量数量。",
        "在最后一层后加 ReLU 限制 logits；预测时仍启用 Dropout；遗漏某层的 parameters。",
    ),
    (
        "07-optimization-and-training.ipynb",
        "优化与训练循环",
        "实现 mini-batch 训练，比较 SGD 与 Momentum，并记录学习曲线。",
        "每个批次执行 forward → loss → backward → step → zero_grad。Momentum 累积更新方向，可减少狭长损失曲面中的震荡。",
        [code(SETUP + """
import numpy as np
import matplotlib.pyplot as plt
from from_scratch import MLP, Momentum, make_spiral, train_classifier

x, y = make_spiral(samples_per_class=60, noise=0.15, seed=4)
model = MLP(2, [32, 32], 3, seed=4)
optimizer = Momentum(model.parameters(), learning_rate=0.08, momentum=0.9)
history = train_classifier(model, x, y, optimizer, epochs=120, batch_size=32, seed=4)
print("loss:", history["loss"][0], "->", history["loss"][-1])
print("accuracy:", history["accuracy"][-1])
"""), code("""
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
axes[0].plot(history["loss"]); axes[0].set_title("Loss")
axes[1].plot(history["accuracy"]); axes[1].set_title("Training accuracy")
plt.tight_layout()
plt.show()
""")],
        "每轮都用显式 seed 打乱数据，因此实验可复现但批次顺序会变化。损失下降和准确率上升需要结合观察。",
        "分别使用不同 batch size 和学习率，记录收敛速度以及最终准确率。",
        "忘记清空梯度；只查看最后一个 batch 的指标；学习率过大时通过增加 epoch 掩盖发散。",
    ),
    (
        "08-validation-and-generalization.ipynb",
        "验证与泛化",
        "划分训练与验证集，观察过拟合，并使用 L2、Dropout 和早停思想控制模型复杂度。",
        "训练集用于更新参数，验证集用于选择超参数和停止时机。正则化只影响训练规则，验证数据绝不能参与 backward。",
        [code(SETUP + """
import numpy as np
from from_scratch import CrossEntropyLoss, MLP, Momentum, accuracy, make_spiral, train_classifier, train_validation_split

x, y = make_spiral(samples_per_class=80, noise=0.22, seed=12)
x_train, x_valid, y_train, y_valid = train_validation_split(x, y, seed=12)
model = MLP(2, [48, 48], 3, dropout=0.1, seed=12)
optimizer = Momentum(model.parameters(), learning_rate=0.07, momentum=0.9, weight_decay=1e-4)
history = train_classifier(model, x_train, y_train, optimizer, epochs=140, batch_size=32, seed=12)
valid_logits = model.forward(x_valid, training=False)
valid_loss = CrossEntropyLoss().forward(valid_logits, y_valid)
print("train accuracy:", history["accuracy"][-1])
print("validation loss/accuracy:", valid_loss, accuracy(valid_logits.argmax(1), y_valid))
"""), code("""
# 早停的核心状态：只在验证损失改善时保存参数副本。
best_loss = float("inf")
best_parameters = None
if valid_loss < best_loss:
    best_loss = valid_loss
    best_parameters = [parameter.copy() for parameter, _ in model.parameters()]
print("saved tensors:", len(best_parameters))
""")],
        "Dropout 在训练时随机丢弃激活并做缩放，验证时必须关闭。L2 通过 weight_decay 惩罚过大的参数。",
        "改变隐藏层宽度和 Dropout 概率，比较训练与验证准确率之间的差距。",
        "用验证集更新参数；验证时仍打开 Dropout；只保存模型对象引用而不是最佳参数副本。",
    ),
    (
        "09-gradient-checking-and-debugging.ipynb",
        "梯度检查与调试",
        "用有限差分检查解析梯度，并建立定位 shape、非有限值和梯度规模问题的顺序。",
        "梯度检查逐个扰动参数，比较数值斜率与 backward 结果。它很慢，适合小输入和小网络，不用于训练。",
        [code(SETUP + """
import numpy as np
from from_scratch import CrossEntropyLoss, Linear, gradient_check

x = np.array([[0.2, -0.3], [0.7, 0.1]])
y = np.array([0, 1])
layer = Linear(2, 2, seed=5)
criterion = CrossEntropyLoss()

def current_loss():
    return criterion.forward(layer.forward(x), y)

current_loss()
layer.backward(criterion.backward())
relative_error = gradient_check(current_loss, layer.weight, layer.grad_weight.copy())
print("maximum relative error:", relative_error)
assert relative_error < 1e-6
"""), code("""
def inspect(name, value):
    print(name, "shape=", value.shape, "finite=", np.isfinite(value).all(), "norm=", np.linalg.norm(value))

inspect("weight", layer.weight)
inspect("grad_weight", layer.grad_weight)
# 调试顺序：数据/标签 → shape → loss → 梯度是否存在 → 梯度范围 → 参数是否更新。
""")],
        "相对误差接近 0 表示解析梯度与数值梯度一致。检查失败时先缩小到单层、少量样本和 float64。",
        "故意把 `grad_weight` 乘以 2，观察梯度检查如何报告明显误差。",
        "在 ReLU 恰好为 0 的不可导点检查；epsilon 太大或太小；用完整数据集进行逐元素数值检查。",
    ),
    (
        "10-spiral-classification-project.ipynb",
        "综合项目：螺旋数据分类",
        "从数据探索到训练、验证和决策边界可视化，完成一个离线可复现的 NumPy MLP 项目。",
        "二维螺旋无法被单条直线分开，适合验证隐藏层和非线性的价值。完整工作流包括数据、基线、训练、验证和误差分析。",
        [code(SETUP + """
import numpy as np
import matplotlib.pyplot as plt
from from_scratch import MLP, Momentum, accuracy, make_spiral, train_classifier, train_validation_split

x, y = make_spiral(samples_per_class=100, noise=0.18, seed=21)
x_train, x_valid, y_train, y_valid = train_validation_split(x, y, validation_fraction=0.2, seed=21)
plt.figure(figsize=(5, 4)); plt.scatter(x[:, 0], x[:, 1], c=y, s=14, cmap="viridis"); plt.title("Spiral data"); plt.show()
"""), code("""
model = MLP(2, [64, 64], 3, dropout=0.05, seed=21)
optimizer = Momentum(model.parameters(), learning_rate=0.07, momentum=0.9, weight_decay=1e-4)
history = train_classifier(model, x_train, y_train, optimizer, epochs=220, batch_size=32, seed=21)
train_accuracy = accuracy(model.predict(x_train), y_train)
valid_accuracy = accuracy(model.predict(x_valid), y_valid)
print(f"train={train_accuracy:.3f}, validation={valid_accuracy:.3f}")
"""), code("""
padding = 0.1
x0, x1 = np.meshgrid(
    np.linspace(x[:, 0].min() - padding, x[:, 0].max() + padding, 220),
    np.linspace(x[:, 1].min() - padding, x[:, 1].max() + padding, 220),
)
grid = np.column_stack((x0.ravel(), x1.ravel()))
regions = model.predict(grid).reshape(x0.shape)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(history["loss"], label="train loss"); axes[0].legend()
axes[1].contourf(x0, x1, regions, alpha=0.35, cmap="viridis")
axes[1].scatter(x_valid[:, 0], x_valid[:, 1], c=y_valid, s=18, cmap="viridis", edgecolors="k")
axes[1].set_title("Validation decision boundary")
plt.tight_layout(); plt.show()
""")],
        "模型只看到训练集；验证准确率评价泛化；固定 seed 使数据、初始化、批次和 Dropout 序列可复现。",
        "移除所有隐藏层或缩小网络，比较决策边界；再调整噪声、正则化和学习率。",
        "根据验证结果反复修改后仍把它称为测试集；只报告训练准确率；没有固定随机种子却比较微小差异。",
    ),
]


def build_notebook(title: str, goal: str, concept: str, cells: list[dict[str, object]], checkpoint: str, experiment: str, mistakes: str) -> dict[str, object]:
    return {
        "cells": [
            markdown(f"# {title}\n\n## 学习目标\n\n{goal}"),
            markdown(f"## 概念模型\n\n{concept}"),
            markdown("## 逐步实现\n\n按顺序运行下面的代码，并在每一步检查 shape、数值范围和中间结果。"),
            *cells,
            markdown(f"## 检查点\n\n{checkpoint}"),
            markdown(f"## 试一试\n\n{experiment}"),
            markdown(f"## 常见错误\n\n{mistakes}"),
        ],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for filename, title, goal, concept, cells, checkpoint, experiment, mistakes in COURSES:
        notebook = build_notebook(title, goal, concept, cells, checkpoint, experiment, mistakes)
        (OUTPUT / filename).write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n")
    print(f"generated {len(COURSES)} notebooks in {OUTPUT}")


if __name__ == "__main__":
    main()
