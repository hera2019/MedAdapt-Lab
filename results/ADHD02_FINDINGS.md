# ADHD-02: original text plus blind rewrites

Completed 2026-10-02 JST. Executor, analyst and report author: Codex / GPT-6 (root). Rewrite authors remain individually credited in the local corpus; the validation helper is by Claude / Opus 5.5. This follow-up plan was declared by the executor before new training, under the owner's overnight authorization; it is not a claim of independent reviewer approval.

## Conclusion

Adding the four rewrite styles did not demonstrate an additional trained-paper QA advantage at fixed compute in either seed. The trained-minus-held-out accuracy-change estimate versus original-only was negative in both seeds, with paper-cluster intervals including zero. This does not establish equivalence or prove that other augmentation designs cannot work.

Seed 42 produced a small ADHD PPL reduction, a general-text PPL regression and a PubMedQA decline. Seed 43 did not replicate the ADHD PPL reduction or the PubMedQA decline; general-text PPL improved relative to its original-only control. Paper QA changes were not significant under the existing paired procedure in either seed. Thus, no consistent augmentation gain is established; retain original-only R3 as the reference for this fixed-compute design. All trained variants still have worse general PPL than the untouched Base within each protocol.

## Fixed design and provenance

The same 269 eligible new-train papers produced 3,481 original chunks and 1,076 blind rewrite texts. Combined: 4,557 rows, 2,876,322 tokenizer-stream tokens (including separators), of which 396,675 are rewrites (~13.791% of the augmented stream). The local file is 14,196,806 bytes. Its SHA-256 is `d3f59e16125a347bdef900e6f43054404a51e97b4dc9cde4d83dbd38f3ee7a1a`. The raw-source licenses/hashes, authors, filtering and regeneration instructions remain in the private `experiments/adhd-02/dataset_manifest.json`; no corpus redistribution is authorized here.

Each independent Base-start run used all-layer rank-16 LoRA, alpha 32, dropout 0, EOS-prefixed sequence 1024, microbatch 1 x accumulation 8, 500 updates, peak lr 2e-4, warmup 30 and minimum ratio 0.1. All 196 linear projections are adapted; 10,092,544 trainable parameters. Each condition processes 4,096,000 targets, about 1.652 original-only stream epochs or 1.424 augmented stream epochs. Epochs are approximations because of packing, dropped remainders and sampled windows. No final adapter was selected using validation-best or intermediate exam scores.

## Completed scores

| Measure / evaluation sample | Original seed 42 (existing R3) | Augmented seed 42 (R5) | Original seed 43 | Augmented seed 43 (R5) |
|---|---:|---:|---:|---:|
| Trained-paper QA (718 questions) | 43.315% | 43.454% | 44.150% | 43.315% |
| Held-out-paper QA (760 questions) | 37.237% | 37.763% | 38.421% | 38.553% |
| ADHD PPL, EOS (270 papers) | 7.491381 | 7.468810 | 7.481391 | 7.478000 |
| General PPL, EOS (50 texts) | 15.267462 | 15.370472 | 15.410162 | 15.324746 |
| ADHD PPL, no EOS | 7.456771 | 7.440135 | 7.451933 | 7.452305 |
| General PPL, no EOS | 15.023890 | 15.198689 | 15.177852 | 15.122234 |
| Psychiatry MCQ (16 questions) | 25.000% | 25.000% | 25.000% | 18.750% |
| General medical MCQ (500 questions) | 31.400% | 31.400% | 31.400% | 30.200% |
| PubMedQA (1000 questions) | 55.200% | 53.800% | 54.600% | 55.100% |

**Headings:** Original = paper text only; augmented = the same original chunks plus four rewrite styles; seed = the fixed initialization/sampling setting. The seed-42 original run predates this batch, using the same captured model/data/config. QA/MCQ cells are percent correct under the frozen character-normalized choice scoring (higher is better). PPL cells are perplexity for next-token prediction (lower is better); they are not percentages or answer accuracy. Parenthetical counts are questions for QA or documents for PPL. EOS/no-EOS denote separate input-prefix protocols; compare only within a protocol.

## Matched-seed paired changes: augmented minus original

| Measure | Seed 42 change [95% CI] | Seed 42 paired verdict | Seed 43 change [95% CI] | Seed 43 paired verdict |
|---|---:|---|---:|---|
| Trained-paper QA (718 questions) | +0.139 pp [-1.950, +2.228] | No significant change | -0.836 pp [-2.925, +1.393] | No significant change |
| Held-out-paper QA (760 questions) | +0.526 pp [-1.447, +2.500] | No significant change | +0.132 pp [-2.105, +2.237] | No significant change |
| ADHD PPL, EOS (270 papers) | -0.301% [-0.404, -0.201] | Significant decrease (better) | -0.045% [-0.150, +0.054] | No significant change |
| General PPL, EOS (50 texts) | +0.675% [+0.308, +1.073] | Significant increase (worse) | -0.554% [-0.905, -0.208] | Significant decrease (better) |
| ADHD PPL, no EOS | -0.223% [-0.327, -0.123] | Significant decrease (better) | +0.005% [-0.147, +0.183] | No significant change |
| General PPL, no EOS | +1.163% [+0.769, +1.581] | Significant increase (worse) | -0.366% [-0.713, -0.018] | Significant decrease (better) |
| Psychiatry MCQ (16 questions) | +0.000 pp [+0.000, +0.000] | No significant change | -6.250 pp [-18.750, +0.000] | No significant change |
| General medical MCQ (500 questions) | +0.000 pp [-2.400, +2.400] | No significant change | -1.200 pp [-3.600, +1.000] | No significant change |
| PubMedQA (1000 questions) | -1.400 pp [-2.300, -0.600] | Significant decline | +0.500 pp [-0.300, +1.300] | No significant change |

**Headings:** Change is augmented minus same-seed original. Accuracy changes use percentage points (pp); PPL changes are relative percentages. Brackets are 95% confidence intervals from paired question/document resampling. The existing QA verdict also requires the paired McNemar test; these intervals are not paper-clustered. No multiplicity adjustment is applied, so nominal significance is exploratory. A CI crossing zero does not prove equality. `p_correct` is a softmax share of normalized scores, not calibrated clinical confidence; it is not the primary endpoint.

PubMedQA seed 42: 55.2% -> 53.8%, -1.4 pp [−2.3, −0.6], exact McNemar p=0.0013123 (nominal). Seed 43: 54.6% -> 55.1%, +0.5 pp [−0.3, +1.3], p=0.3323. The adverse seed-42 result remains visible; neither seed is cherry-picked. Psychiatry has only 16 questions, so one answer changes accuracy by 6.25 pp; it is not a dedicated ADHD clinical benchmark.

## Primary exploratory paper-cluster contrast

| Seed | Trained-paper QA change (pp) | Held-out-paper QA change (pp) | Trained minus held-out change (pp) | 95% paper-cluster CI (pp) |
|---|---:|---:|---:|---|
| 42 | +0.139 | +0.526 | -0.387 | [-3.242, +2.504] |
| 43 | -0.836 | +0.132 | -0.967 | [-3.898, +1.992] |

**Headings:** The two changes compare augmented with its original-only control. The fourth column subtracts the held-out change from the trained-paper change, estimating whether augmentation helps trained papers more. A/B have 223/238 contributing papers and 718/760 questions. Resample whole PMCID clusters independently within each group: 5,000 replicates, seed 20261001; question-weighted accuracy within each sampled cluster. These are resampling replicates, not additional training runs. Both intervals include zero; no additional trained-specific gain is demonstrated.

## Validation and resources

| Condition / seed | Validation loss start -> final | MLX peak (GiB) | Train minutes | Guarded minutes incl. exams | Maximum swap (GiB) |
|---|---:|---:|---:|---:|---:|
| augmented / 42 | 2.129548 -> 2.098794 | 5.710 | 43.58 | 56.91 | 0.781 |
| original / 43 | 2.129548 -> 2.097398 | 5.710 | 43.47 | 56.79 | 0.781 |
| augmented / 43 | 2.129548 -> 2.098306 | 5.710 | 43.46 | 56.78 | 0.781 |

**Headings:** Validation loss = average next-token cross-entropy on the same 100 fixed pool-validation windows, not the test exam (lower is better); use final loss, not the best observed loss. MLX peak = framework-reported memory, not total macOS memory or swap. Train minutes include training/validation/checkpoint work; guarded minutes additionally include model loading and both post-exam protocols. Swap is memory paged to disk, not the model file size. GiB = 1024³ bytes.

The fixed pipeline took 170.67 minutes, finished at 05:44:02 JST, and exited 0. All three train guards and both sink probes exited 0 with no stop reason, no retry, no native checkpoint resume and no AGX override. Maximum swap was 0.781 GiB; minimum observed free disk was 101.620 GiB, above the 15 GiB reserve. Checkpoints were enabled every 50 updates; this uninterrupted batch does not itself validate native resume. The preflight selftest verified tiny-model resumed-versus-uninterrupted equality. Task-bound caffeinate ended with the runner; its utility/session exit 0 and absence of the owned runner were verified.

EOS sink norms: Base 6868, augmented seed42 7415, augmented seed43 7835. Both remain in the expected thousands; the diagnostic is not a clinical capability measure.

## Integrity and interpretation limits

- All 838 captured model/input/frozen/source files and five core framework fingerprints matched the preflight; all 269 licensed raw-source hashes and all four compared adapter hashes were checked. Both independent conditions have the same model fingerprint and frozen validation hash. No frozen exam, question, split or role was regenerated.
- Rewrite checker PASS, word/number screening and limited author spot-checks do not prove every generated statement accurate. Exam phrase avoidance is not proof of zero semantic overlap or model pretraining contamination. The retained source authors/licenses and synthetic authorship are not replaced by the code license.
- Fixed compute is not fixed original-token exposure: augmentation changes corpus size, mixture, packing and shuffle. This tests the declared augmentation package, not paraphrasing isolated from all other factors.
- Seeds change initialization and sampling together. Two seeds do not estimate population seed variance or justify a pooled seed-level significance claim. The same frozen exams have already informed exploratory project choices; no independent confirmation test or multiplicity correction was used.
- QA choices and text prediction are limited proxies; these results do not establish safe clinical advice, treatment benefit or patient outcomes. Preserve earlier ADHD-01 negative results and the paused full-training condition. No further model/download/experiment is scheduled by this plan.

## Run and exam identifiers

- **original, seed 42:** `20260930T184551Z-lora-r3-newonly-eosprefix`. EOS exam `20260930T192941Z-after-20260930T184551Z-lora-r3-newonly-eosprefix`; no-EOS exam `20260930T193840Z-after-20260930T184551Z-lora-r3-newonly-eosprefix`. Adapter SHA-256 `26b2070e8052d8577f6c43642e693508fc4eaf577913e3ec5c0d35127edd8aef`.
- **augmented, seed 42:** `20261001T175323Z-lora-adhd02-r5-aug-seed42`. EOS exam `20261001T183725Z-after-20261001T175323Z-lora-adhd02-r5-aug-seed42`; no-EOS exam `20261001T184624Z-after-20261001T175323Z-lora-adhd02-r5-aug-seed42`. Adapter SHA-256 `ab9529fa56207a2d17ef061b4fbd0e151e5cf23f37478ec0b5fe3feb9fcf1aef`.
- **original, seed 43:** `20261001T185018Z-lora-adhd02-r3-original-seed43`. EOS exam `20261001T193413Z-after-20261001T185018Z-lora-adhd02-r3-original-seed43`; no-EOS exam `20261001T194313Z-after-20261001T185018Z-lora-adhd02-r3-original-seed43`. Adapter SHA-256 `94be5f5f94580b1aa1a7cb65e319e79f15bcd080e2d82fabd55043ed78a56993`.
- **augmented, seed 43:** `20261001T194707Z-lora-adhd02-r5-aug-seed43`. EOS exam `20261001T203101Z-after-20261001T194707Z-lora-adhd02-r5-aug-seed43`; no-EOS exam `20261001T204001Z-after-20261001T194707Z-lora-adhd02-r5-aug-seed43`. Adapter SHA-256 `335368cb60e9ab903d90055dd88edbb9ccbb3300a55aecb078e06c729087cf76`.

## Reviewer check (Claude, Claude Opus 5.5, 2026-10-02)

Exploratory and post hoc; it reuses the frozen per-item results and changes no score.

**1. Each run against R0.** The paper-cluster bootstrap matches the procedure above (5,000 replicates, seed 20261001). Every run trained only on new_train papers has a positive trained-minus-held-out estimate:

| Run | Trained change | Held-out change | Trained − held-out | 95% paper-cluster CI |
|---|---:|---:|---:|---|
| R3 original, seed 42 | +8.64 | +4.47 | +4.16 | [+0.42, +7.97] |
| R3 original, seed 43 | +9.47 | +5.66 | +3.81 | [−0.18, +7.73] |
| R5 augmented, seed 42 | +8.77 | +5.00 | +3.77 | [−0.28, +7.65] |
| R5 augmented, seed 43 | +8.64 | +5.79 | +2.85 | [−1.11, +6.70] |

The seed-43 replication of R3 gives a similar estimate (+3.8 vs +4.2 pp) with an interval just touching zero. All four estimates point the same way. Taken together, concentrated training on the 269 papers gives a modest trained-paper-specific gain of roughly 3–4 pp; no single run is decisive.

**2. Why the rewrites added nothing: dose, not coverage.**
- 410 of the 718 trained-paper answers have every content word present in that paper's rewrites, and 283 more have some. Even the fully covered items show no augmentation gain: −0.7 / −1.2 pp for seeds 42 / 43.
- The rewrites are small: a median of about 1,100 words per paper, 13.8% of the augmented stream, each read about 1.4 times.
- Published synthetic continued-pretraining results use synthetic text many times larger than the source. This experiment therefore tests a small, Claude-specified dose (250–600 words per style). It does not show that augmentation fails in general.
