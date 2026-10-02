# ADHD-03: 1.7B Base with the R3 original-only configuration

2026-10-02 JST. Plan/preparation author: Codex / GPT-6 (root). The owner explicitly selected the 1.7B download and asked to wait for their departure notification before running. Status: **preparation only; formal execution awaits the owner's explicit start message**. No heartbeat, baseline exam, smoke training or formal training is started during preparation.

## Selection and storage

Model: official `Qwen/Qwen3-1.7B-Base`, unquantized bf16, commit `ea980cb0a6c2ae4b936e82123acc929f1cec04c1`. Apache-2.0 was checked in the pinned upstream LICENSE, not inferred from a different model. Selected files total 3,452,687,825 bytes (~3.45 decimal GB / 3.22 GiB); exact acquired file hashes/sizes/dates/URLs and licensing notes belong in the private manifest. Physical weights are centralized in the owner's AI-Models generators directory; the project path `models/qwen3-1.7b-base` is a symbolic link. No existing shared model is replaced. Shared deletion requires checking other consumers, so it is not automatically safe. The local acquisition record contains the absolute target; public docs omit the owner's machine paths.

Source: https://huggingface.co/Qwen/Qwen3-1.7B-Base/tree/ea980cb0a6c2ae4b936e82123acc929f1cec04c1
License: https://huggingface.co/Qwen/Qwen3-1.7B-Base/blob/ea980cb0a6c2ae4b936e82123acc929f1cec04c1/LICENSE

## Fixed comparison

Use the revised R3 seed42 original-only corpus, not ADHD-02 rewrites: `data/train/adhd-01/train_new.jsonl`, with unchanged `data/validation/adhd-01/valid.jsonl`. All 269 eligible papers and frozen evaluation files remain intact. Independent start from the new Base, not from a 0.6B adapter or a previous trained model. Existing 0.6B reference: `20260930T184551Z-lora-r3-newonly-eosprefix`.

Preserve every R3 training setting: all-layer LoRA rank16 / alpha32 / dropout0, sequence1024 with EOS prefix, physical batch1 x accumulation8, 500 updates, lr2e-4 / warmup30 / minimum ratio0.1, 100 fixed validation windows, cache2GiB, checkpoint50, seed42. A larger architecture has different base weights, parameter count and LoRA shapes; equal rank is not equal adapter parameter count or equal compute. Verify tokenizer equivalence during preparation. Model quality is not guaranteed by size.

After the owner's start message, take this exact 1.7B model's own complete untouched baseline before training. `train.py` automatically records it if no exact-model/exam/protocol baseline exists. Use all frozen post-exams and EOS/no-EOS PPL comparisons against that baseline. Compare training-induced changes with the completed 0.6B R3, retaining each size's own baseline. Absolute post-training accuracy alone mixes pretrained knowledge with adaptation. The same 500-update endpoint tests gain at fixed exposure; it does not establish faster factual learning from an intermediate paper-QA learning curve. Validation every50 provides prediction-loss progress, not intermediate QA evidence. No extra training duration, seed or score tuning is selected by this plan.

## Run-time gates

At start, recheck hashes/readiness and use the outer guard: launch swap below3GiB, stop at4GiB, check every10seconds, project budget25GiB and system reserve15GiB. Preserve all layers/context/effective batch; stop on resource or stability failures and record the failure rather than silently shrinking the experiment. The 1.7B load/tokenization check is preparation evidence only; training peak/throughput and stability are not yet measured. The owner's estimate of 2–3x slower is a forecast, not a local result. Checkpoint resume retains original model/data/config/optimizer/order. Do not repeat an interrupted baseline blindly or use a 0.6B baseline for 1.7B.

The launcher defaults to checking only. Formal execution requires an explicit `--start` invocation after the owner's human start message. Task-bound `caffeinate -is` applies only during the authorized launch and releases on exit. No permanent system change, app closing or UI operation. No automatic schedule for this run.

## Acceptance and stopping

Prepare pinned licensed weights, provenance, same-R3 config and a load/readiness check now. Formal results are pending. When authorized, complete exactly one 500-update run with baseline/post-exams, saved adapter fingerprints and resource records, or a signed failure record. Report favorable, adverse and inconclusive outcomes. One seed, reused exams, different pretrained states and architecture/compute confounds limit size conclusions. No evidence here establishes clinical advice safety. R2 remains paused.

## Prepared launcher

Once preparation passes, `.venv/bin/python scripts/run_adhd03.py` verifies captured inputs and runs readiness only. After the owner's explicit start message, use `.venv/bin/python -u scripts/run_adhd03.py --start` with a new local console log. The launcher passes every prepared R3 setting explicitly, checks current resources and frozen exams, and binds sleep prevention to that run. `readiness.json` records preparation evidence only, not baseline or training scores.

## Reacquisition of shared weights

The existing approved downloader's registrar accepts project-local destinations only. Do not invoke it through a shared-directory symlink. To reacquire after an ownership/consumer review, temporarily detach only the project link, use a clean project-local staging directory for `hf_download.py qwen3-1.7b-base --revision ea980cb0a6c2ae4b936e82123acc929f1cec04c1`, verify the registered exact file hashes, and place the verified staging directory in a new or reviewed shared target before recreating the project link. Preserve any existing target until its ownership and condition are resolved; shared deletion is not automatically authorized. Keep the private manifest/readiness/source records for reconstruction. Download URLs point to each exact file at the pinned commit; no account/token is required for these public files.
