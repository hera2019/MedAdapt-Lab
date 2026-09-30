# ADHD-01 实验方案

更新：2026-09-30。状态：数据切分与五套基础考卷已冻结；LoRA 30 步冒烟通过；清理后全参数一次完成但验证损失上升，其他试跑仍遇到 Metal 中断；尚无正式基线或对比考试数值。

## 要回答的问题

1. 只喂论文原文的 DAPT，能不能让模型记住论文里的**具体新知识**？（A 组对比 B 组）
2. 模型对**同领域、没见过的新文本**是否更"熟悉"？（`adhd_new_ppl`）
3. 代价是什么？通用能力忘了多少？（`general_ppl`）
4. LoRA 和全参数微调、不同 rank、学习率、数据量之间，以上三项如何取舍？

## 数据划分

| 集合 | 来源 | 用途 |
|---|---|---|
| pool | PMC 开放获取 ADHD 论文，检索日期截至 2025-12-31（2026-09-30 检索返回 6210 篇候选） | 训练；其中 5% 按 PMCID 划为验证集，只看 loss |
| new_train | 2026 年发表论文的一半（2026 年共约 693 篇） | 训练；A 组出题来源 |
| new_heldout | 2026 年发表论文的另一半 | 永不训练；B 组出题来源，以及 `adhd_new_ppl` |

检索式为 MeSH D001289 或标题含 ADHD / attention deficit，并且许可为 CC0、CC BY 或 CC BY-SA，见 `scripts/pmc_adhd.py`。PMC `pdat` 用于检索；`new` 集抓取时另核对 JATS 最早发表日期，早于 2026-01-01 的论文排除。同一篇论文两个集合都命中时，归入 new。

`eval/pmc_roles.json` 在 2026 年论文抓完后一次性生成，seed 42，之后不再修改。出题只能在它冻结之后进行。

**时间边界：** PMC 检索的 2026 年发表日期只降低预训练重合风险，不能证明模型未见过同研究的早期预印本、在线先发稿或重复文本。抓取后要核查 JATS 中最早发表日期，并在结论中保留这项限制。

## 考卷（ADHD-01-v1）

| 考试 | 类型 | 角色 | 预期 |
|---|---|---|---|
| `newfacts_trained` | 选择题（cloze） | knowledge | 应提升 |
| `newfacts_heldout` | 选择题（cloze） | control | 理想情况下不变 |
| `adhd_new_ppl` | 困惑度 | domain | 应下降 |
| `general_ppl` | 困惑度 | forgetting | 不应明显上升 |
| `medmcqa_psych` / `medmcqa_general` | 选择题 | transfer | 仅作迁移观察；validation 无合格 ADHD 专项题，故不建 `medmcqa_adhd` |
| `pubmedqa` | yes / no / maybe | transfer | 变化小 |

**打分方式。** 选择题采用 Base 模型常用的 cloze 打分：计算每个选项文本在题干之后的对数概率，除以字符数后取最大者（`acc_norm`）。同时记录正确选项的归一化概率 `p_correct`，这个连续指标比准确率更灵敏。困惑度用 1024 token 的不重叠窗口计算。

**对比方式。** 按题目 ID 配对，用 bootstrap 求 95% 置信区间；选择题另做 McNemar 精确检验。题量少于 10 的考试不判定显著性。

## 实验序列（建议）

| 编号 | 设置 | 目的 |
|---|---|---|
| R0 | 0.6B 基线考试 | 起点 |
| R1 | 0.6B LoRA r=16，lr 2e-4，500 步 | 跑通；看 A/B/domain/forgetting 的方向 |
| R2 | 0.6B 全参数，lr 2e-5，步数同 R1 | 暂停：清理后磁盘余量通过；Metal 稳定性和 loss 下降验收未通过，不能启动正式全参数对照 |
| R3 | 0.6B LoRA，只用 new_train 训练 | 数据量与知识注入的关系 |
| R4 | R1 的 2 倍和 4 倍步数 | 多看几遍能否把知识记住 |
| R5 | 1.7B 上重复 R1 | 模型规模的影响 |
| ADHD-02（后续） | 让 Sol 6 把 new_train 论文改写成多种说法再训练 | 检验"换说法、多角度"能否把原文变成可答题的知识（synthetic continued pretraining 思路） |

每次训练都会自动完成以下几步：没有基线就先考基线 → 训练 → 考试 → 生成 `compare_vs_baseline.md`。R2 以后如果要和上一次训练比较，运行 `exam.py compare <runA> <runB>`。

## 纪律

- 调参只看验证集 loss。考卷用于记录结果，不据它反复调同一个参数。
- 如果看了考试结果再改设置，报告里要写明是第几次迭代。
- 每次训练的配置、数据哈希、适配器哈希、峰值内存和训练曲线都在 `experiments/adhd-01/runs/<run_id>/`。
- 结论写进 `results/FINDINGS.md`：每条结论都要引用 run_id 和对比报告。
