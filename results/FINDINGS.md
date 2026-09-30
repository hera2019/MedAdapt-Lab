# ADHD-01 findings

Executor and analyst: Codex / GPT-6 (root). Updated 2026-10-01 JST. Framework correction/review: Claude / Opus 5.5, credited in the change log.

## Status

R0, original R1, revised R1b, R3 and R4 are complete, including their full post-exams and same-protocol paired comparisons. R1b/R3 used 500 updates; R4 used 1000. R2 remains paused. Original R1's unfavorable frozen EOS scores and failed earlier attempts are retained. No further model or experiment was launched.

## Design and evidence

Frozen ADHD-01-v1 exams contain 718 trained-paper questions (223 contributing papers), 760 held-out-paper questions (238 papers), 270 held-out ADHD full texts, 50 general-text items, 16 psychiatry MCQ, 500 general medical MCQ and 1000 labeled PubMedQA items. QA is cloze likelihood, character-normalized; it does not evaluate generated clinical advice. The normalized correct-option score share is not a calibrated probability. New paper dates, identifiers and manual exclusions mitigate overlap but cannot eliminate preprints or semantic duplicates. Question evidence passed automated/source spot checks; independent clinical or psychometric validation is absent.

All formal runs start from the identical pinned Qwen3-0.6B-Base bf16 weights, use all 196 LoRA projections with rank 16/alpha 32/dropout 0, seed 42, 1024-token context, and 8192 scored tokens/update. The successful operational variant uses physical batch 1 / accumulation 8 and 100 fixed packed validation windows within each packing protocol. It differs in possible floating-point kernel rounding from the original batch-4 plan. Original batch-4 R1 failed with a Metal watchdog error and no final adapter; no result is inferred from that attempt.

| Run | Training corpus | Steps / sampled tokens | Approximate packed-corpus epochs | State |
|---|---|---:|---:|---|
| R0 | None | 0 | 0 | Complete |
| R1 | 17,431,219 tokens; full selected corpus | 500 / 4,096,000 | 0.235 | Complete |
| R2 | Planned full-parameter control on the selected corpus | No completed formal run | — | Paused; smoke acceptance unresolved |
| R1b | Same full corpus, now EOS-prefixed windows | 500 / 4,096,000 | 0.235 | Complete; sink gate passed |
| R3 | 2,479,647 tokens; new-train only | 500 / 4,096,000 | 1.652 | Revised EOS-prefixed run complete |
| R4 | Same full corpus and EOS packing as R1b | 1000 / 8,192,000 | 0.470 | Complete |


### Reading the experiment-plan table

- **Run:** R0 is the unadapted model's exam. R1 is the main LoRA experiment; R2 was the full-parameter control; R3 tests new-paper-only corpus selection; R4 tests longer full-corpus training. R1/R1b/R3/R4 each start from the same original Base weights, not from the preceding adapter.
- **Training corpus:** the selected text supplied for training. A token is a tokenizer unit, not necessarily a word or character. “Full” means this selected ADHD corpus, not all of medicine. New-train is 269 selected new papers, disjoint from held-out papers.
- **Steps / sampled tokens:** a step is one optimizer update. Batch 1 × accumulation 8 × context 1024 = 8192 scored tokens/update; 500 updates gives 4,096,000 processed tokens, including any repeats. The proposed full-run amounts are not completion claims for failed/pending runs.
- **Approximate packed-corpus epochs:** processed-token count divided by available corpus-token count. R1's 0.235 is roughly a quarter-corpus amount of processing; it does not mean exactly 23.5% of papers or facts were learned. R3's 1.652 revisits some windows because its corpus is smaller.
- **State:** Complete means training/exams finished where applicable; Failed has no final result; Paused is a deliberate stop; Pending has not started. A dash is not a zero score.

Sampled tokens describe the prescribed stream, not distinct information learned. R1 does not visit every packed window; question facts are not guaranteed to have been encountered. R3 changes corpus selection and exposure per document simultaneously. R4 retains peak LR 2e-4, warmup 30 and minimum ratio 0.1 but stretches cosine decay to 1000 updates: duration and learning-rate trajectory are not independent factors. Rank, peak LR and adaptation method are not varied in completed formal runs.

Legacy R3 failed after its step-40 log before checkpoint support; it has no final result. The completed revised R3 above is a separate EOS-prefixed run. Failure evidence remains local and in the issue/execution records.

## Four experiment questions

1. **Specific trained-paper knowledge:** revised R3 supports a larger trained-paper QA gain in this sample: trained-minus-heldout change +4.161 pp, paper-cluster CI [+0.512,+7.976] versus R0; +5.222 pp [+1.721,+8.792] versus R1b. Original R1, R1b and R4 do not establish this difference. This is a paper-related answer-selection signal, not an isolated demonstration of memorization or clinical competence. R3 changes corpus selection and per-paper exposure together; the full-corpus 500/1000-step runs cover smaller fractions of their available stream.
2. **Unseen ADHD text:** all revised runs improve held-out ADHD PPL under both scoring protocols. R4 is 7.280485 (EOS) / 7.247922 (no EOS), about 10.73% / 9.76% lower than the respective R0. Compared with R1b, R4 reduces PPL about 1.67% / 1.69%; R3 raises it about 1.18% / 1.15%. Paper-question gains and next-token prediction need not move together.
3. **General-language forgetting:** revised general PPL is about 7.77–11.92% higher than the matching R0, with paired document intervals excluding no change. This supports a modest regression on these general texts under both protocols. R4 adds about 1.24% / 1.22% versus R1b. Original R1's much larger EOS regression is strongly prefix-dependent and remains reported. Secondary medical QA has no significant change versus R0 for these revised runs; R4 improves general medical MCQ +2.0 pp versus R1b but is still -0.2 pp versus R0. Neither non-significance nor a narrow text exam proves broad ability preserved.
4. **Method/rank/rate/corpus effects:** R3 concentrates exposure and yields the trained-paper signal; R4's longer full-corpus regimen improves domain prediction, mildly worsens general prediction, and does not clearly improve either paper-QA group versus R1b. R4 doubles steps and stretches cosine decay, so duration and learning-rate trajectory are confounded. Rank 16, peak LR 2e-4 and LoRA method are held, not compared. Full-parameter R2 stays paused; no method/rank/peak-rate superiority is established.

All tests are exploratory: one seed, reused frozen exams, no multiplicity adjustment, and no independent clinical/psychometric validation. The packing correction was prompted by observed benchmark behavior, so its evidence is outcome-informed rather than independent confirmation.

## Reviewed correction and execution

Claude / Opus 5.5 added EOS-prefixed training windows, a position-0 sink probe, supplementary no-EOS PPL scoring, and 50-step checkpoints containing trainable weights, optimizer state and loop position. Codex / GPT-6 (root) reviewed and executed the revised sequence. R1b passed the sink gate: EOS position-0 norm 7803 versus Base 6868; ordinary-word norm 6319 versus 6480, other-token median 27. Norms measure internal activation size, not knowledge scores. The restored norm and both PPL protocols support the practical mitigation on this run, with the changed-window/shuffle limitation below.

The first R1b launch failed before its first checkpoint. Its fresh Base retry completed using `AGX_RELAX_CDM_CTXSTORE_TIMEOUT=1` only in that child. R3 and R4 completed without that hint or interruptions. Native checkpoint files were verified at step 50; the tiny selftest checks interrupted/resumed versus uninterrupted training. No deliberate interruption was introduced into these formal runs, and no native resume occurred: the pre-checkpoint R1b retry was a restart. Current dropout is zero; general stochastic-dropout resume equivalence is unestablished. Frozen files and original failures remain preserved.

The sequential runner completed from 2026-10-01 02:39:42 to 06:22:56 JST, about 223.24 minutes including supplementary scoring, failed launch, training, exams and sink diagnostic. Its task-bound sleep prevention ended with exit 0. Resource policy: launch below 3 GiB swap, stop at 4 GiB, check every 10 seconds; conservative launcher defaults remain unchanged. No persistent sleep/driver setting was changed.

## Complete supplementary no-EOS R0/R1 PPL
Executor: Codex / GPT-6 (root), 2026-10-01 JST. These complete 270-paper/50-general-item scores use the reviewer-approved supplementary protocol and do not replace the frozen EOS scores. Each window starts with its first text token as context, so its first token is not scored. Same protocol is used before and after.
Baseline `20260930T173943Z-baseline`; post-exam `20260930T174323Z-after-20260930T135838Z-lora-r1-lora-micro1`.
| Measure | R0 without EOS | R1 without EOS | Relative change | Paired 95% CI |
|---|---:|---:|---:|---|
| Held-out ADHD PPL | 8.031704 | 7.361024 | -8.350% | [-8.684%, -8.032%] |
| General PPL | 13.431928 | 14.664963 | +9.180% | [+8.763%, +9.604%] |

Under no-EOS scoring, R1 improves held-out ADHD predictability and worsens general predictability modestly. Under the frozen EOS protocol, both regress dramatically. The strong protocol dependence plus sink probes supports a prefix-related side effect; it does not justify erasing adverse EOS results, cross-protocol comparisons, or clinical claims. Both protocols reuse the same original text files; this is an explicitly outcome-informed supplementary analysis, not independent confirmatory evidence.

### Revised packing comparison limit

Codex / GPT-6 (root), 2026-10-01. The EOS-prefixed packer advances 1024 stream tokens/window; original R1 advanced 1025. The same full corpus now yields 17022 windows versus R1's 17006. Although Base/corpus/seed/steps/effective batch/peak LR/rank are held, a different window count changes the seeded shuffle and exact sampled token windows. R1b is therefore a new protocol, not an exact same-token intervention isolating only the prefix. Validation boundaries differ too. Report the mitigation and sink/PPL evidence without attributing every QA difference to EOS alone; revised R3/R4 use R1b as their reference. No training change or additional test made by this observation.

## Revised protocol: completed scores

| Measure | Same-protocol R0 | R1b | R3 | R4 |
|---|---:|---:|---:|---:|
| Trained-paper QA | 34.680% | 36.908% | 43.315% | 37.883% |
| Held-out-paper QA | 32.763% | 36.053% | 37.237% | 36.711% |
| ADHD PPL, EOS | 8.155321 | 7.404098 | 7.491381 | 7.280485 |
| General PPL, EOS | 13.641635 | 14.701741 | 15.267462 | 14.883700 |
| ADHD PPL, no EOS | 8.031704 | 7.372283 | 7.456771 | 7.247922 |
| General PPL, no EOS | 13.431928 | 14.484872 | 15.023890 | 14.662270 |
| Psychiatry MCQ | 31.250% | 25.000% | 25.000% | 31.250% |
| General medical MCQ | 30.800% | 28.600% | 31.400% | 30.600% |
| PubMedQA | 55.200% | 55.200% | 55.200% | 55.300% |

QA/MCQ values are accuracy (higher is better); PPL is token-weighted perplexity (lower is better). Each baseline uses its own EOS/no-EOS protocol; no cross-protocol change is calculated.

## Revised protocol: paired changes versus R0

| Measure | R1b change [95% CI] | R3 change [95% CI] | R4 change [95% CI] |
|---|---|---|---|
| Trained-paper QA | +2.228 pp [-0.279, +4.735] | +8.635 pp [+5.989, +11.421] | +3.203 pp [+0.696, +5.571] |
| Held-out-paper QA | +3.289 pp [+0.789, +5.789] | +4.474 pp [+1.974, +6.842] | +3.947 pp [+1.579, +6.447] |
| ADHD PPL, EOS | -9.211% [-9.534, -8.896] | -8.141% [-8.733, -7.557] | -10.727% [-11.110, -10.351] |
| General PPL, EOS | +7.771% [+7.297, +8.239] | +11.918% [+11.344, +12.515] | +9.105% [+8.605, +9.603] |
| ADHD PPL, no EOS | -8.210% [-8.532, -7.903] | -7.158% [-7.753, -6.574] | -9.759% [-10.151, -9.385] |
| General PPL, no EOS | +7.839% [+7.446, +8.240] | +11.852% [+11.302, +12.409] | +9.160% [+8.727, +9.574] |
| Psychiatry MCQ | -6.250 pp [-18.750, +0.000] | -6.250 pp [-18.750, +0.000] | +0.000 pp [+0.000, +0.000] |
| General medical MCQ | -2.200 pp [-4.600, +0.200] | +0.600 pp [-2.000, +3.200] | -0.200 pp [-2.600, +2.200] |
| PubMedQA | +0.000 pp [-0.300, +0.300] | +0.000 pp [-0.400, +0.400] | +0.100 pp [-0.200, +0.500] |

Accuracy changes are percentage points; PPL changes are relative percentages. These paired item/document intervals are exploratory, not paper-clustered for QA and not multiplicity-adjusted.

## R3 versus R1b: same-protocol paired control

| Measure | Change [95% CI] | Current paired verdict |
|---|---|---|
| Trained-paper QA | +6.407 pp [+3.760, +8.914] | Significant improvement |
| Held-out-paper QA | +1.184 pp [-1.053, +3.421] | No significant change |
| ADHD PPL, EOS | +1.179% [+0.783, +1.563] | Significant increase (worse) |
| General PPL, EOS | +3.848% [+3.481, +4.221] | Significant increase (worse) |
| ADHD PPL, no EOS | +1.146% [+0.749, +1.525] | Significant increase (worse) |
| General PPL, no EOS | +3.721% [+3.340, +4.091] | Significant increase (worse) |
| Psychiatry MCQ | +0.000 pp [+0.000, +0.000] | No significant change |
| General medical MCQ | +2.800 pp [+0.200, +5.400] | No significant change |
| PubMedQA | +0.000 pp [-0.300, +0.300] | No significant change |

## R4 versus R1b: same-protocol paired control

| Measure | Change [95% CI] | Current paired verdict |
|---|---|---|
| Trained-paper QA | +0.975 pp [-0.557, +2.507] | No significant change |
| Held-out-paper QA | +0.658 pp [-0.921, +2.237] | No significant change |
| ADHD PPL, EOS | -1.670% [-1.766, -1.572] | Significant decrease (better) |
| General PPL, EOS | +1.238% [+1.116, +1.361] | Significant increase (worse) |
| ADHD PPL, no EOS | -1.687% [-1.785, -1.591] | Significant decrease (better) |
| General PPL, no EOS | +1.225% [+1.099, +1.347] | Significant increase (worse) |
| Psychiatry MCQ | +6.250 pp [+0.000, +18.750] | No significant change |
| General medical MCQ | +2.000 pp [+0.600, +3.400] | Significant improvement |
| PubMedQA | +0.100 pp [+0.000, +0.400] | No significant change |

## Direct trained-minus-heldout accuracy-change comparison

| Run | Reference exam | Difference / 95% paper-cluster CI (pp) |
|---|---|---|
| R1b | R0 | -1.061 [-4.560, +2.483] |
| R3 | R0 | +4.161 [+0.512, +7.976] |
| R3 | R1b | +5.222 [+1.721, +8.792] |
| R4 | R0 | -0.744 [-4.216, +2.792] |
| R4 | R1b | +0.317 [-1.906, +2.636] |

Independent paper-cluster bootstrap for A/B, 5000 replicates, seed 20261001; question-weighted within sampled clusters. A positive interval excluding zero supports a larger trained-paper gain under this exploratory procedure. It does not isolate memory from transfer or other confounds.

## Completed execution evidence

| Run | Validation start -> end | MLX peak (GiB) | Guarded phase minutes | Maximum swap (GiB) |
|---|---:|---:|---:|---:|
| R1b | 2.129548 -> 2.051779 | 5.710 | 58.52 | 1.410 |
| R3 | 2.129548 -> 2.098452 | 5.714 | 56.69 | 1.379 |
| R4 | 2.129548 -> 2.038087 | 5.714 | 100.36 | 1.379 |

Guarded phase time includes failed attempts/reload and both exam protocols; it is not training-only time. The sink diagnostic is a separate guarded phase. Each `run.json` seconds field covers its final train segment, so it is not a full resumed-run wall time. Original R1 uses different packed validation windows; its loss values cannot be compared directly with this table.

- **R1b** EOS post-exam `20260930T183255Z-after-20260930T174842Z-lora-r1b-eosprefix-retry`; no-EOS post-exam `20260930T184154Z-after-20260930T174842Z-lora-r1b-eosprefix-retry`; adapter SHA-256 `60d31d4f96ab5b76bb3091a4e6a4a2d59b54dba57c6ed0d5483620fff51e1573`.
- **R3** EOS post-exam `20260930T192941Z-after-20260930T184551Z-lora-r3-newonly-eosprefix`; no-EOS post-exam `20260930T193840Z-after-20260930T184551Z-lora-r3-newonly-eosprefix`; adapter SHA-256 `26b2070e8052d8577f6c43642e693508fc4eaf577913e3ec5c0d35127edd8aef`.
- **R4** EOS post-exam `20260930T211003Z-after-20260930T194234Z-lora-r4-x2-eosprefix`; no-EOS post-exam `20260930T211903Z-after-20260930T194234Z-lora-r4-x2-eosprefix`; adapter SHA-256 `6e518a7726004255a4eb893c5eb998684fd14357d850a7ba1d0da7fdce11cae3`.

QA verdicts require both a change interval excluding zero and exact McNemar p<0.05 (and at least 10 items). R3 versus R1b general medical MCQ has CI [+0.2,+5.4] pp but p=0.0541, so its combined verdict is no significant change. Bootstrap and exact tests can differ near the threshold; no score or test was changed.

R1b native training ID: `20260930T174842Z-lora-r1b-eosprefix-retry`.

R3 native training ID: `20260930T184551Z-lora-r3-newonly-eosprefix`.

R4 native training ID: `20260930T194234Z-lora-r4-x2-eosprefix`.

## Original R1: preserved measured results

Baseline `20260930T133505Z-baseline`; training `20260930T135838Z-lora-r1-lora-micro1`; post-exam `20260930T144250Z-after-20260930T135838Z-lora-r1-lora-micro1`. Exact metrics, paired item changes, confidence intervals and hashes are in the local comparison JSON/Markdown and run record.

| Measure | R0 | R1 | Paired change / 95% CI |
|---|---:|---:|---|
| Trained-paper QA | 34.680% | 38.301% | +3.621 pp [+0.975, +6.128] |
| Held-out-paper QA | 32.763% | 36.842% | +4.079 pp [+1.579, +6.579] |
| Held-out ADHD PPL | 8.155 | 27.557 | +237.91% [+228.71%, +246.96%] |
| General PPL | 13.642 | 70.015 | +413.24% [+386.40%, +443.09%] |
| Psychiatry MCQ (16 items) | 31.25% | 25.00% | -6.25 pp [-18.75, 0.00] |
| General medical MCQ | 30.8% | 29.4% | -1.4 pp [-4.0, +1.0] |
| PubMedQA | 55.2% | 55.1% | -0.1 pp [-0.5, +0.2] |


### Reading the result table

- **Measure:** which exam and metric is being reported. QA/MCQ rows show the fraction of choices marked correct; higher is better. PPL rows measure next-token predictability on actual text; lower is better. These units cannot be combined into one score.
- **R0 / R1:** the same frozen exam before and after adaptation. “Trained-paper” describes source-paper membership, not training on exam answers; the question text stays out of training. “Held-out” means excluded from this experiment's training, not proven absent from the original model's pretraining.
- **Paired change:** compare the same items before/after. Accuracy changes use percentage points (pp): 34.680% -> 38.301% is +3.621 pp. PPL changes use relative percentages: 13.642 -> 70.015 is +413.24%, about 5.13 times the baseline, not an accuracy change.
- **95% CI:** a sampling-based uncertainty interval for the change under the stated procedure. An interval crossing zero does not clearly distinguish improvement from deterioration. An interval excluding zero supports a change under that test, not a causal explanation or clinical suitability. PPL ratio intervals in the underlying JSON cross the no-change value at 1; here they are displayed as relative changes whose no-change value is 0%.
- **Counts:** the QA rows use 718, 760, 16, 500 and 1000 questions respectively. PPL uses 270 ADHD texts and 50 general texts; aggregate PPL is computed from total NLL divided by total scored tokens, not an average of document PPL values.

Trained-paper questions gained 56 correct items and lost 30; held-out questions gained 61 and lost 30. Both improved under the original item-bootstrap/McNemar tests. A separately labeled exploratory direct comparison of accuracy changes, bootstrapping independently by paper (5000 replicates, fixed seed 20261001), estimates trained-minus-heldout difference **-0.458 pp**, 95% CI **[-3.877, +3.024]**. This does not establish a trained-paper-specific gain. The original intervals resample items and are not paper-clustered; neither family is multiplicity-adjusted. All conclusions are exploratory, with one training seed.

Training validation loss improved 2.1142765 -> 2.0450741; MLX peak 5.714 GiB. Full guard exited 0, with no swap growth. Validation improvement alone does not establish broad QA or language improvement.

## PPL protocol limitation and bounded diagnosis

The frozen scorer prepends EOS (`<|endoftext|>`, ID 151643) to every non-overlapping text window. Most packed training windows begin inside documents without that prefix. The unfavorable formal PPL measurements remain unchanged. Automatic comparison wording about forgetting is a heuristic, not an isolated causal diagnosis.

Before R3, a fresh saved-adapter reload reproduced full NLL on the first general and first ADHD document exactly, as well as the same 100-window validation loss. Cross-entropy and negative log-probability agreed within 1.6e-7 on three identical windows. No serialization/scoring-formula discrepancy was found in these checks.

| First 1024 tokens; mean NLL | Base with EOS | Base without EOS | R1 with EOS | R1 without EOS |
|---|---:|---:|---:|---:|
| General first item | 2.10476 | 2.09371 | 3.56063 | 2.17415 |
| ADHD first item | 1.78376 | 1.79352 | 2.62495 | 1.69618 |


### Reading the diagnostic table

Each row is only the first 1024 tokens of one text (the first general item or first ADHD item), not the full formal exam. **Mean NLL** is average next-token penalty; lower is better. **Base / R1** identifies the original/adapted model. **With / without EOS** identifies whether the special end-of-text token was put before the window. These are separate diagnostic scores, not replacements for frozen PPL scores. For example, 3.56063 -> 2.17415 compares two prefixes on the same R1 general window, not training before/after.

Strong prefix sensitivity persists after discarding the first 32 token losses. These two diagnostic windows were selected by first-item order after observing formal regression, not by outcome. They are not an alternate full benchmark and cannot prove forgetting absent or estimate its population magnitude. At that diagnostic stage no frozen exam or training setting was changed. The reviewed, separately labeled correction below subsequently changed packing and introduced supplementary scoring; original adverse scores remain intact.

## Reproducibility and public scope

Full evidence remains local: frozen exam/role/split hashes, raw per-item likelihoods, complete baseline/post-exam ledger, adapter SHA-256, training logs, guard logs, comparison reports and actual operator signatures. The separate cluster and prefix diagnoses are labeled and excluded from the formal ledger. Data/model weights/adapters/question text and private development history are excluded from GitHub; only original source and aggregate English reports (SOL6_REPORT.md and FINDINGS.md) are eligible for the audited public snapshot. The Chinese companion stays local. Apache-2.0 applies to original project code/docs; third-party resources retain their own licenses.

## Terminology at a glance

- **DAPT:** continue next-token training on domain text; here, licensed ADHD papers. It does not directly teach the held-out quiz answers.
- **Base / weights / 0.6B:** the original pre-trained checkpoint, its learned numerical parameters, and roughly 600 million parameters respectively. A **checkpoint** is a saved state; our completed LoRA run saves an **adapter**, which is loaded alongside the Base weights.
- **LoRA / adapter / rank:** train small added matrices while freezing the original weights. The adapter holds their learned values; rank 16 controls the low-rank structure, not a quality score. All 196 target projections are wrapped; about 10.093 million parameters are trained.
- **Full-parameter training:** update the original weights rather than only LoRA matrices; it generally needs more gradient/optimizer memory. R2 has no completed formal comparison.
- **Training / validation / test:** text used to update parameters / separate text used to monitor training loss / frozen exams used to assess outcomes. Test scores must not be repeatedly used to tune this experiment's settings.
- **Context / window / packing:** the token span supplied together; a bounded segment; concatenating documents with EOS separators and cutting fixed-length windows. The training windows and PPL windows do not have identical starting prefixes.
- **Loss / NLL / PPL:** next-token error measured as negative log-likelihood; lower is better. For the same scored tokens, PPL = exp(mean NLL). Lower validation loss does not imply higher QA accuracy.
- **Batch / gradient / accumulation / optimizer:** examples processed together / signals describing how parameters affect loss / accumulating signals across eight physical batches before updating / the update rule. Accumulation preserves intended effective batch while reducing physical batch memory.
- **LR / warmup / cosine decay:** learning-rate scale for each update / gradually increasing it initially / then decreasing it along a cosine schedule. LR 2e-4 is 0.0002; R4 stretches the schedule, not just the amount of exposure.
- **Seed / frozen / hash:** an initialization/shuffle reproducibility setting / fixed exams and splits / a file-content fingerprint. A seed does not guarantee bit-identical results across different kernels or hardware.
- **bf16 / float32 / MLX / GiB:** 16-bit and 32-bit floating-point representations; the Apple Silicon numerical framework; a binary storage/memory unit (1 GiB = 1024³ bytes). MLX peak is the framework's reported peak, not total machine usage or swap.
- **Bootstrap / paper clustering / McNemar:** resampling existing paired results to estimate uncertainty / resampling papers together with their related questions / testing whether wrong-to-right and right-to-wrong transitions differ. Bootstrap replicates are not additional model trainings.
- **Statistical significance / multiple comparisons / exploratory:** evidence against no change under a stated test / testing several outcomes creates more chances of false positives / findings remain tentative, especially with one seed and no multiplicity adjustment.
- **Generalization / forgetting / leakage:** improvement on excluded material / deterioration of prior abilities / allowing evaluation material to influence training or tuning. Here, EOS sensitivity limits broad forgetting claims; identifiers and dates do not eliminate every semantic overlap.
- **EOS / Metal watchdog:** a special end-of-text token / the system mechanism that interrupted the legacy R3 attempt. An interrupted training run is not a zero score or evidence that the model learned nothing.

