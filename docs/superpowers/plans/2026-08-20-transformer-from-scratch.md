# Decoder-Only Transformer From Scratch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained Chinese notebook that implements, trains, generates with, and visualizes a small decoder-only Transformer from first principles.

**Architecture:** One notebook progresses from an embedded character corpus through tokenization and batching, manually implemented causal multi-head attention, pre-norm Transformer blocks, a language-model training loop, autoregressive generation, and attention visualization. A temporary extraction-based verification script executes notebook code and asserts mathematical and shape invariants.

**Tech Stack:** Python 3.10, PyTorch, Matplotlib, Jupyter nbformat

**Spec:** `docs/superpowers/specs/2026-08-20-transformer-from-scratch-design.md`

## Global Constraints

- Modify only `07-deep-learning/dive-into-dl/transformer-from-scratch.ipynb` plus these planning artifacts.
- Run offline with an embedded character-level corpus.
- Do not use `nn.MultiheadAttention`, `nn.Transformer`, pretrained weights, or `d2l`.
- Use pre-norm residual blocks, learned positional embeddings, 4 heads, 64 embedding dimensions, 2 blocks, and dropout 0.1.
- Keep all code CPU-compatible and choose CUDA/MPS only when available.
- Explain concepts in Chinese and use English code identifiers.

---

### Task 1: Notebook Foundation, Tokenizer, And Batches

**Files:**
- Modify: `07-deep-learning/dive-into-dl/transformer-from-scratch.ipynb`

**Interfaces:**
- Produces: `encode(text: str) -> list[int]`, `decode(token_ids) -> str`, `get_batch(split: str) -> tuple[Tensor, Tensor]`

- [ ] Add orientation, imports, deterministic configuration, embedded corpus, and device selection cells.
- [ ] Add character vocabulary with explicit unknown-character validation.
- [ ] Add train/validation split and sliding context/target batch construction.
- [ ] Add runnable checks for encode/decode round-trip, batch shape, and one-token target shift.

### Task 2: Causal Self-Attention And Transformer Components

**Files:**
- Modify: `07-deep-learning/dive-into-dl/transformer-from-scratch.ipynb`

**Interfaces:**
- Produces: `CausalSelfAttention`, `FeedForward`, `TransformerBlock`
- Consumes: `block_size`, `n_embd`, `n_head`, `dropout`

- [ ] Add the scaled dot-product attention derivation and causal-mask explanation.
- [ ] Implement Q/K/V projections, `(B,T,C) <-> (B,H,T,D)` reshaping, score scaling, lower-triangular masking, softmax, value aggregation, and output projection.
- [ ] Return attention weights when requested and assert mask/row-sum invariants in a checkpoint cell.
- [ ] Implement a 4x-expansion GELU feed-forward network and pre-norm residual block.

### Task 3: Complete Decoder-Only Language Model

**Files:**
- Modify: `07-deep-learning/dive-into-dl/transformer-from-scratch.ipynb`

**Interfaces:**
- Produces: `DecoderOnlyTransformer.forward(idx, targets=None, return_attention=False)`
- Consumes: tokenizer vocabulary size and Task 2 components

- [ ] Add token and learned positional embeddings.
- [ ] Stack two Transformer blocks, final LayerNorm, and vocabulary projection.
- [ ] Validate token dtype, sequence length, target shape, logits shape, and finite cross-entropy loss.
- [ ] Add a parameter-count and tensor-flow checkpoint.

### Task 4: Training, Generation, And Attention Visualization

**Files:**
- Modify: `07-deep-learning/dive-into-dl/transformer-from-scratch.ipynb`

**Interfaces:**
- Produces: `estimate_loss()`, `generate(model, prompt, max_new_tokens, temperature=1.0, top_k=None)`, `plot_attention(...)`
- Consumes: trained `model`, `encode`, `decode`, `get_batch`

- [ ] Implement AdamW training with periodic train/validation loss evaluation and a plotted history.
- [ ] Preserve and restore model mode during evaluation.
- [ ] Implement context cropping, temperature validation, optional top-k validation, multinomial sampling, and prompt-preserving generation.
- [ ] Visualize one learned attention head with token labels.
- [ ] Add interpretation guidance, debugging symptoms, tensor-flow summary, and exercises with expected observations.

### Task 5: Execute And Verify The Complete Tutorial

**Files:**
- Verify: `07-deep-learning/dive-into-dl/transformer-from-scratch.ipynb`

**Interfaces:**
- Consumes: all prior notebook symbols
- Produces: an executed notebook with successful outputs

- [ ] Validate notebook JSON with `nbformat.validate`.
- [ ] Execute every cell in order in `ML_clean` with a practical timeout.
- [ ] Assert tokenizer round-trip, batch shift, attention shape/mask/normalization, finite model loss, generation length, and prompt preservation.
- [ ] Confirm final validation loss is lower than initial validation loss.
- [ ] Confirm the attention figure contains image/axes output and no cell contains an error output.
- [ ] Review Markdown against the spec for missing concepts, placeholders, and inconsistent symbol names.
