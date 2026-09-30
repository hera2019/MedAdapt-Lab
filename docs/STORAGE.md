# Storage budget and deletion policy

Updated 2026-09-30 by Codex / GPT-6. Latest preparation check: project **4.41 GiB**, system free space **109.25 GiB**. These are point-in-time measurements. Hard project budget: **25 GiB**; system reserve: **15 GiB**.

| Allocation | Initial limit |
|---|---:|
| 0.6B and possible 1.7B bf16 checkpoints | 4.5 GiB |
| Selected ADHD originals and processed text | 1.5 GiB |
| Selected benchmark partitions | 0.5 GiB |
| Environment, cache, adapters, exam records | 3 GiB |
| Temporary files and estimation buffer | 3.5 GiB |

These allocations total about 13 GiB; remaining project budget covers additional training artifacts and operating margin. The existing environment is approximately 645 MiB. One saved 0.6B full float32 checkpoint is approximately 2.22 GiB. No additional model is selected for download merely because more disk space became available.

```sh
.venv/bin/python scripts/storage.py --need-gib N
```

The check requires project usage below 25 GiB and post-allocation free disk above 15 GiB. Runtime swap or temporary allocations can exceed download estimates; monitor actual disk free space during training. APFS sharing and transient allocations mean directory totals alone do not explain all filesystem changes.

## Observed runtime boundary

The original full-parameter attempt briefly reached about 13 GiB system free space and was stopped. The project itself remained around 2.2 GiB. After user cleanup, later attempts observed approximately 82–92 GiB free space; one completed full checkpoint raised project usage to 4.41 GiB. Current R2 pause concerns Metal stability and validation acceptance, rather than disk capacity.

Opus observed heavy swap and suggested conservative formal-training thresholds: less than 1 GiB swap used before launch, record swap/disk each minute, stop when swap exceeds 4 GiB. These are project review thresholds, not official MLX hardware limits. The earlier readiness check observed about 11 GiB used swap and blocked launch. After the owner rebooted, the 2026-09-30 readiness check observed zero swap and formal baseline launch passed. That baseline was then interrupted when the first minute monitor observed 11.38 GiB swap. The evaluation-only cache fix passed a 116-item native probe at 1.98 GiB peak; approximately 5.34 GiB old swap remained afterward, so formal retry is still gated. Do not reboot or close apps automatically.

## Deletion and recovery

Mark a downloaded original/model safely deletable only after recording its source, exact revision, URL, bytes, SHA-256, purpose, filtering, licensing notes and re-download method. Keep human screening decisions before discarding dependent derived files. Preserve benchmark seals, frozen roles/exams, config, dependency lock, run indices and comparisons. Smoke artifacts may be deleted intentionally with a report entry; no artifacts were automatically removed here.
