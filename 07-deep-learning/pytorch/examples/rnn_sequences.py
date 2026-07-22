"""Train an LSTM to classify increasing and decreasing sequences."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.cli import parse_train_config
from common.engine import evaluate, train_one_epoch
from common.models import SequenceClassifier
from common.runtime import choose_device, seed_everything


def make_dataset(size: int = 512, steps: int = 12) -> TensorDataset:
    starts = torch.randn(size, 1, 1)
    direction = torch.randint(0, 2, (size,))
    slopes = direction.float().mul(2).sub(1).view(-1, 1, 1)
    timeline = torch.arange(steps).float().view(1, -1, 1) / steps
    sequences = starts + slopes * timeline + torch.randn(size, steps, 1) * 0.03
    return TensorDataset(sequences, direction)


def main() -> None:
    config = parse_train_config("synthetic-sequences", __doc__ or "RNN sequences")
    seed_everything()
    device = choose_device(config.device)
    size = 128 if config.quick else 1024
    dataset = make_dataset(size)
    split = int(size * 0.8)
    train_set, validation_set = torch.utils.data.random_split(dataset, [split, size - split])
    train_loader = DataLoader(train_set, batch_size=config.batch_size, shuffle=True)
    validation_loader = DataLoader(validation_set, batch_size=config.batch_size)
    model = SequenceClassifier().to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    for epoch in range(1, config.epochs + 1):
        train_result = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        validation_result = evaluate(model, validation_loader, loss_fn, device)
        print(f"epoch={epoch} loss={train_result.loss:.4f} val_acc={validation_result.accuracy:.3f}")


if __name__ == "__main__":
    main()
