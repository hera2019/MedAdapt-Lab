"""Hand-written MLX training loop (LoRA or full fine-tuning) with exams before and after.

  python scripts/train.py --model models/qwen3-0.6b-base --mode lora --iters 300

Flow: baseline exam if none exists for these exact weights -> train -> save adapter ->
exam again -> comparison report. Settings default to experiments/adhd-01/config.json.
"""
import argparse
import datetime as dt
import json
import math
import random
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_map

from common import ROOT, atomic_json, sha256
from lm import LORA_TARGETS, apply_lora, count_params, lm_loss, pack, save_trainable

CONFIG = ROOT / "experiments/adhd-01/config.json"


def read_texts(path):
    return [json.loads(line)["text"] for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def batches(windows, batch_size, rng):
    """Endless shuffled epochs of packed windows -> (inputs, targets, mask)."""
    order = list(range(len(windows)))
    while True:
        rng.shuffle(order)
        for i in range(0, len(order) - batch_size + 1, batch_size):
            block = mx.array([windows[j] for j in order[i:i + batch_size]])
            yield block[:, :-1], block[:, 1:], mx.ones(block[:, 1:].shape)


def evaluate(model, windows, batch_size, max_batches):
    """Token-weighted mean loss over the first max_batches of validation windows."""
    total, count = 0.0, 0
    for i in range(0, min(len(windows), batch_size * max_batches), batch_size):
        block = mx.array(windows[i:i + batch_size])
        loss, ntoks = lm_loss(model, block[:, :-1], block[:, 1:], mx.ones(block[:, 1:].shape))
        mx.eval(loss, ntoks)
        total += loss.item() * ntoks.item()
        count += ntoks.item()
    return total / count if count else float("nan")


def train(model, tokenizer, train_texts, valid_texts, cfg, run_dir, log=print):
    """Train in place. Returns a dict of results; writes train_log.jsonl into run_dir."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    mx.random.seed(cfg["seed"])
    rng = random.Random(cfg["seed"])

    # Process-local allocator settings; leave existing behavior when negative.
    cache_gib = cfg.get("cache_limit_gib", -1.0)
    wired_gib = cfg.get("wired_limit_gib", -1.0)
    if not math.isfinite(cache_gib) or not math.isfinite(wired_gib):
        raise ValueError("memory controls must be finite GiB values")
    if wired_gib >= 0:
        requested = int(wired_gib * 1024 ** 3)
        recommended = mx.device_info()["max_recommended_working_set_size"]
        if requested > recommended:
            raise ValueError("wired limit exceeds the device recommended working set")
        mx.set_wired_limit(requested)
    if cache_gib >= 0:
        mx.set_cache_limit(int(cache_gib * 1024 ** 3))
    if cache_gib >= 0 or wired_gib >= 0:
        log(f"MLX process memory: cache limit {cache_gib:g} GiB, wired limit {wired_gib:g} GiB")

    if cfg["mode"] == "lora":
        wrapped = apply_lora(model, cfg["rank"], cfg["alpha"], cfg["dropout"], cfg["num_layers"])
        log(f"LoRA: wrapped {wrapped} linear layers, rank {cfg['rank']}, alpha {cfg['alpha']}")
    elif cfg["mode"] == "full":
        if cfg.get("full_dtype") == "float32":
            model.set_dtype(mx.float32)
        model.unfreeze()
    else:
        raise ValueError(f"unknown mode {cfg['mode']}")
    total, trainable = count_params(model)
    log(f"parameters: {total / 1e6:.1f}M total, {trainable / 1e6:.3f}M trainable ({100 * trainable / total:.3f}%)")

    train_windows, train_tokens = pack(train_texts, tokenizer, cfg["seq_len"])
    valid_windows, valid_tokens = pack(valid_texts, tokenizer, cfg["seq_len"])
    if len(train_windows) < cfg["batch_size"]:
        raise RuntimeError("not enough training tokens for one batch")
    tokens_per_step = cfg["batch_size"] * cfg["grad_accum"] * cfg["seq_len"]
    log(f"data: {train_tokens:,} train tokens -> {len(train_windows)} windows; {valid_tokens:,} valid tokens; "
        f"{cfg['iters'] * tokens_per_step / max(1, train_tokens):.2f} epochs planned")

    warmup = min(cfg["warmup"], cfg["iters"])
    schedule = optim.join_schedules(
        [optim.linear_schedule(cfg["lr"] * 0.01, cfg["lr"], max(1, warmup)),
         optim.cosine_decay(cfg["lr"], max(1, cfg["iters"] - warmup), cfg["lr"] * cfg["min_lr_ratio"])],
        [warmup])
    optimizer = optim.AdamW(learning_rate=schedule, weight_decay=cfg["weight_decay"])
    loss_and_grad = nn.value_and_grad(model, lm_loss)

    def evaluate_now():
        model.eval()
        value = evaluate(model, valid_windows, cfg["batch_size"], cfg["eval_batches"])
        model.train()
        return value

    history = []
    logfile = (run_dir / "train_log.jsonl").open("w", encoding="utf-8")

    def record(entry):
        history.append(entry)
        logfile.write(json.dumps(entry) + "\n")
        logfile.flush()

    mx.reset_peak_memory()
    first_val = evaluate_now() if valid_windows else None
    record({"step": 0, "val_loss": first_val})
    log(f"step 0: val_loss {first_val:.4f}" if first_val is not None else "step 0: no validation data")
    model.train()
    stream = batches(train_windows, cfg["batch_size"], rng)
    started = time.time()
    window_start, window_tokens, window_loss, window_count = time.time(), 0, 0.0, 0
    for step in range(1, cfg["iters"] + 1):
        grads_sum, loss_sum, tok_sum = None, 0.0, 0.0
        for _ in range(cfg["grad_accum"]):
            inputs, targets, mask = next(stream)
            (loss, ntoks), grads = loss_and_grad(model, inputs, targets, mask)
            grads = tree_map(lambda g: g * ntoks, grads)
            grads_sum = grads if grads_sum is None else tree_map(mx.add, grads_sum, grads)
            mx.eval(grads_sum, loss, ntoks)
            loss_sum += loss.item() * ntoks.item()
            tok_sum += ntoks.item()
        grads = tree_map(lambda g: g / tok_sum, grads_sum)
        grads, grad_norm = optim.clip_grad_norm(grads, cfg["max_grad_norm"])
        optimizer.update(model, grads)
        mx.eval(model.trainable_parameters(), optimizer.state, grad_norm)
        window_loss += loss_sum
        window_count += tok_sum
        window_tokens += tok_sum
        if step % cfg["log_every"] == 0 or step == cfg["iters"]:
            elapsed = time.time() - window_start
            entry = {"step": step, "train_loss": window_loss / window_count, "lr": float(schedule(step)),
                     "grad_norm": grad_norm.item(), "tokens_per_s": window_tokens / elapsed,
                     "peak_mem_gb": mx.get_peak_memory() / 1024 ** 3}
            if valid_windows and (step % cfg["eval_every"] == 0 or step == cfg["iters"]):
                entry["val_loss"] = evaluate_now()
            record(entry)
            log(f"step {step}: train {entry['train_loss']:.4f}" +
                (f", val {entry['val_loss']:.4f}" if "val_loss" in entry else "") +
                f", lr {entry['lr']:.2e}, |g| {entry['grad_norm']:.3f}, {entry['tokens_per_s']:.0f} tok/s, "
                f"peak {entry['peak_mem_gb']:.2f} GB")
            window_start, window_tokens, window_loss, window_count = time.time(), 0, 0.0, 0
    logfile.close()
    model.eval()
    vals = [h["val_loss"] for h in history if h.get("val_loss") is not None]
    return {"train_tokens": train_tokens, "valid_tokens": valid_tokens, "seconds": round(time.time() - started, 1),
            "peak_mem_gb": mx.get_peak_memory() / 1024 ** 3, "val_loss_start": first_val,
            "val_loss_end": vals[-1] if vals else None, "val_loss_best": min(vals) if vals else None,
            "final_train_loss": next((h["train_loss"] for h in reversed(history) if "train_loss" in h), None),
            "trainable_params": trainable, "total_params": total}


def adapter_config(cfg, run_id, model_info, adapter_sha, data_hashes):
    return {"run_id": run_id, "mode": cfg["mode"], "rank": cfg["rank"], "alpha": cfg["alpha"],
            "num_layers": cfg["num_layers"], "targets": list(LORA_TARGETS), "base_model": model_info,
            "adapter_sha256": adapter_sha, "data": data_hashes, "train_config": cfg}


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    defaults = config["training"]
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default=config.get("model_path"))
    p.add_argument("--train", default=config["data"]["train"])
    p.add_argument("--valid", default=config["data"]["valid"])
    p.add_argument("--name", default="", help="short tag added to the run id")
    for key, value in defaults.items():
        kind = type(value) if value is not None else int
        p.add_argument("--" + key.replace("_", "-"), type=kind, default=value)
    p.add_argument("--skip-exam", action="store_true", help="smoke test only; no before/after record")
    p.add_argument("--exam-limit", type=int, help="quick partial exam (recorded as partial)")
    args = p.parse_args()
    if not args.model:
        p.error("--model is required (or set model_path in config.json)")
    cfg = {key: getattr(args, key) for key in defaults}

    from mlx_lm import load
    from exam import compare, find_baseline, load_index, model_fingerprint, run_exams
    model_info = {"path": str(Path(args.model).resolve()), "fingerprint": model_fingerprint(args.model)}
    model, tokenizer = load(args.model)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{stamp}-{cfg['mode']}" + (f"-{args.name}" if args.name else "")
    run_dir = ROOT / "experiments/adhd-01/runs" / run_id
    baseline = None
    if not args.skip_exam:
        version = load_index()["exam_version"]
        baseline = None if args.exam_limit else find_baseline(model_info, version)
        if baseline is None:
            print("== exam before training (baseline)")
            baseline = run_exams(model, tokenizer, label="baseline" if not args.exam_limit else "baseline-partial",
                                 model_info=model_info, limit=args.exam_limit)
        else:
            print(f"== baseline already recorded: {baseline.name}")

    print(f"== training {run_id}")
    data_hashes = {"train": sha256(args.train), "valid": sha256(args.valid)}
    results = train(model, tokenizer, read_texts(args.train), read_texts(args.valid), cfg, run_dir)
    adapter_dir = ROOT / "adapters" / run_id
    adapter_sha = save_trainable(model, adapter_dir / "adapter.safetensors")
    atomic_json(adapter_dir / "adapter_config.json", adapter_config(cfg, run_id, model_info, adapter_sha, data_hashes))
    run_record = {"run_id": run_id, "model": model_info, "config": cfg, "data": data_hashes,
                  "adapter": str(adapter_dir.relative_to(ROOT)), "adapter_sha256": adapter_sha, "results": results}

    if not args.skip_exam:
        print("== exam after training")
        after = run_exams(model, tokenizer, label=f"after:{run_id}", model_info=model_info, limit=args.exam_limit,
                          adapter_info={"run_id": run_id, "path": str(adapter_dir), "sha256": adapter_sha},
                          train_run=run_id)
        report = compare(baseline.name, after.name)
        run_record.update({"exam_before": baseline.name, "exam_after": after.name,
                           "comparison": str(report.relative_to(ROOT))})
        print(f"== report: {report}")
    atomic_json(run_dir / "run.json", run_record)
    print(f"== done: {run_dir}")


if __name__ == "__main__":
    main()
