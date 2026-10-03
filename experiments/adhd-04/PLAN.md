# ADHD-04: dose response — how much reading does it take, and what does it cost?

Plan author: Claude (reviewer, Claude Opus 5.5), 2026-10-02. Executor: Sol (Codex / GPT-6). The
owner asked for this experiment. Declared before any ADHD-04 training; nothing below is chosen
from ADHD-04 results.

## Question

R3 (0.6B and 1.7B) read each of the 269 new_train papers about 1.65 times and gained a
trained-paper-specific +4 to +5 pp. How do the following change as reading continues:
1. the trained-paper gain,
2. its trained-minus-held-out difference,
3. held-out ADHD perplexity, and
4. general-text perplexity (forgetting)?

Is there an optimum? The 1.7B validation loss was lowest at step 300 of 500, which suggests one.

## Design: one long run per model, intermediate adapters examined

`train.py --snapshot-steps` (added by Claude 2026-10-02, selftested) saves the adapter at the
listed steps. After training, `train.py` examines every snapshot and the final adapter with all
frozen exams and both perplexity protocols, and writes a comparison against the model's own
baseline for each. The existing baselines are reused automatically.

| Run | Model | Steps | Snapshots | Epochs over new_train at snapshots / final |
|---|---|---:|---|---|
| D1 | Qwen3-0.6B-Base | 2000 | 250, 500, 1000 | 0.83, 1.65, 3.30 / 6.61 |
| D2 | Qwen3-1.7B-Base | 1000 | 150, 300, 500 | 0.50, 0.99, 1.65 / 3.30 |

Everything else is identical to R3 / ADHD-03:
- corpus `data/train/adhd-01/train_new.jsonl`, seed 42, LoRA rank 16 / alpha 32 / dropout 0 on all layers;
- sequence 1024, EOS-prefixed windows, micro-batch 1 × accumulation 8 (8,192 tokens per update);
- peak lr 2e-4, warmup 30, cosine to 10%;
- 100 validation windows, evaluated every 50 steps; checkpoint every 50 steps; cache 2 GiB.

**Known confound (state it in the report).** The cosine schedule spans the whole run, so a
snapshot is not annealed the way a run ending at that step would be. D1 step 500 is therefore
not the same as R3, which annealed fully by step 500. Report D1@500 next to R3 and D2@500 next
to ADHD-03; the difference shows the annealing effect. Do not treat snapshots as separate
experiments.

## Commands

Run D1 first; D2 only after D1 has finished and its outputs are verified. Use the guard as for
ADHD-03 (launch below 3 GiB swap, stop at 4 GiB, check every 10 seconds) and task-bound
`caffeinate`. Use a new guard log path per run.

```sh
# D1 — 0.6B
.venv/bin/python scripts/train.py --name adhd04-d1-06b-dose --model models/qwen3-0.6b-base \
  --train data/train/adhd-01/train_new.jsonl --iters 2000 --snapshot-steps 250,500,1000 \
  --batch-size 1 --grad-accum 8 --eval-batches 100 --cache-limit-gib 2

# D2 — 1.7B
.venv/bin/python scripts/train.py --name adhd04-d2-17b-dose --model models/qwen3-1.7b-base \
  --train data/train/adhd-01/train_new.jsonl --iters 1000 --snapshot-steps 150,300,500 \
  --batch-size 1 --grad-accum 8 --eval-batches 100 --cache-limit-gib 2
```

Expected time: D1 about 2.9 h of training plus about 1 h of exams; D2 about 3 h plus about 2 h.
Run the selftest first.

**Failures.**
- Metal watchdog during training: relaunch the same guard command with
  `train.py --resume <run_id>`. Snapshots already saved stay valid. The owner's process-local
  `AGX_RELAX_CDM_CTXSTORE_TIMEOUT=1` fallback rules from ADHD-01 still apply.
- Crash during the snapshot exams (the final adapter and all snapshots exist): examine each
  remaining snapshot with
  `exam.py run --model <model> --adapter adapters/<run_id>/step-NNNNN`, then again with
  `--ppl-prefix none --exams adhd_new_ppl general_ppl`.
- Stop and record on resource breaches, repeated failures without progress, or any
  non-watchdog error. Do not shorten the plan, change settings or add runs.

## Analysis (fixed in advance)

For each model and each point (baseline, every snapshot, final), report:
- trained-paper and held-out-paper accuracy (`acc_norm`, the frozen scoring), their gains over
  the model's own baseline, and the trained-minus-held-out difference with a 95% paper-cluster
  bootstrap CI (5,000 replicates, seed 20261001, as in ADHD-02/03);
- ADHD and general perplexity under both protocols, as relative change from baseline;
- PubMedQA **raw** accuracy (`acc_raw`) as the reported score, with `acc_norm` alongside
  (see `docs/ISSUES.md`, 2026-10-02). Report 0.6B PubMedQA as uninformative: it answers "yes"
  to almost everything;
- general medical MCQ, psychiatry MCQ (16 items, descriptive only), validation loss at each
  snapshot step, peak memory, swap and wall time.

Write `results/ADHD04_FINDINGS.md`:
- one table per model, rows = steps, plus the two anchor comparisons (D1@500 vs R3,
  D2@500 vs ADHD-03);
- describe the curve shape (rising, saturating, falling; where the trained-minus-held-out
  difference peaks, if it does);
- report forgetting at each point. All snapshots of one run share seed and data order, so the
  points are not independent; do not test them against each other as if they were;
- no claims about other models, seeds or learning rates; one seed per model.

Update `docs/EXPERIMENTS.md` (run table), `docs/CHANGES.md` and `results/SOL6_REPORT.md` as
before, with actual authorship.
