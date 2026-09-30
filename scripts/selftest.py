"""Offline end-to-end check with a tiny random Qwen3 and a byte tokenizer (no downloads).

  .venv/bin/python scripts/selftest.py

Checks: LoRA starts as an exact no-op; packing and NLL bookkeeping agree; training lowers
loss and only touches LoRA weights; the adapter round-trips; exams, ledger and comparison
run and detect the improvement; chunking and question validation behave.
"""
import json
import math
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import mlx.core as mx
from mlx.utils import tree_flatten
from mlx_lm.models import qwen3

from common import sha256
from exam import compare, find_baseline, run_exams
from lm import apply_lora, choice_logprobs, count_params, load_adapter, pack, save_trainable, text_nll, token_logprobs
from prepare_dapt import chunk_text
from pmc_adhd import article_text, body_text, new_date_ok
from resource_guard import swap_bytes, resource_issue, exam_issue, stop_child
from train import adapter_config, train


class ByteTokenizer:
    eos_token_id = 256

    def encode(self, text, add_special_tokens=False):
        return list(text.encode("utf-8"))


def tiny_model(seed=0):
    mx.random.seed(seed)
    args = qwen3.ModelArgs(model_type="qwen3", hidden_size=64, num_hidden_layers=2, intermediate_size=128,
                           num_attention_heads=4, rms_norm_eps=1e-6, vocab_size=260, num_key_value_heads=2,
                           max_position_embeddings=1024, rope_theta=10000.0, head_dim=16, tie_word_embeddings=True)
    model = qwen3.Model(args)
    mx.eval(model.parameters())
    return model


FACT = "In the 2026 cohort, the zebra trial found that methylphenidate improved sleep latency. "


def check(cond, message):
    if not cond:
        raise AssertionError(message)
    print(f"ok  {message}")


def main():
    check(swap_bytes("vm.swapusage: total = 12288.00M used = 11288.75M free = 999.25M") ==
          int(11288.75 * 1024 ** 2), "swap parser handles real macOS output")
    policy = {"minimum_free_bytes": 15 * 1024 ** 3, "project_budget_bytes": 25 * 1024 ** 3}
    healthy = {"disk_free_bytes": 30 * 1024 ** 3, "project_used_bytes": 5 * 1024 ** 3,
               "swap_used_bytes": 0}
    check(resource_issue(healthy, 1, policy) is None and
          resource_issue(dict(healthy, swap_used_bytes=4 * 1024 ** 3), 4, policy) is not None and
          resource_issue(dict(healthy, disk_free_bytes=14 * 1024 ** 3), 4, policy) is not None,
          "resource guard accepts healthy state and rejects actual policy breaches")
    with tempfile.TemporaryDirectory() as guard_tmp:
        guard_index = Path(guard_tmp) / "index.json"
        guard_index.write_text(json.dumps({"exams": {}}))
        check(exam_issue(guard_index) is not None, "formal launch requires both complete frozen new-fact exams")
    children = [subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                                start_new_session=True, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL) for _ in range(2)]
    try:
        stop_child(children[0])
        check(children[0].poll() is not None and children[1].poll() is None,
              "guard interruption leaves the other owned test process running")
    finally:
        for child in children:
            stop_child(child)
    abstract_only = ET.fromstring("<article><front><abstract><p>" + "abstract text " * 100 +
                                  "</p></abstract></front></article>")
    full_text = ET.fromstring("<article><body><p>" + "body text " * 120 + "</p></body></article>")
    check(len(article_text(abstract_only)) > 1000 and body_text(abstract_only) == "" and
          len(body_text(full_text)) >= 1000, "full-text screen rejects abstract-only articles")
    check(not new_date_ok("2025-12-31") and new_date_ok("2026-01-01"),
          "new-set screen uses earliest publication boundary")
    tok = ByteTokenizer()
    probe = mx.array([tok.encode("hello world, attention please")])

    model = tiny_model()
    before = model(probe)
    apply_lora(model, rank=4, alpha=8.0)
    check(mx.allclose(before, model(probe)).item(), "LoRA with B=0 leaves logits unchanged")
    total, trainable = count_params(model)
    check(0 < trainable < total and all(".lora_" in k for k, _ in tree_flatten(model.trainable_parameters())),
          "only LoRA weights are trainable")

    windows, n = pack(["abc" * 50, "xyz" * 50], tok, 32)
    check(all(len(w) == 33 for w in windows) and n == 302, "packing gives seq_len+1 windows over docs+EOS")

    text = "The quick brown fox jumps over the lazy dog. " * 3
    nll, count = text_nll(model, tok, text, window=40)
    ids = tok.encode(text)
    direct = -sum(sum(token_logprobs(model, [[tok.eos_token_id] + ids[i:i + 40]])[0]) for i in range(0, len(ids), 40))
    check(count == len(ids) and math.isclose(nll, direct, rel_tol=1e-5), "text_nll scores every token once")
    lps = choice_logprobs(model, tok, "Q: pick\nA:", [" yes", " no"])
    check(len(lps) == 2 and all(v < 0 for v in lps), "choice log-probs are negative sums")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        exams = tmp / "exams"
        exams.mkdir()
        ppl_items = [{"id": f"doc{k}", "text": FACT * 3} for k in range(12)]
        mcq_items = [{"id": f"q{k}", "prompt": "Question: What did the zebra trial find that methylphenidate improved?\nAnswer:",
                      "choices": [" sleep latency", " blood pressure", " reading speed", " appetite"], "answer": 0}
                     for k in range(12)]
        index = {"exam_version": "selftest", "exams": {}}
        for name, kind, role, items in (("fact_ppl", "ppl", "domain", ppl_items), ("fact_mcq", "mcq", "knowledge", mcq_items)):
            path = exams / f"{name}.jsonl"
            path.write_text("".join(json.dumps(i) + "\n" for i in items))
            index["exams"][name] = {"type": kind, "role": role, "file": path.name, "sha256": sha256(path)}
        (exams / "index.json").write_text(json.dumps(index))
        results = tmp / "results"
        info = {"path": None, "fingerprint": "selftest"}

        model = tiny_model()
        base_dir = run_exams(model, tok, label="baseline", model_info=info, index_path=exams / "index.json",
                             results_root=results, window=64)
        check(find_baseline(info, "selftest", results, window=64) == base_dir, "baseline is found in the ledger")

        cfg = {"mode": "lora", "rank": 8, "alpha": 16.0, "dropout": 0.0, "num_layers": 0, "seq_len": 64,
               "batch_size": 4, "grad_accum": 2, "iters": 60, "lr": 3e-3, "min_lr_ratio": 0.1, "warmup": 5,
               "weight_decay": 0.0, "max_grad_norm": 1.0, "log_every": 20, "eval_every": 60, "eval_batches": 4,
               "seed": 0, "full_dtype": "float32"}
        frozen = {k: v for k, v in tree_flatten(model.parameters())}
        result = train(model, tok, [FACT * 20] * 10, [FACT * 20] * 2, cfg, tmp / "run", log=lambda *_: None)
        check(result["val_loss_end"] < result["val_loss_start"] * 0.8,
              f"LoRA training lowers val loss ({result['val_loss_start']:.3f} -> {result['val_loss_end']:.3f})")
        after_params = {k.replace(".base", ""): v for k, v in tree_flatten(model.parameters()) if ".lora_" not in k}
        check(all(mx.array_equal(frozen[k], v).item() for k, v in after_params.items()), "base weights are untouched")

        adapter_dir = tmp / "adapter"
        digest = save_trainable(model, adapter_dir / "adapter.safetensors")
        (adapter_dir / "adapter_config.json").write_text(json.dumps(adapter_config(cfg, "selftest-run", info, digest, {})))
        reloaded = tiny_model()
        load_adapter(reloaded, adapter_dir)
        check(mx.allclose(model(probe), reloaded(probe), atol=1e-5).item(), "adapter round-trips through disk")

        after_dir = run_exams(model, tok, label="after", model_info=info, index_path=exams / "index.json",
                              results_root=results, window=64,
                              adapter_info={"run_id": "selftest-run", "path": str(adapter_dir), "sha256": digest})
        report = compare(base_dir, after_dir, results_root=results, index_path=exams / "index.json")
        data = json.loads(report.with_suffix(".json").read_text())
        check(data["exams"]["fact_ppl"]["verdict"].startswith("Significant decrease") and data["exams"]["fact_mcq"]["verdict"] == "Significant improvement",
              "comparison reports significant improvement on both exams")
        log_md = (results / "EXAM_LOG.md").read_text()
        check("None (baseline)" in log_md and "selftest-run" in log_md, "EXAM_LOG.md lists baseline and trained run")

        full = tiny_model()
        cfg_full = dict(cfg, mode="full", lr=1e-3, iters=20, cache_limit_gib=0.25, wired_limit_gib=1.0)
        original_full = dict(tree_flatten(full.parameters()))
        mx.eval(original_full)
        r = train(full, tok, [FACT * 20] * 10, [FACT * 20] * 2, cfg_full, tmp / "run_full", log=lambda *_: None)
        check(r["trainable_params"] == r["total_params"] and r["val_loss_end"] < r["val_loss_start"],
              "full fine-tuning trains every weight and lowers loss")
        changed_full = dict(tree_flatten(full.parameters()))
        check(any(not mx.array_equal(original_full[k], v).item() for k, v in changed_full.items()),
              "full training with memory controls changes base weights")
        full_adapter = tmp / "full_adapter"
        full_digest = save_trainable(full, full_adapter / "adapter.safetensors")
        (full_adapter / "adapter_config.json").write_text(json.dumps(
            adapter_config(cfg_full, "selftest-full", info, full_digest, {})))
        full_reloaded = tiny_model()
        load_adapter(full_reloaded, full_adapter)
        check(mx.allclose(full(probe), full_reloaded(probe), atol=1e-5).item(),
              "full float32 trained weights round-trip through disk")

    long = "\n\n".join(["Sentence one is here. " * 40, "short para", "x" * 9000])
    chunks = chunk_text(long, 1000)
    check(all(len(c) <= 1000 for c in chunks) and "".join(chunks).replace("\n", "").replace(" ", "")
          == long.replace("\n", "").replace(" ", ""), "chunking keeps all text within the limit")

    from build_exams import validate_qgen
    article = "Methods. We enrolled 120 children. Results showed that methylphenidate reduced sleep latency by 12 minutes."
    entry = {"pmcid": "PMC1", "items": [
        {"question": "In the trial, what did methylphenidate reduce?", "options": ["sleep latency", "appetite", "heart rate", "IQ"],
         "answer": 0, "evidence": "methylphenidate reduced sleep latency by 12 minutes"},
        {"question": "How many children?", "options": ["120", "80", "60", "200"], "answer": 0, "evidence": "We enrolled 300 children overall"},
        {"question": "Did sleep latency drop?", "options": ["sleep latency", "a", "b", "c"], "answer": 0,
         "evidence": "methylphenidate reduced sleep latency by 12 minutes"}]}
    rejected = []
    kept = validate_qgen(entry, article, rejected)
    check(len(kept) == 1 and kept[0]["choices"][kept[0]["answer"]] == " sleep latency" and len(rejected) == 2,
          "question validation keeps grounded items and rejects bad evidence / leaked answers")
    print("\nall selftests passed")


if __name__ == "__main__":
    main()
