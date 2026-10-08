# MedAdapt Lab

**What does a small language model learn from reading new research papers, and what does it forget?**

MedAdapt Lab is a completed series of five experiments (ADHD-01 to ADHD-05, September–October 2026). It continued the training of Qwen3 Base models on openly licensed ADHD papers published after the models were released, and on 400 fictional trials whose facts no model could know. Everything ran locally on one Apple M2 Max with a hand-written MLX training loop and LoRA.

**Read the results:** [final report](results/FINAL_REPORT.md) · [project page](https://houjun.dev/lab/medadapt/)

Research only. Nothing here is medical advice, and no model trained here is fit for clinical use.

## Findings

1. **Reading leaves a small, specific trace.** After about 1.65 passes over 269 trained papers, accuracy on their questions rose 3.8–5.0 percentage points more than on questions about 270 never-trained papers (three runs). Most of the overall improvement was general familiarity with the field.
2. **Capacity limits retention.** With more reading, the 0.6B model's extra gain stayed near +4 points up to 6.6 passes. The 1.7B model's rose to +8.7 [+4.4, +12.9] at 3.3 passes.
3. **Specific recall and general benefit peak at different times.** Held-out perplexity, never-trained questions and validation loss were best at about one pass. Specific recall kept rising in the 1.7B model, so stopping at the validation minimum would stop early.
4. **Every gain had a cost.** General-text perplexity rose at every point: +7% to +123% when training on real papers.
5. **Unknowable facts are learnable, slowly.** On fictional trials (chance 25%, control stayed at chance), recall emerged abruptly between about 4 and 8 passes and ended at 44–51%.
6. **Rewording beats repetition.** At equal exposure, four different texts beat one text read four times by +4.5, +6.3 and +7.6 points (three of three runs, intervals excluding zero).
7. **Narrow new-fact training without replay is destructive.** The small, templated fictional corpus raised general perplexity 37–94×.

Details, intervals and limits: [final report](results/FINAL_REPORT.md) and the per-experiment findings ([ADHD-01](results/FINDINGS.md), [02](results/ADHD02_FINDINGS.md), [03](results/ADHD03_FINDINGS.md), [04](results/ADHD04_FINDINGS.md), [05](results/ADHD05_FINDINGS.md)).

## Design

- **Data the model cannot have seen.**
  - 539 CC0 / CC BY / CC BY-SA ADHD papers first published in 2026, split once at random into trained (269) and never-trained (270) halves.
  - 1,817 older papers for domain text.
  - ADHD-05 adds 400 fictional trials with randomly drawn facts.
- **Exams frozen before training.**
  - 1,478 evidence-checked four-option questions about the 2026 papers, written blind to the split.
  - Perplexity on held-out papers and on general WikiText.
  - Existing medical question sets as secondary measures.
  - Every item result is kept, and comparisons are paired with intervals that resample whole papers or trials.
- **A control for every claim.** A gain counts only beyond the gain on never-trained material. Validation loss guides training; the exams are only for measurement.

## What went wrong along the way

- **A collapsed attention sink.** Training stopped the model forming its position-0 "attention sink" when the input began with the end-of-text token, which made perplexity look 238–413% worse. The fix was to start every training window with that token (`scripts/sink_probe.py` checks it).
- **A length-biased score.** It made one benchmark's yes/no/maybe results misleading.
- **Data defects** found before training: abstract-only records, misdated papers, and benchmark questions that mentioned ADHD only as a wrong option.
- **GPU watchdog interruptions.** These led to checkpoint/resume.
- **No full-parameter control.** It never completed reliably on this Mac.

Each is documented in [ISSUES.md](docs/ISSUES.md).

## Repository contents

This public repository contains original source code, plans, configuration, an empty source-registration template and aggregate reports. It does **not** contain papers, benchmark or exam questions, fictional-trial records or texts, frozen sample lists, model weights, adapters, environments or detailed local run records. A fresh clone is the framework, not a copy of the experiment's data.

| Path | Purpose |
|---|---|
| `scripts/lm.py`, `scripts/train.py` | Hand-written LoRA, packing, loss, training loop, checkpoints, snapshots |
| `scripts/exam.py`, `scripts/build_exams.py` | Frozen exams, ledger and paired comparisons |
| `scripts/pmc_adhd.py`, `scripts/prepare_dapt.py`, `scripts/seal_benchmarks.py` | Licensed paper collection, screening, splitting, leakage checks |
| `scripts/synth_trials.py`, `scripts/synth_report.py` | ADHD-05 fictional-trial generator, text validator and fixed analysis |
| `scripts/sink_probe.py`, `scripts/selftest.py` | Attention-sink diagnostic; offline end-to-end selftest with a tiny random model |
| `experiments/` | Configurations and declared plans per experiment |
| `results/` | Aggregate findings reports and the final report |
| `docs/` | Design, data, models, issues, change log with actual authorship |

## Running it

Apple Silicon Mac, Python 3, MLX. Fresh setup and pinned model revisions are in [MODELS.md](docs/MODELS.md).

```sh
.venv/bin/python scripts/selftest.py          # offline check, no downloads
# Then: download pinned files, seal benchmarks, fetch licensed papers, freeze roles,
# write and validate exams, prepare data, and train with before/after exams:
.venv/bin/python scripts/train.py --name first
```

The full procedure with acceptance criteria is in the [taskbook](docs/SOL6_TASKS.md).

## Who did what

- Design, core training and measurement code, and reviews: Claude (Anthropic, Claude Opus 5.5).
- Data collection, question writing, execution and per-experiment analysis: Codex / GPT-6 ("Sol").
- Commissioned and directed by the repository owner.

Every change is attributed in [CHANGES.md](docs/CHANGES.md).

## License

Original code, configuration and documentation: **[Apache License 2.0](LICENSE)**. Papers, benchmarks and models keep their own terms; see [NOTICE](NOTICE) and [resource licensing](docs/LICENSES.md).
