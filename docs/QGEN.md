# New-fact question-writing specification

Write paper-specific questions for the trained/untrained A/B comparison. The actual writer/model is recorded in every file. Questions must require this paper's findings and carry verbatim source evidence.

## Workflow

```sh
.venv/bin/python scripts/qgen_helper.py queue --limit 10
.venv/bin/python scripts/qgen_helper.py show PMCxxxxxxx
# Write eval/qgen/PMCxxxxxxx.json.
.venv/bin/python scripts/qgen_helper.py check PMCxxxxxxx
.venv/bin/python scripts/qgen_helper.py stats
```

Follow the queue order; group identities remain hidden. Do not inspect a paper's A/B membership while writing. Apply identical standards to every paper. Target at least 150 contributing papers and approximately 600 valid questions per group. The hard freeze gate is at least 150 contributing papers and 400 valid questions per group. Complete and validate the queued records before freezing `newfacts_*`; no additions or deletions after freezing.

## Format

Illustrative format only; replace the example with evidence copied from the actual `show` output:

```json
{
  "pmcid": "PMC1234567",
  "generator": "Actual agent / actual model",
  "created": "2026-09-30T08:00:00Z",
  "skipped_reason": null,
  "items": [{
    "question": "In a 2026 Swedish register study of adolescents with ADHD, which outcome was associated with continuous stimulant treatment?",
    "options": ["Fewer emergency visits for injuries", "Higher rates of hospital admission", "No change in school completion", "Increased cardiovascular events"],
    "answer": 0,
    "evidence": "continuous stimulant treatment was associated with fewer emergency department visits for injuries",
    "kind": "finding"
  }]
}
```

- `answer`: index 0–3. Exam construction shuffles options with a fixed seed.
- `evidence`: exact sentence or clause from the original output, at least 30 characters. Validation normalizes punctuation/case for matching.
- `kind`: `finding`, `method`, `population`, or `number`; at most one numerical question per paper.
- Unsuitable protocols, corrections, result-free commentaries or internally contradictory reports use an empty `items` list and a specific `skipped_reason`.

## Quality requirements

1. Test this paper rather than generic ADHD knowledge. A knowledgeable clinician should still need the paper to answer.
2. Make the question stand alone: specify year, design, population and/or setting. Avoid context-free phrases such as “the investigators” or “the program.”
3. Do not reveal the correct option in the question.
4. Use plausible, mutually exclusive distractors of the same type and similar length; avoid differences over roughly 50%. Character-normalized scoring is sensitive to option length.
5. Avoid all/none-of-the-above, negative traps, author/journal names and grant identifiers.
6. Write 3–5 English questions per suitable paper, covering different parts. Stems: at most 60 English words; options: preferably at most 12 words.
7. Avoid an obvious “the intervention worked” answer. Ask which group, outcome or null finding differed, or make alternatives equally plausible directions.

Opus's 2026-09-30 spot check found the correct option was longest in 35% of inspected questions versus a 25% random reference. This is a quality warning, not proof of a measured model bias. Evidence matching alone does not establish clinical accuracy or question quality. Recheck context, option lengths, independent results and observational-versus-causal wording. Every record must pass with zero REJECT entries.
