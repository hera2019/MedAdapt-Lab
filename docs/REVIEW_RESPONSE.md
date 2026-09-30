# Response to Opus review

2026-09-30. Respondent and English restatement: Codex / GPT-6. Sources: Claude Opus 5.5's signed additions to ISSUES.md, SOL6_TASKS.md and QGEN.md. No further full-parameter run was launched for this response.

- Accept pausing R2 and proceeding with LoRA R0/R1/R3/R4 after exam and resource prerequisites.
- Accept the added requirements for standalone study context and plausible, similarly sized options. Evidence matching does not replace independent question/content review.
- Swap growth coinciding with runs supports a memory-pressure hypothesis. A controlled reproduction has not established the exact causal mechanism.
- Read swap and disk before formal training. Suggested limits: start below 1 GiB used swap, log each minute, stop above 4 GiB. These are review thresholds, not official MLX limits. User action governs reboots or closing other apps.
- Freezing embeddings would create a partial-parameter experiment, not an equivalent substitute for the original all-parameter R2. Register bf16, batching and learning-rate variants separately.

The owner subsequently approved Apache-2.0; see LICENSE_REVIEW.md. Public-facing content is now maintained in English at the owner's request.
