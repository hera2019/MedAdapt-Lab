# 问题记录

## 2026-09-30：摘要被误作全文接纳

- 发现者：Codex（GPT-6）。阶段 3 抓取暂停后，已登记 383 篇 XML；逐篇解析发现 75 篇没有 JATS `<body>`，另 1 篇正文段落不足 1,000 字符。例：`PMC13445231` 只有摘要，却因题名加摘要约 3,000 字符通过 `len(article_text) >= 1000`。
- 复现：对 `data/raw/pmc/PMC13445231.xml` 解析 JATS，统计 `<body>` 段落字符为 0；对应 `data/processed/pmc/PMC13445231.json` 已标为 `new`。
- 影响：抽象摘要可能进入 A/B 角色、DAPT 与新知识出题，无法满足“读论文全文”的实验前提。当前尚未冻结角色或生成训练集、考卷。
- 修法：新增正文段落长度检查（至少 1,000 字符）；新抓取不接纳短正文。复核已登记 XML，保留原始文件与 manifest 追溯，但在元数据标记 `excluded_reason`；角色划分和训练切块跳过被排除论文。修改后运行 `scripts/selftest.py`，并复核实际计数。
- 修复验证：自检通过；已登记的 383 篇中，76 篇因正文过短被标记排除，原件与 manifest 仍保留。

## 2026-09-30：ESearch 的 2026 年命中早于 JATS 最早发表日

- 发现者：Codex（GPT-6）。701 个 `new` 候选处理完毕后，560 篇通过正文检查；其中 21 篇的 JATS 最早发表日期早于 2026-01-01。检索 API 的 `pdat` 命中不能直接证明文章首次公开在 2026 年。
- 影响：这些文章如果进入 `new_train` / `new_heldout`，会削弱“模型原本未见过”的时间边界。当前仍未冻结角色、考卷或训练集。
- 修法：在抓取和复核已下载 XML 时，要求 `new` 文章的最早 JATS 发表日期不早于 2026-01-01；保留原件与 manifest，标记元数据排除。再次运行自检和筛选后才冻结角色。

## 2026-09-30：新知识考卷允许过早冻结

- 发现者：Codex（GPT-6）。任务书要求 A/B 组各至少 400 道有效题，但 `build_exams.py --with-newfacts` 原默认门槛只有每组 100 题；若题量不足，旧代码还会先写出 `eval/exams/qgen_rejections.json` 再报错。冻结文件只能生成一次，因此失败运行也不应写入该目录。
- 复现：阅读 `build_exams.py` 的 `--min-newfacts` 默认值与 `build_newfacts` 中写入拒题文件、检查最小题量的先后顺序。当前尚未构建 `newfacts_*` 考卷。
- 修法：最低门槛设为每组 150 篇有有效题的论文、400 题，即使命令行给出更低题量也不放松；数量不足时不写 `qgen_rejections.json`。不改变现有题目的打分或验证逻辑。

## 2026-09-30：MedMCQA ADHD 子集是干扰选项误命中

- 发现者：Codex（GPT-6）。对 validation 分区按原 `build_exams.py` 的“题干 + 四个选项”关键词规则抽查全部 2 道命中题：一题答案是自闭症，ADHD 是干扰选项；另一题是抽动表现的用药选择，methylphenidate 是干扰选项。两题均非 ADHD 专项题。严格在题干寻找显式 ADHD / attention-deficit disorder / hyperkinetic disorder，4,183 行中合格题为 0。
- 复现：用 `pyarrow.parquet` 读取 `data/test/medmcqa/data/validation-00000-of-00001.parquet`，筛选原规则命中题并查看题干、选项和正确答案；再用严格题干正则计数。
- 影响：原规则会生成名为 `medmcqa_adhd` 的伪专项考卷，误导实验结论。考卷尚未冻结。
- 修法：只根据题干中的显式 ADHD 诊断词归类；空子集不建考卷。阶段 4 的基础考卷验收调整为 5 套，报告中记录 ADHD 子集为 0；若以后引入其他来源，需重新核查、另起考卷版本，不能填充假题。

## 2026-09-30：留出综述与旧论文池的近重复题名

- 发现者：Codex（GPT-6）。最终抓取的 1,817 篇旧论文与冻结的 270 篇 `new_heldout` 逐篇比对 PMID、DOI、规范化完全相同题名，跨组完全重复为 0；再去常见词，用题名 token Jaccard ≥0.65 且共有至少 5 个 token 筛出 3 对。其一是 `PMC12425290`（2025 年 ADHD 与磨牙症综述方案）与留出论文 `PMC13576150`（2026 年同主题综述），另两对是相近主题的干预综述。
- 影响：即使 PMID / DOI 不同，旧综述或其方案进入训练也可能泄露留出论文的研究问题、方法或部分引用；无法仅靠精确哈希排除。现阶段尚未生成训练切分。
- 修法：在 `eval/manual_exclusions.json` 登记这 3 篇旧论文、配对留出 PMCID、审核规则和实际执行者；`prepare_dapt.py` 必须读取该清单并从训练、验证均排除，在 `split.json` 记录清单 SHA-256。保留原始 XML、许可证和 manifest。题名近似审计不能发现所有语义重写，报告仍需保留残余风险。

## 2026-09-30：全参数冒烟训练触及系统余量红线

- 发现者与中止者：Codex（GPT-6）。`train.py --skip-exam --iters 30 --mode full --lr 2e-5 --name smoke-full` 在项目用量约 2.2 GiB 时启动；启动前空间检查通过，系统可用约 27 GiB。训练期间 `df -g` 先见约 22–24 GiB，随后降至约 13 GiB，低于必须保留的 15 GiB。项目目录大小未相应增长；目前不能断定空间变化的具体系统原因。
- 复现记录：运行目录 `experiments/adhd-01/runs/20260929T191958Z-full-smoke-full/` 仅有第 0 步验证损失 2.1138；尚无第 10 步记录时手动中断，进程退出码 130、栈显示 `KeyboardInterrupt` 于 `mx.eval(grads_sum, loss, ntoks)`。中断后系统可用空间回升至约 22 GiB，随后 `df` 再读约 28 GiB。此运行不算通过，也不能作为全参数微调结果。
- 处理：暂停所有正式全参数 R2 及同配置重试；不修改评分方式。若未来继续，先审议降低微批大小并增加梯度累积以保持有效批量，且在开跑前确认额外运行时空间足以全程保留 15 GiB；全过程监测 `df`，碰线即停。当前不将全参数方案写成已验证可行。

### 2026-09-30 清理后恢复全参数冒烟

- 执行者：Codex（GPT-6）。用户确认已清理硬盘并要求继续；恢复前 `df -g` 核验可用约 92 GiB。
- 拟采用 `--batch-size 1 --grad-accum 8`，保留 seq_len=1024、每步 8192 token、全参数 float32、lr=2e-5 与 30 步。仅降低微批以减小瞬时激活内存；梯度累积和验证批量改变，验证损失不能直接与旧批量的数值比较。原中断记录保留。
- 开跑前预留 15 GiB 增量并检查系统余量；运行期间监测空间，低于 15 GiB 即中止。完成后据实际记录更新阶段 5 和正式 R2 配置。

### 2026-09-30 恢复运行的 Metal 中断及用户要求重启

- 执行者：Codex（GPT-6）。`20260930T041136Z-full-smoke-full-resume` 到第 10 步：train_loss=2.1405284，1135.49 token/s，MLX 峰值 15.58593 GiB；随后 `mx.eval(grads_sum, loss, ntoks)` 报 `Impacting Interactivity (0000000e:kIOGPUCommandBufferCallbackErrorImpactingInteractivity)`，退出码 1，未保存最终权重。运行期间磁盘最小观测约 82 GiB，退出后约 92 GiB。
- 用户随后说明可能误杀 MLX 进程并要求重新启动；该解释尚未与 Metal 错误建立因果关系。核对进程后未发现本项目仍在运行的训练或 MLX server；本次启动的是 `train.py`，没有创建独立推理服务。按用户指示同配置重试一次，保留失败原件，不能把失败记录算通过。
- 上游参考：MLX issue https://github.com/ml-explore/mlx/issues/3267 报告同类交互 watchdog 错误；这不是本机原因已确诊的证据。若再次失败，优先检查进程内缓存与驻留内存策略（已安装 mlx-lm 的 trainer 会设置 recommended wired limit），不改全局系统参数，不缩短训练段长。

### 2026-09-30 同配置重启再次失败，补充进程内 MLX 内存控制

- 执行者：Codex（GPT-6）。重启 `20260930T041904Z-full-smoke-full-restart` 到第 20 步，train_loss=2.1046、末段 1215 token/s、峰值 15.59 GiB；之后同一 `Impacting Interactivity` 错误退出码 1。空间约 92 GiB。第 10 步后抽查系统交换空间已用 15963.69 MiB、系统空闲比例 17%，但不能据此确诊 watchdog 原因。
- 复现：`.venv/bin/python -u -B scripts/train.py --skip-exam --iters 30 --mode full --lr 2e-5 --batch-size 1 --grad-accum 8 --name smoke-full-restart`。
- 拟修：为训练增加可记录的 `cache_limit_gib`、`wired_limit_gib` 可选参数，默认负数保持原行为；本次全参数重试用缓存 1 GiB、驻留 20 GiB，并拒绝超过设备推荐工作集的驻留值。这与已安装 mlx-lm 0.31.3 trainer 的进程内驻留策略一致，不更改系统 sysctl、不安装依赖、不改损失或评分、不假称已经解决 Metal 问题。参考 MLX 官方 set_cache_limit/set_wired_limit 文档： https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_cache_limit.html 与 https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_wired_limit.html 。
- 修后运行既有 selftest，并补全参数小模型权重确实改变、保存加载一致的检查；随后以原 1024 段长和每步 8192 token 完成 30 步验证。

### 2026-09-30 全参数恢复完成但损失上升

- 执行者：Codex（GPT-6）。缓存 1 GiB、驻留 20 GiB 的 `20260930T042723Z-full-smoke-full-memory` 完成 30 步，训练循环 200.0 秒，MLX 峰值 15.67583 GiB，无 Metal 错误，磁盘最小观测约 90 GiB。一次完成不能证明 500 步长期稳定。
- 原微批改变使验证范围从 100 窗口变为 25 窗口，另以预先定义的原范围前 100 窗口（102400 token）作训练前后核验：2.1137549281 → 2.2403196049，仍然上升。结果见 `results/FULL_SMOKE_DIAGNOSTIC.json`；未考试、未修改考卷，不能把运行完成写成“loss 下降验收通过”。
- 下一项为仅看验证集的低学习率对照：全参数 float32、seq 1024、batch 1×8 保持；lr 从 2e-5 降为 5e-6，30 步采用 warmup 10（原 30 步全部为预热，无法观测预热后过程），每 10 步验证固定前 100 窗口。该调参不用 benchmark；原失败/上升记录保留。正式 R2 尚不解锁，最终采用配置需在任务书和报告中写清楚。

### 2026-09-30 内存控制不能保证 Metal 稳定

- 执行者：Codex（GPT-6）。低学习率对照 `20260930T043526Z-full-smoke-full-low-lr` 在第 0 步验证 2.1138 后、未记录第 10 步时同类 Metal 错误退出码 1。缓存/驻留策略只能算一次运行完成的条件，尚未修复或确诊 watchdog。
- 下一项针对 GPU 命令缓冲，而非改变训练数学：使用 MLX 官方环境参数 `MLX_MAX_OPS_PER_BUFFER=1`、`MLX_MAX_MB_PER_BUFFER=10`，保留低学习率、段长、全参数和批量设置。来源为 MLX 官方 `mlx/utils.h`： https://github.com/ml-explore/mlx/blob/main/mlx/utils.h 。上游 issue 3267 也提示这种限制并非保证有效；若仍失败，不继续无差别重启，不以一次成功宣称 500 步可稳定。不得操作显示器、关闭其他应用或改全局系统限制。

### 2026-09-30 小命令缓冲对照仍中断：保留恢复点

- 执行者：Codex（GPT-6）。`20260930T043844Z-full-smoke-full-buffer` 到第 10 步，固定 100 窗口验证损失 2.1137549281→2.1110010976，吞吐 1214.50 token/s，峰值 14.95535 GiB；之后仍报同一 Metal 交互错误，退出码 1，无最终权重。这是中途观测，不满足 30 步验收。
- 已将五次恢复/诊断运行的实际启动参数、进程内环境变量、退出码和日志哈希写入各运行目录 `execution_record.json`；这些是运行后的重建记录，不能冒充开跑时生成的配置。默认全参数与 LoRA 原始日志保留。
- 不再无差别重启；当前没有本项目训练进程或独立 MLX server。进程内内存设置和命令缓冲限制未能可靠解决问题，原因未确诊；不操作显示器或其他 App、不改全局系统设置。正式 R2 保持未启动。

## 2026-09-30：全参数 Metal 中断与"磁盘神秘减少"的共同原因——内存不足导致大量换页（总管诊断）

- 诊断者：Claude（总管，Claude Opus 5.5）。只做了只读检查，没有运行训练。
- 证据：
  - `sysctl vm.swapusage` 显示当前已用交换空间 13,275 MiB（共 14,336 MiB）。
  - `/System/Volumes/VM` 下的交换文件共占 14 GiB 磁盘，其中 swapfile12–18 在本地时间 2026-09-30 13:12 集中创建，正好是 `20260930T041136Z-full-smoke-full-resume` 运行期间（UTC 04:11）。
  - 交换文件和项目在同一个 APFS 容器上，所以首次全参数运行时 `df` 从约 27 GiB 降到 13 GiB、中断后又回升，最可能的解释是交换文件在增长和回收，而不是项目本身写了文件。
  - 执行报告里也记录过第 10 步后交换空间约 16 GB、空闲内存 17%。
- 机制（高度怀疑，尚未确证）：
  - 全参数 float32 每一步都要读写全部参数、梯度、梯度累积副本以及 Adam 的两份状态，约 10 GB 以上，MLX 峰值 15.6 GiB。
  - 32 GB 统一内存还要同时承载 Chrome、ChatGPT/Codex、Claude 等应用。内存一旦开始换页，GPU 命令就会卡住，macOS 看门狗随后以 `ImpactingInteractivity` 为由终止这个进程。
  - LoRA 每步只读 1.2 GB 的 bf16 权重，所以不容易触发。
  - 调小命令缓冲无效，也符合"瓶颈在换页而不在单个 kernel"。
  - 另外，把驻留上限设为 20 GiB 可能会进一步挤压其他进程，是否有帮助无法确定。
- 用户手动结束的"mlx-server"进程与这个错误无关：
  - 被杀的进程如果是训练本身，退出时会报信号（130 / 137 / 143），而不是 Metal 报错加退出码 1；
  - 那个进程消失后又失败了 4 次；
  - 结束一个占 8 GB 的进程只会释放内存。
  - VoxStage 和 AI-Lab 的代码里都没有名为 mlx-server 的程序，具体是哪个进程无法追溯。
- 另一个独立问题：全参数的梯度范数约 4，LoRA 约 0.37，全参数一直被裁剪上限 1.0 顶住。每步 8192 token 的小批量，加上 Adam 对全部 5.96 亿参数（含共享的词嵌入矩阵）的更新噪声，可能是 30 步内验证 loss 上升的原因。这需要单独实验，不影响主线。
- 决定：
  1. **R2 全参数暂停，不阻塞主线。** ADHD-01 的核心问题（A/B 组知识、领域困惑度、遗忘）用 LoRA 就能回答。阶段 7 先做 R0、R1、R3、R4。
  2. **每次正式训练前**：重启一次电脑以清空交换空间（13 GB 交换空间不会自己归零），关闭 Chrome 等占内存的应用，并确认 `sysctl vm.swapusage` 的 used 低于 1 GB。**训练期间**每分钟记录一次 `vm.swapusage` 和 `df`，写进运行目录；交换空间一旦超过 4 GB 就停止运行并如实记录。
  3. 等 LoRA 主线有了结果，再考虑全参数：先做 bf16 权重、冻结词嵌入、更大有效批量（累积 32）、lr 5e-6 的对照，并同时监测交换空间。
