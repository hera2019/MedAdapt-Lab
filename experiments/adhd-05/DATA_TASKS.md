# ADHD-05 data task: write texts for fictional trials

Task author: Claude (reviewer, Claude Opus 5.5), 2026-10-03. Writer: Sol (Codex / GPT-6).
**This task is data only.** Training starts after Claude reviews the texts and writes the
training plan.

## Why

Real 2026 papers contain findings a model can partly guess (baseline 33–38% on four options).
ADHD-05 uses 400 fictional ADHD-drug trials whose facts were drawn at random by
`scripts/synth_trials.py`, so before training the model can only be at chance (25%). That gives
a clean measurement of what reading does: how much is remembered, whether rewording helps more
than repetition, and how this depends on model size.

Your job: for each of the 300 trials that need texts, write **four different short texts**
describing that trial, using exactly the facts in its record.

## Firewall (any breach invalidates the experiment)

- Use only these commands to get information:

  ```sh
  .venv/bin/python scripts/synth_trials.py list --limit 20   # trials still to write
  .venv/bin/python scripts/synth_trials.py show T001         # the facts of one trial
  .venv/bin/python scripts/synth_trials.py check T001        # must print PASS
  .venv/bin/python scripts/synth_trials.py stats             # progress
  ```

- Do not open, read, list or search `eval/synthetic/`. It holds the trial groups and the exam
  questions, and the writer must not know either.
- Do not read `scripts/synth_trials.py` beyond its usage text. Do not run its `generate`
  command; the data is frozen.
- Do not train or evaluate any model, and do not edit any existing file except `docs/CHANGES.md`
  (one signed row at the end).

## Output

One file per trial: `data/synthetic/texts/T001.json`

```json
{
  "trial": "T001",
  "generator": "<actual agent / actual model>",
  "created": "<UTC time, e.g. 2026-10-03T08:00:00Z>",
  "fictional": true,
  "texts": ["<version 1>", "<version 2>", "<version 3>", "<version 4>"]
}
```

## Writing rules

1. **Four genuinely different texts per trial**, 120–220 English words each (the checker
   allows 100–260):
   1. a structured abstract (background, methods, results, conclusion);
   2. a short news item for a general audience;
   3. a plain-language summary for families;
   4. a brief note from one clinician to another.

   Change the sentence order, framing and wording between versions, not just a few words. The
   checker refuses versions that share more than 40% of their 8-word sequences.
2. **Every fact from `show`, word for word**: drug name, drug class, country, population,
   sample size, duration, primary outcome, result, most common adverse event, dosing.
   Write each value exactly as given; for example, "children aged 6 to 11", not "6–11-year-olds".
   The sentence around it is yours to vary.
3. **Nothing else factual.**
   - No other numbers: no percentages, p-values, ages or dates beyond those in the record.
   - No other drug names, real or invented.
   - No second adverse event, country, outcome or dosing method, even in passing.
   - Neutral filler is fine and encouraged: how visits worked, why the condition matters, what
     placebo means.
4. **The result must read as stated.** For "early termination for lack of efficacy", say the trial
   stopped early. Do not add reasons or numbers.
5. **No quiz-like sentences.** Do not phrase sentences as questions about the facts. The checker
   refuses sentences close to the exam's own wording.
6. Write naturally, as if the trial were real, but never claim it is a real or published study.
   Do not invent authors, journals, institutions or registry numbers.

## Workflow

- Work in `list` order. Write a file, run `check`, fix every FAIL, then move on.
- Up to three collaborating agents may share the work in disjoint ranges of trial IDs (for
  example T001–T133, T134–T266, T267–T400; `list` shows only the trials that need texts). Each
  file names its actual writer.
- Log progress and problems in `data/synthetic/PROGRESS.md`.

## Done when

- `stats` reports 300 / 300 written and 300 pass.
- `data/synthetic/REPORT.md` gives: count, mean words per version type, the FAIL types you
  fixed, and a self-check of 5 random trials (all facts present, versions really different, no
  added facts).
- One signed row is appended to `docs/CHANGES.md`.

Then stop. Claude reviews a sample against the records and the hidden exams before any training
plan is written.
