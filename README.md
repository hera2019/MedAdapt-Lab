# MedAdapt Lab

医学领域继续预训练（DAPT）实验室。目标是**弄懂一次领域训练到底改变了模型什么**，而不是只拿到一个分数。

第一个实验是 **ADHD-01**：用明确许可的 ADHD 论文全文训练 Qwen3 Base 小模型。每次训练前后都用同一套冻结考卷考一次，逐题记录，自动生成对比报告。

## 公开版本

此仓库发布源码、实验方案、配置和空白下载登记模板。数据、考题与逐字证据、冻结清单、模型权重、适配器及本机运行明细不随仓库分发；文档中的实测数字来自本机执行记录。首次克隆后按任务书获取资源并建立自己的切分和考卷，不能将本仓库当作现成训练数据或已训练模型。

**代码许可证待决定**；尚未添加 `LICENSE`，未授予 MIT / Apache-2.0 等许可。讨论见 [许可证审议](docs/LICENSE_REVIEW.md)，上传边界与后续更新见 [公开发布说明](docs/PUBLICATION.md)。

## 核心设计

1. **用较新的论文检验是否学到具体内容。** Qwen3 于 2025-04 发布，2026 年发表的论文可降低与其原始训练资料重合的风险；发表年份本身不能证明模型从未见过预印本或相同内容。把 2026 年的 ADHD 论文按 PMCID 随机、一次性地分成两半：
   - `new_train`：进入训练；
   - `new_heldout`：永不训练，只用于考试。
2. **A/B 两组考题**，都由 Sol 6 读 2026 年论文出题，每题必须附原文证据句，脚本会逐字核验：
   - A 组 `newfacts_trained`：出自训练过的论文。提升说明记住了新知识。
   - B 组 `newfacts_heldout`：出自没训练过的论文。这是对照组，提升只能说明更熟悉题型或领域。
   - 只有 A 组涨、B 组不涨，才算学到了具体知识。
3. **困惑度是最灵敏的尺子。**
   - `adhd_new_ppl`：未见过的 2026 年论文，应下降；
   - `general_ppl`：WikiText 通用文本，用来监测遗忘，不应明显上升。
4. **现成题库只作迁移观察**：MedMCQA 的精神科、全科两档，以及 PubMedQA。MedMCQA validation 没有合格的 ADHD 专项题；这些题库早已公开，可能在预训练数据里出现过，不能作为主证据。
5. **训练循环、LoRA、打分都是手写的**，见 `scripts/lm.py` 和 `scripts/train.py`。mlx-lm 只负责加载 Qwen3 的结构、权重和分词器。自测 `scripts/selftest.py` 用随机初始化的小模型验证整条链路，不需要下载任何东西。

## 硬件与模型

Apple M2 Max，32 GB 统一内存。项目硬上限 25 GiB，并始终保留 15 GiB 系统余量；运行前用 `scripts/storage.py` 读取当时实际可用空间。

| 阶段 | 模型 | 方式 | 状态 |
|---|---|---|---|
| 1 | Qwen3-0.6B-Base（约 1.1 GB，bf16） | LoRA；全参数对照待审议 | 已下载；LoRA 冒烟通过。清理后全参数一次完成但验证损失上升，其他试跑仍有 Metal 中断 |
| 2 | Qwen3-1.7B-Base（约 3.3 GB） | LoRA | 暂缓下载，待当前资源和实验方案审议 |
| 暂缓 | 8B / 14B | QLoRA | 小模型得出可解释结论后再议 |

VoxStage 里已有的 14B 和 30B GGUF 是后训练模型，不用于训练；需要时可只读作为推理对照，见 [模型方案](docs/MODELS.md)。

## 目录

| 路径 | 内容 |
|---|---|
| `scripts/` | 全部代码；`selftest.py` 可离线自测 |
| `data/raw/pmc` | PMC 原件（JATS XML） |
| `data/processed/pmc` | 每篇论文的元数据，含所属数据集 `pool` 或 `new` |
| `data/train`、`data/validation` | 切块后的训练集、验证集 |
| `data/test` | 封存的评测原件 |
| `eval/pmc_roles.json` | 冻结的 `new_train` / `new_heldout` 划分，只生成一次 |
| `eval/qgen/` | Sol 6 出的题，每篇论文一个 JSON |
| `eval/exams/` | 冻结考卷与 `index.json`（含 SHA-256） |
| `models/` | 模型权重 |
| `adapters/<run_id>/` | 训练产物 |
| `experiments/adhd-01/` | 配置 `config.json`、切分记录 `split.json`、每次训练的 `runs/<run_id>/` |
| `results/EXAM_LOG.md` | **考试记录总表**，每次考试一行 |
| `results/exams/<run_id>/` | 单次考试的逐题结果，以及 `compare_vs_*.md` 对比报告 |

## 流程

完整步骤与验收标准见 [Sol 6 任务书](docs/SOL6_TASKS.md)，出题规范见 [出题规范](docs/QGEN.md)。简要流程：

```sh
.venv/bin/python scripts/selftest.py                  # 离线自测
# 下载评测集与模型（固定 commit）→ seal_benchmarks.py → 抓 PMC → assign-roles → 出题
.venv/bin/python scripts/prepare_dapt.py              # 切块，生成训练集
.venv/bin/python scripts/build_exams.py               # 冻结有题的基础考卷
# 等 A/B 两组各至少 150 篇、400 道有效题完成并冻结后，再启动正式考试与训练
.venv/bin/python scripts/train.py --name first        # 先考基线 → 训练 → 再考 → 生成对比报告
```

## 规则

- 下载只通过 `hf_download.py` / `pmc_adhd.py` 进行，并在 [manifest.json](manifest.json) 登记 commit、大小和 SHA-256。
- `eval/benchmark_exclusions.json`、`eval/pmc_roles.json`、`eval/exams/*` 生成后即冻结。如需重建，只能在没有任何考试和训练记录之前进行，并写明原因。
- 不根据考试结果反复调同一套考卷的参数；调参看验证集 loss。
- 研究用途，不构成医疗建议。QA 分数不代表临床可用性。

## 文档

[实验方案](docs/EXPERIMENTS.md) · [Sol 6 任务书](docs/SOL6_TASKS.md) · [出题规范](docs/QGEN.md) · [数据集](docs/DATASETS.md) · [模型与环境](docs/MODELS.md) · [许可证](docs/LICENSES.md) · [空间预算](docs/STORAGE.md)
