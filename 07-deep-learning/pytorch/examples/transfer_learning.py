"""Fine-tune a pretrained ResNet18 on real CIFAR-10 data."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch import nn
from torchvision import models

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.checkpoint import load_checkpoint, save_checkpoint
from common.cli import parse_train_config
from common.data import transfer_learning_loaders
from common.engine import evaluate, train_one_epoch
from common.runtime import choose_device, seed_everything
from common.training import EarlyStopping


def build_model(num_classes: int = 10, pretrained: bool = True) -> nn.Module:
    weights = models.ResNet18_Weights.DEFAULT if pretrained else None
    try:
        model = models.resnet18(weights=weights)
    except Exception as exc:
        raise RuntimeError("Pretrained weights could not be downloaded. Check the network/cache and retry.") from exc
    for parameter in model.parameters():
        parameter.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def unfreeze_last_block(model: nn.Module) -> None:
    for parameter in model.layer4.parameters():
        parameter.requires_grad = True


def main() -> None:
    config = parse_train_config("cifar10", __doc__ or "Transfer learning")
    if config.dataset.lower() not in {"cifar", "cifar10"}:
        raise SystemExit("This transfer-learning lesson supports --dataset cifar10.")
    seed_everything(config.seed)
    device = choose_device(config.device)
    try:
        train_loader, validation_loader, test_loader = transfer_learning_loaders(
            config.data_dir, config.batch_size, quick=config.quick
        )
        model = build_model(pretrained=not config.quick).to(device)
    except Exception as exc:
        raise SystemExit(str(exc)) from exc

    loss_fn = nn.CrossEntropyLoss()
    start_epoch = 1
    if config.resume:
        metadata = load_checkpoint(config.resume, model, map_location=device)
        start_epoch = int(metadata["epoch"]) + 1
        if metadata["metrics"].get("unfrozen", 0.0):
            unfreeze_last_block(model)
    optimizer = (
        torch.optim.AdamW(
            [
                {"params": model.layer4.parameters(), "lr": 1e-4},
                {"params": model.fc.parameters(), "lr": 1e-3},
            ]
        )
        if any(parameter.requires_grad for parameter in model.layer4.parameters())
        else torch.optim.AdamW(model.fc.parameters(), lr=1e-3)
    )
    if config.resume:
        load_checkpoint(config.resume, model, optimizer, map_location=device)
    stopping = EarlyStopping(config.patience, mode="max")
    checkpoint_path = config.output_dir / "transfer_resnet18.pt"

    for epoch in range(start_epoch, config.epochs + 1):
        if epoch == max(2, config.epochs // 2) and not any(
            parameter.requires_grad for parameter in model.layer4.parameters()
        ):
            unfreeze_last_block(model)
            optimizer = torch.optim.AdamW(
                [
                    {"params": model.layer4.parameters(), "lr": 1e-4},
                    {"params": model.fc.parameters(), "lr": 1e-3},
                ]
            )
            print("unfroze layer4 with a smaller learning rate")
        train_result = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        validation_result = evaluate(model, validation_loader, loss_fn, device)
        print(
            f"epoch={epoch} train_loss={train_result.loss:.4f} "
            f"val_loss={validation_result.loss:.4f} val_acc={validation_result.accuracy:.3f}"
        )
        improved, should_stop = stopping.update(validation_result.accuracy)
        if improved:
            save_checkpoint(
                checkpoint_path,
                model,
                optimizer,
                epoch=epoch,
                metrics={
                    "validation_accuracy": validation_result.accuracy,
                    "unfrozen": float(any(p.requires_grad for p in model.layer4.parameters())),
                },
            )
        if should_stop:
            print("early stopping: validation accuracy did not improve")
            break

    load_checkpoint(checkpoint_path, model, map_location=device)
    result = evaluate(model, test_loader, loss_fn, device)
    print(f"test_loss={result.loss:.4f} test_acc={result.accuracy:.3f}")


if __name__ == "__main__":
    main()
