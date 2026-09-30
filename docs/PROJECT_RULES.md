# MedAdapt Lab 项目共同规则

本文件供 `AGENTS.md` 与 `CLAUDE.md` 共同引用。执行 ADHD-01 前先读 [Sol 6 任务书](SOL6_TASKS.md) 和 [出题规范](QGEN.md)；具体实验设计见 [EXPERIMENTS.md](EXPERIMENTS.md)。Claude 负责框架设计与代码审查，执行者对自己的改动和结果负责。

## 署名与交接

- **谁实际修改，谁署名。** 每次修改项目内容时，在 [CHANGES.md](CHANGES.md) 追加日期、Agent 名称及模型（可知时）、改动文件、原因、验证结果。不能代替其他 Agent 署名，也不能把未核实的文件作者写成自己。
- 生成考题的 `generator` 字段填实际出题者与模型；实验报告和结论标明实际执行者。若提交 Git commit，作者/提交者应如实标识操作者，不使用 Hera 身份代签。
- 区分引用的计划、实际执行、命令输出和推测；未运行的命令不能写成已验证。进度和问题追加到 `results/SOL6_REPORT.md`，数据只用实际输出。

## 执行边界

- 使用项目内 `.venv/bin/python`，不改全局 Python；`.venv` 已存在，无需重装。下载仅用 `scripts/hf_download.py` 与 `scripts/pmc_adhd.py`，先检查 `scripts/storage.py --need-gib N`，不下载任务书外的模型或数据。
- 修改代码后运行 `.venv/bin/python scripts/selftest.py`。`scripts/lm.py`、`scripts/exam.py`、`scripts/train.py` 决定训练与测量语义；要改先在 `docs/ISSUES.md` 写明现象、复现和拟修法，再作最小修复。
- `eval/benchmark_exclusions.json`、`eval/pmc_roles.json`、`eval/exams/*` 生成后冻结。需要重建时先在 `docs/ISSUES.md` 记录，交由 Claude 决定。`new_heldout` 的论文、考题和困惑度文本绝不进入训练。
- 按 [任务书](SOL6_TASKS.md) 的阶段顺序与验收标准推进。模型选择和数据用途若与既定实验目标冲突，应先如实记录并解决，不靠修改评分规则来制造更好结果。
