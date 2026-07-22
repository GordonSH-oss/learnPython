"""Train a CNN on real MNIST or CIFAR-10 data."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.checkpoint import save_checkpoint
from common.cli import parse_train_config
from common.data import image_loaders
from common.engine import evaluate, train_one_epoch
from common.models import ImageClassifier
from common.runtime import choose_device, seed_everything


def main() -> None:
    config = parse_train_config("mnist", __doc__ or "Image classification")
    seed_everything()
    device = choose_device(config.device)
    try:
        train_loader, validation_loader, test_loader, channels = image_loaders(
            config.dataset, config.data_dir, config.batch_size, quick=config.quick, augment=True
        )
    except Exception as exc:
        raise SystemExit(f"Dataset download/load failed: {exc}\nRetry with network access or a populated --data-dir.") from exc

    model = ImageClassifier(channels=channels).to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    best_accuracy = -1.0
    patience = 2
    stale_epochs = 0

    for epoch in range(1, config.epochs + 1):
        train_result = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        validation_result = evaluate(model, validation_loader, loss_fn, device)
        print(
            f"epoch={epoch} train_loss={train_result.loss:.4f} "
            f"val_loss={validation_result.loss:.4f} val_acc={validation_result.accuracy:.3f}"
        )
        if validation_result.accuracy > best_accuracy:
            best_accuracy = validation_result.accuracy
            stale_epochs = 0
            save_checkpoint(config.output_dir / "image_classifier.pt", model, optimizer, epoch=epoch,
                            metrics={"validation_accuracy": best_accuracy})
        else:
            stale_epochs += 1
            if stale_epochs >= patience:
                print("early stopping: validation accuracy did not improve")
                break

    test_result = evaluate(model, test_loader, loss_fn, device)
    print(f"test_loss={test_result.loss:.4f} test_acc={test_result.accuracy:.3f}")


if __name__ == "__main__":
    main()
