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

## R0 baseline allocator growth after reboot

Recorded before edits by Codex / GPT-6 (root), 2026-09-30. Guarded R0 started at 12:31:38 UTC with zero swap, 109.25 GiB free disk and all seven frozen exams. Psychiatry MCQ completed (16 items, 31.25%, 1.3 seconds), then the first minute monitor observed 12,222,201,856 swap bytes (11.38 GiB) while scoring general MCQ. The guard interrupted only its child; exit 3, child -2. No complete baseline ledger or training exists. Preserved resource log and partial raw psychiatry results. General MCQ stems+longest option are at most 640 characters (mean 132), so giant input context is not supported by that evidence.

Installed MLX 0.32.3 documents that its free allocator cache defaults to the memory limit and is reclaimed on the next allocation only after a configured bound is exceeded. Hypothesis: varied short MCQ tensor shapes retained excessive cached allocations. Exact cause is not yet established. Minimal proposed change: bound free cache to 512 MiB only inside `run_exams`, clear it at entry/exit, restore the caller's previous limit in `finally`, and record that bound in the run summary. Keep model precision, prompt/choice tokenization, batching, per-token likelihood, character normalization, PPL windows and statistical comparisons identical. Tiny-model tests must show identical scores and restoration after success/error; a bounded native probe must remain measured rather than claimed from theory. No cache-budget change to training and no bypass of the formal swap gate.

### Cache-fix verification and remaining gate

Codex / GPT-6 (root): all selftests passed, including exactly equal tiny-model MCQ/PPL outputs and allocator-policy restoration after success/exception. Native bounded probe: 16 prior psychiatry rows exactly identical; another 100 general items scored; peak 1.983 GiB, no swap increase across ten samples. No full-model unbounded reproduction was attempted. Cache retention remains the working hypothesis. Approximately 5.34 GiB old swap still exceeds the unchanged formal launch gate; requested owner-controlled reboot. Frozen exam/source/training hashes preserved.

## Bounded R0 recovery with decaying residual swap

2026-09-30, decision by Codex / GPT-6 (root), before retry. Owner reports swap falling to about 2.5 GiB. Native observation: used swap 2,636.25 MiB (2.574 GiB), system-reported free-memory percentage 89%, no project training/evaluation process. The previous bounded native probe used 1.983 GiB peak and did not grow swap; all selftests passed. Residual swap alone is not a direct measurement of current memory pressure.

For this R0 retry only, use a documented 3 GiB starting-swap limit instead of the conservative 1 GiB suggestion, keep the absolute 4 GiB stop limit, and shorten monitoring to 10 seconds. The evaluation-only 512 MiB cache bound remains active. Do not change guard defaults, exams, scoring or model precision. This is an operational recovery decision, not evidence of full-exam stability. Check resources again before training; this decision does not automatically change training limits. Owner reboot request is no longer necessary for this bounded baseline attempt.

## Conservative wording for generated outcome interpretations

Codex / GPT-6 (root), before reporting edits. `interpret()` currently treats significant improvement in A and non-significance in B as proof of retained trained-paper knowledge, and absence of significant A accuracy gain as proof that no knowledge was learned. Those conclusions exceed the item-bootstrap/McNemar outputs: a difference between significant and non-significant results is not a tested difference in changes, and accuracy is only one outcome. Replace only those interpretation strings with conditional language and state the need for a direct group-change comparison. Label `p_correct` as a softmax share of character-normalized scores, not a calibrated clinical probability. Preserve all metric fields, numeric tests and scoring; run selftest before R1.

## R1 allocator and resource recovery decision

The complete guarded R0 finished all seven exams with swap never above 2.574 GiB, ending near 2.559 GiB. Earlier real LoRA smoke preserved the intended rank-16/all-layer, sequence-1024, batch-4/accumulation-2 configuration and used 18.21 GiB MLX peak. For R1 retain all scientific settings (500 steps, lr 2e-4 and fixed 100 validation windows), set the existing process-local free-cache option to 2 GiB, and use the documented recovery start limit 3 GiB, absolute stop 4 GiB, interval 10 seconds. Do not change guard defaults or wired limit. Bounding freed allocations does not reduce layer count, context, batch or training capacity. This is a monitored formal attempt, not a claim of long-run stability. R3/R4 require another resource check after R1.

## R1 Metal interruption without swap growth

Codex / GPT-6 (root), 2026-09-30. `20260930T134702Z-lora-r1-lora` logged step 50 (validation 2.0994375 versus 2.1142765 initially), then failed in gradient evaluation with Metal Impacting Interactivity, child/guard exit 1. Last logged step does not identify the exact failing step. Peak MLX memory 18.210 GiB; every guard sample stayed at or below 2.559 GiB swap. No final adapter/run.json/post-training exam. This failure under low, stable swap weakens swap as a complete explanation.

Rechecked upstream [MLX issue 3267](https://github.com/ml-explore/mlx/issues/3267): an issue reporter describes display-active watchdog failures even at low memory usage, and command-buffer environment limits did not resolve their case. This is an external report, not diagnosis of this machine. Previous local full-parameter buffer-bound trials also failed; do not repeat them indiscriminately.

Targeted recovery: use existing CLI microbatch 1 / accumulation 8 instead of 4 / 2, preserving 8,192 tokens per optimizer update, rank 16, all 196 target projections, sequence 1024, learning-rate schedule, 500 steps and corpus. Set eval_batches=100 with microbatch 1 to preserve the original 100 validation windows. Continue cache 2 GiB, guard start 3 / stop 4 GiB, interval 10 seconds. Smaller physical batches aim to shorten individual GPU work; stability is unproven. Token-weighted gradients preserve the intended objective; batch-shaped kernels may change floating-point rounding, so record this operational variant explicitly. No display/app/system operation. If this targeted variant fails, assess the upstream manual-display workaround rather than further blind retries.

## R1 completed and scoring-protocol diagnostic

2026-10-01 JST, Codex / GPT-6 (root). R1 recovery `20260930T135838Z-lora-r1-lora-micro1` completed 500 updates, all seven post-exams and paired comparisons; guard exit 0. Post-exam `20260930T144250Z-after-20260930T135838Z-lora-r1-lora-micro1`: trained-paper accuracy 34.680% -> 38.301% (+3.621 pp, item-bootstrap 95% CI +0.975 to +6.128); held-out-paper accuracy 32.763% -> 36.842% (+4.079 pp, CI +1.579 to +6.579). Both groups improved; this does not establish specific trained-paper retention. Medical QA accuracy changes were not significant under the existing tests. Frozen general PPL 13.642 -> 70.015 (+413.24%, CI +386.40 to +443.09%); ADHD held-out PPL 8.155 -> 27.557 (+237.91%, CI +228.71 to +246.96%). These unfavorable formal measurements remain intact.

Concrete diagnosis before further training: fresh saved-adapter reload reproduced the entire first general and first ADHD document NLL exactly; cross-entropy and negative log-probability agreed within 1.6e-7 on three identical validation windows. Re-evaluating the same 100 validation windows reproduced 2.045074110031128 exactly. No serialization/scoring-formula discrepancy was found in these checks.

The frozen PPL protocol prepends tokenizer EOS (`<|endoftext|>`, ID 151643) to every window; packed training mostly begins inside documents. On the first 1024 tokens of the two sampled documents, base NLL with/without EOS was 2.10476/2.09371 (general) and 1.78376/1.79352 (ADHD); R1 was 3.56063/2.17415 and 2.62495/1.69618. The effect persists after the first 32 tokens. This identifies strong post-training prefix sensitivity in two samples, not a complete alternative benchmark or proof that forgetting is absent. Automatic comparison text is heuristic: interpret the large formal PPL regressions as performance under the frozen EOS-prefixed protocol; broad forgetting claims require additional evidence. Diagnostic is local, separately labeled, absent from the formal ledger. Do not change frozen exams, scoring, training data or LR in response.

## R3/R4 operational decision

2026-10-01 JST, Codex / GPT-6 (root), before R3. R1 physical microbatch 1 / accumulation 8 completed 500 updates and all post-exams with 5.714 GiB peak; swap declined, without a guard breach. Native current swap is 2356.19 MiB (2.301 GiB), project 4.45 GiB and disk free 105.12 GiB. Continue preplanned R3 (new-only, 500) and R4 (full corpus, 1000) with the successful operational settings: microbatch 1, accumulation 8, 100 validation batches, 2 GiB free cache, start swap below 3 GiB, stop at 4 GiB, 10-second monitoring. Recheck resources before R4. Preserve all-layer rank 16, alpha 32, sequence 1024, effective 8192 tokens/update, original learning-rate schedule and frozen exams. Neither run is a benchmark-informed hyperparameter search. R2 stays paused; no new model/download or UI operation.

## R3 interruption and concrete recovery proposal

2026-10-01 JST, Codex / GPT-6 (root). R3 `20260930T150311Z-lora-r3-newonly-micro1` reused the complete R0 baseline, selected only the frozen new-train corpus (2,479,647 packed tokens), and used the identical successful R1 microbatch-1/accumulation-8 policy. Last logged step **40**: train loss 2.108733, MLX peak 5.714 GiB. Subsequent gradient evaluation failed with Metal Impacting Interactivity; exact failing step is not identified. Guard exit 1, no resource breach, max swap **2.301 GiB**. No final adapter, run.json, post-exam or effectiveness result. Training log, resource log and signed failure reconstruction are preserved. An earlier conversational update said 30; the completed log confirms 40 as the last logged update. R4 is not launched while this stability gate is unresolved.

Primary-source recheck: in [MLX issue 3267](https://github.com/ml-explore/mlx/issues/3267), member zcbenz suggested `AGX_RELAX_CDM_CTXSTORE_TIMEOUT=1` on 2026-03-17; the original reporter replied that it resolved their case. The member said OS behavior prevented a straightforward library fix. [Issue 3302](https://github.com/ml-explore/mlx/issues/3302) warns that the timeout override is not a permanent solution; its long-context inference workload differs from this training. Later reports on different, heavier M5 hardware do not establish safety/stability on this M2 Max. Display-off alternatives require specific owner authorization and have not been operated. No new package or model is needed for the environment-variable proposal.

Concrete proposed recovery, **awaiting owner approval**: set `AGX_RELAX_CDM_CTXSTORE_TIMEOUT=1` only in the launched training child's environment (no shell profile, global launch environment, driver installation or system-setting change); preserve the complete R3 500-step configuration, frozen baseline/exams, 2 GiB cache and 3/4 GiB swap guard at 10-second intervals. Restart from base; the failed run has no recoverable optimizer checkpoint. This relaxes a GPU timeout protective mechanism and can affect responsiveness. Memory/disk monitoring does not substitute for the GPU watchdog. If authorized and successful, resource-check before the similarly configured preplanned 1000-step R4. Do not set the override permanently or silently. Proposal is not a measured local fix.
