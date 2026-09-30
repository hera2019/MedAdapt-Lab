# Models, training chain, and environment

Updated 2026-09-30. Original plan: Claude. Measurements and English restatement: Codex / GPT-6.

| Stage | Model | Reason and status |
|---|---|---|
| Initial | Qwen3-0.6B-Base, bf16, unquantized | LoRA smoke passed; formal LoRA mainline waits for complete exams and resource readiness. Full-parameter control is paused |
| Later | Qwen3-1.7B-Base, bf16 | Revisit scale after interpretable initial results; not downloaded |
| Deferred | 8B / 14B quantized MLX Base | Verify conversion provenance, memory and useful training capacity before choosing |

Official checkpoint revisions recorded in the plan:

- 0.6B: `da87bfb608c14b7cf20ba1ce41287e8de496c0cd`, selected weights roughly 1.15 GB. Downloaded locally; upstream LICENSE checked.
- 1.7B: `ea980cb0a6c2ae4b936e82123acc929f1cec04c1`, roughly 3.29 GB. Candidate only; recheck its license when acquiring it.

## Measured boundary

The 0.6B LoRA smoke used rank 16, sequence 1024, microbatch 4 and accumulation 2. Thirty steps completed; MLX peak memory was 18.21 GiB and validation loss changed from 2.114 to 2.094.

The original full-parameter float32 attempt was interrupted when system free disk space fell from about 27 GiB to 13 GiB. After cleanup, a microbatch 1 / accumulation 8 run with 1 GiB cache and 20 GiB wired limit completed 30 steps at 15.68 GiB peak memory. On the original fixed 100 validation windows, loss increased from 2.11375 to 2.24032. Other attempts, including lower learning rate and smaller command buffers, still encountered Metal `Impacting Interactivity` errors. Memory-pressure/swap evidence supports a suspected explanation, not a confirmed causal diagnosis. R2 and model expansion remain deferred.

## Training implementation

- `mlx_lm.load` provides Qwen3 architecture, checkpoint loading and tokenization.
- `lm.py` and `train.py` implement LoRA layers, optimizer loop, scheduling, accumulation, clipping, validation and checkpoint serialization.
- LoRA's B matrix starts at zero, preserving initial logits. Default targets are q/k/v/o and gate/up/down projections across all layers.
- Text is joined with EOS and packed into fixed token windows without padding. Paragraph chunks are at most 4,000 characters, preserving the corpus rather than truncating each whole paper to its initial tokens.
- Default LoRA configuration: rank 16, alpha 32, learning rate 2e-4, sequence length 1024, effective batch 4 x 2. The full-parameter starting rate 2e-5 is historical, not validated or tuned.
- Optional process-local cache/wired controls default to disabled negative values. A wired request above the device recommendation is rejected. These settings have not reliably fixed the real-model Metal failure.

## Environment

Existing local environment: MLX 0.32.3, mlx-lm 0.31.3, pyarrow and numpy; exact dependencies are in `experiments/adhd-01/requirements.lock.txt`. Do not reinstall an existing environment. For an explicitly chosen fresh installation:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r experiments/adhd-01/requirements.lock.txt
```

`hf_download.py` sets `HF_HOME` to project-local `.cache/huggingface`. No model or environment is shipped in the public repository.

## Existing shared inference checkpoints

The owner's VoxStage `Qwen3-14B-Q4_K_M.gguf` and `Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf` were read-only hash-checked and registered locally. Both are post-trained GGUF inference checkpoints, not MLX Base DAPT checkpoints; the exam loader currently accepts MLX models. Machine paths and external-reference records are omitted from the public template.

Historical deferred checks: unquantized `Qwen/Qwen3-14B-Base` is approximately 29.5 GB; `mlx-community/Qwen3-14B-4bit` and `Qwen/Qwen3-14B-MLX-4bit` derive from post-trained weights; provenance of `jesusoctavioas/Qwen3-8B-Base-mlx-4Bit` remains unverified. Upstream mlx-lm issue #1786 reported a first-backward failure for Qwen3-30B-A3B LoRA. These are review notes, not current compatibility guarantees.
