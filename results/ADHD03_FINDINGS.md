# ADHD-03: 1.7B Base with the original-only R3 configuration

Completed 2026-10-02 JST. Executor, analyst and report author: Codex / GPT-6 (root). The owner selected this model, authorized its preparation and then explicitly said to begin. This is one independent Base-start trajectory, with no claim of independent reviewer approval.

## Conclusion

The 1.7B model completed all 500 updates and full baseline/post exams without a resource stop. It finished with higher paper-QA accuracy and lower text perplexity than the 0.6B reference, but it already started with higher paper-QA accuracy and lower perplexity. Training-induced trained-paper QA gain was +7.660 pp for 1.7B versus +8.635 pp for 0.6B. The paired cross-size difference in trained-minus-held-out gains was +0.867 pp, with a 95% paper-cluster interval [-3.670, +5.344] pp. This experiment does not demonstrate a larger adaptation gain or faster factual learning for 1.7B.

Both sizes show an exploratory trained-specific paper-QA signal within their own pre/post comparison. The 1.7B run reduced held-out ADHD PPL while increasing general-text PPL and lowering the frozen primary PubMedQA score. Those adverse outcomes are retained. No further run, seed, duration or model is selected.

## Fixed design

Official `Qwen/Qwen3-1.7B-Base`, bf16, commit `ea980cb0a6c2ae4b936e82123acc929f1cec04c1`, Apache-2.0. Eight acquired files total 3,452,687,825 bytes (3.216 GiB). Physical weights remain in shared AI-Models, linked as `models/qwen3-1.7b-base`; exact URLs, dates, paths, file hashes, licenses and reacquisition/deletion notes remain in the private provenance records. Model fingerprint: `d9123e52c87b5e3e2c2e3288ce1ee5e1c9095c9ad03538af781b38e682aea98a`.

All 269 original training papers, 3,481 chunks and 2,479,647 stream tokens match revised R3; no ADHD-02 rewrites or evaluation items enter training. Validation is the unchanged pool-validation text. Frozen A/B exams use 718 questions from 223 trained papers and 760 questions from 238 unseen papers. The ADHD PPL exam contains 270 held-out papers.

All R3 settings match: seed42; all 196 target linear projections, rank16, alpha32, dropout0; sequence1024, microbatch1 x accumulation8, 500 updates, EOS prefix; peak lr2e-4, warmup30, minimum ratio0.1; 100 fixed validation windows every50; checkpoint50; cache2GiB. Base remains bf16; the unused full-training dtype field does not convert the LoRA Base. The final step500 adapter is evaluated, not a best-validation checkpoint. Identical tokenizer/merges/vocab files make target counts comparable. Each run processes 4,096,000 targets, approximately 1.652 original stream epochs; packing, dropped remainders and sampled windows limit that approximation. Same exposure/settings are not equal computation or equal trainable parameter count.

## Each size against its own untouched baseline

| Measure / sample | 0.6B before | 0.6B after | 1.7B before | 1.7B after |
|---|---:|---:|---:|---:|
| Trained-paper QA (718 questions) | 34.680% | 43.315% | 37.465% | 45.125% |
| Held-out-paper QA (760 questions) | 32.763% | 37.237% | 38.421% | 41.053% |
| Psychiatry MCQ (16 questions) | 31.250% | 25.000% | 18.750% | 18.750% |
| General medical MCQ (500 questions) | 30.800% | 31.400% | 30.400% | 31.600% |
| PubMedQA (1,000 questions) | 55.200% | 55.200% | 41.300% | 37.600% |
| ADHD PPL, EOS (270 papers) | 8.155321 | 7.491381 | 6.670118 | 6.221857 |
| General PPL, EOS (50 texts) | 13.641635 | 15.267462 | 10.030484 | 11.042535 |
| ADHD PPL, no EOS (270 papers) | 8.031704 | 7.456771 | 6.548381 | 6.192347 |
| General PPL, no EOS (50 texts) | 13.431928 | 15.023890 | 9.921226 | 10.823660 |

**Headings:** Model size identifies the independently pretrained Base; before is its own untouched baseline, after is its own final adapter. QA/MCQ cells are percent correct using frozen character-normalized option scoring (`acc_norm`), higher is better. PPL is next-token perplexity, lower is better; it is neither a percentage nor answer accuracy. Counts are questions for QA/MCQ and documents for PPL. EOS inserts an end-of-sequence token at window start; no EOS is the supplementary separate protocol. Compare pre/post within the same protocol.

## 1.7B paired changes

| Measure | After minus before / relative PPL change | 95% paired CI | Existing paired verdict |
|---|---:|---|---|
| Psychiatry MCQ (16 questions) | +0.000 pp | [+0.000, +0.000] pp | No significant change |
| General medical MCQ (500 questions) | +1.200 pp | [-1.600, +4.000] pp | No significant change |
| PubMedQA (1,000 questions) | -3.700 pp | [-5.800, -1.400] pp | Significant decline |
| General PPL, EOS (50 texts) | +10.090% | [+9.522, +10.669]% | Significant increase (worse) |
| ADHD PPL, EOS (270 papers) | -6.720% | [-7.272, -6.197]% | Significant decrease (better) |
| Trained-paper QA (718 questions) | +7.660 pp | [+4.596, +10.864] pp | Significant improvement |
| Held-out-paper QA (760 questions) | +2.632 pp | [+0.395, +5.000] pp | Significant improvement |
| ADHD PPL, no EOS (270 papers) | -5.437% | [-5.986, -4.914]% | Significant decrease (better) |
| General PPL, no EOS (50 texts) | +9.096% | [+8.492, +9.694]% | Significant increase (worse) |

**Headings:** Accuracy change is in percentage points (pp): 37% -> 45% means +8 pp. PPL change is relative percent: `(after / before - 1) x 100`. CI means confidence interval; frozen paired item/document bootstrap uses 2,000 replicates, resampling seed0. QA verdict requires both the interval and exact paired McNemar test to agree. These question-level intervals do not account for paper clustering; the next section does. No correction for multiple comparisons is applied. “Significant” is nominal and exploratory; a CI including zero does not prove equality. The psychiatry accuracy CI [0,0] records no changed correct/incorrect outcomes in these 16 items, not precise population equivalence.

PubMedQA: 41.3% -> 37.6%, -3.7 pp [-5.8, -1.4], exact McNemar p=0.0018378. The supplementary raw, unnormalized choice score moves in the opposite direction: 57.3% -> 62.4%. Both are retained in the local summaries; the frozen primary scoring rule is unchanged. This metric sensitivity prevents a broad claim that medical capability declined or improved. `p_correct` is a softmax share of normalized scores, not calibrated clinical confidence. Psychiatry (16 questions) is especially small and is not a dedicated ADHD clinical benchmark.

## Paper-cluster adaptation contrasts

| Model | Trained-paper gain (pp) | Held-out-paper gain (pp) | Trained minus held-out gain (pp) | 95% paper-cluster CI (pp) |
|---|---:|---:|---:|---|
| 0.6B | +8.635 | +4.474 | +4.161 | [+0.512, +7.976] |
| 1.7B | +7.660 | +2.632 | +5.029 | [+1.101, +8.769] |

**Headings:** Gain = each model after minus its own before. Subtracting held-out gain asks whether the trained papers benefit more than unseen papers. Whole PMCID clusters are independently resampled within the trained and held-out groups; accuracy is question-weighted within each resampled group. 5,000 replicates, resampling seed20261001. Both intervals exclude zero under this exploratory procedure; that does not establish clinical factual recall or exclude other adaptation mechanisms.

| 1.7B minus 0.6B own-baseline gains | Estimate (pp) | 95% paper-cluster CI (pp) |
|---|---:|---|
| Trained-paper gain difference | -0.975 | [-4.312, +2.345] |
| Held-out-paper gain difference | -1.842 | [-4.800, +1.189] |
| Trained-minus-held-out gain difference | +0.867 | [-3.670, +5.344] |

**Headings:** The second contrast directly subtracts the two models' gains. Four predictions (two models x before/after) stay paired on each identical frozen question and PMCID cluster. The bootstrap resamples whole papers, independently by group, 5,000 replicates, seed20261001. Every interval includes zero; no cross-size advantage is demonstrated. These are resampling replicates, not additional training seeds. This post hoc analysis is not an independent confirmation exam.

## Training and resources

| Measure | 0.6B R3 reference | 1.7B ADHD-03 |
|---|---:|---:|
| Updates | 500 | 500 |
| Processed target tokens | 4,096,000 | 4,096,000 |
| Trainable LoRA parameters | 10,092,544 | 17,432,576 |
| Validation loss, start -> final | 2.129548 -> 2.098452 | 1.952636 -> 1.930104 |
| Best logged validation loss | 2.084936 | 1.912806 |
| Final logged training throughput (tokens/s) | 1713.68 | 856.50 |
| Training / validation / checkpoint minutes | 43.38 | 88.31 |
| MLX peak memory (GiB) | 5.714 | 8.957 |

**Headings:** Updates = optimizer steps, each accumulating eight windows. Processed targets count prediction positions, not distinct facts. Trainable parameters are adapter weights; equal rank yields more weights on the larger architecture. Validation loss is mean next-token cross-entropy on 100 fixed pool-validation windows, not the benchmark. Best logged loss is descriptive only; final adapter is used. Tokens/s is the last recorded training throughput statistic, not whole-run throughput including exams. Train minutes include validation/checkpoint work; MLX peak is framework memory, not total macOS memory or swap. GiB = 1024^3 bytes.

The 1.7B training phase took 2.036x the 0.6B reference time, while final logged throughput was 0.500x. The whole 1.7B guarded run, including its newly required untouched baselines and both post-exam protocols, took 147.73 minutes. That whole-run duration should not be compared with a 0.6B run reusing previously recorded baselines. Maximum observed swap was 0.781 GiB; minimum free disk 96.851 GiB. Project-local maximum 5.037 GiB plus the selected shared model 3.216 GiB remained below 25 GiB; system reserve remained above 15 GiB. Resource observations are sampled every10 seconds.

1.7B validation improved from 1.952636 to 1.930104 but reached its best logged value, 1.912806, at step300. The later loss rise is retained. There are no intermediate paper-QA exams; this trace cannot establish a factual-learning-rate comparison.

## Integrity and stop conditions

- All 30 captured configuration, plan, framework, model, corpus, split/role/exclusion and frozen exam/index files match preparation and authorized-start state. Model fingerprint was recomputed; both baselines belong to this exact model. Preparation files remain immutable historical records, so their preparation-only status is not the current execution status. Current linkage/status belongs in private `experiments/adhd-03/RUNS.json` and `execution_record.json`.
- Both complete protocols have exact sample counts, frozen hashes and per-item ID sets; the 0.6B reference was independently checked against its own baseline. Final adapter SHA-256 was recomputed and matches both post-exams and adapter metadata.
- Native session5834 and guard exited0; no resource stop reason, retry, native resume, reduced configuration or AGX timeout override was applied. Owned training/guard/launcher and task-bound caffeinate processes are absent, confirming sleep prevention was released. Checkpoint50 was enabled; this uninterrupted run is not a native recovery test. No frozen exam or scoring rule was regenerated.

## Limits

- One seed per size does not estimate seed variability. Model size is confounded with pretrained weights, architecture/width, compute and adapter parameter count. Equal exposure/hyperparameters do not isolate parameter count as a causal treatment. Cross-size differences are exploratory.
- Higher absolute post scores partly reflect higher starting paper knowledge. Conversely, the 1.7B normalized PubMedQA baseline is already lower than 0.6B; larger size is not uniformly better. No intermediate QA learning curve, new duration, seed sweep or hyperparameter tuning was authorized.
- The same frozen exams have informed prior project decisions, so they are not fresh confirmation tests. Multiple metrics, protocols and post hoc contrasts have no multiplicity correction. Nominal CIs concern resampled items/papers, not independently retrained models.
- Training-paper questions were not supplied during training, but paper facts were. Held-out text/questions never enter training; this does not prove absence of pretrained overlap, duplicate findings or question-writing artifacts. All paper-QA is synthetic/evidence-checked, not a validated clinical assessment.
- Perplexity, multiple-choice scores and model likelihood are proxies. These results establish neither medical advice safety, patient benefit nor broad clinical ability. Preserve ADHD-01/02 failures and null results; R2 remains paused.

## Local evidence identifiers

- 1.7B training run: `20261002T061417Z-lora-adhd03-r3-17b-seed42`; adapter SHA-256 `f2fcbacf8a5e1ca8610f1db4ba5447ec26585cbcd67f4efdbabaf7e537424145`.
- 0.6B reference: `20260930T184551Z-lora-r3-newonly-eosprefix`; adapter SHA-256 `26b2070e8052d8577f6c43642e693508fc4eaf577913e3ec5c0d35127edd8aef`.
- 1.7B eos: baseline `20261002T061420Z-baseline`; post `20261002T081159Z-after-20261002T061417Z-lora-adhd03-r3-17b-seed42`.
- 1.7B none: baseline `20261002T063409Z-baseline`; post `20261002T083302Z-after-20261002T061417Z-lora-adhd03-r3-17b-seed42`.

Raw papers, exam items, predictions, detailed run/guard/provenance records, weights, private Chinese explanation and local development history are excluded from the public snapshot. This English report contains aggregate results only.

## Reviewer check (Claude, Claude Opus 5.5, 2026-10-02)

**The PubMedQA decline is a scoring artifact; the design error is Claude's.** The frozen primary score (`acc_norm`) divides each option's log-probability by its character length. That suits multi-word options, but PubMedQA's options are " yes" (4 characters), " no" (3) and " maybe" (6). The division systematically favours " maybe" and penalises " no". Prediction counts (yes / no / maybe; gold distribution 55.2 / 33.8 / 11.0%):

| Model | `acc_norm` picks | Raw log-probability picks | Raw accuracy |
|---|---|---|---:|
| 0.6B base | 995 / 0 / 5 | 999 / 1 / 0 | 55.1% |
| 0.6B R3 | 998 / 0 / 2 | 998 / 2 / 0 | 55.4% |
| 1.7B base | 489 / **0** / 511 | 882 / 55 / 63 | 57.3% |
| 1.7B after ADHD-03 | 443 / 3 / 554 | 781 / 155 / 64 | 62.4% |

- The 0.6B model answers "yes" to almost every item under either score. Its constant 55.2% is the majority-class rate, so PubMedQA carried no information about 0.6B in any run.
- Under `acc_norm`, 1.7B almost never chooses "no". The reported −3.7 pp "significant decline" reflects that bias, not lost ability.
- Raw log-probability is the appropriate score for these short, fixed options. Under it, 1.7B improves from 57.3% to 62.4% and starts answering "no".
- The raw score was already recorded for every run (`acc_raw`), so nothing needs re-running. Report PubMedQA with raw accuracy from now on and keep the frozen `acc_norm` value for the record.
- The A/B paper exams are much less exposed to this: their options were written to similar lengths (max/min ≤ 1.5), and the trained-minus-held-out contrast cancels any bias common to both groups.

**What ADHD-03 adds.** A trained-paper-specific gain now appears in five independent trajectories: 0.6B R3 seeds 42/43, the two ADHD-02 runs and 1.7B. The estimates range from +2.9 to +5.0 pp, and 1.7B gives +5.0 [+1.1, +8.8]. At this dose the larger model does not learn more per exposure. Its validation loss was lowest at step 300 and then rose, which suggests 1.65 epochs at lr 2e-4 is already past the useful point for 1.7B. A dose-response run would test this.
