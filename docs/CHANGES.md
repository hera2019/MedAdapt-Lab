# 修改与署名记录

新记录追加在末尾。既有文件作者未逐一核实；本记录只归属实际执行的改动。

| 日期 | 执行者 | 修改内容 | 原因与验证 |
|---|---|---|---|
| 2026-09-30 | Codex（GPT-6） | `AGENTS.md`、`CLAUDE.md`、`docs/PROJECT_RULES.md`、`docs/CHANGES.md` | 按用户要求建立双入口共同规则及逐次署名机制；核对两入口均指向同一文件。 |
| 2026-09-30 | Codex（GPT-6） | `manifest.json`、`eval/benchmark_exclusions.json`、`results/SOL6_REPORT.md` | 执行阶段 0–2：自检通过；四组资源按固定 commit 下载，12 个文件完成 SHA-256 登记；封存 11,302 道题与 1,000 个 PMID，记录冻结文件哈希。 |
| 2026-09-30 | Codex（GPT-6） | `scripts/pmc_adhd.py`、`scripts/prepare_dapt.py`、`scripts/selftest.py`、`docs/ISSUES.md` | 修复摘要误收和检索年份与最早发表日期不一致的筛选漏洞；保留已下载原件并标记 97 篇排除；回归自检通过。 |
| 2026-09-30 | Codex（GPT-6） | `README.md`、`docs/EXPERIMENTS.md`、`docs/DATASETS.md`、`results/SOL6_REPORT.md` | 改正“2026 年发表必然未见”的过强断言，登记实际检索数、筛选数和阶段进度；核对冻结文件哈希。 |
| 2026-09-30 | Codex（GPT-6） | `eval/qgen/PMC*.json` | 按冻结队列处理 17 篇论文，12 篇共 48 道有原文证据的题、5 篇说明跳过原因；逐篇 `qgen_helper.py check` 通过，文件中的 `generator` 为实际出题者。 |
| 2026-09-30 | Codex（GPT-6） | `scripts/build_exams.py`、`docs/ISSUES.md`、`.gitignore` | 避免新知识考卷低于每组 150 篇、400 题时被过早冻结；将小型冻结元数据、考题和报告纳入 Git 可见范围，保留大体积数据与模型的忽略规则。 |
| 2026-09-30 | Codex（GPT-6） | `docs/EXPERIMENTS.md`、`docs/STORAGE.md`、`results/SOL6_REPORT.md` | 将日期筛选说明与实测检索、磁盘用量和出题进度同步；与实际 `df`、`du`、`qgen_helper.py stats` 核对。 |
| 2026-09-30 | Codex（GPT-6） | `docs/LICENSES.md` | 将许可说明与实际下载的 0.6B Base 模型对齐；检查项目内 `LICENSE` 与 manifest 登记，未把未下载的 1.7B 许可写成已核验。 |
| 2026-09-30 | Codex（GPT-6） | `scripts/build_exams.py`、`docs/ISSUES.md`、`docs/SOL6_TASKS.md`、`docs/DATASETS.md`、`docs/EXPERIMENTS.md`、`README.md` | 人工核查 MedMCQA validation 两道原误命中题，均非 ADHD；按题干显式主题筛选后为 0，修正专项考卷与阶段 4 验收口径，尚未冻结考卷。 |
| 2026-09-30 | Codex（GPT-6） | `eval/manual_exclusions.json`、`scripts/prepare_dapt.py`、`docs/ISSUES.md` | 最终跨组题名审计发现 3 对近似综述；将旧论文 3 篇列入可追溯人工排除清单，训练切分必须应用该清单并记录 SHA-256；原件与 manifest 保留。 |
| 2026-09-30 | Codex（GPT-6） | `experiments/adhd-01/split.json`、`eval/exams/*`、`docs/MODELS.md`、`docs/STORAGE.md`、`docs/EXPERIMENTS.md`、`docs/SOL6_TASKS.md`、`README.md`、`results/SOL6_REPORT.md` | 完成最终训练切分和五套基础考卷；LoRA 冒烟通过，全参数短跑因系统余量低于 15 GiB 中断，暂停正式全参数与后续扩大模型实验；记录实测、冻结哈希与未完成项。 |
| 2026-09-30 | Codex（GPT-6） | `eval/qgen/PMC*.json`、`results/SOL6_REPORT.md` | 按混排队列累计处理 29 篇，22 篇共 88 道题通过逐字证据检查，7 篇署名说明跳过；A/B 考卷尚未达到冻结门槛。 |

| 2026-09-30 | Codex（GPT-6） | `docs/ISSUES.md`、后续全参数冒烟运行记录 | 用户清理硬盘后恢复；预检可用约 92 GiB，以微批 1、累积 8 保留每步 8192 token，不改变模型、段长或评分方式。运行结果待记录。 |
| 2026-09-30 | Codex（GPT-6） | `eval/qgen/PMC*.json`、`docs/ISSUES.md` | 按混排队列新增 7 篇、28 道题，逐篇 4/4 通过；全参数恢复跑到第 10 步后 Metal 错误退出，记录真实错误和用户重启指示，准备同配置重试。 |
| 2026-09-30 | Codex（GPT-6） | `scripts/train.py`、`scripts/selftest.py`、`experiments/adhd-01/config.json`、`docs/ISSUES.md` | 两次恢复均报 Metal 交互错误后，增加默认关闭的进程内缓存/驻留控制，拒绝超过设备推荐驻留值；补全参数权重变动及保存加载检查。保持损失、评分、模型和有效批量语义。验证待自检和真实模型冒烟。 |
| 2026-09-30 | Codex（GPT-6） | `eval/qgen/PMC*.json`、`results/FULL_SMOKE_DIAGNOSTIC.json`、`docs/ISSUES.md` | 累计处理 50 篇、164 道题；逐篇检查通过。内存控制自检通过；真实全参数 30 步完成，但固定 100 窗口验证损失上升，记录并启动仅看验证集的低学习率对照，不解锁正式 R2。 |
| 2026-09-30 | Codex（GPT-6） | `README.md`、`docs/MODELS.md`、`docs/STORAGE.md`、`docs/EXPERIMENTS.md`、`docs/SOL6_TASKS.md`、`docs/ISSUES.md`、`results/SOL6_REPORT.md`、`.gitignore`、各恢复运行的 `execution_record.json`、`eval/qgen/PMC*.json` | 同步清理后实测与失败恢复点；代码自检此前已全部通过，一次完整全参数冒烟验证损失上升，多次 Metal 中断未解决，不将重启或中途 loss 下降写成通过。累计 56 篇、184 道有效题、10 篇说明跳过，最后新增题逐篇检查通过。最新空间预检通过；保留诊断 JSON 供 Git 审查，未重建冻结考卷。 |
| 2026-09-30 | Claude（总管，Claude Opus 5.5） | `docs/ISSUES.md`、`docs/SOL6_TASKS.md`、`docs/QGEN.md` | 审查 Sol 6 阶段 0–6 的执行记录与代码改动，自测通过。只读诊断全参数 Metal 中断：交换空间 13 GB，交换文件在运行期间集中创建，判断主因是内存不足导致换页，与用户手动结束的进程无关。决定 R2 暂停、主线改用 LoRA，并规定训练前清空交换空间、训练中监测；出题规范补充两条质量要求。未修改代码或冻结文件。 |
| 2026-09-30 | Codex（GPT-6） | `docs/REVIEW_RESPONSE.md`、`docs/LICENSE_REVIEW.md`、`docs/PUBLICATION.md`、`README.md`、`scripts/public_snapshot.py` | 阅读 Opus 5.5 新审议，接受暂停 R2 / LoRA 主线和出题质量要求，保留换页因果未确诊的限制。按用户授权通过现有 Claude Code 与实际 `claude-opus-5-5` 无工具讨论，双方推荐 Apache-2.0 但未添加 LICENSE；准备独立公开快照，保留本机数据与开发历史。发布验证另记执行报告。 |
| 2026-09-30 | Codex（GPT-6） | `scripts/public_snapshot.py`、`results/SOL6_REPORT.md` | 公开模板初审拦截了候选共享目录字段，补充去除本机引用；44 文件清单复查无常见凭据/个人路径匹配、语法检查通过，项目全部自检通过。原本机历史有个人路径，使用无该历史祖先的公开快照；原始 manifest 和冻结文件保持本地。 |
| 2026-09-30 | Codex（GPT-6） | `docs/PUBLICATION.md`、`results/SOL6_REPORT.md`、项目 Git 的 `public` 分支及 origin 映射 | 按用户明确授权创建 https://github.com/hera2019/MedAdapt-Lab public 仓库，上传经过独立历史审查的44文件快照；API 核验 public、main、无许可证和远端树一致。只推送 public:main，本机原开发历史/index/manifest 完整保留；补入已执行的发布记录。 |
