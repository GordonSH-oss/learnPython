"""Real dataset loaders with deterministic train/validation splits."""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset, Subset, random_split
from torchvision import datasets, transforms


def _limit(dataset: Dataset, quick: bool, size: int) -> Dataset:
    return Subset(dataset, range(min(size, len(dataset)))) if quick else dataset


def image_loaders(
    name: str,
    data_dir: Path,
    batch_size: int,
    *,
    quick: bool = False,
    augment: bool = False,
) -> tuple[DataLoader, DataLoader, DataLoader, int]:
    normalized = name.lower()
    if normalized == "mnist":
        base_transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        train_dataset = datasets.MNIST(data_dir, train=True, download=True, transform=base_transform)
        test_dataset = datasets.MNIST(data_dir, train=False, download=True, transform=base_transform)
        channels = 1
    elif normalized in {"cifar", "cifar10"}:
        train_steps: list[object] = []
        if augment:
            train_steps.extend([transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip()])
        train_steps.extend([transforms.ToTensor(), transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261))])
        train_dataset = datasets.CIFAR10(data_dir, train=True, download=True, transform=transforms.Compose(train_steps))
        test_dataset = datasets.CIFAR10(
            data_dir,
            train=False,
            download=True,
            transform=transforms.Compose(train_steps[-2:]),
        )
        channels = 3
    else:
        raise ValueError(f"Unsupported dataset: {name}. Choose mnist or cifar10.")

    try:
        train_dataset = _limit(train_dataset, quick, 1024)
        test_dataset = _limit(test_dataset, quick, 256)
        validation_size = max(1, int(len(train_dataset) * 0.2))
        train_size = len(train_dataset) - validation_size
        train_subset, validation_subset = random_split(
            train_dataset,
            [train_size, validation_size],
            generator=torch.Generator().manual_seed(42),
        )
    except RuntimeError as exc:
        raise RuntimeError(f"Could not prepare {name} under {data_dir}. Check the network/cache and retry.") from exc

    options = {"batch_size": batch_size, "num_workers": 0}
    return (
        DataLoader(train_subset, shuffle=True, **options),
        DataLoader(validation_subset, shuffle=False, **options),
        DataLoader(test_dataset, shuffle=False, **options),
        channels,
    )
