"""ADHD-05 analysis, fixed before training: learning curve of fictional-trial recall.

  python scripts/synth_report.py <train_run_id> [<train_run_id> ...]

For every examined point of a run (each snapshot and the final adapter) against that model's
own baseline, per group (P = four different texts, R = one text read four times, C = never
described):
  accuracy      frozen acc_norm score (chance 25%)
  raw accuracy  unnormalised log-probability (no length adjustment)
  margin        log p(correct) minus mean log p(distractors), raw sums. A before/after change in
                margin cancels any fixed preference for longer options.
Contrasts P-R, P-C and R-C on the gains, with 95% intervals from resampling whole trials within
each group (5,000 replicates, seed 20261003). General-text perplexity change measures
forgetting. Writes results/adhd05/<run_id>.md and .json. Author: Claude (Opus 5.5), 2026-10-03.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

from common import ROOT, atomic_json
from exam import RESULTS

GROUPS = {"P": "synth_paraphrased", "R": "synth_repeated", "C": "synth_control"}
REPS, SEED = 5000, 20261003


def items(exam_run, exam):
    path = RESULTS / "exams" / exam_run / "items" / f"{exam}.jsonl"
    return {r["id"]: r for r in map(json.loads, path.read_text(encoding="utf-8").splitlines())}


def margin(row):
    lps, k = row["logprobs"], row["answer"]
    return lps[k] - (sum(lps) - lps[k]) / (len(lps) - 1)


def per_trial(before, after, metric):
    """Gain per question, grouped by trial: {trial: array of after-minus-before values}."""
    out = {}
    for qid, a in after.items():
        out.setdefault(qid.split("-")[0], []).append(metric(a) - metric(before[qid]))
    return {t: np.array(v, dtype=float) for t, v in out.items()}


def mean_gain(clusters, keys):
    return float(np.concatenate([clusters[k] for k in keys]).mean())


def contrast(a, b, rng):
    ka, kb = list(a), list(b)
    point = mean_gain(a, ka) - mean_gain(b, kb)
    draws = sorted(mean_gain(a, rng.choice(ka, len(ka))) - mean_gain(b, rng.choice(kb, len(kb))) for _ in range(REPS))
    return point, draws[int(0.025 * REPS)], draws[int(0.975 * REPS) - 1]


def ppl(exam_run):
    rows = items(exam_run, "general_ppl").values()
    return math.exp(sum(r["nll"] for r in rows) / sum(r["tokens"] for r in rows))


def analyse(run_id):
    run = json.loads((ROOT / "experiments/adhd-01/runs" / run_id / "run.json").read_text(encoding="utf-8"))
    log = [json.loads(l) for l in (ROOT / "experiments/adhd-01/runs" / run_id / "train_log.jsonl").read_text().splitlines()]
    val = {e["step"]: e["val_loss"] for e in log if "val_loss" in e and "step" in e}
    points = [(s["step"], s["exam_eos"]["after"], s.get("exam_none", {}).get("after")) for s in run.get("snapshots", [])]
    points.append((run["config"]["iters"], run["exam_eos"]["after"], run.get("exam_none", {}).get("after")))
    base_eos = run["exam_eos"]["before"]
    base_none = run.get("exam_none", {}).get("before")
    base = {g: items(base_eos, e) for g, e in GROUPS.items()}
    rows = []
    for step, after_eos, after_none in sorted(points):
        rng = np.random.default_rng(SEED)
        after = {g: items(after_eos, e) for g, e in GROUPS.items()}
        row = {"step": step, "val_loss": val.get(step)}
        for g in GROUPS:
            row[f"{g}_acc"] = 100 * np.mean([r["correct"] for r in after[g].values()])
            row[f"{g}_acc_raw"] = 100 * np.mean([r["correct_raw"] for r in after[g].values()])
            gains = per_trial(base[g], after[g], margin)
            row[f"{g}_margin_gain"] = mean_gain(gains, list(gains))
        acc = {g: per_trial(base[g], after[g], lambda r: 100 * r["correct"]) for g in GROUPS}
        mar = {g: per_trial(base[g], after[g], margin) for g in GROUPS}
        for a, b in (("P", "R"), ("P", "C"), ("R", "C")):
            row[f"{a}-{b}_acc"] = contrast(acc[a], acc[b], rng)
            row[f"{a}-{b}_margin"] = contrast(mar[a], mar[b], rng)
        row["general_ppl_change_eos"] = 100 * (ppl(after_eos) / ppl(base_eos) - 1)
        if after_none and base_none:
            row["general_ppl_change_none"] = 100 * (ppl(after_none) / ppl(base_none) - 1)
        rows.append(row)
    final = {g: items(points[-1][1], e) for g, e in GROUPS.items() if g != "C"}
    by_attr = {}
    for g, rs in final.items():
        for qid, r in rs.items():
            by_attr.setdefault(qid.split("-", 1)[1], {}).setdefault(g, []).append(r["correct"])
    base_acc = {g: 100 * np.mean([r["correct"] for r in base[g].values()]) for g in GROUPS}
    return run, rows, base_acc, by_attr


def fmt(c):
    return f"{c[0]:+.1f} [{c[1]:+.1f}, {c[2]:+.1f}]"


def main():
    out_dir = RESULTS / "adhd05"
    out_dir.mkdir(parents=True, exist_ok=True)
    for run_id in sys.argv[1:]:
        run, rows, base_acc, by_attr = analyse(run_id)
        model = Path(run["model"]["path"]).name
        md = [f"# ADHD-05 learning curve: `{run_id}`", "",
              f"Model `{model}`; baseline accuracy P {base_acc['P']:.1f}% / R {base_acc['R']:.1f}% / "
              f"C {base_acc['C']:.1f}% (chance 25%). Generated by `scripts/synth_report.py`; exploratory, one seed.", "",
              "## Accuracy (frozen acc_norm) and contrasts of gains, percentage points", "",
              "| Step | Val loss | P | R | C | P−R gain | P−C gain | R−C gain | General PPL |",
              "|---:|---:|---:|---:|---:|---|---|---|---:|"]
        for r in rows:
            md.append(f"| {r['step']} | {r['val_loss'] or float('nan'):.4f} | {r['P_acc']:.1f} | {r['R_acc']:.1f} | "
                      f"{r['C_acc']:.1f} | {fmt(r['P-R_acc'])} | {fmt(r['P-C_acc'])} | {fmt(r['R-C_acc'])} | "
                      f"{r['general_ppl_change_eos']:+.1f}% |")
        md += ["", "## Margin (log p correct − mean log p distractors), gain over baseline, nats", "",
               "| Step | P | R | C | P−R | P−C | R−C | Raw acc P / R / C |", "|---:|---:|---:|---:|---|---|---|---|"]
        for r in rows:
            md.append(f"| {r['step']} | {r['P_margin_gain']:+.3f} | {r['R_margin_gain']:+.3f} | {r['C_margin_gain']:+.3f} | "
                      f"{r['P-R_margin'][0]:+.3f} [{r['P-R_margin'][1]:+.3f}, {r['P-R_margin'][2]:+.3f}] | "
                      f"{r['P-C_margin'][0]:+.3f} [{r['P-C_margin'][1]:+.3f}, {r['P-C_margin'][2]:+.3f}] | "
                      f"{r['R-C_margin'][0]:+.3f} [{r['R-C_margin'][1]:+.3f}, {r['R-C_margin'][2]:+.3f}] | "
                      f"{r['P_acc_raw']:.1f} / {r['R_acc_raw']:.1f} / {r['C_acc_raw']:.1f} |")
        md += ["", "## Final accuracy by fact type (%)", "", "| Fact | P | R |", "|---|---:|---:|"]
        for attr, gs in sorted(by_attr.items()):
            md.append(f"| {attr} | {100 * np.mean(gs['P']):.1f} | {100 * np.mean(gs['R']):.1f} |")
        md += ["", "Snapshots of one run share seed and data order, so they are not independent. Intervals "
               "resample trials, not training runs. C rising above its baseline means the model learned the answer "
               "pools or format, not facts; P−C and R−C remove that."]
        path = out_dir / f"{run_id}.md"
        path.write_text("\n".join(md) + "\n", encoding="utf-8")
        atomic_json(path.with_suffix(".json"), {"run_id": run_id, "baseline_accuracy": base_acc, "points": rows,
                                                 "final_by_attribute": {a: {g: float(np.mean(v)) for g, v in gs.items()}
                                                                        for a, gs in by_attr.items()}})
        print(path)


if __name__ == "__main__":
    main()
