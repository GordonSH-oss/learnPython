"""Transfer learning structure with torchvision.

Run:
    python 07-deep-learning/transfer_learning.py
"""

from __future__ import annotations

try:
    import torch
    from torch import nn
    from torchvision import models
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


def build_model(num_classes: int) -> "nn.Module":
    model = models.resnet18(weights=None)
    for parameter in model.parameters():
        parameter.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def main() -> None:
    model = build_model(num_classes=3)
    images = torch.randn(2, 3, 224, 224)
    logits = model(images)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print("output shape:", logits.shape)
    print("trainable parameters:", trainable)


if __name__ == "__main__":
    main()
