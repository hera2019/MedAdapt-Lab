# GitHub 公开发布范围

日期：2026-09-30。维护：Codex（GPT-6）。目标仓库：`hera2019/MedAdapt-Lab`，public；代码许可证待决定。

## 发布内容

使用 `scripts/public_snapshot.py` 的明确文件清单：原创源码、项目文档、实验配置、依赖锁定、原创汇总报告及去掉本地下载记录的资源登记模板。空目录用 `.gitkeep` 保留。

不上传 `data/` 中的数据、模型权重、适配器、缓存、虚拟环境、`eval/` 中的题文/证据/冻结清单、运行明细、认证文件或机器绝对路径。空白模板 `manifest.json` 的 `downloads` 与 `external_references` 均为空；本机原始 manifest 保持完整。本仓库提供执行框架和来源方案，公开克隆不含本次实验的冻结样本与考卷，不能把它当作本机结果的完整数据副本。

## Git 历史与后续更新

本机 `main` 和工作区保留原开发历史。公开分支 `public` 从检查过的快照开始，第一条提交没有本地历史父提交；只推送 `public:main` 到 GitHub。后续公开提交只继承已检查的 `public` 历史。不要将本机开发 `main` 或所有 refs/tags 推到公开远端。

```sh
.venv/bin/python scripts/public_snapshot.py check
.venv/bin/python scripts/public_snapshot.py prepare --author-name '实际执行者与模型' --author-email '实际执行者的公开署名邮箱'
git push origin public:main
```

`prepare` 不联网，不推送：它使用独立临时 Git index，保留当前工作区和开发 index，检查清单、体积、常见凭据模式、个人路径及提交中的所有文件，然后更新本机 `public` 分支。它不是通用秘密扫描器，不能发现所有敏感内容；每次新增公开文件仍需人工审查。公开分支已存在时会先扫描其全部可达历史。

检查记录位于 `.cache/publication/audit.json`，不上传。凭据扫描只报告文件和行号，不输出匹配值。实际 GitHub 是否 public、远端 commit 是否与审查后的快照一致，发布后另行核验。

## 首次发布核验

2026-09-30，Codex（GPT-6）创建并推送 [hera2019/MedAdapt-Lab](https://github.com/hera2019/MedAdapt-Lab)。GitHub API 确认 visibility=public、default_branch=main、license=null。首次公开提交 `8d43224a212fe4b70b86d1e92de9752966622f8e` 无父提交，远端仅有 main 分支、无 tags；44 个文件的路径和 Git blob 哈希均与审查快照一致。公开副本的模板读取、来源 ID、存储检查及下载/筛选帮助入口已核验；项目自检通过，但没有重新跑完整训练。后续提交只补入此发布记录，继续继承已经检查过的公开历史。

若从 GitHub 首次克隆后准备发布更新，先从已公开历史建立本地 public 分支（尚不存在时使用 `git branch public origin/main`），再执行上述检查与 prepare。首次发布所用的本机 remote push 映射不随克隆传播，更新仍明确使用 `git push origin public:main`。
