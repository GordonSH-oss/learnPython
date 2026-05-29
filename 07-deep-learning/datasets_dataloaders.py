"""Dataset and DataLoader basics.

Run:
    python 07-deep-learning/datasets_dataloaders.py
"""

from __future__ import annotations

try:
    import torch
    from torch.utils.data import DataLoader, TensorDataset
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/ai.txt") from exc


def main() -> None:
    features = torch.arange(20, dtype=torch.float32).reshape(10, 2)
    labels = (features.sum(dim=1) > 10).long()

    dataset = TensorDataset(features, labels)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)

    for batch_index, (x, y) in enumerate(loader):
        print(f"batch {batch_index}: x={tuple(x.shape)} y={y.tolist()}")


if __name__ == "__main__":
    main()
