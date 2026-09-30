# MedAdapt Lab

**Medical Domain Adaptation Laboratory** — local experiments to measure what domain-adaptive pretraining (DAPT) changes in a language model.

The first experiment, **ADHD-01**, uses openly licensed ADHD papers and Qwen3 Base models on Apple Silicon. It evaluates specific paper knowledge, familiarity with unseen domain text, and general-language forgetting.

## Current status

- Data splits and all seven exams are frozen in the owner's local experiment. All 539 paper records were validated; A/B exams contain 718 and 760 questions.
- Qwen3-0.6B-Base LoRA completed a 30-step smoke run. This is an engineering check, not a formal effectiveness result.
- Full-parameter training is paused: several attempts encountered Metal errors; one completed run increased fixed-range validation loss.
- Full R0 and 500-step R1 LoRA are complete. Both paper-question groups improved; frozen EOS-prefixed PPL regressed sharply. Local scoring checks identify prefix sensitivity in two samples, limiting broad forgetting claims. R3 then failed with a Metal watchdog error after its step-40 log; R4 awaits resolution. A child-process timeout workaround requires owner approval; see the aggregate report.

## Experiment design

1. Split eligible 2026 papers once by PMCID into `new_train` and `new_heldout`, using seed 42. Held-out papers never enter training.
2. Write paper-specific multiple-choice questions with verbatim evidence. Group A uses trained papers; group B uses unseen papers. Apply identical writing and validation rules while hiding group identities.
3. Measure held-out ADHD perplexity and general WikiText perplexity alongside knowledge exams. Existing MedMCQA and PubMedQA exams provide secondary transfer observations.
4. Preserve baseline and post-training raw results, paired metrics, 95% confidence intervals, changed questions, and a comparison ledger. Tune on training validation loss, not benchmark answers.

Publication dates reduce possible pretraining overlap but do not prove that related preprints or duplicated findings were absent from the original model. Public medical QA benchmarks may already have appeared in pretraining.

## Hardware and model plan

Apple M2 Max, 32 GB unified memory. Project budget: **25 GiB**; minimum system free space: **15 GiB**.

| Stage | Model | Plan |
|---|---|---|
| Initial | Qwen3-0.6B-Base, bf16 | LoRA main experiments; full-parameter R2 paused |
| Later | Qwen3-1.7B-Base, bf16 | Revisit after the initial experiment and resource review |
| Deferred | 8B / 14B Base in MLX | Verify provenance and practical training capacity first |

Existing VoxStage 14B and 30B GGUF models are post-trained inference models. They are not used as Base DAPT checkpoints. See [MODELS.md](docs/MODELS.md).

## Repository contents

This public repository contains original source code, plans, configuration, an empty download-registration template, and aggregate engineering reports. It does **not** distribute papers, benchmark questions, evidence-bearing questions, frozen local sample lists, model weights, adapters, environments, caches, or detailed local run records. A fresh clone is not a data copy of the owner's experiment.

| Directory | Purpose |
|---|---|
| `scripts/` | Downloading, filtering, packing, training, exams, and selftests |
| `data/raw`, `data/processed` | Local source files and paper metadata |
| `data/train`, `data/validation`, `data/test` | Isolated local training, validation, and benchmark data |
| `models/`, `adapters/` | Local weights and training artifacts |
| `eval/` | Local frozen roles, evidence questions, and exam files |
| `experiments/adhd-01/` | Configuration, dependency lock, split and run records |
| `results/` | Aggregate reports and local exam ledger |
| `manifest.json` | Source catalog; local downloads are registered after acquisition |

## Workflow

Use the project-local environment. Existing installations need no dependency reinstallation. Fresh setup is described in [MODELS.md](docs/MODELS.md).

```sh
.venv/bin/python scripts/selftest.py
# Download exact revisions, seal benchmarks, fetch licensed PMC papers,
# freeze roles, prepare training data, and write/validate the complete exams.
.venv/bin/python scripts/prepare_dapt.py
.venv/bin/python scripts/build_exams.py
# Only after both complete new-fact exams meet their minimum gates:
.venv/bin/python scripts/resource_guard.py \
  --log experiments/adhd-01/runs/first-resources.jsonl \
  -- .venv/bin/python scripts/train.py --name first
```

Follow [the taskbook](docs/SOL6_TASKS.md) for commands and acceptance criteria. Do not regenerate existing frozen files in an ongoing experiment.

## License and use

Original project code, configuration, and documentation are licensed under the **[Apache License 2.0](LICENSE)**. Third-party data and models retain their own terms; this license does not cover them. See [NOTICE](NOTICE) and [resource licensing](docs/LICENSES.md).

Research use only. The framework and its QA scores do not establish clinical suitability or provide medical advice.

## Documentation

[Experiment](docs/EXPERIMENTS.md) · [Taskbook](docs/SOL6_TASKS.md) · [Question writing](docs/QGEN.md) · [Datasets](docs/DATASETS.md) · [Models](docs/MODELS.md) · [Storage](docs/STORAGE.md) · [Publication](docs/PUBLICATION.md) · [Review response](docs/REVIEW_RESPONSE.md)

All future public-facing content is maintained in English. Agent contributions are recorded in [CHANGES.md](docs/CHANGES.md).
