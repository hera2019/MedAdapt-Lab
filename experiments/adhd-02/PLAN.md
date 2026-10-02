# ADHD-02: original text plus blind paraphrases

Declared before new training on 2026-10-02 JST by Codex / GPT-6 (root). The owner authorized continued overnight training and relevant additional experiments. This is the executor's new exploratory plan; it is not a claim of prior Opus review. No new model, dependency or download is required.

## Question and fixed design

Does adding four independently written styles for each of the same 269 new-train papers improve paper-specific QA under equal optimizer updates, compared with original text alone? The completed ADHD-01 revised R3 (seed 42, run `20260930T184551Z-lora-r3-newonly-eosprefix`) is the existing control. R5 denotes original new-train chunks followed by the four rewrites per paper in sorted PMCID / summary, plain, facts, news order. The source texts and rewrites are not modified.

Tonight's fixed sequence:

1. R5, original plus rewrites, seed 42.
2. R3 replication, original only, seed 43.
3. R5 replication, original plus rewrites, seed 43.

All start independently from the pinned Qwen3-0.6B-Base bf16 weights. Preserve all-layer LoRA rank 16 / alpha 32 / dropout 0, 500 updates, EOS-prefixed sequence 1024, microbatch 1 x accumulation 8, lr 2e-4 / warmup 30 / minimum ratio 0.1, fixed 100 validation windows, cache 2 GiB, checkpoint every 50 updates. Seed changes initialization and shuffled sampling together. Both seeds are fixed in advance; no intermediate scores select a seed, duration or hyperparameter. The existing full corpus R1b/R4 are contextual references, not matched controls for augmentation.

## Data and evaluation firewall

`data/train/adhd-02/train_original_plus_rewrites.jsonl` is a new derived file. Include only the same split's new-train PMCID set. No validation/held-out papers, questions, options, evidence sentences or evaluation outputs are used as training input. Check the completed rewrite corpus through `augment_check.py stats`, membership, four styles, actual author metadata, 250–600 words, and frozen source hashes. Record each input and generated output with SHA-256, size and provenance in `dataset_manifest.json`. The original raw/derived files and frozen roles, benchmark exclusions, split, exams and index stay unchanged. Validation remains the ADHD-01 pool validation file. Keep all text/weights/raw scoring local.

Reuse existing exact-model/exam baselines. Every run takes full frozen post-exams and both separately labelled PPL protocols. After the entire fixed sequence, compare R5 with its same-seed R3 control using the existing paired scoring. Primary exploratory contrast: trained-minus-held-out accuracy change, bootstrapped by PMCID (5,000 replicates, seed 20261001). Report trained and held-out QA separately, domain/general PPL, medical controls, validation and resources, including adverse/null findings. Never subtract between EOS and no-EOS PPL protocols. Two seeds are a limited replication, not a robust estimate of seed variance or an independent test set; no multiplicity adjustment. Existing exams have been reused and motivated this exploratory follow-up.

## Confounds and limits

Both conditions sample 4.096 million training targets. The augmented corpus is larger and changes window boundaries, shuffled order, style mixture and exposure per original token. This tests the augmentation package at fixed compute, not paraphrasing isolated from document exposure or a token-matched original-only intervention. Synthetic text may contain errors despite checks and limited spot reviews. The numeric/wording checker is not semantic validation; exam phrase avoidance is not proof of zero semantic overlap. Paper QA and PPL do not establish clinical safety or usefulness. No promise of benefit is made.

## Operational gates and stopping

Run fresh native selftests because the rewrite helper was added since the previous batch. Check storage with 1 GiB planned allowance: project budget 25 GiB, system reserve 15 GiB. Native launch swap must be below 3 GiB; guard stops at 4 GiB, polling every 10 seconds. Verify frozen/model/core hashes before every launch. Use task-bound `caffeinate -is`; no permanent system setting, app closing or UI operation.

Begin without a GPU timeout override. The previously explained and owner-authorized process-local Metal fallback remains limited to the owned child after the specific watchdog failure. Resume a saved checkpoint with the same config/data; restart once if failure precedes its first checkpoint. Stop on resource/other failures or repeated lack of checkpoint progress. Do not keep adding experiments after this fixed sequence; summarize evidence and release sleep assertions on completion/failure.

Outputs: independent native run records (existing trainer stores them under `experiments/adhd-01/runs`, with ADHD-02 linkage in `RUNS.json`), private attempt/resource logs, `results/ADHD02_FINDINGS.md`, a Chinese explanation, signed CHANGES/SOL6_REPORT entries. Public material is English and must pass the existing snapshot audit; private datasets and development history are excluded.
