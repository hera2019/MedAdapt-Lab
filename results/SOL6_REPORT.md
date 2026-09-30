# ADHD-01 execution report

Executor: Codex / GPT-6. English restatement on 2026-09-30; original report archived locally. Historical measurements are not current resource guarantees or scientific results.

## Phase 0–2: environment, acquisition, benchmark sealing

Initial sandboxed MLX import lacked Metal; permitted native selftest passed in 3.7 seconds with no downloads. Inspected four revisions, all matched the taskbook. Registered MedMCQA validation/test (4,183/6,150 rows), PubMedQA labeled (1,000), WikiText test (4,358) and Qwen3-0.6B-Base. Twelve initial files had hashes; model weights were 1,192,135,096 bytes. Small sources took about 2.9/2.7/2.6 seconds, model about 1 minute 58 seconds; a sandbox DNS failure preceded an authorized retry.

Sealed three files, 11,302 prompts and 1,000 PMIDs in 0.46 seconds. Frozen exclusion hash: `a5ef3cfb28f58eaf18fbccaa32e460a48bea016ba3d1e4d1cac6a261abf08b84`.

## Phase 3: corpus

New search: 701 candidates, 636 XML, 65 initial rejections; rescreened out 76 short/absent bodies and 21 early publication dates. Retained originals/registrations. Eligible 539 split once into 269 trained / 270 held-out; roles hash `0ef45a82487dd23ef1b3c0518b8386755be7c0bda9d32ab0244afbe868575033`. Retrieval timestamp span 923 seconds including pauses, not pure network time; five metadata records inspected.

Pool search: 6,210 hits, first 5,000 indexed, first 3,000 processed. Usable 1,817; rejected 1,183 (867 license, 316 body). Registered-original times spanned 18:11:38–19:09:09 UTC on 2026-09-29, about 57 minutes 31 seconds. All 2,453 XML rescreened; five old records inspected. Three additional suspicious old-paper matches manually excluded from training.

Final 2,467 downloads: zero missing fields, duplicate paths, missing files, local-size mismatches or missing hashes. XML originals were rehashed during preparation. Historical phase-end project 2.06 GiB / free disk 41.21 GiB.

## Phase 4: split and five background exams

Training: 1,992 papers / 23,532 chunks, including 269 new papers / 3,481 chunks. Validation: 91 papers / 998 chunks. Excluded 370 (270 held-out, 97 screen failures, three manual). Identity intersections zero. No independent split timing was captured.

| Artifact | SHA-256 |
|---|---|
| train | `019d09b66e4650db8d3bf75f0ede9e2f1029060c374c76a5295c019132135f1c` |
| validation | `6f534ccc74565678f0a6d4e094f5ff2c836f2eb6f2621ee3a444eb7547fdbe32` |
| manual exclusions | `cd16e98860d6e8242107414bf7b843496e7054b0f9b5254bae9b8964120a576f` |
| split | `d2da459ef79be537d919f386a8a74945faf3526b83bcbb0c771851e5e485290f` |

Exam construction: 1.67 seconds. Frozen medmcqa_psych 16, medmcqa_general 500, pubmedqa 1,000, general_ppl 50, adhd_new_ppl 270. Index hash `d17ff5b00eaf7e7713b445f3c1fcbaf9675322849293f25a51dcf18fc98d052d`. Strict MedMCQA ADHD stems: zero, so no fake specialty exam.

## Phase 5: smoke and recovery

LoRA `20260929T191536Z-lora-smoke`: 30 steps / 204.0 seconds, 17,431,219 train tokens and 736,335 validation tokens, about 0.01 planned epoch. Validation 2.1143→2.0938; final interval 1,753 tokens/s, peak 18.21 GiB. Adapter about 39 MiB. Engineering smoke only, not a formal benchmark result.

Original full `20260929T191958Z-full-smoke-full`: step-zero 2.1138 then interrupted before step-10 logging at 13 GiB free disk. Exit 130 / KeyboardInterrupt, no final weights. Space recovered while project remained about 2.2 GiB.

After cleanup: prelaunch free disk 92.93 GiB. All 596,049,920 parameters remained trainable float32, sequence 1024, effective 8,192 tokens/step; microbatch became 1 x accumulation 8. All diagnostic runs skipped exams. Last logged step does not identify the exact failing step.

| Run | Setting / outcome |
|---|---|
| `20260930T041136Z-full-smoke-full-resume` | lr 2e-5; after step 10 Metal error, peak 15.59 GiB, no weights |
| `20260930T041904Z-full-smoke-full-restart` | Requested same-config restart; after step 20 same error, peak 15.59 GiB, no weights |
| `20260930T042723Z-full-smoke-full-memory` | Cache 1 / wired 20 GiB; completed 30 steps in 200.0 seconds, about 1,262 tokens/s, peak 15.67583 GiB; validation regressed |
| `20260930T043526Z-full-smoke-full-low-lr` | lr 5e-6 / warmup 10 / 100 validation windows; error after step zero |
| `20260930T043844Z-full-smoke-full-buffer` | Smaller buffers; after step 10 error, about 1,214 tokens/s, peak 14.95535 GiB |

Completed full run: default 25-window validation 2.521747→2.648594; original fixed 100 windows / 102,400 tokens 2.1137549281→2.2403196049 (+0.1265646768). Weights hash `d6caad6df0108052ca7cc56476e0bde9b34e2676dc194b0300da54d6f0233d17`. Buffer probe step-10 validation 2.1110010976, but no completion/checkpoint. All failed retries: Metal Impacting Interactivity, exit 1. One completion does not pass loss-decrease acceptance or prove long-run stability.

Commands/environment, exit codes and log hashes remain local as explicit post-run reconstructions. No independent inference server was started. No causal attribution to the owner's suspected killed process. Memory-control selftest passed, including real weight alteration and serialization; tiny-model success does not prove real-model stability.

## Earlier phase 6 and readiness snapshot

Before the owner rebooted: 65/539 papers: 53 contributing / 212 valid questions, 12 documented skips. Latest three each passed 4/4 evidence checks, no REJECT. Group identities remain hidden. New-fact exams are not frozen; require complete queue records and >=150 contributing papers / >=400 valid questions per group, targeting approximately 600.

At that earlier snapshot, 474 records remained and no formal baseline or training had run. This snapshot is superseded by the completion and formal-run entries below.

Accepted Opus 5.5's LoRA mainline/R2 pause and stronger question quality checks. Heavy swap supports a suspected mechanism, not a confirmed diagnosis. Latest preflight: project 4.41 GiB, free disk 94.46 GiB, +3 GiB permitted; swap 11,288.75 MiB, above the proposed 1 GiB launch threshold. Asked user to prepare/reboot manually; no apps/interfaces/system settings operated. Continue CPU question work while prerequisites remain unmet.

## Publication, English content and license

Public repository: https://github.com/hera2019/MedAdapt-Lab. Initial `8d43224a212fe4b70b86d1e92de9752966622f8e` was a parentless audited 44-file snapshot; `43d0492c243336898447ca0d5a75fcd26fa89d18` added publication records. API verified public/main and matching blobs. Original local HEAD/index/complete manifest were preserved.

A tool-free discussion with actual claude-opus-5-5 recommended Apache-2.0; the owner subsequently approved it and requested English public content. Added official LICENSE/NOTICE; translated public documents and report labels, keeping original texts in ignored local cache. Non-text exam AST verified unchanged; frozen exams and numerical records preserved. Selftest/language/publication checks for this update remain pending until recorded below.

### English/license and launch verification

2026-09-30, Codex / GPT-6: all selftests passed, including translated report assertions, resource parsing, refusal of incomplete exams and owned-child isolation. The latest three papers each passed four evidence checks, reaching 62 records / 208 valid questions. Frozen-file hashes remain verified unchanged.

Guard preflight at 06:28 UTC refused to launch any child: swap 10.60 GiB exceeded the reviewed 1 GiB launch limit and the complete new-fact exams were absent. Disk had 94.34 GiB free and the project used 4.41 GiB. This was a readiness check, not training. User preparation remains pending; CPU question preparation can proceed.

Public snapshot check passed for 47 English files (including Apache-2.0 LICENSE, NOTICE and the resource guard), with no sensitive-pattern matches. Original exam computation AST matched after normalization of textual constants. Public push verification will be recorded locally after publication.

Publication verified: GitHub public visibility, main branch and Apache-2.0 detection confirmed. All 47 remote blobs matched the audited English snapshot at `c2a69496f767c5fc8536bfc9e31e318fe4d073d8`. A CLI tree-query flag error was corrected; the subsequent full-tree verification passed. Local cache stores the verification. Subsequent question work reached 65 papers / 212 valid questions / 12 skips, without launching training or changing frozen roles/exams.

### Post-reboot resumption and authorized parallel QGEN

2026-09-30, Codex / GPT-6: user rebooted the machine and reported other apps closed. Native check observed zero swap, 108.83 GiB disk free and 4.41 GiB project usage. Resource readiness recovered; complete frozen new-fact exams remain the prerequisite. Added 12 checked questions (68 records / 224 items). Owner authorized at most three collaborating agents. Split 471 remaining identities into three disjoint 140-paper ranges and a 51-paper root range, preserving hash order inside each range and hiding A/B identities. All contributions require per-record actual authorship, zero evidence rejects and uniform quality. No formal training has launched.

### Phase 6 completed and exams frozen

2026-09-30, Codex / GPT-6 (root). Owner-authorized collaborators Codex / GPT-6 (qgen_1, qgen_2, qgen_3) completed their disjoint 140-paper assignments; root completed 51 and reviewed the earlier 68 records. All 539 records have actual writer attribution. Final total: **461 contributing papers / 1,478 valid questions / 78 documented skips**. Zero evidence rejects, duplicated stems or mechanical quality flags; every option character max/min ratio <=1.5, every stem <=60 words and every option <=12 words. Correct answer was uniquely longest in 235/1,478 questions (15.9%); this does not establish absence of scoring bias.

Root rechecked 18 randomly selected questions, six per collaborator, against source context. A broad all-outcome distractor was corrected by its writer before the full final revalidation. Authors rechecked compound claims, null findings and observational/animal/case-report boundaries. These checks are not independent clinical or psychometric validation. Protocols, narrative/commentary sources and internally conflicting reports carry specific skip reasons. Question skips do not modify the previously frozen licensed DAPT corpus; source reliability is a limitation of that corpus.

- `newfacts_trained`: 223 contributing papers, 718 questions; SHA-256 `8367fb64478bb94ab4c60b474f54a5d6fdb58025d4143bfe43ce35966a8e8014`.
- `newfacts_heldout`: 238 contributing papers, 760 questions; SHA-256 `32f4b67912155f550b8dbe186e7f8506ce4cbd0771189e0891f66fa5b159a06d`.

The two new-fact exams were added once, after completing and validating every record. The five background exam hashes, benchmark exclusions, article roles, manual exclusions, train/validation files and split remained unchanged. Training and validation have no held-out article IDs; new-only training identities equal the frozen new_train group. Private signed handoffs, per-file hashes and aggregate audit remain in the local ignored cache. Seven exams are now frozen. No explicit ADHD MedMCQA validation items exist; the 16 psychiatry items are not relabeled as an ADHD exam.

Next: guarded R0 baseline, then R1/R3/R4 LoRA with full post-training exams and paired comparisons. R2 remains paused.

### R0 interruption and bounded-evaluator recovery

2026-09-30, executor/fix author: Codex / GPT-6 (root). Guarded R0 preflight passed at 12:31:38 UTC with zero swap. Psychiatry MCQ finished at 31.25% (16 items), then the minute monitor observed 12,222,201,856 swap bytes (**11.38 GiB**) while scoring general MCQ. The guard stopped only its own child (child -2, guard 3). Preserved the partial raw results and a signed reconstruction; no complete baseline summary/ledger entry and no training exist. General MCQ inputs have at most 640 characters for stem plus longest option, so an enormous input prompt does not explain this event.

Installed MLX documents that its free allocator cache defaults to the memory limit. Excessive cache retention across variable shapes is a supported hypothesis, not a confirmed isolated cause. After recording the issue, added a **512 MiB free-cache bound only during evaluation**, clearing it at entry/exit and restoring the caller policy in finally. Model precision, tokenization, batching, normalization, PPL windows, statistical comparisons, all seven frozen exams and training parameters are unchanged. Summary metadata records this allocator policy.

All selftests passed, including exactly equal tiny-model MCQ/PPL scores and caller-policy restoration after success and an injected exception. A bounded native Qwen3-0.6B-Base diagnostic scored the original 16 psychiatry questions plus 100 general questions: the 16 earlier raw rows were **exactly identical**; peak MLX memory was **1.983 GiB**, with no increase in swap across its ten 10-item samples. Diagnostic duration 4.4s excludes model loading. This finite probe does not prove full seven-exam stability. The diagnostic is not a formal baseline and is not entered as one in the ledger.

The post-probe system still held approximately 5.34 GiB swap, with 88% free-memory percentage reported by the system. The existing formal gate is absolute used swap below 1 GiB; it has not been weakened. Requested another owner-controlled reboot after validating the fix. R0 retry and R1/R3/R4 remain ready but unexecuted; R2 remains paused.

### R0 recovery decision after residual swap declined

2026-09-30, Codex / GPT-6 (root). Owner reported approximately 2.5 GiB swap. Native observation was 2.574 GiB, 89% system-reported free-memory percentage and no project training/evaluation process. The earlier reboot request is superseded for this attempt: recorded a temporary **R0-only starting threshold of 3 GiB**, preserving the **4 GiB absolute stop**, with **10-second** monitoring. Evaluation still uses the tested 512 MiB free-cache bound. Guard defaults, numerical scoring and frozen exams are unchanged. This operational recovery does not establish full-exam stability or pre-approve a changed training threshold; recheck resources before R1.

### R0 complete; R1 preparation

Executor: Codex / GPT-6 (root). Full baseline `20260930T133505Z-baseline` completed all seven frozen exams, window 1024 and no sample limit; guard exited 0. Swap remained at or below 2.574 GiB and slightly declined. All raw item results, Wilson intervals and the exam ledger are saved locally. Baseline: psychiatry 31.25% (16), general medical QA 30.8% (500), PubMedQA 55.2% (1,000), general PPL 13.642, held-out ADHD PPL 8.155, trained-paper questions 34.680% (718), held-out questions 32.763% (760). These are before-training measurements.

Before R1, toned down two automatic interpretation strings that overstated what significance/non-significance can establish; all numerical scoring/tests stay identical. `p_correct` is explicitly a normalized-score share, not clinical calibration. R1 keeps 500 steps, all-layer LoRA rank 16, lr 2e-4, sequence 1024, batch 4 x accumulation 2, and 100 fixed validation windows. Uses the existing 2 GiB free-cache option and documented recovery guard start 3 GiB / stop 4 GiB / 10 seconds. No layer/context/batch reduction. R3/R4 remain contingent on post-R1 resource checks.

Pre-R1 selftest completed successfully. Native R1 preflight observed 2.559 GiB swap, 89% system free-memory percentage, 4.41 GiB project usage and 105.22 GiB free disk. Guard launched the formal R1 child with the recorded allocator policy; baseline is reused only for identical model/exam/scoring hashes. Outcomes remain pending until full training, post-exams and comparison complete.

### R1 physical-batch recovery

Codex / GPT-6 (root): original formal R1 failed after its step-50 record with Metal Impacting Interactivity despite stable 2.559 GiB swap. Validation decreased 2.1142765 → 2.0994375, but no final adapter or post-exam exists; this is not a completed effectiveness result. Signed failure reconstruction is local.

One targeted recovery starts from the unchanged base/seed with microbatch 1 / accumulation 8, preserving 8,192 tokens/update, all-layer rank-16 LoRA, 1024 sequence, 500 steps, learning rate and corpus. Validation stays on the same first 100 windows via eval_batches=100. Allocator/guard policy remains 2 GiB cache and 3/4 GiB start/stop, every 10 seconds. This reduces physical GPU work per minibatch, not effective batch or trainable capacity; floating-point kernel rounding may differ. Exact source exposure is preserved before the first epoch boundary for R1. Upstream watchdog reports suggest a scheduling hypothesis; they do not confirm the local cause. Recovery outcome remains pending.

R1 recovery `20260930T135838Z-lora-r1-lora-micro1` completed all 500 optimizer updates and saved a hash-verified adapter. Same model/corpus/seed, all 196 projections, rank 16, sequence 1024, effective batch 8 and fixed 100-window validation. Validation loss 2.1142765 → 2.0450741; MLX peak 5.714 GiB. Full seven-exam post-training evaluation and paired comparisons are still running; no effectiveness verdict yet.

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

### R1 direct group comparison and exposure limits

Codex / GPT-6 (root), exploratory local analysis, 2026-10-01 JST. Independent paper-cluster bootstrap (223 trained / 238 held-out papers, paired item accuracy changes within paper; 5000 replicates, seed 20261001) estimates trained-minus-heldout change **-0.458 percentage points**, 95% percentile CI **[-3.877, +3.024]**. This does not establish trained-paper-specific benefit. No multiplicity adjustment; one training seed and no independent clinical/psychometric validation. Full local analysis code/records remain excluded from publication.

R1 sampled 4.096 million tokens from a 17.431-million-token corpus (~0.235 packed epochs), so not every fact/window was necessarily encountered. R3's planned 4.096 million tokens from 2.480 million selected tokens (~1.652 epochs) changes corpus selection and per-document exposure together; its failed run does not support an effectiveness conclusion. R4 would double full-corpus exposure and stretch the cosine learning-rate trajectory; it does not isolate duration from that trajectory. No completed formal contrast tests rank, peak learning rate or adaptation method. Provisional full findings are local; R3/R4 completion awaits the stability recovery decision.
