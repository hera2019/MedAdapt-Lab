# 许可与出处边界

核查日期：2026-09-29。此文是数据处理规则，不是法律意见。

- [PMC OAI-PMH](https://pmc.ncbi.nlm.nih.gov/tools/oai/) 说明每篇许可不同，只有指定服务可用于自动全文获取。文章“免费阅读”不等于可用于训练。只接纳逐篇可识别的 CC0 / CC BY / CC BY-SA；CC BY-SA 的改编与发布义务另行核查。CC BY-NC、ND、缺失或不明许可先排除。保留题名、作者、期刊、年份、PMCID、DOI、许可 URL 与获取日期；发布语料或适配器前再复核附带材料与署名义务。
- [MedMCQA 仓库](https://huggingface.co/datasets/openlifescienceai/medmcqa) 标 Apache-2.0，遵循其署名和 NOTICE 条件；原始题目若有第三方来源，应检查仓库说明。
- [PubMedQA 仓库](https://github.com/pubmedqa/pubmedqa/blob/master/LICENSE) 标 MIT；题目包含论文摘要上下文，单独核查引用内容的权利。仅评测，暂不训练。
- [AfriMed-QA 公共镜像](https://huggingface.co/datasets/afrimedqa/afrimedqa_v2) 标 CC BY 4.0；[另一个版本](https://huggingface.co/datasets/intronhealth/afrimedqa_v2) 标 CC BY-SA 4.0 且有访问条件。先核查同源版本和使用条件，勿混用。
- 当前已下载的 [Qwen3-0.6B-Base](https://huggingface.co/Qwen/Qwen3-0.6B-Base) 在固定版本中附带 Apache-2.0 `LICENSE`，本地路径 `models/qwen3-0.6b-base/LICENSE`，其 SHA-256 已登记在 `manifest.json`。候选 [Qwen3-1.7B-Base](https://huggingface.co/Qwen/Qwen3-1.7B-Base) 尚未下载；下载前复核对应固定版本的许可文件。暂缓的 [Qwen3-14B-Base](https://huggingface.co/Qwen/Qwen3-14B-Base) 如以后使用转换版，需同时记录转换包和上游来源许可、commit。

每次下载都在 `manifest.json` 记录来源、URL、版本或 commit、下载日期、许可证、原始及本地大小、路径、SHA-256、用途、筛选规则、删除和重下方式以及注意事项。缺一项不进入可复现训练。机器无法确定的字段填 `null` 并保持 `planned` / `review_required`，不要猜测。
