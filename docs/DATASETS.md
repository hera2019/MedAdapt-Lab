# 数据集与 ADHD-01 选择

> **2026-09-30 更新**：主证据改为 2026 年 PMC 论文（A/B 组自出题与困惑度），见 [实验方案](EXPERIMENTS.md)。检索式加入标题匹配以弥补 MeSH 标引滞后。本次实际检索返回 2026 年 701 个候选、旧论文池 6210 个候选；候选数不是可训练全文数。MedMCQA validation 原关键词规则命中的 2 题经人工核查均非 ADHD 专项题；严格筛选后为 0，不构建该专项考卷。MedMCQA test 分区不提供答案（cop=-1），只用于封存防泄漏。新增 WikiText-103 test 作为通用困惑度考卷（CC BY-SA 3.0，仅用于评测）。PubMedQA 只提供 PMID，所以 `benchmark_exclusions.json` 的 `pmcids`/`dois` 为空，排除依靠 JATS 中的 PMID 比对完成。

核查日期：2026-09-29。这里的大小是来源页标示值或预算估计，**不是本地下载实测**。下载原件后以 `manifest.json` 记录真实字节数和 SHA-256。

| 来源 | 许可、规模 | ADHD-01 用途与决定 |
|---|---|---|
| [PMC Open Access / OAI-PMH](https://pmc.ncbi.nlm.nih.gov/tools/oai/) | 单篇许可证不同；仅接纳 CC0 / CC BY / CC BY-SA。按 PMCID 抽样，不抓全库。 | 本次 2026 年 701 个候选中，539 篇通过许可证、正文和最早发表日期检查，已冻结 269/270 训练/留出划分；旧论文池正在抓取。主 DAPT 候选。 |
| [MedMCQA](https://huggingface.co/datasets/openlifescienceai/medmcqa) | Apache-2.0；来源卡约 88.3 MB 下载、135.5 MB 展开，含 182,822 train、4,183 validation、6,150 test；有 subject/topic 标签。 | **仅评测**。先取 validation/test；精神科标签并非 ADHD 标签，ADHD 子集需逐题核验，另保留全科对照。train 分区不进入 DAPT/SFT。 |
| [PubMedQA](https://huggingface.co/datasets/qiaojin/PubMedQA) | 仓库标 MIT；全仓约 301 MB，包含 labeled/artificial/unlabeled。MIT 仓库标签不自动清除所引论文文本的版权义务。 | 仅取 1k labeled 做评测；其 PMID 与上下文对应文章必须从 PMC DAPT 排除。不要取 artificial/unlabeled。 |
| [AfriMed-QA v2](https://huggingface.co/datasets/afrimedqa/afrimedqa_v2) | 该公开镜像标 CC BY 4.0、约 8.66 MB；另一个 [intronhealth 版本](https://huggingface.co/datasets/intronhealth/afrimedqa_v2) 标 CC BY-SA 4.0 且有访问条件，二者不可混同。 | 候选外部评测；当前不下载。对版本、授权来源、专科标签及 ADHD 题量做二次确认后再纳入。不可将精神科整体算作 ADHD。 |

## PMC 筛选

索引用 NCBI ESearch 查询 MeSH `Attention Deficit Disorder with Hyperactivity` 或标题中的 `ADHD` / `attention deficit`，再加 CC0 / CC BY / CC BY-SA 许可过滤；完整检索式以 `scripts/pmc_adhd.py` 和登记的原始索引响应为准。MeSH [D001289](https://www.ncbi.nlm.nih.gov/mesh?from_uid=1954874&linkname=gap_mesh) 是目标主题词。文章可能尚未完整编目，因此这不是所有 ADHD 文献。

全文仅通过 [PMC OAI-PMH API](https://pmc.ncbi.nlm.nih.gov/tools/oai/) `GetRecord` 的 `metadataPrefix=pmc` 取得。脚本从 JATS `license/@xlink:href` 核查许可，无法明确识别的文章拒收；还要求正文段落至少 1000 字符，`new` 集的 JATS 最早发表日期不早于 2026-01-01。已下载但后来排除的原件继续登记，元数据标明原因。脚本单线程、低于 3 请求/秒，并限制单篇和总下载量。仅提取题名、摘要、正文段落；去除参考文献、表格和补充材料。仍需人工抽查文本与第三方图片/引用的特殊声明。

## 评测封存与防泄漏

1. 先下载拟用的 benchmark **指定文件**，登记 commit、SHA-256、用途 `eval`，存于 `data/test` 或 `data/validation`，不得复制进 `data/train`。
   `python3 scripts/hf_download.py medmcqa --inspect` 与 `python3 scripts/hf_download.py pubmedqa-labeled --inspect` 可只查看当前 commit 和文件；随后用 `--revision <完整40位commit>` 下载固定文件。安装本项目环境见 `docs/MODELS.md`。
2. 生成 `eval/benchmark_exclusions.json`，内容至少有所有 PubMedQA PMID、所有评测题干的规范化 SHA-256、完整题干（用于精确子串扫描）。来源文件与排除表也记 SHA-256。
   例：`python3 scripts/seal_benchmarks.py --medmcqa data/test/medmcqa/data/validation-*.parquet data/test/medmcqa/data/test-*.parquet --pubmedqa data/test/pubmedqa/pqa_labeled/*.parquet`。真实文件名以 `--inspect` 为准。
3. 文章按 PMCID 分组决定训练或验证；相同 PMID、PMCID、DOI 或评测题干命中即排除。疑似复写、引用题干或不同版本不能只靠精确哈希，训练前还需近重复审核并记录报告。
4. 基线、训练后评测使用相同冻结集；迭代中不根据 test 调参。MedMCQA 题库在预训练模型中的先验污染无法证明不存在，报告须注明。

`prepare_dapt.py` 在排除表缺失时 fail closed。当前不提供 QA SFT 数据；待评测边界固定、许可核实后再单独设计。
