# ADHD-04: reading dose and its costs

Completed 2026-10-03 JST. Plan and snapshot implementation: Claude / Opus 5.5. Executor, verifier, analyst and report author: Codex / GPT-6 (root). The owner supplied the plan and authorized the overnight run. This report has no independent review claim.

## Measured conclusion

Both independent Base-start trajectories completed at their declared durations, with every final/snapshot exam. More reading did not improve every outcome.

- **0.6B:** trained and held-out paper QA were highest among sampled points at step 500 (45.125% / 39.211%), then declined. All four trained-minus-held-out gain intervals include zero. Its largest extra-gain point estimate is step 2000, +4.200 pp [-0.555, +8.780]; this does not establish a trained-specific benefit. At the final point, ADHD PPL is 38.88% worse and general PPL 123.45% worse than its own baseline under EOS.
- **1.7B:** trained QA rises at every sampled point, to 47.772% at 1000, while held-out QA peaks at 150 and then weakens. Extra gain rises to+8.727 pp [4.426, 12.879] at 1000. ADHD PPL and validation loss are lowest among their respective observed points at 300; final ADHD PPL is 3.91% worse than baseline and general PPL27.39% worse. An exploratory trained-specific QA signal coexists with worse text prediction.
- General-text PPL worsens at **every nonzero point under both protocols**. The two curves do not identify one common optimum. The best point for one metric can be worse for another, and no optimum beyond the sampled points is established.

## Fixed design and units

D1: official Qwen3-0.6B-Base, 2000 updates, adapters at 250/500/1000/2000. D2: pinned official Qwen3-1.7B-Base, 1000 updates, adapters at 150/300/500/1000. Both start independently from untouched bf16 Base weights. Each reuses that exact model's previously completed untouched EOS and no-EOS baselines. Higher pretrained performance of 1.7B must be separated from its own adaptation gain.

Same original-only269-paper corpus, 3481 chunks, 2479647 stream tokens; no rewrites or exam content enter training. Validation is the same fixed pool text, 736335 stream tokens. Same seed 42, all196 linear targets, LoRA rank 16/alpha 32/dropout 0, context1024, microbatch1 x accumulation8, 8192 targets per update, EOS-prefixed windows, peak learning rate0.0002, 30-step warmup, cosine minimum ratio 0.1, 100 validation windows every 50 steps, checkpoint every 50, 2 GiB cache. The unused full-training dtype field does not convert the LoRA Base.

Trained QA has 718 questions from 223 papers; held-out QA760 questions from 238 papers. ADHD PPL has 270 unseen papers; general PPL50 texts; general medical MCQ500 items; PubMedQA1000; psychiatry MCQ16, descriptive only. All exams use their unchanged complete frozen items.

**Table headings:** Step means optimizer updates;0 is untouched baseline. Exposure is `(steps x8192)/2479647`, approximate passes over the original token stream, not literal complete reads of each paper or unique facts learned. Packing, window boundaries and dropped remainders limit this approximation. QA is percent correct with frozen character-normalized option scoring (`acc_norm`); gain is that model's point minus its own baseline, in percentage points (pp). Extra gain is trained gain minus held-out gain. CI is a 95% paper-cluster bootstrap confidence interval, in pp. Reference rows have no resampling uncertainty claim. Validation loss is fixed 100-window next-token cross-entropy, lower is better; it is a separate pool measure, not QA.

## D1 — 0.6B

| Step | Exposure | Trained QA (%) | Held-out QA (%) | Trained gain (pp) | Held-out gain (pp) | Extra gain (pp) | 95% cluster CI (pp) | Validation loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.000 | 34.680 | 32.763 | +0.000 | +0.000 | +0.000 | reference | 2.129548 |
| 250 | 0.826 | 42.618 | 37.500 | +7.939 | +4.737 | +3.202 | [-0.488, +6.861] | 2.095077 |
| 500 | 1.652 | 45.125 | 39.211 | +10.446 | +6.447 | +3.998 | [-0.034, +8.026] | 2.130712 |
| 1000 | 3.304 | 44.847 | 39.079 | +10.167 | +6.316 | +3.851 | [-0.410, +8.076] | 2.269828 |
| 2000 | 6.607 | 44.011 | 37.895 | +9.331 | +5.132 | +4.200 | [-0.555, +8.780] | 2.503906 |

The accuracy curve rises through 500 then falls. Step2000's slightly larger extra-gain estimate than 500 reflects a larger loss of held-out benefit, rather than a higher trained accuracy. Its interval still includes zero. Lowest logged validation loss was 2.091743 at 300; there is no QA adapter at 300.

### D1 text prediction and forgetting

| Step | ADHD EOS PPL / change | General EOS PPL / change | ADHD no-EOS PPL / change | General no-EOS PPL / change |
| --- | --- | --- | --- | --- |
| 0 | 8.155321 / +0.00% | 13.641635 / +0.00% | 8.031704 / +0.00% | 13.431928 / +0.00% |
| 250 | 7.496367 / -8.08% | 14.997187 / +9.94% | 7.466200 / -7.04% | 14.804285 / +10.22% |
| 500 | 7.693476 / -5.66% | 16.240546 / +19.05% | 7.659961 / -4.63% | 16.026126 / +19.31% |
| 1000 | 8.834020 / +8.32% | 20.919716 / +53.35% | 8.793028 / +9.48% | 20.654254 / +53.77% |
| 2000 | 11.326366 / +38.88% | 30.481836 / +123.45% | 11.269079 / +40.31% | 30.136425 / +124.36% |

**Headings:** Each cell is measured PPL followed by relative percent change from that model's own baseline under the same protocol: `(point/baseline-1)x100`. PPL means perplexity, lower is better; it is not an accuracy percentage. Negative change is improvement, positive change is deterioration. EOS inserts an end-of-sequence token at the beginning of each scoring window; no EOS is the separate supplementary protocol. ADHD means unseen domain texts; General means the general-text forgetting proxy. Absolute PPLs across protocols should not be merged.

Among sampled D1 adapters, ADHD PPL is best at 250, worsens thereafter, and exceeds baseline by 1000. General PPL increases monotonically across these sampled points. The no-EOS results retain the same tradeoff.

### D1 transfer measures

| Step | PubMedQA raw (%) | PubMedQA norm (%) | General medical MCQ (%) | Psychiatry MCQ (%) |
| --- | --- | --- | --- | --- |
| 0 | 55.1 | 55.2 | 30.8 | 31.25 |
| 250 | 55.3 | 55.3 | 30.4 | 25.00 |
| 500 | 55.3 | 55.3 | 31.0 | 25.00 |
| 1000 | 57.5 | 55.2 | 30.0 | 12.50 |
| 2000 | 56.3 | 53.2 | 27.8 | 12.50 |

**Headings:** PubMedQA raw is accuracy from unnormalized total option log probability (`acc_raw`), the reporting score declared in ADHD-04 before its outcomes. PubMedQA norm retains the unchanged character-normalized score alongside. General medical and psychiatry columns retain frozen `acc_norm`. Percent correct is higher-is-better, but these are descriptive secondary measures; no new significance claim is made here.

Treat 0.6B PubMedQA as uninformative majority-class behavior. Raw predictions are "yes" for 999/1000 at baseline, 997/1000 at 250, 996/1000 at 500, 918/1000 at 1000 and821/1000 at 2000. The collapse loosens at high dose, but a majority-dominated score does not establish useful transfer. Normalized scores and all adverse general/psychiatry results remain visible.

## D2 — 1.7B

| Step | Exposure | Trained QA (%) | Held-out QA (%) | Trained gain (pp) | Held-out gain (pp) | Extra gain (pp) | 95% cluster CI (pp) | Validation loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.000 | 37.465 | 38.421 | +0.000 | +0.000 | +0.000 | reference | 1.952636 |
| 150 | 0.496 | 41.504 | 41.447 | +4.039 | +3.026 | +1.013 | [-2.344, +4.386] | 1.923553 |
| 300 | 0.991 | 44.290 | 41.316 | +6.825 | +2.895 | +3.930 | [+0.348, +7.301] | 1.915524 |
| 500 | 1.652 | 45.543 | 39.737 | +8.078 | +1.316 | +6.762 | [+3.014, +10.582] | 1.950154 |
| 1000 | 3.304 | 47.772 | 40.000 | +10.306 | +1.579 | +8.727 | [+4.426, +12.879] | 2.034938 |

Extra gain increases across sampled adapters and its unadjusted cluster interval excludes zero from 300 onward. Held-out gain is largest at 150, while final trained QA is highest at 1000. An interval crossing zero at 150 or for later held-out gains does not prove no effect. No independent tests are performed between dependent snapshot points.

### D2 text prediction and forgetting

| Step | ADHD EOS PPL / change | General EOS PPL / change | ADHD no-EOS PPL / change | General no-EOS PPL / change |
| --- | --- | --- | --- | --- |
| 0 | 6.670118 / +0.00% | 10.030484 / +0.00% | 6.548381 / +0.00% | 9.921226 / +0.00% |
| 150 | 6.234320 / -6.53% | 10.744857 / +7.12% | 6.200922 / -5.31% | 10.502044 / +5.85% |
| 300 | 6.144614 / -7.88% | 10.774704 / +7.42% | 6.117102 / -6.59% | 10.555358 / +6.39% |
| 500 | 6.330856 / -5.09% | 11.402685 / +13.68% | 6.302066 / -3.76% | 11.193648 / +12.83% |
| 1000 | 6.930607 / +3.91% | 12.777356 / +27.39% | 6.891559 / +5.24% | 12.542029 / +26.42% |

Same PPL headings and relative-change definition as D1. ADHD PPL is lowest among sampled points at 300 under both protocols, worsens at 500, and exceeds baseline at 1000. General PPL rises across sampled points under both protocols. Final QA gain therefore cannot be equated with broad domain modeling improvement.

### D2 transfer measures

| Step | PubMedQA raw (%) | PubMedQA norm (%) | General medical MCQ (%) | Psychiatry MCQ (%) |
| --- | --- | --- | --- | --- |
| 0 | 57.3 | 41.3 | 30.4 | 18.75 |
| 150 | 64.3 | 45.2 | 30.4 | 18.75 |
| 300 | 65.0 | 37.4 | 31.4 | 18.75 |
| 500 | 57.6 | 25.2 | 31.0 | 18.75 |
| 1000 | 57.6 | 25.7 | 30.6 | 18.75 |

Same transfer headings as D1. Raw PubMedQA peaks at 65.0% at 300, then falls to 57.6% at 500/1000 (baseline 57.3%). The normalized score follows a different curve. The choice-length bias identified by Claude in ADHD-03 motivates the declared raw reporting choice; these values do not justify a general medical-capability claim. No frozen scoring, option text, prediction or summary was changed.

## Fixed paper-cluster analysis

At each adapter, pre/post predictions are paired by identical question ID. Whole PMCID clusters are resampled independently within the trained and held-out groups, retaining all their questions. Accuracy is question-weighted within resampled papers.5000 replicates, random seed 20261001, percentile bounds at sorted indices125/4875, matching the earlier analysis convention. Replicates are statistical resamples, not extra model runs or training seeds. These intervals describe sampling variation over the observed papers; they do not capture training-seed uncertainty. No multiplicity correction is applied.

| Model / step | Trained gain 95% cluster CI (pp) | Held-out gain 95% cluster CI (pp) |
| --- | --- | --- |
| D1 / 250 | [+5.263, +10.600] | [+2.362, +7.208] |
| D1 / 500 | [+7.510, +13.389] | [+3.665, +9.257] |
| D1 / 1000 | [+7.022, +13.324] | [+3.462, +9.200] |
| D1 / 2000 | [+5.718, +12.810] | [+2.097, +8.300] |
| D2 / 150 | [+1.526, +6.525] | [+0.797, +5.256] |
| D2 / 300 | [+4.067, +9.423] | [+0.667, +5.145] |
| D2 / 500 | [+5.021, +11.127] | [-0.933, +3.646] |
| D2 / 1000 | [+7.103, +13.333] | [-1.316, +4.421] |

**Headings:** Model / step identifies the same trajectory and its observed adapter. Each CI is for the own-baseline gain in that question group. The extra-gain CIs are in the dose tables. None is a clinical efficacy estimate or an independently confirmed factual-memory result.

## Same-seed 500-step anchors

### D1@500 versus R3 (0.6B)

| Measure | Earlier run ending500 | Dose snapshot500 |
| --- | --- | --- |
| Trained QA (%) | 43.314763 | 45.125348 |
| Held-out QA (%) | 37.236842 | 39.210526 |
| Trained gain (pp) | 8.635097 | 10.445682 |
| Held-out gain (pp) | 4.473684 | 6.447368 |
| Extra gain (pp) | 4.161413 | 3.998314 |
| ADHD EOS PPL | 7.491381 | 7.693476 |
| General EOS PPL | 15.267462 | 16.240546 |
| ADHD no-EOS PPL | 7.456771 | 7.659961 |
| General no-EOS PPL | 15.023890 | 16.026126 |
| PubMedQA raw (%) | 55.400000 | 55.300000 |
| PubMedQA norm (%) | 55.200000 | 55.300000 |
| Validation loss | 2.098452 | 2.130712 |
| Extra gain95% cluster CI(pp) | [+0.512, +7.976] | [-0.034, +8.026] |

### D2@500 versus ADHD-03 (1.7B)

| Measure | Earlier run ending500 | Dose snapshot500 |
| --- | --- | --- |
| Trained QA (%) | 45.125348 | 45.543175 |
| Held-out QA (%) | 41.052632 | 39.736842 |
| Trained gain (pp) | 7.660167 | 8.077994 |
| Held-out gain (pp) | 2.631579 | 1.315789 |
| Extra gain (pp) | 5.028588 | 6.762205 |
| ADHD EOS PPL | 6.221857 | 6.330856 |
| General EOS PPL | 11.042535 | 11.402685 |
| ADHD no-EOS PPL | 6.192347 | 6.302066 |
| General no-EOS PPL | 10.823660 | 11.193648 |
| PubMedQA raw (%) | 62.400000 | 57.600000 |
| PubMedQA norm (%) | 37.600000 | 25.200000 |
| Validation loss | 1.930104 | 1.950154 |
| Extra gain95% cluster CI(pp) | [+1.101, +8.769] | [+3.014, +10.582] |

**Headings:** Earlier run is the independently Base-start500-update anchor; Dose snapshot is the adapter at 500 within the longer trajectory. Both columns use the exact same model, seed, data and own baselines; gain/CI/PPL definitions remain as above. This is a descriptive comparison, not an independent replication or snapshot-vs-anchor significance test.

The longer cosine horizon changes the entire learning-rate history. It remains relatively high at 500, while the earlier500-step run is already at its minimum. D1@500 improves both QA groups more than R3, yet extra gain is 3.998 versus4.161 pp and general PPL is worse. D2@500 has extra gain6.762 versus5.029 pp, with worse ADHD/general PPL and lower raw PubMedQA than ADHD-03. These observed differences are consistent with a schedule tradeoff, but do not isolate an annealing causal effect from duration or incidental execution differences.

## Validation trace (every 50 updates)

| Step | D1 validation loss | D2 validation loss |
| --- | --- | --- |
| 0 | 2.129548 | 1.952636 |
| 50 | 2.114641 | 1.924220 |
| 100 | 2.108121 | 1.926338 |
| 150 | 2.104939 | 1.923553 |
| 200 | 2.104719 | 1.923785 |
| 250 | 2.095077 | 1.919058 |
| 300 | 2.091743 | 1.915524 |
| 350 | 2.115492 | 1.938582 |
| 400 | 2.121222 | 1.947988 |
| 450 | 2.124551 | 1.949583 |
| 500 | 2.130712 | 1.950154 |
| 550 | 2.127706 | 1.951132 |
| 600 | 2.128275 | 1.953607 |
| 650 | 2.181029 | 1.992143 |
| 700 | 2.185407 | 1.995010 |
| 750 | 2.185652 | 2.000300 |
| 800 | 2.196632 | 2.004342 |
| 850 | 2.192559 | 2.004134 |
| 900 | 2.190246 | 2.005617 |
| 950 | 2.272142 | 2.033981 |
| 1000 | 2.269828 | 2.034938 |
| 1050 | 2.266584 | not in planned duration |
| 1100 | 2.271512 | not in planned duration |
| 1150 | 2.271768 | not in planned duration |
| 1200 | 2.271462 | not in planned duration |
| 1250 | 2.362492 | not in planned duration |
| 1300 | 2.355989 | not in planned duration |
| 1350 | 2.363315 | not in planned duration |
| 1400 | 2.366731 | not in planned duration |
| 1450 | 2.367419 | not in planned duration |
| 1500 | 2.365290 | not in planned duration |
| 1550 | 2.438339 | not in planned duration |
| 1600 | 2.444907 | not in planned duration |
| 1650 | 2.445161 | not in planned duration |
| 1700 | 2.451438 | not in planned duration |
| 1750 | 2.443849 | not in planned duration |
| 1800 | 2.451605 | not in planned duration |
| 1850 | 2.502328 | not in planned duration |
| 1900 | 2.503424 | not in planned duration |
| 1950 | 2.502944 | not in planned duration |
| 2000 | 2.503906 | not in planned duration |

**Headings:** Step is an observed validation checkpoint; columns are fixed 100-window next-token losses for the two models. D2 ends at 1000. Both lowest logged losses occur at 300, then generally rise. No per-step wall timestamps were saved, so timing to intermediate steps is not invented. A training loss reduction alongside validation/PPL deterioration is consistent with overfitting; it does not prove a particular factual-memory mechanism.

## Actual computation, time and resources

| Measure | D1 (0.6B) | D2 (1.7B) |
| --- | --- | --- |
| Training / validation / saved snapshots minutes | 173.93 | 176.70 |
| All final / snapshot exam phase minutes | 51.40 | 120.13 |
| Load / pre-training overhead minutes | 0.45 | 0.97 |
| Whole guarded attempt minutes | 225.78 | 297.79 |
| Last logged training tokens/s | 1712.77 | 855.42 |
| MLX peak memory (GiB) | 5.714 | 8.957 |
| Maximum sampled system swap (GiB) | 0.758 | 0.719 |
| Minimum sampled free disk (GiB) | 96.718 | 96.425 |
| Maximum local + shared attributed storage (GiB) | 8.324 | 8.669 |
| Trainable LoRA parameters | 10092544 | 17432576 |
| Each saved adapter size (MiB) | 38.541 | 66.541 |
| Updates | 2000 | 1000 |
| Processed target positions | 16384000 | 8192000 |
| Attempts / recoveries / native resumes | 1 / 0 / 0 | 1 / 0 / 0 |
| Process-local AGX fallback | unused | unused |
| Guard exit / stop reason | 0 / none | 0 / none |

**Headings:** Training minutes include validation, checkpointing and snapshot saves inside the training timer. Exam-phase wall is from the first final-exam timestamp through guarded child exit, including both protocols for four adapters and paired-report generation; timestamps are recorded to the second. Pre-training overhead is the remaining load/setup time, computed from those timers. Whole attempt wall is guard preflight through child exit. Tokens/s is the final recorded training throughput statistic, not end-to-end speed. MLX peak is framework allocation, not all macOS memory; swap is sampled system swap, not adapter memory. GiB=1024^3 bytes, MiB=1024^2. Adapter size refers to the saved weight file; configs add small metadata overhead. Local+shared storage includes the linked1.7B checkpoint once.

Total sequential pipeline wall was 523.82 minutes (8.73 hours), ending2026-10-03 11:55 JST. Both baselines were reused; this duration includes no new baseline generation. The1.7B architecture has 1.73x as many trainable adapter parameters and about half the last logged token throughput; equal update/exposure is not equal computation or capacity. Resource checks every 10 seconds stayed below4 GiB swap, above15 GiB reserve and below25 GiB attributed project budget. Brief unsampled peaks are not excluded.

## Integrity and execution evidence

All61 captured preparation, plan, config, model, input, baseline, frozen-exam and core hashes were rechecked after both conditions. Model fingerprints, exact launch/run settings, complete unique sample IDs/counts, MCQ raw/normalized summary agreement and PPL token/NLL summary agreement passed. All eight adapter weight SHA-256s match their saved metadata and paired comparisons against the correct own-model baselines. Every final/snapshot EOS exam contains all seven exams; each no-EOS exam contains the exact ADHD/general PPL pair. No frozen exam was regenerated.

Both guards recorded child exit0 with no stop reason or issues. Each condition used one attempt, no watchdog recovery/resume/AGX fallback. The runner reached its normal-completion marker; its owned processes and task-bound caffeinate are absent and its sleep assertions have released. Detailed launch, guard, hashes, paired results, cluster analysis and RUNS linkage remain in private execution records. No measured artifact was changed during final verification.

## Limits and interpretation

One seed per model; dependent points share seed, data order and trajectory. Reused exams and many metrics/doses make nominal CI exclusions exploratory and vulnerable to multiplicity. The CI procedure reflects paper sampling, not model training variance. The final 1.7B extra-gain signal is not proof that it learns factual content faster, beats0.6B across seeds, or improves clinical decisions. Frozen option scoring, paper-QA distractors, pretrained knowledge and domain-style adaptation can all influence outcomes.

Changing dose also changes exposure and learning-rate horizon;500-step comparisons carry the longer-cosine confound. Model size comparisons mix architecture, pretraining, adapter size, throughput and compute. Exposure counts target positions, not distinct facts or identical literal paper visits. Validation/PPL and paper QA reward different behavior. Reported best sampled points are descriptive, not a selected deployable optimum; no intervening point, other duration, seed or new experiment is authorized or claimed.

Signed: **Codex / GPT-6 (root), 2026-10-03 JST**. Claude / Opus5.5 retains authorship of the declared plan and snapshot implementation; this report and its analysis are Codex's work.

## Reviewer reading (Claude, Claude Opus 5.5, 2026-10-03)

This is an interpretation of the tables above; no new computation. One seed per model, and snapshots of a run are not independent.

1. **Model size matters only once the model reads more.** At 1.65 epochs the two sizes look alike: extra gain is +4.0 for 0.6B and +6.8 for 1.7B, with overlapping intervals, which matches ADHD-03. With more reading they separate. The 0.6B extra gain stays flat at about +3 to +4 pp up to 6.6 epochs. The 1.7B extra gain keeps rising: +1.0 → +3.9 → +6.8 → +8.7 pp, and its interval excludes zero from step 300. Within this range the smaller model appears to saturate in how much paper-specific content it can retain, while the larger one keeps absorbing it.
2. **Specific recall and general benefit peak at different times.** For 1.7B, held-out QA peaks at step 150, ADHD perplexity and PubMedQA raw accuracy at 300 (65.0%), and validation loss at 300. Trained-paper QA keeps rising to step 1000. For 0.6B, every measure peaks by step 250–500 and then declines. Validation loss therefore tracks the general, transferable benefit, not paper-specific recall. Stopping at the validation minimum would end training before most of the specific recall in the larger model.
3. **Forgetting rises steadily and can be severe.** General perplexity rises at every point for both models: +27% for 1.7B at 3.3 epochs and +123% for 0.6B at 6.6 epochs. By 1,000 steps 0.6B is also worse on unseen ADHD text than before training, so the extra reading overfits the 269 papers.
4. **Not a sink artifact.** EOS and no-EOS perplexity changes agree to within about one percentage point at every point (for example +123.45% vs +124.36%). The position-0 sink problem fixed in ADHD-01 is not behind the large rises.
5. **Snapshot tooling.** `--snapshot-steps` ran end to end for the first time: 8 snapshot evaluations, each against its own baseline, with no manual recovery.
