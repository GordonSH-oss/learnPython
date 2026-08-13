"""Add idempotent official PyTorch tutorial supplements to course notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "07-deep-learning/pytorch/notebooks"
MARKER = "official-pytorch-supplement-v1"


SUPPLEMENTS = {
    "00-prerequites.ipynb": ("beginner_source/basics/intro.py", "官方快速入门把环境检查、数据、模型、优化和保存串成一条最小工作流。把本章当作 API 字典，而不是记忆清单：先确认 `torch.__version__` 与设备，再用小张量验证 dtype、shape 和随机种子。官方示例也提醒，下载数据和加速器可用性属于运行环境边界，代码应能安全回退到 CPU。"),
    "01-tensors-and-devices.ipynb": ("beginner_source/basics/tensorqs_tutorial.py；beginner_source/blitz/tensor_tutorial.py；recipes_source/recipes/changing_default_device.py；recipes_source/recipes/reasoning_about_shapes.py", "官方教程强调 Tensor 同时具有 shape、dtype、layout 和 device。`torch.from_numpy` 可共享 CPU 内存，原地修改会互相可见；`.to(device)` 通常返回新对象，计算两侧必须位于同一设备。广播从尾维对齐，矩阵乘法只约束收缩维；遇到错误时先写出每一维的业务含义，再检查 stride/contiguous，而不是盲目 reshape。"),
    "02-autograd.ipynb": ("beginner_source/basics/autogradqs_tutorial.py；beginner_source/blitz/autograd_tutorial.py；beginner_source/understanding_leaf_vs_nonleaf_tutorial.py", "官方材料把 Autograd 描述为运行时构建的有向无环图：叶子张量保存 `.grad`，非叶子节点用 `grad_fn` 记录反向规则。`backward()` 对标量隐式使用上游梯度 1，并把结果累加到叶子梯度；重复使用同一张已释放的图需要重新前向，或有意识地设置 `retain_graph=True`。推理使用 `no_grad`/`inference_mode`，而 `detach` 只切断某个张量之后的图。"),
    "03-neural-networks.ipynb": ("beginner_source/basics/buildmodel_tutorial.py；beginner_source/blitz/neural_networks_tutorial.py；recipes_source/recipes/defining_a_neural_network.py", "官方示例的核心契约是：子模块和 `nn.Parameter` 只要作为属性赋值，就会被注册到 `state_dict`，并被 `.to()`、`.train()` 和优化器统一管理。`forward` 只描述数据流，调用 `model(x)` 还会经过 Module 的 hook 等机制，因此不要直接调用 `model.forward(x)`。分类头返回 logits，让交叉熵内部处理 LogSoftmax。"),
    "04-datasets-and-dataloaders.ipynb": ("beginner_source/basics/data_tutorial.py；beginner_source/basics/transforms_tutorial.py；beginner_source/data_loading_tutorial.py；recipes_source/loading_data_recipe.rst", "官方教程把 `Dataset` 定义为索引到单样本的协议，把 `DataLoader` 定义为采样、组 batch 和并行加载的执行器。训练集可 `shuffle=True`，验证/测试集应保持稳定；transform 负责输入，target_transform 负责标签。增加 worker、pin memory 或异步拷贝前要测量瓶颈，并确保自定义 Dataset 在多进程环境中不会共享不安全状态。"),
    "05-training-and-validation.ipynb": ("beginner_source/basics/optimization_tutorial.py；beginner_source/basics/quickstart_tutorial.py；recipes_source/recipes/zeroing_out_gradients.py；recipes_source/recipes/saving_and_loading_a_general_checkpoint.rst", "官方训练步骤固定为清梯度、前向、损失、反向、更新；梯度会累加，所以边界必须明确。验证阶段切换 `eval()` 并关闭梯度，但两者职责不同：前者改变 Dropout/BatchNorm 行为，后者改变 Autograd 记录。可恢复 checkpoint 除模型外还应保存 optimizer、epoch 和关键配置，并在恢复后核对学习率与设备。"),
    "06-linear-regression.ipynb": ("beginner_source/pytorch_with_examples.rst；beginner_source/examples_nn/polynomial_optim.py；beginner_source/examples_autograd/polynomial_autograd.py", "官方多项式回归示例逐层展示 Tensor 手写更新、Autograd、`nn.Module` 和 optimizer 的边界。线性回归同样遵循 `prediction -> scalar loss -> gradients -> update`；`MSELoss` 要求预测与标签 shape 一致，广播虽可能运行却会改变问题。用已知合成参数做恢复实验，可以同时验证数据、梯度方向和训练循环。"),
    "07-cnn-mnist.ipynb": ("beginner_source/blitz/cifar10_tutorial.py；beginner_source/nn_tutorial.py；recipes_source/recipes/reasoning_about_shapes.py", "官方 CNN 教程要求持续追踪 NCHW：卷积改变通道和空间尺寸，池化下采样，flatten 之后才进入线性层。分类模型输出 logits，训练后不仅看 accuracy，也要按类别与错误样本检查。若替换输入分辨率或卷积配置，先用一个假 batch 验证每层 shape，避免把展平尺寸硬编码错。"),
    "08-regularization.ipynb": ("intermediate_source/pruning_tutorial.py；beginner_source/knowledge_distillation_tutorial.py；recipes_source/recipes/tuning_guide.py", "官方材料把正则化放在泛化和资源约束中理解：weight decay 约束参数，Dropout 只在训练模式随机屏蔽激活，早停依赖独立验证指标；剪枝和知识蒸馏则改变部署侧的容量/计算权衡。比较方法时保持数据划分、初始化预算和评估协议一致，不能用测试集选择超参数。"),
    "09-transfer-learning.ipynb": ("beginner_source/transfer_learning_tutorial.py；beginner_source/finetuning_torchvision_models_tutorial.rst", "官方迁移学习区分固定特征提取器和全量微调：先替换任务相关分类头，冻结主干并只把可训练参数交给 optimizer；解冻后需要重新检查 optimizer 参数组，并常对预训练层使用更小学习率。输入归一化必须匹配预训练权重提供的 transforms，否则即使 shape 正确，特征分布也会偏移。"),
    "10-rnn-sequences.ipynb": ("beginner_source/nlp/sequence_models_tutorial.py；intermediate_source/char_rnn_classification_tutorial.py；intermediate_source/char_rnn_generation_tutorial.py", "官方序列教程强调区分 batch、time、feature 三个维度，以及输出序列与最终 hidden state。LSTM 同时维护 hidden/cell state；跨 batch 传递状态时若不想反向穿过整段历史，需要 detach。变长序列要用 padding mask、pack 或长度感知的聚合，不能把 padding 当真实 token。"),
    "11-attention.ipynb": ("intermediate_source/scaled_dot_product_attention_tutorial.py；intermediate_source/transformer_building_blocks.py；intermediate_source/variable_length_attention_tutorial.py", "官方实现以 `scaled_dot_product_attention` 为核心：`QK^T / sqrt(d)` 控制分数尺度，mask 决定可见关系，softmax 后对 V 加权。布尔 mask 与加性 mask 的语义和形状要按 API 验证；训练时 dropout 是否启用必须显式传入。优化内核能否使用取决于设备、dtype、布局和 mask，先保证语义正确再做性能选择。"),
    "12-mixed-precision.ipynb": ("recipes_source/recipes/amp_recipe.py；recipes_source/recipes/tuning_guide.py", "官方 AMP 配方把 autocast 与 GradScaler 分工：autocast 为合适的算子选择低精度，scaler 放大损失以减少 float16 梯度下溢。反向传播不应包在 autocast 中；裁剪梯度前先 `unscale_`。AMP 的收益依赖 CUDA、Tensor Core 友好的尺寸和足够计算量，CPU/MPS 路径及 bfloat16 支持要按当前环境探测。"),
    "13-model-export.ipynb": ("beginner_source/saving_loading_models.py；beginner_source/basics/saveloadrun_tutorial.py；intermediate_source/torch_export_tutorial.py；beginner_source/onnx/export_simple_model_to_onnx_tutorial.py", "官方内容区分持久化与导出：`state_dict` 依赖 Python 模型定义，checkpoint 支持恢复训练；`torch.export`/ONNX 描述面向其他运行时的程序与输入约束。导出后必须在代表性输入上比较 eager 与 artifact 输出，并记录动态维、dtype、预处理和类别映射。不要把 pickle 来源不明的完整模型当作安全交换格式。"),
    "14-transformer-encoder.ipynb": ("beginner_source/transformer_tutorial.rst；intermediate_source/transformer_building_blocks.py；intermediate_source/variable_length_attention_tutorial.py", "官方 Transformer 材料把 embedding、位置信息、多头自注意力、残差/LayerNorm 和前馈层组成 encoder block。padding mask 表示哪些 token 无效，causal mask 表示时间可见性，两者不可混用；聚合序列时也要排除 padding。现代 attention 内核对 batch-first 和嵌套/变长表示有优化，但模型的 logits、mask 与长度契约应先独立测试。"),
    "15-debugging-and-reproducibility.ipynb": ("recipes_source/debug_mode_tutorial.py；recipes_source/torch_logs.py；intermediate_source/visualizing_gradients_tutorial.py", "官方调试建议先缩小问题：固定 seed、用单 batch 过拟合、断言 shape/dtype/device 和有限值，再检查梯度与参数是否更新。可复现不等于跨平台逐位一致，确定性算法可能降低性能且仍受版本/硬件影响。遇到编译或分布式问题时使用 PyTorch 日志接口增加可观测性，而不是只依赖最终异常。"),
    "16-image-classification-project.ipynb": ("beginner_source/basics/quickstart_tutorial.py；beginner_source/blitz/cifar10_tutorial.py；intermediate_source/torchvision_tutorial.py", "官方端到端图像任务把数据、增强、模型、优化、checkpoint 和推理视为一条契约链。训练增强与评估预处理应分离；最佳模型依据验证集保存，测试集只做最终报告。除总体准确率外，检查类别指标、混淆和错误样本，并把类别顺序、归一化参数和输入尺寸随 artifact 一起保存。"),
    "17-evaluation-and-inference.ipynb": ("beginner_source/basics/saveloadrun_tutorial.py；recipes_source/recipes/saving_and_loading_models_for_inference.rst；recipes_source/recipes/save_load_across_devices.rst", "官方推理流程是重建结构、加载 state dict、移动设备、`eval()`、`inference_mode()` 和一致预处理。指标必须先明确样本级还是 batch 级聚合；最后一个小 batch 使“batch 平均”可能偏离“样本平均”。生产接口应固定输入 shape/dtype、输出 logits/概率语义和类别映射，并用 round-trip 测试保护。"),
    "18-data-preprocessing-and-augmentation.ipynb": ("beginner_source/basics/transforms_tutorial.py；beginner_source/data_loading_tutorial.py；beginner_source/audio_data_augmentation_tutorial.rst", "官方 transforms 示例强调变换属于数据契约：训练集可用随机增强，验证/测试只用确定性预处理；归一化统计只能从训练数据估计。增强必须同时正确变换图像与结构化标签（框、mask 等），且输出 dtype/range 要满足模型预期。随机增强的复现还涉及 worker seed。"),
    "19-experiment-management.ipynb": ("beginner_source/introyt/tensorboardyt_tutorial.py；intermediate_source/tensorboard_tutorial.rst；beginner_source/hyperparameter_tuning_tutorial.py", "官方实验工具把配置、标量、图像、模型图和超参数结果绑定到一次 run。最低限度应记录代码/环境版本、随机种子、数据划分、完整配置、epoch 与验证指标、最佳 checkpoint 路径。超参数搜索只能基于验证目标，失败或提前停止的 run 也应保留状态，避免只记录成功结果造成偏差。"),
    "20-testing-pytorch-code.ipynb": ("intermediate_source/custom_function_double_backward_tutorial.rst；intermediate_source/jacobians_hessians.py；recipes_source/recipes/reasoning_about_shapes.py", "官方示例体现三层测试：shape/dtype/device 契约，数值结果或梯度，以及保存加载后的行为一致性。浮点测试使用 `torch.testing.assert_close` 并设置合理容差；随机模块分别测试 train/eval。自定义梯度用 double precision 的 `gradcheck`，训练循环则用小数据证明 loss 可下降且目标参数确实更新。"),
    "21-profiling-and-performance.ipynb": ("beginner_source/profiler.py；recipes_source/recipes/profiler_recipe.py；recipes_source/recipes/benchmark.py；recipes_source/recipes/timer_quick_start.py", "官方性能流程先用 `torch.utils.benchmark` 做可靠微基准，再用 profiler 定位 CPU/CUDA 时间、调用栈和内存。GPU 是异步的，普通墙钟计时前后需同步；应预热并重复测量。Profiler 本身有开销，只采样代表性步骤；先优化占比最大的算子或数据等待，再考虑布局、融合和编译。"),
    "22-training-stability.ipynb": ("recipes_source/recipes/zeroing_out_gradients.py；intermediate_source/visualizing_gradients_tutorial.py；intermediate_source/optimizer_step_in_backward_tutorial.py", "官方材料把稳定性问题拆为数值、梯度和更新三层。每步检查 loss/梯度是否有限，记录梯度范数；梯度裁剪限制更新冲击但不能修复错误数据或学习率。梯度累积时应按累积步数缩放 loss，并只在真实 optimizer step 后推进按步 scheduler。把 optimizer step 融入 backward 可省显存，但会改变 hook 与调试边界。"),
    "23-reading-and-modifying-pytorch-code.ipynb": ("beginner_source/basics/quickstart_tutorial.py；intermediate_source/torchvision_tutorial.py；intermediate_source/parametrizations.py", "阅读官方示例时先找外部契约：输入/标签、`nn.Module.forward`、loss、optimizer 和 artifact；再沿实际执行顺序追踪，而不是按文件顺序扫读。修改模型优先通过子模块、参数化或明确扩展点完成，并用 shape、梯度和 round-trip 测试保护。注册参数、buffer 与普通属性的差异会影响设备移动和 state dict。"),
    "24-deployment-contract.ipynb": ("intermediate_source/torch_export_tutorial.py；beginner_source/onnx/intro_onnx.py；recipes_source/recipes/saving_and_loading_models_for_inference.rst", "官方部署材料要求把模型之外的契约显式化：输入名称/shape/dtype、动态维约束、预处理、输出语义、类别表和版本。导出只是转换步骤，必须在目标 runtime 上做数值一致性与边界输入测试。模型 artifact 与任意 Python pickle 的信任边界不同；加载外部权重时优先使用受限模式并验证来源。"),
    "25-custom-autograd-and-gradcheck.ipynb": ("beginner_source/examples_autograd/polynomial_custom_function.py；intermediate_source/custom_function_double_backward_tutorial.rst；intermediate_source/custom_function_conv_bn_tutorial.py", "官方自定义 `autograd.Function` 把 forward 与 backward 视为严格的数学契约：`ctx.save_for_backward` 只保存反向所需张量，backward 接收上游梯度并为每个输入返回梯度或 None。用 float64 小输入运行 `gradcheck`；若需要二阶梯度，还要让 backward 本身可被 Autograd 记录并运行 `gradgradcheck`。原地修改必须特别声明并谨慎处理。"),
    "26-transformer-decoder-generation.ipynb": ("intermediate_source/seq2seq_translation_tutorial.py；beginner_source/chatbot_tutorial.py；intermediate_source/transformer_building_blocks.py", "官方 seq2seq 教程区分训练与生成：训练可用 teacher forcing 并行处理已知目标，推理只能根据已生成 token 自回归前进。decoder 必须使用 causal mask，padding 仍需单独屏蔽；生成在 EOS 或最大长度停止。贪心、采样和 beam search 改变质量/多样性/计算权衡，缓存 K/V 可避免每步重复计算历史。"),
    "27-distributed-data-parallel.ipynb": ("beginner_source/ddp_series_intro.rst；beginner_source/ddp_series_theory.rst；intermediate_source/ddp_tutorial.rst；beginner_source/dist_overview.rst", "官方 DDP 采用每进程一份模型：各 rank 处理不同数据分片，反向时对梯度 all-reduce，使参数更新保持一致。`DistributedSampler` 需要每 epoch 调用 `set_epoch` 以获得一致但变化的 shuffle；日志、评估聚合和 checkpoint 通常只由 rank 0 写入。启动、设备绑定和进程组销毁都属于生命周期契约，单卡正确不代表多卡无死锁。"),
    "28-torch-compile.ipynb": ("intermediate_source/torch_compile_tutorial.py；intermediate_source/torch_compile_full_example.py；recipes_source/torch_logs.py；recipes_source/regional_compilation.py", "官方 `torch.compile` 教程把编译看作捕获 Python 执行并生成优化图：首次调用含编译成本，后续匹配 guard 的输入才复用。数据相关 Python 控制流、动态 shape 或副作用可能造成 graph break/recompile；用日志解释原因。性能比较必须预热并包含多个稳态迭代，且始终先比较 eager 与 compiled 的数值和梯度。"),
    "29-loss-and-task-contracts.ipynb": ("beginner_source/basics/optimization_tutorial.py；beginner_source/nn_tutorial.py；beginner_source/fgsm_tutorial.py", "官方分类示例直接把 logits 传给 `CrossEntropyLoss`，标签是 long 类别索引；二分类/多标签通常用同 shape 的浮点标签和 `BCEWithLogitsLoss`。提前 Softmax/Sigmoid 既重复计算又损害数值稳定性。预测阈值和业务指标属于评估契约，应在验证集选择；类别不平衡时同时报告按类 precision/recall/F1。"),
}


def make_cell(source: str, body: str) -> dict:
    text = (
        "## 官方教程补充\n\n"
        f"**对应官方源文件：** `{source.replace('；', '`、`')}`\n\n"
        f"{body}\n\n"
        "**验证练习：** 找到上面源文件中的对应 API，先写出输入、输出和状态变化，再运行本 notebook 的相关实验；如果行为不同，优先检查本地 PyTorch 版本、设备能力和输入契约。\n\n"
        f"<!-- {MARKER} -->"
    )
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def main() -> None:
    expected = {path.name for path in NOTEBOOKS.glob("*.ipynb")}
    if expected != set(SUPPLEMENTS):
        raise RuntimeError(f"mapping mismatch: missing={expected-set(SUPPLEMENTS)}, extra={set(SUPPLEMENTS)-expected}")

    changed = 0
    for name, (source, body) in SUPPLEMENTS.items():
        path = NOTEBOOKS / name
        notebook = json.loads(path.read_text(encoding="utf-8"))
        cells = notebook["cells"]
        existing = next((i for i, cell in enumerate(cells) if MARKER in "".join(cell.get("source", []))), None)
        cell = make_cell(source, body)
        if existing is None:
            insert_at = next((i for i, item in enumerate(cells) if "## 检查点" in "".join(item.get("source", []))), len(cells))
            cells.insert(insert_at, cell)
        else:
            cells[existing] = cell
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        changed += 1
    print(f"updated {changed} notebooks")


if __name__ == "__main__":
    main()
