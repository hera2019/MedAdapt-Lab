# 项目代码许可证讨论（待决定）

日期：2026-09-30。Codex（GPT-6）与 Claude Opus 5.5 的文字讨论。用户要求暂不确定许可证；本文件是审议记录，不授予任何许可，仓库暂不添加 `LICENSE`。

## 讨论与建议

Codex 初步建议 **Apache-2.0**；通过已安装的 Claude Code 作一次无工具文字审议，响应中实际模型标识为 `claude-opus-5-5`。Opus 同意推荐 Apache-2.0，认为明确的贡献者专利许可、专利诉讼终止条件及保留声明规则适合此协作实验框架。没有要求 Opus 修改文件或自行发布。

| 方案 | 适合的偏好 | 取舍 |
|---|---|---|
| Apache-2.0（共同推荐，待用户决定） | 宽松使用，同时明确贡献者专利和保留声明规则 | 文本较长，需要遵守修改标记、许可副本和相关 NOTICE 规则 |
| MIT（备选） | 更短、便于阅读的宽松许可 | 没有单独的明示专利授权条款 |
| GPL / AGPL（以后可议） | 希望衍生代码或网络服务中的修改保持开放 | 用户尚未表达这一偏好，本次不默认采用 |

Codex 补充：许可证只能覆盖权利人实际有权授予的部分；选择 Apache-2.0 并不会自动证明 AI 生成内容的权属，也不会取得训练数据或模型的再发布权。将来接收外部贡献时需另行明确贡献与署名规则。

## 范围

- 原创代码、配置、下载登记模板及原创文档可考虑统一用 Apache-2.0，待用户决定。
- 数据集、论文全文、benchmark 题文、论文证据句、基础模型及训练适配器各自核查许可与出处，不能被代码许可一并覆盖。本次均不上传。
- 将来若公开语料或适配器，需要单独核查基础模型、逐篇论文及第三方材料的条款与署名要求。
- 当前公开只表明代码可见，项目尚未发放 MIT 或 Apache-2.0 等许可；GitHub 平台上的查看和 fork 权利另依平台条款。

后续选择时最关键的偏好：是否要求他人的衍生代码（包括网络服务中的修改）也公开。用户要求讨论后再决定，本次不催促确认、不阻塞已授权的 public 仓库创建。

依据：[Apache 官方许可](https://www.apache.org/licenses/LICENSE-2.0)、[OSI 的 MIT 文本](https://opensource.org/license/mit)、[GitHub 许可证说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)。
