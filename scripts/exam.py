"""Frozen exams before and after every training run, a ledger, and paired comparisons.

  python scripts/exam.py run --model models/qwen3-0.6b-base --label baseline
  python scripts/exam.py run --model models/qwen3-0.6b-base --adapter adapters/<run_id>
  python scripts/exam.py compare <run_a> <run_b>        # run ids under results/exams
  python scripts/exam.py log                            # rebuild results/EXAM_LOG.md

Exams are listed in eval/exams/index.json (built once by build_exams.py, then frozen).
Every item result is kept, so a comparison can say *which* questions changed.
"""
import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import math
import re
import time
from pathlib import Path

from common import ROOT, atomic_json, sha256

SCORING_VERSION = 1
INDEX = ROOT / "eval/exams/index.json"
RESULTS = ROOT / "results"
MIN_ITEMS = 10  # below this no exam is called significant, whatever the interval says
EXAM_CACHE_LIMIT = 512 * 1024 ** 2  # Free allocator cache only, not live tensor memory.

# What each exam role is expected to show after ADHD DAPT; used to phrase the report.
ROLE_TEXT = {
    "knowledge": "Group A: new knowledge from trained papers (expected to improve)",
    "control": "Group B: questions from untrained papers (control; ideally unchanged)",
    "domain": "Unseen 2026 ADHD paper perplexity (expected to decrease)",
    "forgetting": "General-text perplexity (forgetting monitor; should not increase substantially)",
    "transfer": "Existing medical QA (transfer; small changes expected)",
}


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def load_index(index_path=INDEX):
    index_path = Path(index_path)
    if not index_path.exists():
        raise RuntimeError(f"missing {index_path}; run scripts/build_exams.py first")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    base = index_path.parent
    for name, spec in index["exams"].items():
        path = base / spec["file"]
        if sha256(path) != spec["sha256"]:
            raise RuntimeError(f"exam file changed after freezing: {name}")
    return index


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def model_fingerprint(path):
    """Hash of config and weight files, so a baseline is only reused for identical weights."""
    path = Path(path)
    parts = []
    for f in sorted([path / "config.json", *path.glob("*.safetensors")]):
        parts.append(f"{f.name}:{sha256(f)}")
    return sha256_text("\n".join(parts))


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (centre - half, centre + half)


# ---------------------------------------------------------------- scoring

def score_ppl(model, tokenizer, items, window, prefix_eos=True):
    from lm import text_nll
    out = []
    for item in items:
        nll, tokens = text_nll(model, tokenizer, item["text"], window, prefix_eos)
        out.append({"id": item["id"], "nll": nll, "tokens": tokens, "chars": len(item["text"])})
    return out


def score_mcq(model, tokenizer, items):
    """Cloze scoring: log p(option | prompt); acc_norm divides by option length in chars."""
    from lm import choice_logprobs
    out = []
    for item in items:
        lps = choice_logprobs(model, tokenizer, item["prompt"], item["choices"])
        norm = [lp / max(1, len(c)) for lp, c in zip(lps, item["choices"])]
        top = max(norm)
        weights = [math.exp(v - top) for v in norm]
        p_correct = weights[item["answer"]] / sum(weights)
        pred = max(range(len(norm)), key=norm.__getitem__)
        pred_raw = max(range(len(lps)), key=lps.__getitem__)
        out.append({"id": item["id"], "pred": pred, "answer": item["answer"],
                    "correct": int(pred == item["answer"]), "correct_raw": int(pred_raw == item["answer"]),
                    "p_correct": p_correct, "logprobs": lps})
    return out


def summarize(kind, rows, items):
    if kind == "ppl":
        nll = sum(r["nll"] for r in rows)
        tokens = sum(r["tokens"] for r in rows)
        chars = sum(r["chars"] for r in rows)
        return {"n": len(rows), "tokens": tokens, "ppl": math.exp(nll / tokens) if tokens else None,
                "bits_per_char": nll / math.log(2) / chars if chars else None}
    k = sum(r["correct"] for r in rows)
    n = len(rows)
    by_id = {i["id"]: i for i in items}
    return {"n": n, "acc_norm": k / n if n else None, "acc_norm_ci95": wilson(k, n),
            "acc_raw": sum(r["correct_raw"] for r in rows) / n if n else None,
            "mean_p_correct": sum(r["p_correct"] for r in rows) / n if n else None,
            "chance": sum(1 / len(by_id[r["id"]]["choices"]) for r in rows) / n if n else None}


def headline(kind, summary):
    if summary.get("n", 0) == 0:
        return "-"
    if kind == "ppl":
        return f"PPL {summary['ppl']:.3f}"
    return f"{summary['acc_norm'] * 100:.1f}%"


# ---------------------------------------------------------------- running

@contextmanager
def bounded_exam_cache(limit=EXAM_CACHE_LIMIT):
    """Bound inference allocator retention and restore the training caller's policy.

    Author: Codex / GPT-6, 2026-09-30. Does not alter numerical scoring.
    """
    import mlx.core as mx
    previous = mx.set_cache_limit(limit)
    try:
        mx.clear_cache()
        yield
    finally:
        try:
            mx.clear_cache()
        finally:
            mx.set_cache_limit(previous)


@bounded_exam_cache()
def run_exams(model, tokenizer, *, label, model_info, adapter_info=None, names=None, limit=None,
              window=1024, index_path=INDEX, results_root=RESULTS, train_run=None, ppl_prefix="eos"):
    """Score every selected exam, write per-item results, append the ledger; return run dir."""
    index = load_index(index_path)
    model.eval()
    selected = names or list(index["exams"])
    stamp = utc_now()
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", label).strip("-")[:60] or "run"
    run_id = f"{stamp:%Y%m%dT%H%M%SZ}-{slug}"
    run_dir = Path(results_root) / "exams" / run_id
    (run_dir / "items").mkdir(parents=True, exist_ok=True)
    summary = {"run_id": run_id, "label": label, "date": stamp.isoformat().replace("+00:00", "Z"),
               "exam_version": index["exam_version"], "scoring_version": SCORING_VERSION,
               "model": model_info, "adapter": adapter_info, "train_run": train_run,
               "limit": limit, "window": window, "ppl_prefix": ppl_prefix, "exams": {},
               "evaluation_memory_policy": {"free_cache_limit_bytes": EXAM_CACHE_LIMIT,
                                            "restore_caller_policy": True}}
    for name in selected:
        spec = index["exams"][name]
        items = read_jsonl(Path(index_path).parent / spec["file"])[:limit] if limit else \
            read_jsonl(Path(index_path).parent / spec["file"])
        started = time.time()
        rows = (score_ppl(model, tokenizer, items, window, ppl_prefix == "eos") if spec["type"] == "ppl"
                else score_mcq(model, tokenizer, items))
        (run_dir / "items" / f"{name}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        result = summarize(spec["type"], rows, items)
        result.update({"type": spec["type"], "role": spec["role"], "file_sha256": spec["sha256"],
                       "seconds": round(time.time() - started, 1)})
        summary["exams"][name] = result
        print(f"  {name:<26} {headline(spec['type'], result):>12}  n={result['n']}  ({result['seconds']}s)")
    atomic_json(run_dir / "summary.json", summary)
    ledger = Path(results_root) / "exam_log.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(summary, ensure_ascii=False) + "\n")
    write_log_md(results_root)
    return run_dir


def find_baseline(model_info, exam_version, results_root=RESULTS, window=1024, ppl_prefix="eos", need=None):
    """Latest complete, adapter-free exam run of exactly these weights and exam version."""
    ledger = Path(results_root) / "exam_log.jsonl"
    if not ledger.exists():
        return None
    found = None
    for line in ledger.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if (row["adapter"] is None and row["limit"] is None and row["window"] == window
                and row.get("ppl_prefix", "eos") == ppl_prefix and set(need or ()) <= set(row["exams"])
                and row["exam_version"] == exam_version and row["scoring_version"] == SCORING_VERSION
                and row["model"].get("fingerprint") == model_info.get("fingerprint")):
            found = Path(results_root) / "exams" / row["run_id"]
    return found


def write_log_md(results_root=RESULTS):
    ledger = Path(results_root) / "exam_log.jsonl"
    rows = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
    names = []
    for row in rows:
        names += [n for n in row["exams"] if n not in names]
    lines = ["# Exam ledger", "", "One exam run per row. Lower PPL is better; percentages are acc_norm. Details: `results/exams/<run_id>/`.", "",
             "| Time | run_id | Model | Adapter | " + " | ".join(names) + " |",
             "|---|---|---|---|" + "---|" * len(names)]
    for row in rows:
        adapter = row["adapter"]["run_id"] if row["adapter"] else "None (baseline)"
        cells = [headline(row["exams"][n]["type"], row["exams"][n]) if n in row["exams"] else "" for n in names]
        partial = (f" (limit {row['limit']})" if row["limit"] else "") + \
            (" (PPL without EOS prefix)" if row.get("ppl_prefix", "eos") == "none" else "")
        lines.append(f"| {row['date']} | `{row['run_id']}`{partial} | {Path(row['model']['path'] or 'selftest').name} "
                     f"| {adapter} | " + " | ".join(cells) + " |")
    (Path(results_root) / "EXAM_LOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- comparison

def _bootstrap(stat, n, reps=2000, seed=0):
    import numpy as np
    rng = np.random.default_rng(seed)
    values = sorted(stat(rng.integers(0, n, n)) for _ in range(reps))
    return values[int(0.025 * reps)], values[int(0.975 * reps) - 1]


def _mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def compare(run_a, run_b, results_root=RESULTS, index_path=INDEX, out=None):
    """Paired before/after comparison on the items both runs scored. Returns markdown path."""
    import numpy as np
    root = Path(results_root) / "exams"
    dir_a, dir_b = (Path(r) if Path(r).is_dir() else root / r for r in (run_a, run_b))
    sa = json.loads((dir_a / "summary.json").read_text(encoding="utf-8"))
    sb = json.loads((dir_b / "summary.json").read_text(encoding="utf-8"))
    if (sa["scoring_version"] != sb["scoring_version"] or sa["window"] != sb["window"]
            or sa.get("ppl_prefix", "eos") != sb.get("ppl_prefix", "eos")):
        raise RuntimeError("runs used different scoring settings; not comparable")
    index = json.loads(Path(index_path).read_text(encoding="utf-8"))
    report = {"a": sa["run_id"], "b": sb["run_id"], "exams": {}}
    table, details = [], []
    for name, ea in sa["exams"].items():
        eb = sb["exams"].get(name)
        if not eb or ea["file_sha256"] != eb["file_sha256"]:
            continue
        rows_a = {r["id"]: r for r in read_jsonl(dir_a / "items" / f"{name}.jsonl")}
        rows_b = {r["id"]: r for r in read_jsonl(dir_b / "items" / f"{name}.jsonl")}
        ids = [i for i in rows_a if i in rows_b]
        if not ids:
            continue
        spec = index["exams"].get(name, {})
        items = {i["id"]: i for i in read_jsonl(Path(index_path).parent / spec["file"])} if spec else {}
        if ea["type"] == "ppl":
            na = np.array([rows_a[i]["nll"] for i in ids])
            nb = np.array([rows_b[i]["nll"] for i in ids])
            ta = np.array([rows_a[i]["tokens"] for i in ids])
            tb = np.array([rows_b[i]["tokens"] for i in ids])
            ppl_a, ppl_b = math.exp(na.sum() / ta.sum()), math.exp(nb.sum() / tb.sum())
            lo, hi = _bootstrap(lambda s: math.exp(nb[s].sum() / tb[s].sum() - na[s].sum() / ta[s].sum()), len(ids))
            verdict = ("Too few items; no verdict" if len(ids) < MIN_ITEMS else
                       "Significant decrease (better)" if hi < 1 else "Significant increase (worse)" if lo > 1 else "No significant change")
            table.append(f"| {name} | {ROLE_TEXT.get(ea['role'], ea['role'])} | {len(ids)} | PPL {ppl_a:.3f} | "
                         f"PPL {ppl_b:.3f} | {100 * (ppl_b / ppl_a - 1):+.2f}% | [{100 * (lo - 1):+.2f}%, {100 * (hi - 1):+.2f}%] | {verdict} |")
            per_doc = sorted(((nb[k] / tb[k] - na[k] / ta[k], i) for k, i in enumerate(ids)))
            better = [f"`{i}` {d:+.3f}" for d, i in per_doc[:5] if d < 0]
            worse = [f"`{i}` {d:+.3f}" for d, i in per_doc[::-1][:5] if d > 0]
            details.append(f"### {name}\n\nPer-token NLL change (negative means improvement). Largest improvements: " + (", ".join(better) or "None") +
                           "\n\nLargest regressions: " + (", ".join(worse) or "None") + "\n")
            report["exams"][name] = {"n": len(ids), "ppl_a": ppl_a, "ppl_b": ppl_b, "ratio_ci95": [lo, hi], "verdict": verdict}
        else:
            ca = np.array([rows_a[i]["correct"] for i in ids])
            cb = np.array([rows_b[i]["correct"] for i in ids])
            pa = np.array([rows_a[i]["p_correct"] for i in ids])
            pb = np.array([rows_b[i]["p_correct"] for i in ids])
            lo, hi = _bootstrap(lambda s: cb[s].mean() - ca[s].mean(), len(ids))
            plo, phi = _bootstrap(lambda s: pb[s].mean() - pa[s].mean(), len(ids))
            gained = [i for k, i in enumerate(ids) if cb[k] > ca[k]]
            lost = [i for k, i in enumerate(ids) if cb[k] < ca[k]]
            p_value = _mcnemar(len(gained), len(lost))
            # Both the bootstrap interval and McNemar's exact test must agree.
            verdict = ("Too few items; no verdict" if len(ids) < MIN_ITEMS else
                       "Significant improvement" if lo > 0 and p_value < 0.05 else
                       "Significant decline" if hi < 0 and p_value < 0.05 else "No significant change")
            table.append(f"| {name} | {ROLE_TEXT.get(ea['role'], ea['role'])} | {len(ids)} | {100 * ca.mean():.1f}% | "
                         f"{100 * cb.mean():.1f}% | {100 * (cb.mean() - ca.mean()):+.1f} pp | "
                         f"[{100 * lo:+.1f}, {100 * hi:+.1f}] | {verdict} |")

            def show(i):
                q = items.get(i, {}).get("prompt", "").replace("\n", " ")
                return f"- `{i}` {q[:140]}"
            details.append(
                f"### {name}\n\nMean correct-option normalized-score share (not calibrated): {pa.mean():.3f} → {pb.mean():.3f}(difference 95% CI "
                f"[{plo:+.3f}, {phi:+.3f}]).McNemar p = {p_value:.3g}.\n\n"
                f"Changed from incorrect to correct: {len(gained)} items: \n" + "\n".join(show(i) for i in gained[:10]) +
                f"\n\nChanged from correct to incorrect: {len(lost)} items: \n" + "\n".join(show(i) for i in lost[:10]) + "\n")
            report["exams"][name] = {"n": len(ids), "acc_a": float(ca.mean()), "acc_b": float(cb.mean()),
                                     "diff_ci95": [lo, hi], "p_correct_diff_ci95": [plo, phi],
                                     "gained": gained, "lost": lost, "mcnemar_p": p_value, "verdict": verdict}
    notes = interpret(report, sa, sb)
    md = [f"# Training outcome comparison: `{sa['run_id']}` → `{sb['run_id']}`", "",
          f"- Before: {sa['label']}, adapter {sa['adapter']['run_id'] if sa['adapter'] else 'None'}",
          f"- After: {sb['label']}, adapter {sb['adapter']['run_id'] if sb['adapter'] else 'None'}",
          f"- Exam version: {sa['exam_version']}; compare only shared items with matching exam hashes. CIs use paired item bootstrap.", "",
          "## Conclusions", "", *[f"- {n}" for n in notes], "",
          "## Exams", "", "| Exam | Role | Items | Before | After | Change | 95% CI | Verdict |",
          "|---|---|---:|---:|---:|---:|---|---|", *table, "", "## Details", "", *details]
    out = Path(out) if out else dir_b / f"compare_vs_{sa['run_id']}.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    atomic_json(out.with_suffix(".json"), report)
    return out


def interpret(report, sa, sb):
    """Plain-language reading of the role pattern; deliberately conservative."""
    ex = report["exams"]
    role = {name: sa["exams"][name]["role"] for name in ex}
    pick = lambda r: [ex[n] for n in ex if role[n] == r]
    notes = []
    know, ctrl = pick("knowledge"), pick("control")
    if know:
        up = any(e["verdict"] == "Significant improvement" for e in know)
        ctrl_up = any(e["verdict"] == "Significant improvement" for e in ctrl)
        if up and not ctrl:
            notes.append("Group A significantly improved, but no group B control is available; knowledge retention cannot be distinguished from format familiarity.")
        elif up and not ctrl_up:
            notes.append("Group A significantly improved while group B did not show a significant improvement. This pattern is consistent with a trained-paper benefit, but a direct comparison of group changes is needed to establish that difference.")
        elif up and ctrl_up:
            notes.append("Both groups improved: at least part may reflect format or domain familiarity rather than specific knowledge retention.")
        elif all(e["verdict"] == "Too few items; no verdict" for e in know):
            notes.append("Group A contains too few items to judge.")
        else:
            notes.append("Group A accuracy did not significantly improve in this run. This does not prove absence of learning; inspect the correct-choice score share, uncertainty and other outcomes.")
    for e in pick("domain"):
        notes.append(f"Unseen new-paper perplexity: {e['verdict']}({100 * (e['ppl_b'] / e['ppl_a'] - 1):+.2f}%).")
    for e in pick("forgetting"):
        change = e["ppl_b"] / e["ppl_a"] - 1
        notes.append(f"General-text perplexity {100 * change:+.2f}%" + ("; substantial forgetting: consider a lower learning rate or general-text mixing." if change > 0.05 else "."))
    small = [n for n in ex if MIN_ITEMS <= ex[n]["n"] < 50]
    if small:
        notes.append("Exams with fewer than 50 items have wide confidence intervals; do not conclude from them alone: " + ", ".join(small) + ".")
    if sa.get("limit") or sb.get("limit"):
        notes.append("At least one exam used sampling (--limit); use it only as a quick check.")
    return notes or ["No comparable exams."]


# ---------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run")
    r.add_argument("--model", required=True)
    r.add_argument("--adapter")
    r.add_argument("--label")
    r.add_argument("--exams", nargs="+")
    r.add_argument("--limit", type=int, help="first N items per exam; quick check only")
    r.add_argument("--window", type=int, default=1024)
    r.add_argument("--ppl-prefix", choices=("eos", "none"), default="eos",
                   help="eos = frozen ADHD-01 protocol; none = supplementary protocol added 2026-10-01")
    c = sub.add_parser("compare")
    c.add_argument("run_a")
    c.add_argument("run_b")
    sub.add_parser("log")
    args = p.parse_args()
    if args.command == "log":
        write_log_md()
        print(RESULTS / "EXAM_LOG.md")
    elif args.command == "compare":
        print(compare(args.run_a, args.run_b))
    else:
        from mlx_lm import load
        from lm import load_adapter
        model, tokenizer = load(args.model)
        model_info = {"path": str(Path(args.model).resolve()), "fingerprint": model_fingerprint(args.model)}
        adapter_info = None
        if args.adapter:
            cfg = load_adapter(model, args.adapter)
            adapter_info = {"run_id": cfg["run_id"], "path": str(Path(args.adapter).resolve()), "sha256": cfg["adapter_sha256"]}
        label = args.label or (f"after:{adapter_info['run_id']}" if adapter_info else "baseline")
        run_dir = run_exams(model, tokenizer, label=label, model_info=model_info, adapter_info=adapter_info,
                            names=args.exams, limit=args.limit, window=args.window, ppl_prefix=args.ppl_prefix)
        print(f"saved {run_dir}")
        if adapter_info:
            base = find_baseline(model_info, json.loads(INDEX.read_text())["exam_version"], window=args.window,
                                 ppl_prefix=args.ppl_prefix, need=args.exams)
            if base:
                print(f"compare: {compare(base.name, run_dir.name)}")


if __name__ == "__main__":
    main()
