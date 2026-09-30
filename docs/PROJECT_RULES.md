# Shared project rules

AGENTS.md and CLAUDE.md refer to this file. Read [SOL6_TASKS.md](SOL6_TASKS.md) and [QGEN.md](QGEN.md) before executing ADHD-01. Claude oversees framework design and review; each executor owns their changes and measured results.

## Attribution and reporting

- Attribute each change to the actual author. Append date, agent/model, files, reason, and verification to [CHANGES.md](CHANGES.md). Do not sign for another agent or infer unknown authorship.
- Question `generator` fields identify the actual writer and model. Experiment reports identify the executor. Git authors and committers identify the operator, not the owner by proxy.
- Distinguish proposals, observed outputs, measurements, and hypotheses. Append progress and issues to `results/SOL6_REPORT.md`; never call an unexecuted command verified.
- Maintain all public-facing content in English, including README, documentation, repository descriptions, issues, pull requests, release notes, and generated reports. User conversation can remain in Chinese.

## Execution boundaries

- Use `.venv/bin/python`; do not modify global Python or reinstall the existing environment. Download models/data only through `hf_download.py` and `pmc_adhd.py`; check `storage.py --need-gib N` first. Do not fetch resources outside the agreed taskbook.
- After code edits run `scripts/selftest.py`. Before changing `lm.py`, `exam.py`, or `train.py`, record the observed issue, reproduction, and proposed minimal fix in [ISSUES.md](ISSUES.md). Preserve measurement semantics.
- Freeze `eval/benchmark_exclusions.json`, `eval/pmc_roles.json`, and `eval/exams/*` once generated. Proposed regeneration must be recorded and reviewed by Claude before execution. Held-out paper text, questions, and perplexity text never enter training.
- Follow phase order and acceptance gates. Resolve conflicts between model/data choices and the experiment's purpose explicitly; do not alter scoring to improve results.
- Main experiments use LoRA; R2 remains paused. Before formal training check the review's swap and disk limits. Do not reboot the computer, close other apps, or control interfaces without the user's specific authorization.
- Publish only an audited snapshot through the publication procedure. The owner's complete local manifest, data, exams, and development history remain local.
