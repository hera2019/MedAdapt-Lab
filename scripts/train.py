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
import shutil
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_flatten, tree_map, tree_unflatten

from common import ROOT, atomic_json, sha256
from lm import LORA_TARGETS, apply_lora, count_params, lm_loss, pack, save_trainable

CONFIG = ROOT / "experiments/adhd-01/config.json"


def read_texts(path):
    return [json.loads(line)["text"] for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def batch_indices(n_windows, batch_size, rng):
    """Endless shuffled epochs of window indices; replayable from the seed for resume."""
    order = list(range(n_windows))
    while True:
        rng.shuffle(order)
        for i in range(0, len(order) - batch_size + 1, batch_size):
            yield order[i:i + batch_size]


def as_batch(windows, indices):
    block = mx.array([windows[j] for j in indices])
    return block[:, :-1], block[:, 1:], mx.ones(block[:, 1:].shape)


CKPT, CKPT_NEW, CKPT_OLD = "checkpoint", "checkpoint.new", "checkpoint.old"


def save_checkpoint(run_dir, model, optimizer, state):
    """Trainable weights + AdamW state + loop state, swapped in with renames only."""
    new, cur, old = (run_dir / n for n in (CKPT_NEW, CKPT, CKPT_OLD))
    shutil.rmtree(new, ignore_errors=True)
    new.mkdir()
    mx.save_safetensors(str(new / "trainable.safetensors"), dict(tree_flatten(model.trainable_parameters())))
    mx.save_safetensors(str(new / "optimizer.safetensors"), dict(tree_flatten(optimizer.state)))
    atomic_json(new / "state.json", state)
    shutil.rmtree(old, ignore_errors=True)
    if cur.exists():
        cur.rename(old)
    new.rename(cur)
    shutil.rmtree(old, ignore_errors=True)


def find_checkpoint(run_dir):
    for name in (CKPT, CKPT_OLD):  # .old survives only a crash between the two renames
        path = Path(run_dir) / name
        if (path / "state.json").exists():
            return path
    return None


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


def snapshot_steps(cfg):
    """Steps listed in cfg["snapshot_steps"] ("250,500,1000"), excluding the final step."""
    raw = str(cfg.get("snapshot_steps") or "")
    steps = sorted({int(x) for x in raw.replace(" ", "").split(",") if x})
    if any(s <= 0 for s in steps):
        raise ValueError("snapshot steps must be positive")
    return [s for s in steps if s < cfg["iters"]]


def train(model, tokenizer, train_texts, valid_texts, cfg, run_dir, log=print, resume=False, on_snapshot=None):
    """Train in place. Returns a dict of results; writes train_log.jsonl into run_dir.

    With cfg["checkpoint_every"] > 0 a checkpoint is kept in run_dir/checkpoint; resume=True
    continues from it (same data order, optimizer moments and schedule position).
    on_snapshot(step) is called after each step listed in cfg["snapshot_steps"]: one long run
    then yields intermediate adapters for a learning curve. They are not annealed like a run
    that ends at that step, because the learning-rate schedule spans the whole run.
    """
    snapshots = set(snapshot_steps(cfg))
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

    prefix_eos = cfg.get("window_prefix_eos", False)
    train_windows, train_tokens = pack(train_texts, tokenizer, cfg["seq_len"], prefix_eos)
    valid_windows, valid_tokens = pack(valid_texts, tokenizer, cfg["seq_len"], prefix_eos)
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

    history, start_step, first_val = [], 0, None
    checkpoint = find_checkpoint(run_dir) if resume else None
    if resume and checkpoint is None:
        raise RuntimeError(f"no checkpoint to resume in {run_dir}")
    if checkpoint:
        state = json.loads((checkpoint / "state.json").read_text(encoding="utf-8"))
        if state["cfg"] != cfg:
            raise RuntimeError("checkpoint was written with a different training config")
        model.load_weights(list(mx.load(str(checkpoint / "trainable.safetensors")).items()), strict=False)
        optimizer.state = tree_unflatten(list(mx.load(str(checkpoint / "optimizer.safetensors")).items()))
        mx.eval(model.parameters(), optimizer.state)
        history, start_step, first_val = state["history"], state["step"], state["first_val"]
        log(f"resumed from step {start_step} ({checkpoint.name})")
    logfile = (run_dir / "train_log.jsonl").open("a" if checkpoint else "w", encoding="utf-8")
    if checkpoint:
        logfile.write(json.dumps({"resumed_at_step": start_step}) + "\n")

    def record(entry):
        history.append(entry)
        logfile.write(json.dumps(entry) + "\n")
        logfile.flush()

    mx.reset_peak_memory()
    if not checkpoint:
        first_val = evaluate_now() if valid_windows else None
        record({"step": 0, "val_loss": first_val})
        log(f"step 0: val_loss {first_val:.4f}" if first_val is not None else "step 0: no validation data")
    model.train()
    stream = batch_indices(len(train_windows), cfg["batch_size"], rng)
    for _ in range(start_step * cfg["grad_accum"]):  # replay the data order up to the checkpoint
        next(stream)
    started = time.time()
    window_start, window_tokens, window_loss, window_count = time.time(), 0, 0.0, 0
    for step in range(start_step + 1, cfg["iters"] + 1):
        grads_sum, loss_sum, tok_sum = None, 0.0, 0.0
        for _ in range(cfg["grad_accum"]):
            inputs, targets, mask = as_batch(train_windows, next(stream))
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
        if on_snapshot and step in snapshots:
            on_snapshot(step)
        if cfg.get("checkpoint_every", 0) and step % cfg["checkpoint_every"] == 0 and step < cfg["iters"]:
            save_checkpoint(run_dir, model, optimizer, {"step": step, "cfg": cfg, "history": history,
                                                       "first_val": first_val})
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


PPL_EXAMS = ("adhd_new_ppl", "general_ppl")


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
        if kind is bool:
            p.add_argument("--" + key.replace("_", "-"), type=lambda v: v.lower() in ("1", "true", "yes"), default=value)
        else:
            p.add_argument("--" + key.replace("_", "-"), type=kind, default=value)
    p.add_argument("--skip-exam", action="store_true", help="smoke test only; no before/after record")
    p.add_argument("--exam-limit", type=int, help="quick partial exam (recorded as partial)")
    p.add_argument("--resume", metavar="RUN_ID", help="continue a crashed run from its last checkpoint; "
                   "config, data and flags come from the saved run, other options are ignored")
    args = p.parse_args()

    if args.resume:
        run_id = args.resume
        run_dir = ROOT / "experiments/adhd-01/runs" / run_id
        launch = json.loads((run_dir / "launch.json").read_text(encoding="utf-8"))
        cfg, model_path, train_path, valid_path = launch["config"], launch["model"], launch["train"], launch["valid"]
        skip_exam, exam_limit = launch["skip_exam"], launch["exam_limit"]
    else:
        if not args.model:
            p.error("--model is required (or set model_path in config.json)")
        cfg = {key: getattr(args, key) for key in defaults}
        model_path, train_path, valid_path = args.model, args.train, args.valid
        skip_exam, exam_limit = args.skip_exam, args.exam_limit
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_id = f"{stamp}-{cfg['mode']}" + (f"-{args.name}" if args.name else "")
        run_dir = ROOT / "experiments/adhd-01/runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

    from mlx_lm import load
    from exam import compare, find_baseline, load_index, model_fingerprint, run_exams
    model_info = {"path": str(Path(model_path).resolve()), "fingerprint": model_fingerprint(model_path)}
    data_hashes = {"train": sha256(train_path), "valid": sha256(valid_path)}
    if args.resume:
        if launch["model_info"] != model_info or launch["data"] != data_hashes:
            raise RuntimeError("model or data changed since the run was launched; cannot resume")
    else:
        atomic_json(run_dir / "launch.json", {"config": cfg, "model": model_path, "train": train_path,
                                             "valid": valid_path, "skip_exam": skip_exam, "exam_limit": exam_limit,
                                             "model_info": model_info, "data": data_hashes})
    model, tokenizer = load(model_path)

    # Baselines are taken from the untouched base weights, so they must exist before training.
    baselines = {}
    if not skip_exam:
        version = load_index()["exam_version"]
        for prefix, names in (("eos", None), ("none", PPL_EXAMS)):
            found = None if exam_limit else find_baseline(model_info, version, ppl_prefix=prefix, need=names)
            if found is None:
                if args.resume:
                    raise RuntimeError(f"baseline ({prefix}) missing on resume; weights are no longer untouched")
                print(f"== exam before training (baseline, PPL prefix {prefix})")
                found = run_exams(model, tokenizer, label="baseline" if not exam_limit else "baseline-partial",
                                  model_info=model_info, limit=exam_limit, names=names, ppl_prefix=prefix)
            else:
                print(f"== baseline already recorded ({prefix}): {found.name}")
            baselines[prefix] = found

    print(f"== training {run_id}" + (" (resumed)" if args.resume else ""))
    adapter_dir = ROOT / "adapters" / run_id

    def save_snapshot(step):
        snap_id = f"{run_id}-step{step:05d}"
        snap_dir = adapter_dir / f"step-{step:05d}"
        sha = save_trainable(model, snap_dir / "adapter.safetensors")
        atomic_json(snap_dir / "adapter_config.json", adapter_config(cfg, snap_id, model_info, sha, data_hashes))
        print(f"== snapshot saved: {snap_dir.relative_to(ROOT)}")

    results = train(model, tokenizer, read_texts(train_path), read_texts(valid_path), cfg, run_dir,
                    resume=bool(args.resume), on_snapshot=save_snapshot)
    adapter_sha = save_trainable(model, adapter_dir / "adapter.safetensors")
    atomic_json(adapter_dir / "adapter_config.json", adapter_config(cfg, run_id, model_info, adapter_sha, data_hashes))
    run_record = {"run_id": run_id, "model": model_info, "config": cfg, "data": data_hashes,
                  "adapter": str(adapter_dir.relative_to(ROOT)), "adapter_sha256": adapter_sha, "results": results}

    if not skip_exam:
        adapter_info = {"run_id": run_id, "path": str(adapter_dir), "sha256": adapter_sha}
        for prefix, names in (("eos", None), ("none", PPL_EXAMS)):
            print(f"== exam after training (PPL prefix {prefix})")
            after = run_exams(model, tokenizer, label=f"after:{run_id}", model_info=model_info, limit=exam_limit,
                              adapter_info=adapter_info, train_run=run_id, names=names, ppl_prefix=prefix)
            report = compare(baselines[prefix].name, after.name)
            run_record[f"exam_{prefix}"] = {"before": baselines[prefix].name, "after": after.name,
                                            "comparison": str(report.relative_to(ROOT))}
            print(f"== report: {report}")
        # Learning curve: examine every snapshot the same way, swapping only the adapter weights.
        snaps = []
        for step in snapshot_steps(cfg):
            snap_dir = adapter_dir / f"step-{step:05d}"
            snap_cfg = json.loads((snap_dir / "adapter_config.json").read_text(encoding="utf-8"))
            if sha256(snap_dir / "adapter.safetensors") != snap_cfg["adapter_sha256"]:
                raise RuntimeError(f"snapshot hash mismatch: {snap_dir}")
            model.load_weights(list(mx.load(str(snap_dir / "adapter.safetensors")).items()), strict=False)
            info = {"run_id": snap_cfg["run_id"], "path": str(snap_dir), "sha256": snap_cfg["adapter_sha256"]}
            entry = {"step": step, "adapter": str(snap_dir.relative_to(ROOT))}
            for prefix, names in (("eos", None), ("none", PPL_EXAMS)):
                print(f"== exam snapshot step {step} (PPL prefix {prefix})")
                after = run_exams(model, tokenizer, label=f"after:{snap_cfg['run_id']}", model_info=model_info,
                                  limit=exam_limit, adapter_info=info, train_run=run_id, names=names, ppl_prefix=prefix)
                report = compare(baselines[prefix].name, after.name)
                entry[f"exam_{prefix}"] = {"after": after.name, "comparison": str(report.relative_to(ROOT))}
            snaps.append(entry)
        run_record["snapshots"] = snaps
    atomic_json(run_dir / "run.json", run_record)
    shutil.rmtree(run_dir / CKPT, ignore_errors=True)  # the adapter supersedes the checkpoint
    print(f"== done: {run_dir}")


if __name__ == "__main__":
    main()
