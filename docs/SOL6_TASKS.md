# Sol 6 taskbook: ADHD-01 execution

Framework/review lead: Claude. Execution: Sol 6 / the actual identified agent. Read README, EXPERIMENTS.md and QGEN.md. Run from the project root using `.venv/bin/python`.

## Rules

- Preserve core semantics in `lm.py`, `exam.py`, `train.py`. Record bugs and minimal proposed fixes in ISSUES.md before changes, then run selftest.
- Generate benchmark exclusions, paper roles and exams once. Record and refer proposed rebuilds to the reviewer.
- Held-out paper text, questions and perplexity texts never enter training.
- Download only through the agreed scripts and inspect storage before acquisition.
- Append actual quantities, time, failures and operator attribution to `results/SOL6_REPORT.md` at each phase. All public content is English.

## Phase 0: environment and selftest

```sh
.venv/bin/python scripts/selftest.py
```

Require `all selftests passed`. Existing MLX 0.32.3 / mlx-lm 0.31.3 environment is installed; dependencies are locked in `experiments/adhd-01/requirements.lock.txt`.

## Phase 1: pinned model and evaluation files

Inspect current upstream revision first. If it differs, explicitly record the revision selected for this experiment.

| source_id | Recorded revision | Approximate selected size |
|---|---|---|
| medmcqa | `91c6572c454088bf71b679ad90aa8dffcd0d5868` | Tens of MB |
| pubmedqa-labeled | `9001f2853fb87cab8d220904e0de81ac6973b318` | About 1 MB |
| wikitext-103-test | `b08601e04326c79dfdd32d625aee71d232d685c3` | About 0.7 MB |
| qwen3-0.6b-base | `da87bfb608c14b7cf20ba1ce41287e8de496c0cd` | About 1.15 GB |

```sh
.venv/bin/python scripts/hf_download.py medmcqa --inspect
.venv/bin/python scripts/hf_download.py medmcqa --revision <commit>
# Repeat for the other selected sources after storage checks.
```

Acceptance: local manifest registers every downloaded file's SHA-256 and model weights exist. These artifacts are absent from public clones.

## Phase 2: seal benchmarks

```sh
.venv/bin/python scripts/seal_benchmarks.py \
  --medmcqa data/test/medmcqa/data/validation-*.parquet data/test/medmcqa/data/test-*.parquet \
  --pubmedqa data/test/pubmedqa/pqa_labeled/*.parquet
```

Acceptance: `eval/benchmark_exclusions.json` exists with `sealed=true`. Do not rerun on an already frozen experiment.

## Phase 3: PMC papers

```sh
.venv/bin/python scripts/pmc_adhd.py discover --set new --limit 1000
.venv/bin/python scripts/pmc_adhd.py fetch --set new --limit 1000 --max-total-mib 800
.venv/bin/python scripts/pmc_adhd.py assign-roles
.venv/bin/python scripts/pmc_adhd.py discover --set pool --limit 5000
.venv/bin/python scripts/pmc_adhd.py fetch --set pool --limit 3000 --max-total-mib 1500
```

Single-threaded fetches pause between papers and resume by skipping processed identities. Record license/body/date rejections and inspect five metadata records per set. Freeze new roles only after the selected new-paper fetch completes.

Acceptance: at least 300 usable new papers, 1,500 usable pool papers, and frozen roles. Local execution reached 539 new and 1,817 pool papers before three additional manual exclusions.

## Phase 4: training data and background exams

```sh
.venv/bin/python scripts/prepare_dapt.py
.venv/bin/python scripts/build_exams.py
.venv/bin/python scripts/build_exams.py --status
```

Acceptance revised after actual screening: nonempty `train_new_pmcids` and five nonempty background exams. Strict MedMCQA ADHD stem screening found zero suitable validation questions, so no sixth fake ADHD exam is created. Record that limitation.

## Phase 5: smoke training

Historical commands:

```sh
.venv/bin/python scripts/train.py --skip-exam --iters 30 --name smoke
# R2 is paused; do not run the historical full command now:
# .venv/bin/python scripts/train.py --skip-exam --iters 30 --mode full --lr 2e-5 --name smoke-full
```

Acceptance: decreasing validation loss, no error, recorded throughput and peak memory. Label artifacts as smoke outputs, not formal experiment results. LoRA passed. Full-parameter attempts encountered a disk reserve breach initially and Metal failures later; one completion regressed on fixed validation windows. Full-parameter acceptance remains unmet.

Review decision: **pause R2; LoRA does not wait for a full-parameter fix**. Before formal training, read swap/disk state; suggested starting swap limit is 1 GiB, stop limit 4 GiB with minute-by-minute records. These are conservative project thresholds. The user prepares/reboots the system manually; agents do not close apps or reboot automatically. The swap hypothesis is not a confirmed diagnosis.

## Phase 6: write the new-fact exams

Apply QGEN.md uniformly in hidden-group queue order. Complete and check the queued paper records, with at least 150 contributing papers per group, then:

```sh
.venv/bin/python scripts/qgen_helper.py stats
.venv/bin/python scripts/build_exams.py --with-newfacts
```

Run the freeze command only once, after all prerequisites are satisfied. Acceptance: at least 400 valid questions per group; under 10% rejected. Target approximately 600 per group.

## Phase 7: formal experiments

Prerequisites: complete, frozen A/B exams and a ready monitored environment. Do not launch before these gates. The mainline is R0/R1/R3/R4; R2 remains paused.

```sh
.venv/bin/python scripts/exam.py run --model models/qwen3-0.6b-base --label baseline
.venv/bin/python scripts/train.py --name r1-lora
.venv/bin/python scripts/train.py --name r3-newonly --train data/train/adhd-01/train_new.jsonl
.venv/bin/python scripts/train.py --name r4-lora-x2 --iters 1000
```

Every training ends with exams and a comparison report. For cross-run comparisons use `exam.py compare`. R3's selected-corpus hash is in the split record. Only after review, consider 1.7B revision `ea980cb0a6c2ae4b936e82123acc929f1cec04c1` (about 3.3 GB) and repeat R0/R1.

Acceptance: baseline and every post-training exam appear in EXAM_LOG.md, with raw results and paired comparisons.

### Guarded formal launch

Use the outer launcher for formal training; it enforces frozen A/B exam hashes/counts and resource thresholds before spawning. Give each launch a new local log path:

```sh
.venv/bin/python scripts/resource_guard.py \
  --log experiments/adhd-01/runs/guard-r1/resources.jsonl \
  -- .venv/bin/python scripts/train.py --name r1-lora
```

`--check-only` records readiness without spawning. Default logging interval is 60 seconds. Breached limits interrupt only the launcher's own child/session; outcomes and resource records remain local. `--smoke` explicitly bypasses the exam gate only for diagnostic runs, not formal experiments. Do not override review thresholds without recording the decision.

## Phase 8: findings

Answer the four experiment questions in `results/FINDINGS.md`, citing actual run IDs and comparison numbers. Report no significant difference when appropriate. Keep hypotheses separate from measured results. Do not write scientific conclusions for runs that do not exist.
