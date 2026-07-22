from __future__ import annotations

import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

PYTORCH_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PYTORCH_ROOT))

from common.checkpoint import load_checkpoint, save_checkpoint
from common.engine import evaluate, train_one_epoch
from common.models import ImageClassifier, ScaledDotProductAttention, SequenceClassifier
from common.runtime import choose_device, seed_everything


def test_choose_device_cpu_and_seed_are_deterministic() -> None:
    assert choose_device("cpu").type == "cpu"
    seed_everything(7)
    first = torch.rand(3)
    seed_everything(7)
    torch.testing.assert_close(first, torch.rand(3))


def test_training_and_evaluation_aggregate_metrics() -> None:
    inputs = torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [-1.0, -1.0]])
    targets = torch.tensor([0, 1, 0, 1])
    loader = DataLoader(TensorDataset(inputs, targets), batch_size=2)
    model = nn.Linear(2, 2)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    train_result = train_one_epoch(model, loader, loss_fn, optimizer, torch.device("cpu"))
    evaluation_result = evaluate(model, loader, loss_fn, torch.device("cpu"))
    assert train_result.examples == evaluation_result.examples == 4
    assert 0 <= evaluation_result.accuracy <= 1
    assert evaluation_result.loss >= 0


def test_checkpoint_round_trip(tmp_path: Path) -> None:
    model = nn.Linear(2, 1)
    optimizer = torch.optim.Adam(model.parameters())
    expected = {name: value.detach().clone() for name, value in model.state_dict().items()}
    path = save_checkpoint(tmp_path / "model.pt", model, optimizer, epoch=3, metrics={"loss": 0.5})
    with torch.no_grad():
        model.weight.add_(10)
    metadata = load_checkpoint(path, model, optimizer)
    assert metadata == {"epoch": 3, "metrics": {"loss": 0.5}}
    for name, value in model.state_dict().items():
        torch.testing.assert_close(value, expected[name])


def test_model_output_shapes_and_attention_mask() -> None:
    assert ImageClassifier()(torch.randn(2, 1, 28, 28)).shape == (2, 10)
    assert SequenceClassifier()(torch.randn(2, 5, 1)).shape == (2, 2)
    query = key = value = torch.randn(2, 4, 8)
    mask = torch.ones(4, 4, dtype=torch.bool).tril().unsqueeze(0)
    output, weights = ScaledDotProductAttention()(query, key, value, mask)
    assert output.shape == query.shape
    torch.testing.assert_close(weights.sum(dim=-1), torch.ones(2, 4))
    assert weights.triu(diagonal=1).sum().item() == 0
