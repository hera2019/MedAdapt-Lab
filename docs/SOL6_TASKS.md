# Sol 6 任务书：ADHD-01 执行

总管：Claude（负责框架设计与代码审查）。执行：Sol 6。开始前请先读 [README](../README.md)、[实验方案](EXPERIMENTS.md) 和 [出题规范](QGEN.md)。

所有命令都在项目根目录下运行，并使用项目内的 `.venv/bin/python`。

## 执行规则

1. **不改核心语义。** 以下三个文件决定了"学到什么、怎么量"：
   - `scripts/lm.py`
   - `scripts/exam.py`
   - `scripts/train.py`
   
   如果发现 bug：先写进 `docs/ISSUES.md`（现象、复现方法、修法），再做最小修复，然后跑通 `scripts/selftest.py`。不要为了让结果好看去改打分方式。
2. **冻结文件只生成一次。** 包括：
   - `eval/benchmark_exclusions.json`
   - `eval/pmc_roles.json`
   - `eval/exams/*`
   
   需要重建时，停下来写进 `docs/ISSUES.md`，由总管决定。
3. **`new_heldout` 的论文永远不能进入训练数据**，出的题和困惑度文本也不能。
4. 下载只走 `hf_download.py` 和 `pmc_adhd.py`。每次下载前运行 `scripts/storage.py --need-gib N`。不下载本任务书以外的模型或数据。
5. 每完成一个阶段，把以下内容追加到 `results/SOL6_REPORT.md`：做了什么、耗时、数量、遇到的问题。数字必须来自实际输出，不能估算。

## 阶段 0：环境与自测

```sh
.venv/bin/python scripts/selftest.py        # 必须输出 all selftests passed
```

`.venv` 已由总管建好（mlx 0.32.3，mlx-lm 0.31.3），依赖锁定在 `experiments/adhd-01/requirements.lock.txt`。

## 阶段 1：下载评测集与模型（固定 commit）

先用 `--inspect` 核对当前 commit。如果和下表不同，用新的 commit，并在报告里注明。

| source_id | 2026-09-30 的 commit | 约大小 |
|---|---|---|
| medmcqa | `91c6572c454088bf71b679ad90aa8dffcd0d5868` | 数十 MB |
| pubmedqa-labeled | `9001f2853fb87cab8d220904e0de81ac6973b318` | 约 1 MB |
| wikitext-103-test | `b08601e04326c79dfdd32d625aee71d232d685c3` | 0.7 MB |
| qwen3-0.6b-base | `da87bfb608c14b7cf20ba1ce41287e8de496c0cd` | 1.15 GB |

```sh
.venv/bin/python scripts/hf_download.py medmcqa --inspect
.venv/bin/python scripts/hf_download.py medmcqa --revision <commit>
# 其余三个同样操作
```

**验收：** `manifest.json` 的 `downloads` 中有全部文件的 SHA-256；`models/qwen3-0.6b-base/model.safetensors` 存在。

## 阶段 2：封存评测集

```sh
.venv/bin/python scripts/seal_benchmarks.py \
  --medmcqa data/test/medmcqa/data/validation-*.parquet data/test/medmcqa/data/test-*.parquet \
  --pubmedqa data/test/pubmedqa/pqa_labeled/*.parquet
```

**验收：** `eval/benchmark_exclusions.json` 已生成，其中 `sealed` 为 true。

## 阶段 3：抓取 PMC 论文

```sh
.venv/bin/python scripts/pmc_adhd.py discover --set new --limit 1000
.venv/bin/python scripts/pmc_adhd.py fetch --set new --limit 1000 --max-total-mib 800
.venv/bin/python scripts/pmc_adhd.py assign-roles           # 冻结 2026 年论文的 A/B 划分，只运行一次
.venv/bin/python scripts/pmc_adhd.py discover --set pool --limit 5000
.venv/bin/python scripts/pmc_adhd.py fetch --set pool --limit 3000 --max-total-mib 1500
```

- `fetch` 是单线程的，每篇间隔 0.5 秒，3000 篇需要一两个小时。中断后重跑会自动跳过已处理的论文。
- 许可证无法识别的论文会被拒收，这是正常的。统计拒收数量和原因，写进报告。
- 抽查 5 篇论文的 `data/processed/pmc/*.json`，确认标题和日期合理。

**验收：** new 集至少 300 篇、pool 集至少 1500 篇；`eval/pmc_roles.json` 已冻结。

## 阶段 4：切块、训练集与非出题考卷

```sh
.venv/bin/python scripts/prepare_dapt.py
.venv/bin/python scripts/build_exams.py          # 先不加 --with-newfacts
.venv/bin/python scripts/build_exams.py --status
```

**验收（2026-09-30 核验修订）：** `experiments/adhd-01/split.json` 中 `train_new_pmcids` 非空；构建 5 套有题的基础考卷。MedMCQA validation 原关键词规则仅命中 2 题，逐题核查后均非 ADHD 题，严格题干筛选为 0，故不构建 `medmcqa_adhd`。把这项缺口写入报告；不可为了凑第六套而混入非 ADHD 题。原因和复现见 `docs/ISSUES.md`。

## 阶段 5：冒烟训练（不考试，只测速度和内存）

**2026-09-30 实测状态：** LoRA 命令已通过。默认全参数最初触及 15 GiB 空间红线；用户清理后改为微批 1×累积 8，空间检查通过。缓存 1 GiB、驻留 20 GiB 时一次完成 30 步，但固定 100 窗口验证损失上升；同配置重启、低学习率及小命令缓冲对照仍有 Metal 中断，阶段 5 全参数验收未通过。不要继续无差别重启或直接启动正式 R2。详见 `docs/ISSUES.md`、运行目录的 `execution_record.json` 和执行报告。以下命令保留为原计划记录。

```sh
.venv/bin/python scripts/train.py --skip-exam --iters 30 --name smoke
.venv/bin/python scripts/train.py --skip-exam --iters 30 --mode full --lr 2e-5 --name smoke-full
```

**验收：** loss 下降，没有报错。在报告中记录 tokens/s 和峰值内存。冒烟训练的产物可以留在 `adapters/` 里，但报告中要标注"冒烟"。

> **总管决定（2026-09-30，Claude）：** 全参数中断的主因是内存不足导致大量换页，与用户结束的进程无关，详见 `docs/ISSUES.md` 最后一条。R2 暂停，主线只做 LoRA。每次正式训练前先重启电脑、关闭占内存的应用，确认 `sysctl vm.swapusage` used 低于 1 GB；训练中每分钟记录交换空间，超过 4 GB 即停止运行。

## 阶段 6：出题（主要工作量）

按 [出题规范](QGEN.md) 执行，两组各至少 150 篇。全部完成后：

```sh
.venv/bin/python scripts/qgen_helper.py stats
.venv/bin/python scripts/build_exams.py --with-newfacts     # 只运行一次
```

**验收：** `newfacts_trained` 和 `newfacts_heldout` 各不少于 400 题；`eval/exams/qgen_rejections.json` 的被拒比例低于 10%。

## 阶段 7：正式实验

**执行边界：** 阶段 6 的 A/B 考卷尚未达冻结门槛，不能启动以下正式考试；R2 全参数另因阶段 5 的 Metal 稳定性和验证 loss 验收未通过而暂停。磁盘清理已核验；恢复前应解决训练失败、满足冒烟验收，并核对冻结考卷状态。

```sh
.venv/bin/python scripts/exam.py run --model models/qwen3-0.6b-base --label baseline     # R0
.venv/bin/python scripts/train.py --name r1-lora                                         # R1，默认配置
.venv/bin/python scripts/train.py --name r2-full --mode full --lr 2e-5                   # R2
.venv/bin/python scripts/train.py --name r4-lora-x2 --iters 1000                         # R4
```

- 每次训练结束，`train.py` 会打印对比报告的路径。
- R3（只用 new_train 训练）：`train.py --name r3-newonly --train data/train/adhd-01/train_new.jsonl`。这个文件由 `prepare_dapt.py` 一并生成，哈希记录在 `split.json` 中。
- 额度还有富余的话，下载 `qwen3-1.7b-base`（commit `ea980cb0a6c2ae4b936e82123acc929f1cec04c1`，约 3.3 GB），重复 R0 和 R1。

**验收：** `results/EXAM_LOG.md` 中有基线和每次训练后的记录；每次训练都有 `compare_vs_*.md`。

## 阶段 8：写结论

在 `results/FINDINGS.md` 中，对 [实验方案](EXPERIMENTS.md) 开头的 4 个问题逐一回答：

- 每个结论都要引用 run_id 和对比报告中的数字；
- 没有显著差异就写"没有显著差异"；
- 不做推测性解释，想法写在单独的"猜测"小节里。
