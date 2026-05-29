"""Tiny image classification example using random image-like tensors.

Run:
    python 07-deep-learning/image_classification.py
"""

from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


class TinyImageClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(3 * 16 * 16, 32),
            nn.ReLU(),
            nn.Linear(32, 4),
        )

    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        return self.net(x)


def main() -> None:
    images = torch.randn(8, 3, 16, 16)
    labels = torch.randint(0, 4, (8,))
    model = TinyImageClassifier()
    loss = nn.CrossEntropyLoss()(model(images), labels)
    print("logits shape:", model(images).shape)
    print("loss:", loss.item())


if __name__ == "__main__":
    main()
