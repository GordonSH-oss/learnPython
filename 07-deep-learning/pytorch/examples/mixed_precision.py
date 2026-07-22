"""Run one CUDA mixed-precision training step, or explain why it is skipped."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.cli import parse_train_config
from common.runtime import choose_device


def main() -> None:
    config = parse_train_config("synthetic-images", __doc__ or "Mixed precision")
    device = choose_device(config.device)
    if device.type != "cuda":
        print("AMP training is skipped: this lesson requires a CUDA device.")
        print("CPU and MPS examples remain available in the other lessons.")
        return

    model = nn.Sequential(nn.Flatten(), nn.Linear(3 * 32 * 32, 10)).to(device)
    optimizer = torch.optim.AdamW(model.parameters())
    scaler = torch.amp.GradScaler("cuda")
    images = torch.randn(min(config.batch_size, 16), 3, 32, 32, device=device)
    labels = torch.randint(0, 10, (images.shape[0],), device=device)
    optimizer.zero_grad(set_to_none=True)
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        loss = nn.CrossEntropyLoss()(model(images), labels)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
    print("AMP step completed; loss:", loss.item())


if __name__ == "__main__":
    main()
