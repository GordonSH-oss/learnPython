"""PyTorch tensor basics.

Run:
    python 07-deep-learning/tensors.py
"""

from __future__ import annotations

try:
    import torch
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


def main() -> None:
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    y = torch.ones((2, 2))

    print("x shape:", x.shape)
    print("x + y:\n", x + y)
    print("matrix multiply:\n", x @ y)
    print("mean by column:", x.mean(dim=0))

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device:", device)
    print("x on device:", x.to(device).device)


if __name__ == "__main__":
    main()
