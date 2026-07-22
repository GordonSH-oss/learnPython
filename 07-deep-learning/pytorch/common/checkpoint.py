"""Checkpoint persistence with enough state to resume training."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from torch import nn


def save_checkpoint(
    path: str | Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    epoch: int = 0,
    metrics: dict[str, float] | None = None,
    scheduler: Any | None = None,
    scaler: Any | None = None,
) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "epoch": epoch,
        "metrics": metrics or {},
    }
    if optimizer is not None:
        payload["optimizer_state"] = optimizer.state_dict()
    if scheduler is not None:
        payload["scheduler_state"] = scheduler.state_dict()
    if scaler is not None:
        payload["scaler_state"] = scaler.state_dict()
    torch.save(payload, destination)
    return destination


def load_checkpoint(
    path: str | Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    map_location: str | torch.device = "cpu",
    scheduler: Any | None = None,
    scaler: Any | None = None,
) -> dict[str, Any]:
    payload = torch.load(Path(path), map_location=map_location, weights_only=True)
    model.load_state_dict(payload["model_state"])
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if scheduler is not None and "scheduler_state" in payload:
        scheduler.load_state_dict(payload["scheduler_state"])
    if scaler is not None and "scaler_state" in payload:
        scaler.load_state_dict(payload["scaler_state"])
    return {"epoch": payload.get("epoch", 0), "metrics": payload.get("metrics", {})}
