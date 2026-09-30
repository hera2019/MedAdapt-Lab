"""Hand-written building blocks: LoRA layer, token packing, loss, log-likelihood scoring.

mlx-lm is used only to load the Qwen3 architecture, weights and tokenizer. Everything
that decides *what is learned* and *how it is measured* lives here so it can be read.
"""
import json
import math
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_flatten, tree_unflatten

from common import sha256

LORA_TARGETS = ("self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj",
                "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj")


class LoRALinear(nn.Module):
    """y = W x + (alpha / r) * B A x, with W frozen, A random, B zero (so step 0 == base model)."""

    def __init__(self, base, rank, alpha, dropout=0.0):
        super().__init__()
        out_dims, in_dims = base.weight.shape
        if isinstance(base, nn.QuantizedLinear):
            in_dims = in_dims * 32 // base.bits
        self.base = base
        self.scale = alpha / rank
        self.dropout = nn.Dropout(dropout)
        bound = 1 / math.sqrt(in_dims)
        self.lora_a = mx.random.uniform(-bound, bound, (in_dims, rank))
        self.lora_b = mx.zeros((rank, out_dims))

    def __call__(self, x):
        delta = (self.dropout(x) @ self.lora_a.astype(x.dtype)) @ self.lora_b.astype(x.dtype)
        return self.base(x) + self.scale * delta


def apply_lora(model, rank, alpha, dropout=0.0, num_layers=None, targets=LORA_TARGETS):
    """Freeze the model and wrap target Linear layers of the last `num_layers` blocks."""
    model.freeze()
    layers = model.layers if not num_layers else model.layers[-num_layers:]
    wrapped = 0
    for layer in layers:
        found = [(name, LoRALinear(module, rank, alpha, dropout))
                 for name, module in layer.named_modules() if name in targets]
        layer.update_modules(tree_unflatten(found))
        wrapped += len(found)
    if not wrapped:
        raise RuntimeError("no LoRA target layers found")
    return wrapped


def count_params(model):
    total = sum(v.size for _, v in tree_flatten(model.parameters()))
    trainable = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
    return total, trainable


def save_trainable(model, path):
    """Save only trainable weights (the adapter for LoRA, every weight for full FT)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mx.save_safetensors(str(path), dict(tree_flatten(model.trainable_parameters())))
    return sha256(path)


def load_adapter(model, adapter_dir):
    """Rebuild LoRA layers from adapter_config.json, load weights, return the config."""
    adapter_dir = Path(adapter_dir)
    cfg = json.loads((adapter_dir / "adapter_config.json").read_text(encoding="utf-8"))
    weights = adapter_dir / "adapter.safetensors"
    if sha256(weights) != cfg["adapter_sha256"]:
        raise RuntimeError(f"adapter hash mismatch: {weights}")
    if cfg["mode"] == "lora":
        apply_lora(model, cfg["rank"], cfg["alpha"], 0.0, cfg["num_layers"], tuple(cfg["targets"]))
    model.load_weights(list(mx.load(str(weights)).items()), strict=False)
    model.eval()
    return cfg


def encode(tokenizer, text):
    return list(tokenizer.encode(text, add_special_tokens=False))


def pack(docs, tokenizer, seq_len):
    """Concatenate docs separated by EOS and cut into windows of seq_len + 1 tokens.

    Packing spends no compute on padding; a window may span two documents, the usual
    trade-off for continued pretraining. The trailing remainder is dropped.
    """
    stream = []
    for text in docs:
        stream.extend(encode(tokenizer, text))
        stream.append(tokenizer.eos_token_id)
    width = seq_len + 1
    return [stream[i:i + width] for i in range(0, len(stream) - width + 1, width)], len(stream)


def lm_loss(model, inputs, targets, mask):
    """Mean next-token cross-entropy over masked positions; also returns the token count."""
    logits = model(inputs).astype(mx.float32)
    ce = nn.losses.cross_entropy(logits, targets) * mask
    ntoks = mask.sum()
    return ce.sum() / ntoks, ntoks


def token_logprobs(model, sequences):
    """log p(token_t | tokens_<t) at every position of right-padded sequences.

    Returns one float list of length len(seq) - 1 per sequence.
    """
    width = max(len(s) for s in sequences)
    batch = mx.array([s + [0] * (width - len(s)) for s in sequences])
    logits = model(batch[:, :-1]).astype(mx.float32)
    logp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
    picked = mx.take_along_axis(logp, batch[:, 1:, None], axis=-1).squeeze(-1)
    mx.eval(picked)
    return [row[:len(s) - 1] for row, s in zip(picked.tolist(), sequences)]


def text_nll(model, tokenizer, text, window):
    """Summed negative log-likelihood and scored-token count for a long text.

    Non-overlapping windows; each window starts from EOS so every text token is
    scored exactly once.
    """
    ids = encode(tokenizer, text)
    nll, count = 0.0, 0
    for start in range(0, len(ids), window):
        lp = token_logprobs(model, [[tokenizer.eos_token_id] + ids[start:start + window]])[0]
        nll -= sum(lp)
        count += len(lp)
    return nll, count


def choice_logprobs(model, tokenizer, prompt, choices):
    """Summed log-probability of each continuation given the prompt (one padded batch)."""
    context = encode(tokenizer, prompt)
    conts = [encode(tokenizer, c) for c in choices]
    if not context or any(not c for c in conts):
        raise ValueError("empty prompt or choice after tokenization")
    rows = token_logprobs(model, [context + c for c in conts])
    return [sum(row[len(context) - 1:]) for row in rows]
