from __future__ import annotations

import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("torchvision")
from PIL import Image

PYTORCH_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PYTORCH_ROOT))

from common import data as data_module


class FakeVisionDataset(torch.utils.data.Dataset):
    def __init__(self, root, train=True, download=False, transform=None):
        self.transform = transform
        self.train = train
        self.values = [Image.new("RGB", (32, 32), color=(index, index, index)) for index in range(40)]

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        image = self.values[index]
        if self.transform:
            image = self.transform(image)
        return image, index % 10


def test_validation_transform_is_separate_from_training_augmentation(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(data_module.datasets, "CIFAR10", FakeVisionDataset)
    train_loader, validation_loader, _, _ = data_module.image_loaders(
        "cifar10", tmp_path, batch_size=8, quick=True, augment=True
    )
    training_transform = train_loader.dataset.dataset.transform
    validation_transform = validation_loader.dataset.dataset.transform
    training_names = {step.__class__.__name__ for step in training_transform.transforms}
    validation_names = {step.__class__.__name__ for step in validation_transform.transforms}
    assert {"RandomCrop", "RandomHorizontalFlip"} <= training_names
    assert "RandomCrop" not in validation_names
    assert "RandomHorizontalFlip" not in validation_names
    assert set(train_loader.dataset.indices).isdisjoint(validation_loader.dataset.indices)
