"""Build a small neural network with torch.nn.

Run:
    python 07-deep-learning/neural_networks.py
"""

from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


class Classifier(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        return self.net(x)


def main() -> None:
    model = Classifier(input_dim=4, hidden_dim=8, num_classes=3)
    batch = torch.randn(5, 4)
    logits = model(batch)

    print(model)
    print("input shape:", batch.shape)
    print("output shape:", logits.shape)


if __name__ == "__main__":
    main()
