"""Linear regression with synthetic data.

Run:
    python 07-deep-learning/linear_regression.py
"""

from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


def main() -> None:
    torch.manual_seed(42)
    x = torch.linspace(-1, 1, 100).unsqueeze(1)
    y = 3 * x + 2 + torch.randn_like(x) * 0.1

    model = nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.2)
    loss_fn = nn.MSELoss()

    for _ in range(100):
        loss = loss_fn(model(x), y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    weight = model.weight.item()
    bias = model.bias.item()
    print(f"learned y = {weight:.2f}x + {bias:.2f}")


if __name__ == "__main__":
    main()
