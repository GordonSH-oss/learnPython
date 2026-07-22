"""Build a pretrained ResNet classifier and run one quick optimization step."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch import nn
from torchvision import models

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.cli import parse_train_config
from common.runtime import choose_device


def build_model(num_classes: int = 10, pretrained: bool = True) -> nn.Module:
    weights = models.ResNet18_Weights.DEFAULT if pretrained else None
    try:
        model = models.resnet18(weights=weights)
    except Exception as exc:
        raise RuntimeError("Pretrained weights could not be downloaded. Check the network/cache and retry.") from exc
    for parameter in model.parameters():
        parameter.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def main() -> None:
    config = parse_train_config("cifar10", __doc__ or "Transfer learning")
    device = choose_device(config.device)
    model = build_model(pretrained=not config.quick).to(device)
    images = torch.randn(min(config.batch_size, 4), 3, 224, 224, device=device)
    labels = torch.randint(0, 10, (images.shape[0],), device=device)
    optimizer = torch.optim.Adam(model.fc.parameters(), lr=1e-3)
    loss = nn.CrossEntropyLoss()(model(images), labels)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    print("output classes: 10")
    print("trainable parameters:", sum(p.numel() for p in model.parameters() if p.requires_grad))


if __name__ == "__main__":
    main()
