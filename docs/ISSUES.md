# Issues and diagnostic history

English restatement: Codex / GPT-6, 2026-09-30. Original Chinese texts are archived locally. Original discoverers and reviewers remain attributed; frozen files and numerical records are unchanged.

## Corpus and evaluation fixes (Codex / GPT-6)

- **Abstract-only records:** first 383 XML contained 75 missing bodies and one body under 1,000 characters. PMC13445231 had passed on abstract/title length. Added a >=1,000 body-character check and marked 76 excluded without deleting originals. Selftest passed before freezing.
- **Earliest publication dates:** 21 of 560 initially body-qualified new records had earliest JATS dates before 2026 despite ESearch pdat matches. Excluded them, leaving 539 eligible new papers. Year does not prove the model never saw earlier versions.
- **Premature exam freezing:** original minimum was 100 questions/group, with rejection files written before count failure. Set hard minimums of 150 contributing papers and 400 valid questions/group; failed gates write no frozen output. New-fact exams have not been frozen.
- **False ADHD benchmark matches:** both old MedMCQA validation hits were non-ADHD stems with ADHD/medication distractors. Strict stem screening of 4,183 items found zero. No fake ADHD exam is created; acceptance became five background exams.
- **Near duplicates:** exact PMID/DOI/normalized-title cross-group duplicates were zero. Title-token Jaccard >=0.65 with >=5 shared tokens found three suspicious pairs, including old PMC12425290 / held-out PMC13576150. Added a hashed manual old-paper exclusion list. Keep originals; semantic duplicates remain possible.

## Disk reserve breach and cleanup (Codex / GPT-6)

Full smoke `20260929T191958Z-full-smoke-full` logged step-zero validation 2.1138, then was interrupted before a step-10 record when free disk fell from about 27 to 13 GiB. Exit 130 / KeyboardInterrupt in gradient evaluation; no final weights. Project stayed around 2.2 GiB; available space later recovered to 22–28 GiB. Initial observations did not establish the system cause. R2 paused.

The owner cleared disk and requested continuation. About 92 GiB was available before recovery. Microbatch changed from 4 x accumulation 2 to 1 x 8, preserving float32 all-parameter training, sequence 1024 and 8,192 tokens/step. Default validation then covers 25 rather than 100 windows; compare on a fixed range separately.

## Metal recovery attempts (Codex / GPT-6)

- `20260930T041136Z-full-smoke-full-resume`: step 10 train loss 2.1405284, 1,135.49 tokens/s, peak 15.58593 GiB; then Metal Impacting Interactivity, exit 1, no weights. Minimum observed disk about 82 GiB.
- The owner suspected accidentally killing an MLX server and requested restart. This task had created a training process, not an independent inference service; no causal link was established.
- `20260930T041904Z-full-smoke-full-restart`: same-config retry logged step 20, train loss 2.1046, about 1,215 tokens/s, peak 15.59 GiB; same failure. A snapshot showed 15,963.69 MiB used swap / 17% free-memory reading, insufficient alone to diagnose the watchdog.

Before editing train.py, recorded optional finite process-local cache/wired controls: negative defaults preserve behavior; reject wired values above the device recommendation. Trial limits 1 GiB cache / 20 GiB wired. No system setting, install or numerical scoring change. Selftest passed, including actual full-weight changes and saved/reloaded logits.

- `20260930T042723Z-full-smoke-full-memory`: 30 steps completed in 200.0 seconds, peak 15.67583 GiB. Default 25-window validation increased 2.521747→2.648594. Original fixed 100 windows / 102,400 tokens increased 2.1137549281→2.2403196049. Completion did not pass loss-decrease acceptance or establish 500-step stability.
- `20260930T043526Z-full-smoke-full-low-lr`: lr 5e-6, warmup 10, validate 100 windows each 10 steps; failed after step zero before logging step 10. Model/sequence/effective batch unchanged; benchmark not used for tuning.
- `20260930T043844Z-full-smoke-full-buffer`: added MLX_MAX_OPS_PER_BUFFER=1 and MLX_MAX_MB_PER_BUFFER=10. Step-10 validation 2.1110010976, 1,214.50 tokens/s, peak 14.95535 GiB; same failure, no final weights. Intermediate decrease is not completed acceptance.

Actual failure: `[METAL] Command buffer execution failed: Impacting Interactivity (0000000e:kIOGPUCommandBufferCallbackErrorImpactingInteractivity)`, exit 1. Per-run execution records retain actual parameters/environment, log hashes and outcomes as explicitly post-run reconstructions. Stopped indiscriminate retries; did not operate displays/apps or global system settings.

References: [cache control](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_cache_limit.html), [wired control](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_wired_limit.html), [MLX issue 3267](https://github.com/ml-explore/mlx/issues/3267), [buffer parameters](https://github.com/ml-explore/mlx/blob/main/mlx/utils.h).

## Opus 5.5 read-only review and decision

Reviewer: Claude / Opus 5.5, 2026-09-30, no training launched. Observed 13,275 MiB swap used of 14,336 MiB, approximately 14 GiB swap files, and files created at 13:12 Japan time during the 04:11 UTC recovery. Shared APFS storage supports swap as a plausible source of transient disk loss.

Hypothesis: full float32 model/gradients/Adam state plus other applications exhausted available unified memory; paging delayed GPU work until watchdog termination. This causal mechanism remains unconfirmed. Cache/wired settings did not reliably fix it. Repeated failures after the suspected service was gone weaken a one-off kill explanation; the killed process was never identified.

Separate hypothesis: full gradient norms around 4 versus LoRA around 0.37, clipping at 1.0, and optimizer/batch noise may relate to validation regression. Requires a separate comparison.

Decision: pause R2, continue LoRA R0/R1/R3/R4 after exam/resource gates. Suggested policy: start below 1 GiB used swap, record swap/disk each minute, stop above 4 GiB. These are project review thresholds, not official MLX limits. User controls reboots/closing apps. Later bf16, embedding-freezing and larger-accumulation variants require separate experiment labels; frozen embeddings are not the original all-parameter R2.

## English localization and approved license

Recorded by Codex / GPT-6 before core reporting edits. Owner requested English public content and approved Apache-2.0. Translate exam.py labels/verdict comparisons and selftest assertions together, preserving numeric scoring, thresholds, bootstrap/McNemar and raw metric fields. Archived prior texts locally; normalized non-text exam AST verified unchanged. Run selftest after edits. New public snapshots reject CJK; previous published history retains credential/path checks without retroactive language enforcement.

## Current formal-training readiness

Readiness check observed 11,288.75 MiB used swap, above the reviewed 1 GiB starting threshold. User was asked to prepare the system manually. At this record: 59/539 papers, 196 valid questions, no new-fact exam freeze. Continue question preparation without bypassing complete-exam or resource prerequisites. No formal baseline or LoRA R1 has started.

## Guarded LoRA launch preparation

Codex / GPT-6, 2026-09-30. Add a stdlib-only outer launcher to enforce existing formal-exam and resource gates before starting a child process, log swap/disk/project usage each minute, and interrupt only the child session if limits are breached. Keep train.py and numerical training unchanged. Validate missing-exam rejection, resource parsing/thresholds and isolation from another owned test process; run project selftest. Current preflight should refuse launch, not claim resumed training.
