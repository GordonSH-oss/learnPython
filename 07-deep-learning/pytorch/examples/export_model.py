"""Export a CNN with TorchScript and compare eager/exported outputs."""

from __future__ import annotations

import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.cli import parse_train_config
from common.models import ImageClassifier
from common.runtime import choose_device


def main() -> None:
    config = parse_train_config("mnist", __doc__ or "Model export")
    device = choose_device(config.device)
    model = ImageClassifier().to(device).eval()
    example = torch.randn(1, 1, 28, 28, device=device)
    with torch.inference_mode():
        expected = model(example)
        exported = torch.jit.trace(model, example)
        actual = exported(example)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    destination = config.output_dir / "image_classifier_torchscript.pt"
    exported.save(str(destination))
    torch.testing.assert_close(actual, expected)
    print("saved:", destination)
    print("max output difference:", (actual - expected).abs().max().item())


if __name__ == "__main__":
    main()
