# 出题规范（A/B 组新知识考题）

出题人：Sol 6。题目用来检验模型有没有从 2026 年论文里学到**具体知识**，所以题目必须满足两点：**只有读过这篇论文才答得出**，**答案在原文里有逐字证据**。

## 流程

```sh
.venv/bin/python scripts/qgen_helper.py queue --limit 10   # 取下一批论文（两组混排，不显示分组）
.venv/bin/python scripts/qgen_helper.py show PMCxxxxxxx    # 读原文；证据句只能从这里复制
# 写 eval/qgen/PMCxxxxxxx.json
.venv/bin/python scripts/qgen_helper.py check PMCxxxxxxx   # 必须 0 REJECT；否则修改后重查
.venv/bin/python scripts/qgen_helper.py stats              # 看两组进度
```

- 按 `queue` 给出的顺序出题，不要跳着挑论文，不要去查某篇论文属于哪一组。**两组题必须用完全相同的标准写**，否则 B 组就失去了对照意义。
- 目标：两组各至少 150 篇论文、各约 600 道有效题。额度允许的话，把 2026 年的论文全部做完。
- 考卷用 `build_exams.py` 冻结以后，就不能再增删题目。所以全部题目出完、检查完，再构建 `newfacts_*` 两套考卷。

## 文件格式

```json
{
  "pmcid": "PMC1234567",
  "generator": "Sol 6 / <模型名>",
  "created": "2026-10-01T08:00:00Z",
  "skipped_reason": null,
  "items": [
    {
      "question": "In a 2026 Swedish register study of adolescents with ADHD, which outcome was associated with continuous stimulant treatment?",
      "options": ["Fewer emergency visits for injuries", "Higher rates of hospital admission", "No change in school completion", "Increased cardiovascular events"],
      "answer": 0,
      "evidence": "continuous stimulant treatment was associated with fewer emergency department visits for injuries",
      "kind": "finding"
    }
  ]
}
```

- `answer`：正确选项在 `options` 中的下标（0 到 3）。构建考卷时脚本会按固定种子打乱选项顺序，所以不必刻意把答案分散到不同位置。
- `evidence`：从 `show` 的输出中**原样复制**一句或半句话，至少 30 个字符。脚本会忽略大小写和标点，逐字核验。
- `kind`：取 `finding`（结论、方向、哪组更好）、`method`（设计、量表、干预方式）或 `population`（人群、国家、样本来源）之一。`number` 类数值题每篇最多 1 道。
- 如果论文不适合出题（研究方案、勘误、没有结果的评论等），写 `"items": []` 并填写 `skipped_reason`。

## 好题标准

1. **只针对这篇论文。** 反例："Which drug class is first-line for ADHD?"，这类题用常识就能答。正例：点明研究设计、人群和国家，但不泄露结论，再问结论。
2. **题目能脱离原文单独成立。** 不写"本研究""作者发现"这类没有上下文的指代，用 "In a 2026 [设计] of [人群] in [地点] ..." 来锁定是哪项研究。
3. **正确答案不能在题干里出现**（脚本会检查），也不能从选项的措辞里猜出来。
4. **干扰项要合理**：与正确答案同一类型，长度接近，相差不要超过 50%，而且彼此互斥。模型按每个字符的平均概率打分，长短悬殊会引入偏差。
5. 不用"以上都对/都不对"，不用否定句陷阱，不考作者名、期刊名、基金号。
6. 每篇写 3 到 5 题，分别覆盖论文的不同部分。题干不超过 60 个英文单词，选项尽量不超过 12 个单词。全部用英文，与论文语言保持一致。

## 自查清单

- 在不看论文的前提下，一个熟悉 ADHD 的医生能答对吗？如果能，删掉这道题。
- 四个选项里有没有明显的"异类"？如果有，重写干扰项。
- `check` 的结果是否为 0 REJECT？
- 题干有没有写明年份、设计、人群或地点？"the investigators"、"the program" 这类没有上下文的指代，模型无从判断问的是哪项研究。（2026-09-30 抽查中发现，Claude 补充）
- 正确答案是不是"干预有效 / 结果积极"这类不读论文也能猜中的方向？如果是，改问具体方向（哪一组、哪个指标、哪一项没有改善），或者让几个干扰项也是"积极"的说法。抽查中正确选项是四个里最长的比例为 35%（随机应为 25%），写干扰项时注意长度接近。
