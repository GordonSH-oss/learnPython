from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_all_notebooks_are_valid_and_have_teaching_sections() -> None:
    notebooks = sorted((ROOT / "pytorch/notebooks").glob("*.ipynb"))
    assert len(notebooks) == 30
    required = ("学习目标", "概念模型", "检查点", "试一试", "常见错误")
    for path in notebooks:
        notebook = json.loads(path.read_text())
        text = "".join("".join(cell["source"]) for cell in notebook["cells"])
        code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
        assert notebook["nbformat"] == 4
        if path.name != "00-prerequites.ipynb":
            assert all(section in text for section in required)
        minimum_code_cells = 2 if path.name in {"25-custom-autograd-and-gradcheck.ipynb", "27-distributed-data-parallel.ipynb"} else 3 if path.name in {"18-data-preprocessing-and-augmentation.ipynb", "19-experiment-management.ipynb", "24-deployment-contract.ipynb", "26-transformer-decoder-generation.ipynb", "28-torch-compile.ipynb", "29-loss-and-task-contracts.ipynb"} else 4
        assert len(code_cells) >= minimum_code_cells
        assert sum(len(cell["source"]) for cell in code_cells) >= 12


def test_curriculum_topics_have_executable_lessons() -> None:
    notebooks = {path.name: path.read_text() for path in (ROOT / "pytorch/notebooks").glob("*.ipynb")}
    required_topics = {
        "14-transformer-encoder.ipynb": ("TransformerEncoder", "padding mask", "causal mask", "推理"),
        "15-debugging-and-reproducibility.ipynb": ("device", "dtype", "grad", "seed_everything"),
        "16-image-classification-project.ipynb": ("checkpoint", "train_one_epoch", "evaluate", "推理"),
        "17-evaluation-and-inference.ipynb": ("accuracy", "precision", "recall", "confusion_matrix", "推理"),
        "18-data-preprocessing-and-augmentation.ipynb": ("数据泄漏", "normalize", "training", "class_weights"),
        "19-experiment-management.ipynb": ("ExperimentConfig", "metrics.json", "config.json", "parameter_count"),
        "20-testing-pytorch-code.ipynb": ("assert_close", "checkpoint", "parameter.grad", "shape"),
        "21-profiling-and-performance.ipynb": ("profiler", "synchronize", "inference_mode", "预热"),
        "22-training-stability.ipynb": ("accumulation_steps", "clip_grad_norm_", "scheduler", "梯度范数"),
        "23-reading-and-modifying-pytorch-code.ipynb": ("inspect.signature", "_run_epoch", "ImageClassifier", "调用关系"),
        "24-deployment-contract.ipynb": ("input_shape", "class_names", "inference_mode", "artifact"),
        "25-custom-autograd-and-gradcheck.ipynb": ("gradcheck", "save_for_backward", "backward", "Function"),
        "26-transformer-decoder-generation.ipynb": ("teacher forcing", "causal mask", "generate", "Decoder"),
        "27-distributed-data-parallel.ipynb": ("DistributedDataParallel", "DistributedSampler", "rank", "world_size"),
        "28-torch-compile.ipynb": ("torch.compile", "graph break", "预热", "compiled_output"),
        "29-loss-and-task-contracts.ipynb": ("BCEWithLogitsLoss", "CrossEntropyLoss", "multi-hot", "macro F1"),
    }
    for notebook, topics in required_topics.items():
        assert notebook in notebooks
        assert all(topic in notebooks[notebook] for topic in topics)


def test_fundamentals_do_not_import_torch() -> None:
    for path in (ROOT / "fundamentals").glob("*"):
        if path.suffix in {".py", ".md"}:
            assert "import torch" not in path.read_text().lower()


def test_readme_routes_all_curriculum_stages() -> None:
    readme = (ROOT / "pytorch/README.md").read_text()
    for notebook_number in ("01", "06", "14", "16", "20", "25", "27", "28"):
        assert notebook_number in readme
    for stage in ("阶段 1", "阶段 2", "阶段 3", "阶段 4", "完成标准"):
        assert stage in readme


def test_readme_defines_canonical_learning_path_and_categories() -> None:
    readme = (ROOT / "pytorch/README.md").read_text()
    expected_path = ("01 -> 02 -> 25 -> 03 -> 29 -> 06 -> 04 -> 18 -> 05 -> 15 -> 22", "11 -> 14 -> 26")
    assert all(fragment in readme for fragment in expected_path)
    for category in ("参考索引", "基础机制", "模型结构", "训练工程", "部署与系统", "综合项目"):
        assert category in readme
    assert "不属于必读主线" in readme
