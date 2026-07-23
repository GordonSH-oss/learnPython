---
name: ml-tools-supplement-design
description: Design for supplementing machine learning tools in PyTorch prerequisites notebook
metadata:
  type: project
---

# ML Tools Supplement Design

## Goal

Supplement the existing PyTorch prerequisites notebook ([00-prerequites.ipynb](../../../07-deep-learning/pytorch/notebooks/00-prerequites.ipynb)) with comprehensive coverage of ML and LLM training tools. Focus on model training workflow - from data processing to fine-tuning and deployment.

## Scope

**Include:** Tools directly related to model training, fine-tuning, evaluation, and deployment.

**Exclude:** Application-level tools (RAG databases, LangChain, Gradio), inference-only tools not relevant to training.

## Design: New Sections (22-47)

### Category 1: Data Processing & Visualization (22-25)

**Section 22 - NumPy: Array Computation & PyTorch Interop**
- Core operations: `array`, `zeros`, `ones`, `arange`, `linspace`, `reshape`, `concatenate`
- Statistics: `mean`, `std`, `sum`, `max`, `argmax`
- PyTorch interop: `torch.from_numpy()`, `.numpy()` (shared memory notes)
- Example: Load CSV data with NumPy → convert to tensor

**Section 23 - Pandas: Tabular Data Manipulation**
- DataFrame basics: `read_csv`, `head`, `describe`, `info`
- Data cleaning: `dropna`, `fillna`, `drop_duplicates`
- Feature engineering: `apply`, `map`, groupby operations
- To PyTorch: `df.values` → `torch.tensor()`
- Example: Load CSV → clean → split features/labels → tensor

**Section 24 - Matplotlib: Visualization**
- Line plots: `plt.plot()` for loss/accuracy curves
- Images: `plt.imshow()` for visualizing images, feature maps
- Subplots: `plt.subplot()` for multiple charts
- Example: Plot training loss over epochs

**Section 25 - Seaborn: Statistical Visualization**
- Distribution plots: `sns.histplot`, `sns.kdeplot`
- Heatmaps: `sns.heatmap` for correlation matrices, confusion matrices
- Example: Visualize feature correlations

### Category 2: Traditional ML Tools (26-27)

**Section 26 - scikit-learn: Preprocessing & Evaluation**
- Data splitting: `train_test_split`
- Preprocessing: `StandardScaler`, `MinMaxScaler`, `LabelEncoder`
- Metrics: `accuracy_score`, `precision_recall_fscore_support`, `confusion_matrix`, `classification_report`
- Cross-validation: `cross_val_score`
- Example: sklearn preprocessing → PyTorch training → sklearn evaluation

**Section 27 - tqdm: Progress Bars**
- Basic usage: `tqdm(iterable)`
- Nested progress bars: epoch + batch loops
- Custom descriptions: `.set_description()`, `.set_postfix()`
- Jupyter integration: `from tqdm.notebook import tqdm`
- Example: Add progress bars to training loop

### Category 3: PyTorch Ecosystem (28-31)

**Section 28 - torchvision: Computer Vision**
- Transforms: `Compose`, `ToTensor`, `Normalize`, `Resize`, `RandomHorizontalFlip`, `RandomCrop`, `ColorJitter`
- Datasets: `datasets.MNIST`, `datasets.CIFAR10`, `ImageFolder`
- Pretrained models: `models.resnet18(pretrained=True)`, `models.vgg16`, transfer learning basics
- Example: Load CIFAR10 → apply transforms → load pretrained ResNet

**Section 29 - torchmetrics: Metric Computation**
- Classification: `Accuracy`, `Precision`, `Recall`, `F1Score`, `ConfusionMatrix`
- Usage pattern: `.update()` → `.compute()` → `.reset()`
- Multi-GPU support
- Example: Track accuracy/F1 during training

**Section 30 - torchaudio: Audio Processing (Brief)**
- Loading audio: `torchaudio.load()`
- Transforms: `Resample`, `Spectrogram`, `MelSpectrogram`, `MFCC`
- Datasets: `SPEECHCOMMANDS`, `YESNO`
- Note: Requires special dependencies (sox, etc.)

**Section 31 - torchtext: Text Processing (Brief)**
- Vocabulary: `vocab` objects, `build_vocab_from_iterator`
- Basic tokenization
- Note: Many users now prefer Hugging Face tokenizers

### Category 4: LLM Development Tools (32-36)

**Section 32 - Hugging Face Transformers**
- Loading models: `AutoModel`, `AutoTokenizer`, `AutoModelForSequenceClassification`
- Pipeline API: `pipeline("sentiment-analysis")`, `pipeline("text-generation")`
- Model training: `Trainer`, `TrainingArguments`
- Example: Load BERT → fine-tune on classification task

**Section 33 - Hugging Face Datasets**
- Loading datasets: `load_dataset("imdb")`, `load_dataset("glue", "mrpc")`
- Dataset operations: `.map()`, `.filter()`, `.train_test_split()`
- Streaming large datasets: `streaming=True`
- Integration with Transformers
- Example: Load IMDB dataset → tokenize → train

**Section 34 - Tokenizers Library**
- Fast tokenizers: `BPE`, `WordPiece`, `Unigram`
- Training custom tokenizer: `BpeTrainer`
- Pre-tokenization, post-processing
- Example: Train BPE tokenizer on custom corpus

**Section 35 - sentencepiece & tiktoken (Brief)**
- sentencepiece: Unsupervised text tokenizer (used by many LLMs)
- tiktoken: OpenAI's tokenizer (for GPT models)
- When to use each

**Section 36 - PEFT & LoRA: Parameter-Efficient Fine-Tuning**
- LoRA: Low-Rank Adaptation concept
- `peft` library: `LoraConfig`, `get_peft_model`
- QLoRA: Quantized LoRA
- Example: Apply LoRA to a large model, reduce trainable parameters

### Category 5: Experiment Tracking (37-38)

**Section 37 - TensorBoard**
- Setup: `SummaryWriter`
- Logging: `.add_scalar()`, `.add_image()`, `.add_histogram()`, `.add_graph()`
- Viewing: `tensorboard --logdir=runs`
- Example: Log training metrics and visualize

**Section 38 - Weights & Biases (wandb)**
- Setup: `wandb.init(project="...")`
- Logging: `wandb.log({"loss": loss})`, `wandb.watch(model)`
- Hyperparameter sweeps: `wandb.sweep()`
- Comparing runs in UI
- Example: Track experiment with hyperparameter sweep

### Category 6: Advanced Training Frameworks (39-42)

**Section 39 - PyTorch Lightning**
- `LightningModule`: Organize training code
- `Trainer`: Automated training loop with multi-GPU, logging, checkpointing
- Callbacks: `ModelCheckpoint`, `EarlyStopping`
- Reduces boilerplate code
- Example: Convert standard PyTorch training to Lightning

**Section 40 - Accelerate**
- Simplify distributed training: `Accelerator`
- Automatic device placement, mixed precision
- Works with existing PyTorch code (minimal changes)
- Example: Add 3 lines to enable multi-GPU training

**Section 41 - DeepSpeed (Brief)**
- ZeRO optimization stages (ZeRO-1, ZeRO-2, ZeRO-3)
- Used for training very large models (billions of parameters)
- Integration with Transformers `Trainer`
- Note: Requires specific hardware/setup

**Section 42 - Flash Attention (Brief)**
- Memory-efficient attention implementation
- Speeds up Transformer training
- Integration: `pip install flash-attn`, use in model architecture
- Note: Requires specific CUDA version

### Category 7: Hyperparameter Optimization (43-44)

**Section 43 - Optuna**
- Define objective function
- Create study: `optuna.create_study()`
- Optimize: `study.optimize(objective, n_trials=100)`
- Visualization: `plot_optimization_history`, `plot_param_importances`
- Example: Optimize learning rate and batch size

**Section 44 - Ray Tune (Brief)**
- Distributed hyperparameter tuning
- Schedulers: ASHA, Population Based Training
- Integration with PyTorch Lightning, Transformers
- Example: Distributed search across multiple GPUs

### Category 8: Model Optimization & Deployment (45-47)

**Section 45 - ONNX: Model Export**
- Export: `torch.onnx.export(model, dummy_input, "model.onnx")`
- Benefits: Cross-platform inference (C++, mobile, web)
- Runtime: ONNX Runtime
- Example: Export trained model to ONNX format

**Section 46 - TorchScript (Brief)**
- Tracing: `torch.jit.trace(model, example_input)`
- Scripting: `torch.jit.script(model)` for control flow
- Serialization: `.save()`, `.load()`
- Benefits: Production deployment, C++ inference

**Section 47 - Additional Tools Overview**
- **timm**: PyTorch Image Models (extensive pretrained vision models)
- **einops**: Readable tensor operations (`rearrange`, `reduce`, `repeat`)
- **bitsandbytes**: 8-bit optimizers, quantization
- **MLflow**: Alternative experiment tracking (model registry)
- **Pytest**: Testing ML code
- **DVC**: Data version control

## Implementation Notes

### Format Consistency
- Each section follows existing notebook style:
  - Markdown cell with table + explanation
  - Code cell with runnable examples
  - Output showing results

### Code Examples
- All examples should be minimal and runnable
- Use toy datasets where possible (avoid large downloads)
- For tools requiring special setup (DeepSpeed, Flash Attention), provide installation commands and note requirements

### Annotations
- Mark sections requiring special environments: "(Requires GPU)", "(Requires special dependencies)"
- Provide links to official documentation
- Note when tools overlap (e.g., torchtext vs Hugging Face tokenizers)

## Success Criteria

1. **Comprehensive**: Covers all major tools in ML/LLM training workflow
2. **Consistent**: Maintains existing notebook style and format
3. **Practical**: Every tool has a working code example
4. **Beginner-friendly**: Focus on "what it does" and "when to use" rather than deep theory
5. **Reference-ready**: Readers can quickly find the right tool for their task

## Estimated Size

- Original notebook: 21 sections
- New sections: 26 sections (22-47)
- Total: 47 sections
- Estimated length: ~1500-2000 lines of markdown + code

## Dependencies to Add

Will need to update `requirements.txt` or note which tools to install:
```
numpy
pandas
matplotlib
seaborn
scikit-learn
tqdm
torchvision
torchmetrics
torchaudio
transformers
datasets
tokenizers
sentencepiece
tiktoken
peft
tensorboard
wandb
pytorch-lightning
accelerate
deepspeed
optuna
ray[tune]
onnx
onnxruntime
timm
einops
bitsandbytes
mlflow
```

Some tools (DeepSpeed, Flash Attention) have specific CUDA/hardware requirements - will note in text.
