# MedAdapt Lab — final report (ADHD-01 to ADHD-05)

Author: Claude (reviewer, Claude Opus 5.5), 2026-10-04. Built on the executor's findings reports (Codex / GPT-6, "Sol"), which hold every table, run ID and hash: `FINDINGS.md` (ADHD-01), `ADHD02_FINDINGS.md`, `ADHD03_FINDINGS.md`, `ADHD04_FINDINGS.md` and `ADHD05_FINDINGS.md`. Research only; nothing here is medical advice.

## The question

Can a small open language model learn new findings by continuing its training on research papers it has never seen? What does that cost in general ability?

## What was built

- **Data.** 539 openly licensed (CC0 / CC BY / CC BY-SA) ADHD papers first published in 2026, after the base models were released. They were split once, at random, into 269 papers used for training and 270 never trained on. 1,817 older ADHD papers provided general domain text.
- **Exams, frozen before training.** 1,478 four-option questions from the 2026 papers, each tied to a verbatim evidence sentence, written blind to the split. Also perplexity on the 270 held-out papers and on 50 general WikiText articles, plus existing medical question sets.
- **Training.** Qwen3-0.6B-Base and Qwen3-1.7B-Base with a hand-written MLX training loop and LoRA (rank 16, all linear layers), on one Apple M2 Max.
- **Clean test (ADHD-05).** 400 fictional trials with randomly drawn facts. Each fact was taught either through four different texts (P) or through one text read four times (R), against never-described controls (C).

Key measure: **extra gain**, the accuracy gain on trained-paper questions minus the gain on never-trained-paper questions. 95% intervals resample whole papers or trials.

## Findings

1. **Reading leaves a small, specific trace.** After about 1.65 passes over the 269 papers, extra gain was +4.2 [+0.5, +8.0] (0.6B, seed 42), +3.8 [−0.2, +7.7] (0.6B, seed 43) and +5.0 [+1.1, +8.8] pp (1.7B). Most of the improvement (+3 to +5 pp) also appeared on never-trained papers: it was general familiarity with this kind of paper, not specific knowledge.
2. **Capacity limits how much is retained.** With more reading the 0.6B extra gain stayed near +4 pp up to 6.6 passes. The 1.7B extra gain rose to +8.7 [+4.4, +12.9] pp at 3.3 passes.
3. **Specific recall and general benefit peak at different times.** Held-out papers' perplexity, never-trained questions and validation loss were best at about one pass. Recall of trained papers kept rising in the 1.7B model. Stopping at the validation minimum would stop before most specific recall.
4. **Every gain had a cost.** General-text perplexity rose at every measured point: +7% to +123% on real papers, depending on model and dose. With heavy reading the 0.6B model became worse than before even on unseen ADHD text.
5. **Facts the model cannot know are learnable, but only with many exposures.** On fictional trials, recall started at chance (25%) and the control group stayed there. Recall emerged abruptly between about 4 and 8 passes (16–32 mentions of each fact) and ended at 44–51% (P) and 40–43% (R).
6. **Rewording beats repetition.** At equal exposure, four different texts beat one text read four times by +4.5, +6.3 and +7.6 pp in three of three runs, with all intervals excluding zero. Four short rewrites of real papers (about 14% of the training text, ADHD-02) had shown no gain; the amount was too small, not the idea wrong.
7. **Narrow new-fact training without replay is destructive.** Training on the small, repetitive fictional corpus raised general perplexity 5–11× after one pass and 37–94× by the end. Real-paper training changed it by about 10% over hundreds of steps. Partial recall came at the price of a badly damaged general model. Mixing in general text, lower learning rates or retrieval instead of training are the usual remedies; they were not tested.

## What went wrong, and how it was handled

- **Collapsed attention sink.** The first full run seemed to raise perplexity by 238–413%. Training had stopped the model forming its position-0 activation (norm about 6,800 down to 84) whenever the window began with the end-of-text token, which the perplexity test always placed there. The fix was to start every training window with that token. Perplexity is now measured with and without it, and the two agree.
- **Biased benchmark score.** Character-length normalisation favoured "maybe" over "no" on PubMedQA. The 1.7B model never chose "no", and a reported decline was an artifact. The 0.6B model answered "yes" to almost everything, so that benchmark never informed the small model.
- **Data defects caught before training.** Abstract-only records, papers dated 2026 but first published earlier, benchmark questions that mentioned ADHD only as a wrong option, and three near-duplicate old reviews were removed.
- **GPU watchdog interruptions** (macOS "Impacting Interactivity"). Training gained 50-step checkpoints and resume. Memory pressure contributed in some full-parameter attempts, but the root cause was not confirmed.
- **Not completed.** A full-parameter fine-tuning control (paused after unresolved Metal failures and rising validation loss).

## Limits

- Mostly one training seed per condition. Intervals describe question and paper sampling, not training variability.
- The frozen exams were reused across experiments, and later designs were informed by earlier results. These are exploratory findings, not confirmatory tests.
- Questions were written by an AI model and checked against source text, not validated by clinicians. Multiple-choice likelihood scoring measures recall, not understanding or safety.
- Publication in 2026 lowers, but cannot exclude, prior exposure to the same work.
- The fictional texts are heavily templated (about 65–71% of each text's 6-word sequences recur across 30 or more trials), so ADHD-05 measures recall of templated statements.
- Model size differs from the other conditions in architecture, parameter count and compute, not only in size.

## Reproducibility

Code: `scripts/` (Apache-2.0, public at github.com/hera2019/MedAdapt-Lab). Run configurations, data and model hashes, training logs, per-item exam results and comparisons are kept locally (`experiments/`, `results/exams/`). Papers, model weights, adapters, question texts and all fictional-trial data are not redistributed.
