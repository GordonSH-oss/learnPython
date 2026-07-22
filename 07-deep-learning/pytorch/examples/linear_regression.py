"""Train and checkpoint a linear regression model on synthetic numeric data."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.checkpoint import load_checkpoint, save_checkpoint
from common.cli import parse_train_config
from common.runtime import choose_device, seed_everything


def main() -> None:
    config = parse_train_config("synthetic", __doc__ or "Linear regression")
    seed_everything(config.seed)
    device = choose_device(config.device)
    points = 128 if config.quick else 1024
    x = torch.linspace(-1, 1, points, device=device).unsqueeze(1)
    y = 3 * x + 2 + torch.randn_like(x) * 0.05
    model = nn.Linear(1, 1).to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.2)
    loss_fn = nn.MSELoss()
    start_epoch = 1
    if config.resume:
        metadata = load_checkpoint(config.resume, model, optimizer, map_location=device)
        start_epoch = int(metadata["epoch"]) + 1
        print(f"resumed from epoch {metadata['epoch']}: {config.resume}")

    for epoch in range(start_epoch, config.epochs + 1):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_fn(model(x), y)
        loss.backward()
        optimizer.step()
        print(f"epoch={epoch} loss={loss.item():.6f}")

    save_checkpoint(config.output_dir / "linear_regression.pt", model, optimizer, epoch=config.epochs)
    print(f"learned y = {model.weight.item():.2f}x + {model.bias.item():.2f}")


if __name__ == "__main__":
    main()
