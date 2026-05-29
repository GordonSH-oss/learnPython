"""CNN shape walkthrough with MNIST-sized tensors.

This does not download MNIST. It uses random tensors with the same shape so the
model structure can be studied offline.

Run:
    python 07-deep-learning/cnn_mnist.py
"""

from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


class MNISTCnn(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(8, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(nn.Flatten(), nn.Linear(16 * 7 * 7, 10))

    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        return self.classifier(self.features(x))


def main() -> None:
    images = torch.randn(16, 1, 28, 28)
    labels = torch.randint(0, 10, (16,))
    model = MNISTCnn()
    logits = model(images)
    loss = nn.CrossEntropyLoss()(logits, labels)
    print("logits shape:", logits.shape)
    print("loss:", loss.item())


if __name__ == "__main__":
    main()
