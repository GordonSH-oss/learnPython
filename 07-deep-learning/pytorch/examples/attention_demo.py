"""Inspect scaled dot-product attention values and causal masking."""

from __future__ import annotations

import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).parents[1]))
from common.cli import parse_train_config
from common.models import ScaledDotProductAttention
from common.runtime import choose_device, seed_everything


def main() -> None:
    config = parse_train_config("synthetic-tokens", __doc__ or "Attention")
    seed_everything()
    device = choose_device(config.device)
    tokens = 4 if config.quick else 8
    query = torch.randn(2, tokens, 16, device=device)
    key = torch.randn(2, tokens, 16, device=device)
    value = torch.randn(2, tokens, 16, device=device)
    mask = torch.ones(tokens, tokens, dtype=torch.bool, device=device).tril().view(1, tokens, tokens)
    output, weights = ScaledDotProductAttention()(query, key, value, mask)
    print("output shape:", tuple(output.shape))
    print("attention row sums:", weights[0].sum(dim=-1))
    print("future attention mass:", weights[0].triu(diagonal=1).sum().item())


if __name__ == "__main__":
    main()
