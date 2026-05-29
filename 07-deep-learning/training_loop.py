"""A minimal supervised training loop.

Run:
    python 07-deep-learning/training_loop.py
"""

from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


def main() -> None:
    torch.manual_seed(0)
    x = torch.randn(64, 3)
    true_w = torch.tensor([[2.0], [-1.0], [0.5]])
    y = x @ true_w + 0.1

    model = nn.Linear(3, 1)
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

    for epoch in range(20):
        prediction = model(x)
        loss = loss_fn(prediction, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch in {0, 1, 5, 19}:
            print(f"epoch={epoch:02d} loss={loss.item():.4f}")


if __name__ == "__main__":
    main()
