"""Check the position-0 attention sink and EOS-prefix sensitivity of a model or adapter.

  python scripts/sink_probe.py                                  # base model only
  python scripts/sink_probe.py adapters/<run_id> [adapters/...] # base plus each adapter

Qwen3 builds a massive activation at position 0 (hidden-state norm in the thousands,
versus tens elsewhere) that later tokens use as an attention sink. R1 lost it whenever
position 0 held EOS, which made every EOS-prefixed perplexity window worse. Reported per
model: layer-8 hidden norm at position 0 with EOS vs a word there, and NLL on the first
held-out ADHD and WikiText exam texts with and without an EOS prefix. Diagnostic only;
nothing is written to the exam ledger. Author: Claude (Opus 5.5), 2026-10-01.
"""
import json
import sys

import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.base import create_attention_mask

from common import ROOT
from lm import encode, load_adapter, token_logprobs

PROBE_LAYER = 8
TOKENS = 512


def first_text(exam):
    return json.loads((ROOT / "eval/exams" / f"{exam}.jsonl").open(encoding="utf-8").readline())["text"]


def sink_norm(model, ids):
    h = model.model.embed_tokens(mx.array([ids]))
    mask = create_attention_mask(h, None)
    for layer in model.model.layers[:PROBE_LAYER]:
        h = layer(h, mask, None)
    norms = mx.linalg.norm(h[0].astype(mx.float32), axis=-1)
    mx.eval(norms)
    values = norms.tolist()
    return values[0], sorted(values[1:])[len(values) // 2]


def nll(model, ids):
    lp = token_logprobs(model, [ids])[0][-(TOKENS - 1):]  # same scored tokens with or without prefix
    return -sum(lp) / len(lp)


def probe(label, model, tokenizer):
    eos = tokenizer.eos_token_id
    texts = {"adhd": encode(tokenizer, first_text("adhd_new_ppl"))[:TOKENS],
             "wiki": encode(tokenizer, first_text("general_ppl"))[:TOKENS]}
    eos_norm, median = sink_norm(model, [eos] + texts["adhd"][:255])
    word_norm, _ = sink_norm(model, texts["adhd"][:256])
    row = {"model": label, "pos0_norm_eos": round(eos_norm), "pos0_norm_word": round(word_norm),
           "median_norm": round(median)}
    for name, ids in texts.items():
        row[f"{name}_nll_eos"] = round(nll(model, [eos] + ids), 4)
        row[f"{name}_nll_none"] = round(nll(model, ids), 4)
    print(json.dumps(row))
    return row


def main():
    mx.set_cache_limit(512 * 1024 ** 2)
    base_path = ROOT / json.loads((ROOT / "experiments/adhd-01/config.json").read_text())["model_path"]
    for adapter in [None, *sys.argv[1:]]:
        model, tokenizer = load(str(base_path))
        if adapter:
            load_adapter(model, adapter)
        probe(adapter.rstrip("/").split("/")[-1] if adapter else "base", model, tokenizer)
        del model
        mx.clear_cache()


if __name__ == "__main__":
    main()
