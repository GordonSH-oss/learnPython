"""Train a CNN on real MNIST or CIFAR-10 data."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.checkpoint import load_checkpoint, save_checkpoint
from common.cli import parse_train_config
from common.data import image_loaders
from common.engine import evaluate, train_one_epoch
from common.models import ImageClassifier
from common.runtime import choose_device, seed_everything
from common.training import EarlyStopping


def main() -> None:
    config = parse_train_config("mnist", __doc__ or "Image classification")
    seed_everything(config.seed)
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
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", patience=1)
    start_epoch = 1
    if config.resume:
        metadata = load_checkpoint(config.resume, model, optimizer, map_location=device, scheduler=scheduler)
        start_epoch = int(metadata["epoch"]) + 1
        print(f"resumed from epoch {metadata['epoch']}: {config.resume}")
    early_stopping = EarlyStopping(patience=config.patience, mode="max")
    checkpoint_path = config.output_dir / "image_classifier.pt"

    for epoch in range(start_epoch, config.epochs + 1):
        train_result = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        validation_result = evaluate(model, validation_loader, loss_fn, device)
        scheduler.step(validation_result.accuracy)
        print(
            f"epoch={epoch} train_loss={train_result.loss:.4f} "
            f"val_loss={validation_result.loss:.4f} val_acc={validation_result.accuracy:.3f}"
        )
        improved, should_stop = early_stopping.update(validation_result.accuracy)
        if improved:
            save_checkpoint(
                checkpoint_path,
                model,
                optimizer,
                epoch=epoch,
                metrics={"validation_accuracy": validation_result.accuracy},
                scheduler=scheduler,
            )
        if should_stop:
            print("early stopping: validation accuracy did not improve")
            break

    load_checkpoint(checkpoint_path, model, map_location=device)
    test_result = evaluate(model, test_loader, loss_fn, device)
    print(f"best_checkpoint={checkpoint_path}")
    print(f"test_loss={test_result.loss:.4f} test_acc={test_result.accuracy:.3f}")


if __name__ == "__main__":
    main()
