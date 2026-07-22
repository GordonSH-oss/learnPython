"""Real dataset loaders with deterministic train/validation splits."""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset, Subset
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
        evaluation_transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
        )
        training_steps: list[object] = []
        if augment:
            training_steps.append(transforms.RandomAffine(degrees=8, translate=(0.05, 0.05)))
        training_steps.extend(evaluation_transform.transforms)
        dataset_type = datasets.MNIST
        channels = 1
    elif normalized in {"cifar", "cifar10"}:
        training_steps = []
        if augment:
            training_steps.extend([transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip()])
        evaluation_transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
            ]
        )
        training_steps.extend(evaluation_transform.transforms)
        dataset_type = datasets.CIFAR10
        channels = 3
    else:
        raise ValueError(f"Unsupported dataset: {name}. Choose mnist or cifar10.")

    try:
        training_dataset = dataset_type(
            data_dir, train=True, download=True, transform=transforms.Compose(training_steps)
        )
        validation_dataset = dataset_type(
            data_dir, train=True, download=False, transform=evaluation_transform
        )
        test_dataset = dataset_type(
            data_dir, train=False, download=True, transform=evaluation_transform
        )
        full_size = min(1024, len(training_dataset)) if quick else len(training_dataset)
        generator = torch.Generator().manual_seed(42)
        indices = torch.randperm(len(training_dataset), generator=generator)[:full_size].tolist()
        validation_size = max(1, int(full_size * 0.2))
        validation_indices = indices[:validation_size]
        training_indices = indices[validation_size:]
        train_subset = Subset(training_dataset, training_indices)
        validation_subset = Subset(validation_dataset, validation_indices)
        test_dataset = _limit(test_dataset, quick, 256)
    except Exception as exc:
        raise RuntimeError(f"Could not prepare {name} under {data_dir}. Check the network/cache and retry.") from exc

    options = {"batch_size": batch_size, "num_workers": 0}
    return (
        DataLoader(train_subset, shuffle=True, **options),
        DataLoader(validation_subset, shuffle=False, **options),
        DataLoader(test_dataset, shuffle=False, **options),
        channels,
    )


def transfer_learning_loaders(
    data_dir: Path,
    batch_size: int,
    *,
    quick: bool = False,
) -> tuple[DataLoader, DataLoader, DataLoader]:
    """CIFAR-10 loaders resized and normalized for pretrained ResNet."""
    weights_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ]
    )
    training_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ]
    )
    try:
        training_dataset = datasets.CIFAR10(data_dir, train=True, download=True, transform=training_transform)
        validation_dataset = datasets.CIFAR10(data_dir, train=True, download=False, transform=weights_transform)
        test_dataset = datasets.CIFAR10(data_dir, train=False, download=True, transform=weights_transform)
        full_size = min(256, len(training_dataset)) if quick else len(training_dataset)
        indices = torch.randperm(len(training_dataset), generator=torch.Generator().manual_seed(42))[:full_size].tolist()
        validation_size = max(1, int(full_size * 0.2))
        training_subset = Subset(training_dataset, indices[validation_size:])
        validation_subset = Subset(validation_dataset, indices[:validation_size])
        test_subset = _limit(test_dataset, quick, 128)
    except Exception as exc:
        raise RuntimeError(f"Could not prepare CIFAR-10 under {data_dir}. Check the network/cache and retry.") from exc
    options = {"batch_size": batch_size, "num_workers": 0}
    return (
        DataLoader(training_subset, shuffle=True, **options),
        DataLoader(validation_subset, shuffle=False, **options),
        DataLoader(test_subset, shuffle=False, **options),
    )
