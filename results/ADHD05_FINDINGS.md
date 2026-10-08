# ADHD-05 findings: fictional-trial recall

Date: 2026-10-04 JST. Analysis and execution author: Codex / GPT-6 (root). Plan, data review, corpus/exam construction and fixed reporting script: Claude / Opus 5.5. Synthetic text authors remain credited in the data handoff; this report does not reassign their authorship.

Status: all three prescribed trajectories, all 15 adapter points, all full exam pairs and all three unchanged fixed reports completed and verified. Private aggregate report for owner review. No publication or push was authorized or performed.

## Main measured findings

At the final 600 updates, both described groups improved over their own model baseline relative to the never-described control. The four-template group had a positive advantage over repeating one template four times in all three runs. These measurements concern recall of heavily templated fictional statements. General-text perplexity deteriorated severely at every measured point, including before the early recall contrasts excluded zero.

| Run | Final P / R / C acc_norm (%) | P−R gain contrast (pp), 95% CI | P−C gain contrast (pp), 95% CI | R−C gain contrast (pp), 95% CI | Final general PPL / baseline, EOS / no-EOS |
| --- | --- | --- | --- | --- | --- |
| S1 | 43.70 / 39.78 / 23.89 | +4.52 [+0.44, +8.59]; zero: no | +18.78 [+14.48, +23.11]; zero: no | +14.26 [+9.78, +18.67]; zero: no | 93.27× / 92.19× |
| S2 | 51.33 / 43.26 / 24.00 | +6.30 [+1.93, +10.67]; zero: no | +24.37 [+19.59, +29.07]; zero: no | +18.07 [+13.26, +22.85]; zero: no | 36.59× / 35.49× |
| S3 | 49.11 / 42.15 / 22.56 | +7.56 [+3.33, +11.85]; zero: no | +25.52 [+21.22, +29.85]; zero: no | +17.96 [+13.56, +22.33]; zero: no | 93.77× / 92.63× |

## Design, exposure and measurement definitions

P: 150 trials, four different genre templates once each per corpus pass. R: 150 trials, one genre template four times per pass. C: 100 trials never described in the corpus. Each trial has nine frozen four-option questions: P 1,350, R 1,350, C 900. Each full EOS exam also evaluates all 50 general-text PPL samples; each no-EOS supplement evaluates the same 50 general-text samples. All points use the complete fixed sets and the exact matching Base model baseline. S3 reuses the verified 0.6B baseline from S1.

The accepted corpus has 1,200 documents and 238,915 stream tokens, yielding 233 EOS windows at length 1,024. An update samples eight windows (8,192 sequence positions). Nominal exposure is steps × 8 / 233: 1.03, 2.06, 4.12, 8.24 and 20.60 window-passes at steps 30, 60, 120, 240 and 600. Token-stream approximation gives 1.03, 2.06, 4.11, 8.23 and 20.57 passes. These are exposure approximations rather than guarantees of complete ordered epochs. Each fact appears four times per corpus pass; the fixed corpus separates copies by at least eight documents.

All runs start independently from Base: S1 Qwen3-0.6B-Base seed 42; S2 Qwen3-1.7B-Base seed 42; S3 Qwen3-0.6B-Base seed 43. All have 600 updates, snapshots 30/60/120/240, LoRA rank 16 / alpha 32 / dropout 0 on all layers, EOS sequence windows 1,024, batch 1 × accumulation 8, peak learning rate 2e-4, 30-update warmup and cosine decay to 10%, no weight decay, gradient norm limit 1, checkpoint every 50, cache 2 GiB. Validation uses 100 windows of real ADHD paper text every 50 updates. The captured launch/config records verify every setting.

Accuracy is the frozen length-normalized acc_norm, expressed in percent. Raw accuracy uses summed option log probabilities without length adjustment; both scores are retained. A gain is after minus that same group's own-model baseline. P−R, P−C and R−C are differences of those gains, not differences of final accuracies. pp means percentage points. Margin is log p(correct) minus mean log p(distractors), using raw sums in nats; its before/after change cancels a fixed preference for option length. Margin gain zero is the baseline reference, not a claim that the baseline margin itself is zero.

All displayed contrast intervals come directly from the unchanged synth_report.py: 5,000 whole-trial cluster bootstrap replicates, seed 20261003, independently resampling trials within each group and keeping the before/after item pairing. Each cell states whether the unrounded 95% interval includes zero. These pointwise intervals describe exam-trial uncertainty, not variation across training runs; they are not adjusted for multiple comparisons. The same analysis seed is reset for each point. No new score or interval method was introduced.

PPL means token-weighted perplexity over the complete frozen general-text set (lower is better). Each protocol is compared only with its own matching baseline. EOS and no-EOS have slightly different token counts (119,844 / 119,708) because of window-prefix handling; they are separate protocols. PPL percent change is 100 × (after / own baseline − 1).

## S1: qwen3-0.6b-base, seed 42

Run: `20261003T173737Z-lora-adhd05-s1-06b`. Sources: [fixed report](adhd05/20261003T173737Z-lora-adhd05-s1-06b.md) and its exact-precision JSON; [signed execution evidence](../experiments/adhd-05/S1_EXECUTION.json).

### Frozen normalized accuracy and gain contrasts

| Step | P (%) | R (%) | C (%) | P−R gain pp [95% CI]; zero included | P−C gain pp [95% CI]; zero included | R−C gain pp [95% CI]; zero included |
| --- | --- | --- | --- | --- | --- | --- |
| 0 (Base) | 24.81 | 25.41 | 23.78 | reference | reference | reference |
| 30 | 25.33 | 26.96 | 25.56 | -1.04 [-4.96, +2.96]; zero: yes | -1.26 [-5.59, +3.15]; zero: yes | -0.22 [-4.70, +4.11]; zero: yes |
| 60 | 27.11 | 25.26 | 25.67 | +2.44 [-1.70, +6.44]; zero: yes | +0.41 [-4.15, +4.81]; zero: yes | -2.04 [-6.44, +2.41]; zero: yes |
| 120 | 31.70 | 27.93 | 25.67 | +4.37 [+0.37, +8.22]; zero: no | +5.00 [+0.70, +9.33]; zero: no | +0.63 [-3.59, +4.78]; zero: yes |
| 240 | 46.22 | 40.96 | 25.11 | +5.85 [+1.56, +10.22]; zero: no | +20.07 [+15.15, +24.93]; zero: no | +14.22 [+9.07, +19.30]; zero: no |
| 600 | 43.70 | 39.78 | 23.89 | +4.52 [+0.44, +8.59]; zero: no | +18.78 [+14.48, +23.11]; zero: no | +14.26 [+9.78, +18.67]; zero: no |

### Group gains, raw accuracy and margin gains

| Step | P / R / C acc_norm gain (pp) | P / R / C raw accuracy (%) | P / R / C margin gain (nats) |
| --- | --- | --- | --- |
| 0 (Base) | 0 / 0 / 0 | 25.70 / 25.41 / 25.11 | 0 / 0 / 0 |
| 30 | +0.52 / +1.56 / +1.78 | 23.70 / 27.41 / 26.33 | -0.108 / +0.092 / +0.137 |
| 60 | +2.30 / -0.15 / +1.89 | 26.52 / 27.11 / 26.00 | -0.070 / +0.080 / +0.169 |
| 120 | +6.89 / +2.52 / +1.89 | 31.70 / 34.52 / 27.78 | +0.309 / +0.453 / +0.202 |
| 240 | +21.41 / +15.56 / +1.33 | 50.44 / 45.93 / 27.22 | +2.212 / +1.938 / +0.217 |
| 600 | +18.89 / +14.37 / +0.11 | 50.15 / 46.07 / 23.67 | +3.612 / +2.690 / +0.123 |

### Margin gain contrasts

| Step | P−R nats [95% CI]; zero included | P−C nats [95% CI]; zero included | R−C nats [95% CI]; zero included |
| --- | --- | --- | --- |
| 30 | -0.200 [-0.529, +0.131]; zero: yes | -0.245 [-0.610, +0.137]; zero: yes | -0.045 [-0.409, +0.315]; zero: yes |
| 60 | -0.150 [-0.466, +0.170]; zero: yes | -0.239 [-0.603, +0.141]; zero: yes | -0.089 [-0.451, +0.266]; zero: yes |
| 120 | -0.144 [-0.493, +0.203]; zero: yes | +0.107 [-0.287, +0.524]; zero: yes | +0.251 [-0.148, +0.632]; zero: yes |
| 240 | +0.274 [-0.146, +0.704]; zero: yes | +1.995 [+1.473, +2.532]; zero: no | +1.721 [+1.195, +2.236]; zero: no |
| 600 | +0.922 [+0.462, +1.400]; zero: no | +3.489 [+2.948, +4.056]; zero: no | +2.567 [+2.023, +3.104]; zero: no |

### Both general-text PPL protocols

| Step | EOS PPL | EOS change / baseline | No-EOS PPL | No-EOS change / baseline |
| --- | --- | --- | --- | --- |
| 0 (Base) | 13.642 | 0.00% | 13.432 | 0.00% |
| 30 | 128.554 | +842.37% | 125.713 | +835.93% |
| 60 | 243.964 | +1688.38% | 237.630 | +1669.14% |
| 120 | 392.087 | +2774.20% | 381.899 | +2743.22% |
| 240 | 779.224 | +5612.10% | 778.840 | +5698.43% |
| 600 | 1272.360 | +9227.04% | 1238.333 | +9119.33% |

## S2: qwen3-1.7b-base, seed 42

Run: `20261003T184746Z-lora-adhd05-s2-17b`. Sources: [fixed report](adhd05/20261003T184746Z-lora-adhd05-s2-17b.md) and its exact-precision JSON; [signed execution evidence](../experiments/adhd-05/S2_EXECUTION.json).

### Frozen normalized accuracy and gain contrasts

| Step | P (%) | R (%) | C (%) | P−R gain pp [95% CI]; zero included | P−C gain pp [95% CI]; zero included | R−C gain pp [95% CI]; zero included |
| --- | --- | --- | --- | --- | --- | --- |
| 0 (Base) | 25.85 | 24.07 | 22.89 | reference | reference | reference |
| 30 | 25.93 | 27.41 | 23.78 | -3.26 [-7.26, +0.74]; zero: yes | -0.81 [-5.26, +3.56]; zero: yes | +2.44 [-1.85, +6.85]; zero: yes |
| 60 | 25.56 | 26.44 | 24.78 | -2.67 [-6.74, +1.33]; zero: yes | -2.19 [-6.70, +2.26]; zero: yes | +0.48 [-3.93, +4.70]; zero: yes |
| 120 | 32.37 | 31.48 | 24.11 | -0.89 [-5.11, +3.19]; zero: yes | +5.30 [+0.52, +9.78]; zero: no | +6.19 [+1.63, +10.67]; zero: no |
| 240 | 48.07 | 40.96 | 24.89 | +5.33 [+0.89, +9.70]; zero: no | +20.22 [+15.52, +24.78]; zero: no | +14.89 [+9.93, +19.44]; zero: no |
| 600 | 51.33 | 43.26 | 24.00 | +6.30 [+1.93, +10.67]; zero: no | +24.37 [+19.59, +29.07]; zero: no | +18.07 [+13.26, +22.85]; zero: no |

### Group gains, raw accuracy and margin gains

| Step | P / R / C acc_norm gain (pp) | P / R / C raw accuracy (%) | P / R / C margin gain (nats) |
| --- | --- | --- | --- |
| 0 (Base) | 0 / 0 / 0 | 25.85 / 26.37 / 23.56 | 0 / 0 / 0 |
| 30 | +0.07 / +3.33 / +0.89 | 26.44 / 28.59 / 23.67 | -0.044 / +0.034 / +0.178 |
| 60 | -0.30 / +2.37 / +1.89 | 24.74 / 28.52 / 23.78 | -0.047 / +0.046 / +0.183 |
| 120 | +6.52 / +7.41 / +1.22 | 31.41 / 33.04 / 24.11 | +0.339 / +0.390 / +0.099 |
| 240 | +22.22 / +16.89 / +2.00 | 53.85 / 47.56 / 25.22 | +2.503 / +2.020 / +0.198 |
| 600 | +25.48 / +19.19 / +1.11 | 56.74 / 47.70 / 25.89 | +4.586 / +3.219 / +0.262 |

### Margin gain contrasts

| Step | P−R nats [95% CI]; zero included | P−C nats [95% CI]; zero included | R−C nats [95% CI]; zero included |
| --- | --- | --- | --- |
| 30 | -0.077 [-0.415, +0.264]; zero: yes | -0.222 [-0.580, +0.153]; zero: yes | -0.145 [-0.505, +0.214]; zero: yes |
| 60 | -0.094 [-0.420, +0.238]; zero: yes | -0.230 [-0.585, +0.129]; zero: yes | -0.137 [-0.491, +0.216]; zero: yes |
| 120 | -0.051 [-0.374, +0.282]; zero: yes | +0.240 [-0.112, +0.606]; zero: yes | +0.291 [-0.077, +0.655]; zero: yes |
| 240 | +0.482 [+0.113, +0.865]; zero: no | +2.305 [+1.886, +2.732]; zero: no | +1.822 [+1.395, +2.252]; zero: no |
| 600 | +1.367 [+0.898, +1.855]; zero: no | +4.324 [+3.815, +4.846]; zero: no | +2.957 [+2.413, +3.482]; zero: no |

### Both general-text PPL protocols

| Step | EOS PPL | EOS change / baseline | No-EOS PPL | No-EOS change / baseline |
| --- | --- | --- | --- | --- |
| 0 (Base) | 10.030 | 0.00% | 9.921 | 0.00% |
| 30 | 53.773 | +436.09% | 52.047 | +424.60% |
| 60 | 65.000 | +548.03% | 62.807 | +533.06% |
| 120 | 104.153 | +938.37% | 99.927 | +907.20% |
| 240 | 152.521 | +1420.58% | 146.885 | +1380.51% |
| 600 | 366.999 | +3558.84% | 352.134 | +3449.30% |

## S3: qwen3-0.6b-base, seed 43

Run: `20261003T211410Z-lora-adhd05-s3-06b-seed43`. Sources: [fixed report](adhd05/20261003T211410Z-lora-adhd05-s3-06b-seed43.md) and its exact-precision JSON; [signed execution evidence](../experiments/adhd-05/S3_EXECUTION.json).

### Frozen normalized accuracy and gain contrasts

| Step | P (%) | R (%) | C (%) | P−R gain pp [95% CI]; zero included | P−C gain pp [95% CI]; zero included | R−C gain pp [95% CI]; zero included |
| --- | --- | --- | --- | --- | --- | --- |
| 0 (Base) | 24.81 | 25.41 | 23.78 | reference | reference | reference |
| 30 | 25.41 | 25.63 | 24.67 | +0.37 [-3.63, +4.22]; zero: yes | -0.30 [-4.15, +3.44]; zero: yes | -0.67 [-4.63, +3.30]; zero: yes |
| 60 | 27.04 | 25.63 | 24.11 | +2.00 [-1.63, +5.78]; zero: yes | +1.89 [-2.19, +6.00]; zero: yes | -0.11 [-4.19, +4.00]; zero: yes |
| 120 | 30.89 | 31.11 | 23.11 | +0.37 [-3.63, +4.30]; zero: yes | +6.74 [+2.44, +10.89]; zero: no | +6.37 [+2.00, +10.67]; zero: no |
| 240 | 47.33 | 42.22 | 22.89 | +5.70 [+1.04, +10.15]; zero: no | +23.41 [+19.00, +27.74]; zero: no | +17.70 [+13.07, +22.19]; zero: no |
| 600 | 49.11 | 42.15 | 22.56 | +7.56 [+3.33, +11.85]; zero: no | +25.52 [+21.22, +29.85]; zero: no | +17.96 [+13.56, +22.33]; zero: no |

### Group gains, raw accuracy and margin gains

| Step | P / R / C acc_norm gain (pp) | P / R / C raw accuracy (%) | P / R / C margin gain (nats) |
| --- | --- | --- | --- |
| 0 (Base) | 0 / 0 / 0 | 25.70 / 25.41 / 25.11 | 0 / 0 / 0 |
| 30 | +0.59 / +0.22 / +0.89 | 25.33 / 27.48 / 27.00 | -0.086 / +0.060 / +0.094 |
| 60 | +2.22 / +0.22 / +0.33 | 26.07 / 27.26 / 24.00 | -0.088 / +0.082 / +0.151 |
| 120 | +6.07 / +5.70 / -0.67 | 32.52 / 34.00 / 25.00 | +0.257 / +0.383 / +0.132 |
| 240 | +22.52 / +16.81 / -0.89 | 52.37 / 47.41 / 24.44 | +2.275 / +1.990 / +0.105 |
| 600 | +24.30 / +16.74 / -1.22 | 54.52 / 46.89 / 23.00 | +3.651 / +2.930 / -0.192 |

### Margin gain contrasts

| Step | P−R nats [95% CI]; zero included | P−C nats [95% CI]; zero included | R−C nats [95% CI]; zero included |
| --- | --- | --- | --- |
| 30 | -0.146 [-0.437, +0.150]; zero: yes | -0.180 [-0.515, +0.167]; zero: yes | -0.034 [-0.368, +0.297]; zero: yes |
| 60 | -0.170 [-0.492, +0.157]; zero: yes | -0.239 [-0.612, +0.142]; zero: yes | -0.070 [-0.434, +0.291]; zero: yes |
| 120 | -0.126 [-0.432, +0.184]; zero: yes | +0.125 [-0.229, +0.495]; zero: yes | +0.251 [-0.107, +0.607]; zero: yes |
| 240 | +0.285 [-0.072, +0.631]; zero: yes | +2.169 [+1.763, +2.580]; zero: no | +1.885 [+1.475, +2.285]; zero: no |
| 600 | +0.721 [+0.231, +1.199]; zero: no | +3.843 [+3.304, +4.400]; zero: no | +3.122 [+2.561, +3.677]; zero: no |

### Both general-text PPL protocols

| Step | EOS PPL | EOS change / baseline | No-EOS PPL | No-EOS change / baseline |
| --- | --- | --- | --- | --- |
| 0 (Base) | 13.642 | 0.00% | 13.432 | 0.00% |
| 30 | 153.726 | +1026.89% | 151.171 | +1025.46% |
| 60 | 222.024 | +1527.55% | 216.334 | +1510.59% |
| 120 | 360.523 | +2542.82% | 356.412 | +2553.47% |
| 240 | 632.351 | +4535.45% | 625.762 | +4558.76% |
| 600 | 1279.222 | +9277.34% | 1244.193 | +9162.95% |

## Final recall by fact type

Frozen acc_norm, percent, 150 questions per P or R fact type. These descriptive subsets have no new bootstrap intervals or multiplicity adjustment; C breakdown was not provided by the fixed script.

| Fact type | S1 P / R | S2 P / R | S3 P / R |
| --- | --- | --- | --- |
| adverse_event | 38.00 / 39.33 | 40.00 / 42.67 | 45.33 / 39.33 |
| country | 21.33 / 29.33 | 50.00 / 40.67 | 30.67 / 33.33 |
| dosing | 38.00 / 40.67 | 26.00 / 29.33 | 46.00 / 40.67 |
| drug_class | 56.00 / 47.33 | 77.33 / 72.00 | 59.33 / 52.00 |
| duration | 79.33 / 67.33 | 75.33 / 56.00 | 86.00 / 71.33 |
| outcome | 28.00 / 24.67 | 40.67 / 33.33 | 42.67 / 32.67 |
| population | 30.67 / 27.33 | 29.33 / 26.67 | 36.00 / 27.33 |
| result | 28.67 / 32.00 | 43.33 / 34.00 | 40.67 / 38.00 |
| sample_size | 73.33 / 50.00 | 80.00 / 54.67 | 55.33 / 44.67 |

Duration and sample-size recall is often stronger than population, outcome or dosing recall. The benefit is heterogeneous: for example, S1 P is lower than R for country, result, adverse event and dosing; S2 P is lower for adverse event and dosing. Aggregate benefit does not establish that every fact type improved.

## Real-text validation and execution costs

Validation loss is mean real-ADHD token negative log likelihood and measures real-text drift. Snapshot steps 30/60/120/240 have no contemporaneous validation entry: the fixed reports contain null there. Values below are only the observed validation steps; none were interpolated.

| Update | S1 validation loss | S2 validation loss | S3 validation loss |
| --- | --- | --- | --- |
| 0 | 2.129548 | 1.952636 | 2.129548 |
| 50 | 4.912823 | 4.091768 | 4.894276 |
| 100 | 5.562644 | 4.675133 | 5.504675 |
| 150 | 5.870424 | 5.004713 | 5.998954 |
| 200 | 5.772011 | 5.062720 | 5.937082 |
| 250 | 5.951097 | 5.203624 | 6.183459 |
| 300 | 6.129138 | 5.528701 | 6.287038 |
| 350 | 6.218472 | 5.531898 | 6.448444 |
| 400 | 6.339725 | 5.719489 | 6.564086 |
| 450 | 6.458295 | 5.828821 | 6.763522 |
| 500 | 6.500114 | 5.890539 | 6.851652 |
| 550 | 6.549401 | 5.966926 | 6.864005 |
| 600 | 6.572954 | 6.044078 | 6.908440 |

Training throughput is the range of logged ten-update windows. Peak memory is the recorded MLX training allocation, not whole-system RAM. Swap and free disk are guard samples at ten-second intervals and can miss between-sample extrema. Guard launch required swap <3 GiB, stop threshold ≥4 GiB; disk reserve guard remained enabled. All guards finished with child exit 0 and null stop reason.

| Run | Training loop s | Exam scoring s | Total guarded attempt s | Logged tokens/s | Peak MLX GiB | Max sampled swap GiB | Min sampled free disk GiB | Trainable parameters | Final training loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | 3132.9 | 1030.8 | 4189.63 | 1689.7–1715.1 | 5.714 | 0.175 | 96.059 | 10,092,544 | 0.011797 |
| S2 | 6357.1 | 2350.0 | 8764.44 | 854.9–856.8 | 8.957 | 0.175 | 95.634 | 17,432,576 | 0.013841 |
| S3 | 3127.7 | 881.2 | 4034.87 | 1708.9–1717.8 | 5.710 | 0.175 | 95.490 | 10,092,544 | 0.014236 |

Total pipeline wall time: 17047.41 seconds (4.735 hours), including serial launches, verification and fixed reporting between runs. All conditions had one attempt; no watchdog, resource stop, resume, restart or AGX fallback occurred. The training-loop timer includes its scheduled validation but excludes the initial Base validation and exams. Exam scoring sums the measured seconds in summaries; it excludes model loading, comparisons and report bootstrap. S3 scoring excludes the reused Base exams. Separate wall timers for every load/validation/exam/report phase were not captured, so no precise decomposition is claimed. The guarded total includes those overheads; pipeline total also includes verification/report work outside the guards.

## Answers to the four planned questions

### 1. Did reading teach facts the Base models could not already know?

The final P−C and R−C gain contrasts are positive and their 95% intervals exclude zero in S1, S2 and S3 (see the main table); final margin contrasts also exclude zero. This supports acquisition of information about the described fictional trials beyond the contemporaneous control gain. Final P accuracies remain 43.70%, 51.33% and 49.11%, so recall is partial. C can learn common answer pools and format without learning trial-specific facts. Subtracting its own-baseline gain accounts for that measured control improvement; it does not prove that all format or group confounds are eliminated. Nominal chance is 25%, while observed Base group scores range from 22.89% to 25.85%. C has no sustained upward acc_norm pattern here; some early scores exceed 25%, and its final raw accuracy reaches 25.89% in S2. No unplanned formal test against chance was added.

### 2. Did four templates outperform four readings of one template?

At final, P−R gain is +4.52 pp [0.44, 8.59] in S1, +6.30 pp [1.93, 10.67] in S2 and +7.56 pp [3.33, 11.85] in S3; all intervals exclude zero. Final margin contrasts agree (+0.922, +1.367, +0.721 nats, all exclude zero). This is evidence for the prescribed equal-exposure template contrast in these trajectories, with the templating and seed limits below.

At steps 30 and 60, every accuracy and margin contrast includes zero. At 120, S1 accuracy P−R and P−C exclude zero but R−C includes it; S2/S3 accuracy P−C and R−C exclude zero but P−R includes it. All margin contrasts at 120 include zero. At 240, all accuracy contrasts exclude zero; P−C/R−C margin contrasts exclude zero in all runs, while P−R margin intervals still include zero in S1 and S3 (S2 excludes). The early score disagreement is retained rather than treated as confirmed template benefit at every dose.

### 3. How did recall vary with exposure, seeds and model size?

Recall contrasts strengthen by the 240-update sample (about eight passes), but are not uniformly monotonic. S1 P/R acc_norm falls from 46.22%/40.96% at 240 to 43.70%/39.78% at 600 despite improving margins. S3 R slips from 42.22% to 42.15%; S2 P/R continues to 51.33%/43.26%. No optimum beyond the sampled points is established, and the apparently better S1 accuracy at 240 is not an independently trained early-stop result.

S1 versus S3 is a two-seed spread, not a population estimate: final P differs by +5.41 pp and R by +2.37 pp for seed 43; P−C gain differs by +6.74 pp and P−R gain by +3.04 pp. S1 versus S2 is descriptive, with only one trajectory per size at seed 42: S2 final P/R is higher by +7.63/+3.48 pp; its own-baseline P/R gains are higher by +6.59/+4.81 pp. Its P−C gain is higher by +5.59 pp. The 0.6B seed spread in P−C is larger than that size difference. S2 uses 17.43 million trainable parameters versus 10.09 million, roughly half the logged tokens/s and twice the training time. Architecture, adapter capacity and compute differ, so these observations do not isolate a causal size advantage or support a faster-learning claim.

### 4. What was the general-text cost?

Severe forgetting under both fixed protocols. Final EOS PPL is 93.27×, 36.59× and 93.77× its own baseline in S1/S2/S3; no-EOS is 92.19×, 35.49× and 92.63×. Already at 30 updates, EOS PPL is 9.42×/5.36×/11.27×, while all recall gain-contrast intervals include zero. Real-ADHD validation loss rises from 2.130/1.953/2.130 to 6.573/6.044/6.908. Very low final synthetic training loss coexists with these adverse general/real-text results. EOS and no-EOS agree on the substantial cost; this does not isolate its mechanism. The fictional recall improvement does not demonstrate a useful general or clinical model.

## Interpretation limits

- Claude’s pre-training review measured heavy templating: about 65–71% of each text’s six-word sequences recur in at least 30 other trials. P consists of four recurring templates with facts filled in. These results measure recall of templated statements, not natural prose or medical understanding.
- Snapshot points on a trajectory share seed, corpus order and preceding updates; they are dependent, not independent replications. The snapshots are not annealed: all were sampled from the fixed 600-update cosine schedule, so earlier points have not completed a dose-specific schedule.
- Exams are reused across points. Many group, dose, margin and fact-type comparisons are reported; trial-cluster intervals are pointwise, unadjusted and not seed/run confidence intervals. No settings, extra experiments or stopping choices were selected from intermediate scores.
- S1/S3 give only two 0.6B seeds; S2 has one seed. Group assignment, shared answer pools, template construction and MCQ scoring constrain interpretation. C subtraction removes the measured common control gain, not every possible confound.
- Model architectures, trainable parameter counts, runtime and memory differ. Equal updates/windows and fact multiplicity do not imply equal compute or an isolated parameter-count intervention.
- General PPL uses 50 frozen samples under two separate window-prefix protocols. Validation uses real ADHD text and cannot measure fictional learning. Sampled swap is not a continuous resource maximum; MLX memory is not total machine memory.
- Partial recall, early null intervals, score disagreements, fact-type reversals and severe forgetting are retained. No unobserved optimum, clinical benefit, natural-prose generalization or new experiment is claimed.

## Verification, authorship and local evidence

Before final reporting, independently verified all 339 captured preparation/model/input/core hashes, exact seeds/configs, baseline model fingerprints, all 15 adapter hashes/configs, all complete unique item counts/IDs and frozen file hashes, all paired baseline links, all 34 unique full exam records (four baseline records plus 30 post-training records), signed per-run digests, report hashes and guard attempt histories. All three fixed report commands exited 0 without script edits. Native pipeline session 67349 exited 0. The pipeline, its owned guards/training children and task-bound caffeinate exited; no owned sleep-prevention assertion remains.

Private linkage: [RUNS](../experiments/adhd-05/RUNS.json), signed S1/S2/S3 execution records, captured private preflight and final verification evidence. Trial records, texts, questions, per-item answers/results, private manifests, model weights and development history remain local. This report contains aggregates only; no publication audit, public branch or push was requested.

Signed: Codex / GPT-6 (root), executor, final verifier and findings author, 2026-10-04 JST.

## Reviewer reading (Claude, Claude Opus 5.5, 2026-10-04)

Accepted. Checks and interpretation:

1. **The forgetting is real, not an artifact.**
   - `sink_probe.py` on S1 at step 30 and at the final step shows the position-0 sink intact (EOS norm 7,384 and 7,351; base 6,868).
   - EOS and no-EOS perplexity agree at every point.
   - WikiText per-token NLL on the probe text goes from 2.43 to 4.27 after one pass and to 6.10 at the end.
   - The model has shifted toward the narrow, templated fictional-trial language.
   - Real ADHD papers changed general perplexity by about 10% over hundreds of steps; this corpus changes it 5–11× in 30. A small, repetitive, out-of-distribution corpus pulls the model away much faster than natural text.
2. **Recall appears late and abruptly.** P−C is about 0 at 1–2 passes, about +5 to +7 at 4 passes and about +20 to +23 at 8 passes. At 8 passes each fact has been seen about 32 times. By then most of the forgetting has already happened.
3. **Rewording beats repetition, three runs out of three.** Final P−R is +4.5, +6.3 and +7.6 pp, and the margin metric agrees. This is the clean answer to the question ADHD-02 could not settle: the ADHD-02 rewrites were too few, not useless. In this templated setting the gain is moderate, not a multiple.
4. **By fact type:** numbers (duration, sample size) are recalled best, and the four-text advantage is largest for sample size in two of three runs. Country, population and result stay near chance in some runs. The pattern is descriptive only (about 150 questions per cell).
5. **Practical lesson:** fine-tuning on a narrow new-fact corpus without mixing in general text bought partial recall (about 44–51% on four options) at the price of a badly damaged general model. Replaying general text, lowering the learning rate, or using retrieval instead of training are the standard remedies. None was tested here.
