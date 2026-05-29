"""Autograd basics: forward pass, loss, backward pass.

Run:
    python 07-deep-learning/autograd.py
"""

from __future__ import annotations

try:
    import torch
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


def main() -> None:
    x = torch.tensor([1.0, 2.0, 3.0])
    weight = torch.tensor([0.5, 0.5, 0.5], requires_grad=True)
    target = torch.tensor(4.0)

    prediction = (x * weight).sum()
    loss = (prediction - target) ** 2
    loss.backward()

    print("prediction:", prediction.item())
    print("loss:", loss.item())
    print("gradient:", weight.grad)


if __name__ == "__main__":
    main()
