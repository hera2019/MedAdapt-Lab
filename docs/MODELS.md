# 模型、训练链与环境

更新：2026-09-30（方案作者 Claude；本次实测补充 Codex / GPT-6）。

## 决定

| 阶段 | 模型 | 理由 |
|---|---|---|
| 1 | **Qwen3-0.6B-Base**，bf16，不量化 | LoRA 30 步冒烟已通过；清理后全参数一次完成但验证损失上升，多次试跑仍有 Metal 中断。稳定全参数对照未通过验收。 |
| 2 | **Qwen3-1.7B-Base**，bf16 | 阶段 1 的结论要在更大模型上验证。 |
| 暂缓 | 8B / 14B Base 的 MLX 量化版 | 量化 Base 权重的来源难以核实，单次训练也慢。等小模型给出可以解释的结论后再议。之前的核查记录保留在本文末尾。 |

2026-09-30 实测：0.6B LoRA（r=16、序列 1024、微批 4、梯度累积 2）30 步完成，MLX 峰值内存 18.21 GiB、验证损失 2.114→2.094。默认全参数 float32 冒烟仅完成第 0 步验证；训练计算期间 `df` 可用空间从启动前约 27 GiB 一度降到 13 GiB，违反 15 GiB 系统余量要求，已手动中断。空间变化的系统原因尚未证实。清理后空间已充足：微批 1×累积 8、缓存 1 GiB、驻留 20 GiB 的全参数 30 步一次完成，峰值 15.68 GiB；固定 100 窗口验证损失 2.11375→2.24032。低学习率与小命令缓冲对照仍遇到 Metal 中断，不能宣称已修复。全参数 R2 和 1.7B 扩展暂缓，详见 [问题记录](ISSUES.md) 与 [执行报告](../results/SOL6_REPORT.md)。

两者都是官方 Base 权重，Apache-2.0 许可，由 `hf_download.py` 按固定 commit 下载到 `models/`。2026-09-30 的 commit 与大小：

- `qwen3-0.6b-base`：`da87bfb608c14b7cf20ba1ce41287e8de496c0cd`，1.15 GB
- `qwen3-1.7b-base`：`ea980cb0a6c2ae4b936e82123acc929f1cec04c1`，3.29 GB

## 训练链

- mlx-lm 只用来加载 Qwen3 的结构、权重和分词器（`mlx_lm.load`）。
- LoRA 层、训练循环、学习率调度、梯度累积、梯度裁剪、验证、保存和加载全部手写，见 `scripts/lm.py` 和 `scripts/train.py`。这样可以对照读懂每一步做了什么。
- LoRA 的 B 矩阵初始化为零，所以第 0 步与原模型完全一致（自测会验证这一点）。默认包住全部层的 q/k/v/o 和 gate/up/down。
- 训练数据按 EOS 拼接后切成等长窗口（packing），不做 padding。切块在 `prepare_dapt.py` 中完成，每块不超过 4000 字符。**旧版把整篇论文写成一条记录，mlx-lm 会在 2048 token 处直接截断，大部分正文实际没有被训练到；这个问题已修复。**
- 默认配置见 `experiments/adhd-01/config.json`：LoRA r=16、alpha=32、lr 2e-4、seq 1024、batch 4×2。全参数微调建议 lr 2e-5。这些只是起点，并未调优。

## 环境

`.venv` 已安装 mlx 0.32.3、mlx-lm 0.31.3、pyarrow 和 numpy，完整依赖锁定在 `experiments/adhd-01/requirements.lock.txt`。`hf_download.py` 把 `HF_HOME` 设为项目内的 `.cache/huggingface`。重建环境：

```sh
python3 -m venv .venv && .venv/bin/python -m pip install -r experiments/adhd-01/requirements.lock.txt
```

## 已有模型（仅作对照，不用于训练）

VoxStage 中的 `Qwen3-14B-Q4_K_M.gguf` 和 `Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf` 已于 2026-09-30 做过只读哈希校验，详见 `manifest.json` 的 `external_references`。它们都是后训练模型的 GGUF，不是 Base 权重，也不是 MLX 格式。本项目的考试系统目前只加载 MLX 模型，暂不使用它们。

## 历史核查（暂缓项）

- `Qwen/Qwen3-14B-Base`：上游约 29.5 GB，超出预算。
- `mlx-community/Qwen3-14B-4bit` 与 `Qwen/Qwen3-14B-MLX-4bit`：都由后训练模型转换而来，不能当 Base 使用。
- `jesusoctavioas/Qwen3-8B-Base-mlx-4Bit`：社区转换版本，来源未经核实。
- mlx-lm 的一份问题报告（ml-explore/mlx-lm#1786）记录过 Qwen3-30B-A3B LoRA 在首次反向传播时失败。
