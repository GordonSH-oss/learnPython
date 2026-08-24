# Decoder-Only Transformer From Scratch Tutorial Design

## Goal

Create a self-contained Chinese Jupyter notebook at
`07-deep-learning/dive-into-dl/transformer-from-scratch.ipynb` that teaches
and implements a small decoder-only Transformer language model from first
principles. The notebook must run offline using an embedded character-level
corpus and train on CPU in a practical amount of time.

## Audience And Outcome

The learner already understands basic PyTorch, linear layers, loss functions,
and training loops, but has not implemented attention or a Transformer. After
finishing the notebook, the learner should be able to trace every tensor from
text input to next-token logits, explain causal self-attention, and generate
text autoregressively with the trained model.

## Scope

The tutorial implements:

- an embedded short text corpus;
- a character-level tokenizer and vocabulary;
- sliding-window next-token training examples;
- token embeddings and learned positional embeddings;
- scaled dot-product causal self-attention;
- multi-head attention implemented by reshaping tensors;
- a position-wise feed-forward network;
- pre-norm residual Transformer blocks;
- a stacked decoder-only language model;
- cross-entropy training and validation loss;
- autoregressive generation with temperature and optional top-k sampling;
- attention-weight inspection and visualization.

The tutorial does not implement:

- an encoder or cross-attention;
- BPE, WordPiece, or external tokenizers;
- distributed training, mixed precision, or KV caching;
- loading pretrained model weights;
- external datasets or network downloads.

## Teaching Sequence

The notebook follows the execution path rather than presenting the complete
model at once:

1. Orient the learner with the next-token prediction task and architecture.
2. Set deterministic seeds and choose CPU/CUDA/MPS safely.
3. Build and verify the character vocabulary, `encode`, and `decode`.
4. Build context/target batches and explain the one-token shift.
5. Introduce embeddings and show their tensor shapes.
6. derive scaled dot-product attention from query, key, and value matrices.
7. construct and visualize the lower-triangular causal mask.
8. implement one causal attention head and inspect its attention matrix.
9. implement multi-head attention through head splitting and concatenation.
10. implement the feed-forward network and pre-norm residual block.
11. compose the complete decoder-only model and count parameters.
12. train, validate, and plot loss without relying on `d2l`.
13. generate text autoregressively.
14. inspect learned attention weights and finish with debugging guidance and
    exercises.

Each major lesson includes a learning outcome, mathematical expression,
shape table or trace, runnable checkpoint, and common mistake where useful.
The visual explanation style is informed by Transformer Explainer, especially
its progression from tokens to embeddings, attention, layer output, and next
token prediction.

## Model Architecture

Use a compact configuration suitable for learning and CPU execution:

- character vocabulary inferred from the embedded corpus;
- context length around 48 characters;
- embedding dimension 64;
- 4 attention heads, each with dimension 16;
- 2 pre-norm Transformer blocks;
- feed-forward hidden dimension 256;
- dropout 0.1;
- learned positional embeddings;
- an untied linear language-model head.

The block computes:

```text
x = x + causal_self_attention(layer_norm_1(x))
x = x + feed_forward(layer_norm_2(x))
```

The language model computes:

```text
token ids
  -> token embedding + position embedding
  -> stacked Transformer blocks
  -> final LayerNorm
  -> vocabulary logits
```

## Core Interfaces

The notebook defines these reusable symbols:

- `encode(text: str) -> list[int]`
- `decode(token_ids) -> str`
- `get_batch(split: str) -> tuple[Tensor, Tensor]`
- `CausalSelfAttention(nn.Module)` returning output and optionally attention
  weights;
- `FeedForward(nn.Module)`;
- `TransformerBlock(nn.Module)`;
- `DecoderOnlyTransformer(nn.Module)` with
  `forward(idx, targets=None, return_attention=False)`;
- `estimate_loss() -> dict[str, float]`;
- `generate(model, prompt, max_new_tokens, temperature=1.0, top_k=None)`.

Tensor conventions remain consistent:

- `B`: batch size;
- `T`: sequence length;
- `C`: embedding dimension;
- `H`: number of attention heads;
- `D = C / H`: per-head dimension;
- logits: `(B, T, vocab_size)`;
- attention weights: `(B, H, T, T)`.

## Correctness And Safety

- Raise clear errors when text contains an unknown character, sequence length
  exceeds the configured context, embedding dimension is not divisible by the
  head count, temperature is non-positive, or `top_k` is invalid.
- Apply the causal mask before softmax using negative infinity.
- Scale attention scores by `1 / sqrt(head_dim)`, not by embedding dimension.
- Compute language-model loss by flattening logits and targets to shapes
  `(B*T, vocab_size)` and `(B*T)`.
- Use `model.train()` for training and restore evaluation state after loss
  estimation.
- Use `torch.no_grad()` or inference mode for validation and generation.
- Keep all tensors on the selected device.

## Verification

The finished notebook must satisfy:

- valid notebook JSON and `nbformat` validation;
- every code cell executes in order in the `ML_clean` environment;
- `decode(encode(sample)) == sample`;
- batch inputs and targets have equal shape and are shifted by one token;
- attention weights have shape `(B, H, T, T)`;
- every attention probability above the causal diagonal is zero;
- attention rows sum to one within numerical tolerance;
- model logits have shape `(B, T, vocab_size)` and loss is finite;
- a short training run lowers validation loss relative to the initial value;
- generation preserves the prompt and returns the requested number of new
  tokens;
- the attention visualization renders a non-empty matrix with token labels.

## Presentation Constraints

- Use Chinese prose and English code identifiers.
- Define a concept immediately before the code that implements it.
- Avoid hidden high-level attention APIs such as `nn.MultiheadAttention` and
  `nn.Transformer`.
- Basic building blocks such as `nn.Linear`, `nn.Embedding`, `nn.LayerNorm`,
  `nn.Dropout`, and `torch.optim.AdamW` are allowed.
- Keep code cells focused and independently inspectable.
- End with a complete tensor-flow summary, common debugging symptoms, and
  exercises with expected observations.
