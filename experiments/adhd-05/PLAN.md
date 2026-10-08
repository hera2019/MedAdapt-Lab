# ADHD-05 training plan: learning fictional trials

Plan author: Claude (reviewer, Claude Opus 5.5), 2026-10-03, written after reviewing the data and
before any ADHD-05 training. Executor: Sol (Codex / GPT-6). The owner asked for this experiment.

## Data review (Claude)

- `synth_trials.py stats`: 300 / 300 pass.
- Spot reading confirms that every fact appears word for word and that nothing was invented.
- **Limitation:** the texts are heavily templated. About 65–71% of each text's 6-word sequences
  recur in 30 or more other trials. Each genre is in effect one template with the facts filled
  in, padded with generic sentences.
- This matches the standard synthetic-biography paradigm (multiple templates per entity), so
  "P = four templates once each" versus "R = one template four times" is a meaningful contrast.
- Results must be read as recall of templated statements, not of natural prose.
- The texts call each trial "fictional". That is harmless for the measurement and good for safety.
- Accepted.

## Questions

1. Does reading make the model recall facts it could not know? Measured by P and R against
   the never-described control C, whose baseline is chance (25%).
2. Is reading four different texts better than reading one text four times, at the same
   exposure (P vs R)? This is the ADHD-02 question, asked cleanly.
3. How does recall grow with exposure, and does model size change that (0.6B vs 1.7B)?
4. What does it cost in general-text perplexity?

## Corpus and exams (built and frozen by Claude; do not regenerate)

- `data/train/adhd-05/train.jsonl`, built with `synth_trials.py build-corpus`. Hashes are in
  `corpus_manifest.json`.
  - 1,200 documents: P trials contribute their four texts; R trials contribute one text (genre
    rotated by trial number) four times.
  - The documents are shuffled so copies of a trial are at least 8 documents apart.
  - About 238,900 stream tokens, about 29 updates per pass. Every fact appears 4 times per pass.
- Exams: `eval/synthetic/exams/index.json`.
  - `synth_paraphrased` 1,350, `synth_repeated` 1,350 and `synth_control` 900 four-option
    questions (9 per trial).
  - `general_ppl` is linked from the frozen ADHD-01 exams to measure forgetting.
  - Baselines are taken automatically for each model.

## Runs (fixed in advance)

| Run | Model | Seed | Steps | Snapshots | Passes at snapshots / final |
|---|---|---:|---:|---|---|
| S1 | Qwen3-0.6B-Base | 42 | 600 | 30, 60, 120, 240 | ≈1, 2, 4, 8 / 20.5 |
| S2 | Qwen3-1.7B-Base | 42 | 600 | 30, 60, 120, 240 | same |
| S3 | Qwen3-0.6B-Base | 43 | 600 | 30, 60, 120, 240 | same (seed replication) |

All other settings are as in ADHD-03/04: LoRA rank 16 / alpha 32 / dropout 0 on all layers,
sequence 1024, EOS-prefixed windows, micro-batch 1 × accumulation 8, peak lr 2e-4, warmup 30,
cosine to 10%, checkpoint every 50, cache 2 GiB. Validation uses the usual pool-validation text
(real ADHD papers) with 100 windows every 50 steps. It measures real-text drift, not
fictional-trial learning.

```sh
.venv/bin/python scripts/selftest.py
.venv/bin/python scripts/train.py --name adhd05-s1-06b --model models/qwen3-0.6b-base \
  --train data/train/adhd-05/train.jsonl --exam-index eval/synthetic/exams/index.json \
  --iters 600 --snapshot-steps 30,60,120,240 --seed 42 \
  --batch-size 1 --grad-accum 8 --eval-batches 100 --cache-limit-gib 2
# S2: --name adhd05-s2-17b --model models/qwen3-1.7b-base (otherwise identical)
# S3: --name adhd05-s3-06b-seed43 --seed 43 (otherwise as S1)
```

Run them in the order S1, S2, S3 under the usual guard (launch below 3 GiB swap, stop at 4 GiB,
check every 10 seconds) with task-bound `caffeinate`. Expected time is about 1.7 h each for S1
and S3 and about 3.2 h for S2. Failure handling follows ADHD-04 (resume from checkpoint; the
process-local AGX fallback only after a watchdog failure). Do not change settings, add runs or
choose anything from intermediate results.

## Analysis (fixed in advance)

After each run: `.venv/bin/python scripts/synth_report.py <run_id>`. It writes
`results/adhd05/<run_id>.md` and `.json` with:
- accuracy per group;
- P−R, P−C and R−C gain contrasts with trial-cluster intervals;
- the log-probability margin metric;
- raw accuracy;
- general-perplexity change;
- final accuracy by fact type.

Do not alter the script. If it fails, record the error and stop.

Then write `results/ADHD05_FINDINGS.md`:
- one table per run, taken from the reports;
- answer the four questions, stating plainly when an interval includes zero;
- S1 vs S3 shows the seed spread, and S1 vs S2 is descriptive only (one seed each);
- the templating limitation above; snapshots are dependent and not annealed (as in ADHD-04);
- C may rise above 25% if the model learns the answer pools. That is format learning, and P−C
  and R−C remove it.

Signed rows in `docs/CHANGES.md` and `results/SOL6_REPORT.md` as usual.

**Fictional data stays local.** Do not publish trial records, texts, exam items or per-item
results, in GitHub or anywhere else. Aggregate tables in the findings report may be published
under the existing public-snapshot audit.
