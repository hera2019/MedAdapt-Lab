# ADHD-01 experiment

Updated 2026-10-01 by Codex / GPT-6 (root). R0, original R1, revised R1b (500 updates), R3 (new-only, 500) and R4 (full corpus, 1000) completed their full exams and paired comparisons. R2 remains paused. Revised R3 shows a larger trained-paper QA gain under an exploratory paper-cluster analysis; R4 improves domain PPL further than R1b with a small additional general-text regression. Both scoring protocols and original R1's adverse EOS results are preserved. The correction was outcome-informed; one seed and no multiplicity adjustment limit conclusions. See [the findings](../results/FINDINGS.md). Frozen A/B exams contain 718/760 questions from 223/238 contributing papers; 539 records yielded 1478 questions and 78 documented skips. Native runs preserve 50-step checkpoint traces. Resource policy was launch below 3 GiB swap, stop at 4 GiB and check every 10 seconds; guard defaults are unchanged.

## Questions

1. Does DAPT on paper text retain specific findings from trained papers, relative to unseen-paper questions?
2. Does held-out ADHD perplexity improve?
3. How much general-language performance is lost?
4. How do adaptation method, rank, rate and corpus size affect these outcomes?

## Paper roles

| Set | Local source and count | Role |
|---|---|---|
| `pool` | Pre-2026 search: 6,210 candidates, 1,817 usable texts | DAPT; approximately 5% held for training validation by PMCID |
| `new_train` | 269 eligible 2026 papers | DAPT and group A knowledge questions |
| `new_heldout` | 270 eligible 2026 papers | Never train; group B questions and held-out ADHD perplexity |

Select MeSH D001289 or ADHD/attention-deficit title matches and eligible article licenses. Screen earliest JATS publication date; exclude new candidates first published before 2026. Freeze new roles once with seed 42. A paper in both searches belongs to the new set.

Publication year reduces overlap risk but does not establish that the base model never saw related preprints, earlier versions or duplicated findings. Exact identifiers and hashes also cannot detect every semantic duplicate; three suspicious old-paper matches were manually excluded and recorded.

## Exams: ADHD-01-v1

| Exam | Type | Role |
|---|---|---|
| `newfacts_trained` | Cloze multiple choice | Knowledge; trained-paper questions |
| `newfacts_heldout` | Cloze multiple choice | Control; unseen-paper questions |
| `adhd_new_ppl` | Perplexity | Domain familiarity; 270 held-out papers |
| `general_ppl` | Perplexity | Forgetting; 50 WikiText items |
| `medmcqa_psych`, `medmcqa_general` | Multiple choice | Secondary transfer; 16 and 500 items |
| `pubmedqa` | yes/no/maybe | Secondary transfer; 1,000 items |

Strict ADHD stem screening found zero suitable MedMCQA validation items, so no `medmcqa_adhd` exam is fabricated.

Multiple-choice scoring sums option log-probability after the prompt, divides by character count (`acc_norm`), and selects the best option. Record `p_correct` too: it is the correct option's softmax share of character-normalized log scores, not a calibrated probability of clinical correctness. Perplexity uses non-overlapping 1024-token windows. Evaluation temporarily bounds the free MLX allocator cache to 512 MiB and restores the caller policy on success or failure; this does not alter scoring or the training cache settings. Pair item IDs, use bootstrap 95% confidence intervals, and require McNemar's exact test agreement for choice significance. Exams under 10 items receive no significance verdict; small exams still warrant caution.

## Run sequence

| ID | Configuration | Purpose/status |
|---|---|---|
| R0 | 0.6B Base baseline | Only after complete A/B exams are frozen |
| R1 | 0.6B LoRA r=16, lr 2e-4, 500 steps | Main adaptation run |
| R2 | Historical 0.6B full float32, lr 2e-5 | Paused: Metal and validation acceptance unresolved |
| R1b | R1 with EOS-prefixed packing | Reviewed protocol correction |
| R3 | EOS-prefixed LoRA on `new_train` only | Effect of corpus selection |
| R4 | R1b at 2x steps (1000), independently from Base | Additional exposure |
| R5 | 1.7B repeat of R1 | Deferred scale comparison |
| ADHD-02 | Possible paraphrased/synthetic continued pretraining | Later experiment, not currently selected |

Before formal training, complete all queued paper records, validate evidence and quality, and meet at least 150 contributing papers / 400 valid questions per A/B group. Target roughly 600 questions per group. Freeze only once.

Each formal training run obtains a baseline if absent, trains, examines the adapter and creates `compare_vs_baseline.md`. Preserve configs, data/model/adapter hashes, raw responses, training curves, peak memory and the comparison ledger. Use `exam.py compare` for additional paired run comparisons.

Tune on training validation loss; exams measure outcomes rather than selecting settings repeatedly. If exam-informed changes occur, identify the iteration explicitly. Do not turn an incomplete smoke run or absence of statistical significance into a scientific improvement claim. Cite run IDs and actual paired reports in `results/FINDINGS.md` when those runs exist.
