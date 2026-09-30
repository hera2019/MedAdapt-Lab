# Project license decision

**Decision: Apache-2.0, approved by the owner on 2026-09-30.** Original project code, configuration and documentation are covered by LICENSE; third-party resources retain their own terms.

## Discussion record

Codex / GPT-6 proposed Apache-2.0. At the owner's request, an existing Claude Code installation conducted one tool-free text discussion. The response identified the actual model as `claude-opus-5-5`. Opus agreed with the recommendation, citing explicit contributor patent licensing, patent-litigation termination conditions and preservation of notices. No file edits or publishing tools were delegated to Opus.

The initial public snapshot left the license undecided as requested. The owner subsequently accepted the recommendation, and Codex installed the official Apache-2.0 text and NOTICE. This decision record supersedes the earlier pending status.

| Option considered | Rationale | Trade-off |
|---|---|---|
| Apache-2.0 — selected | Permissive reuse with explicit patent and notice provisions | Longer text; redistribution and modification notices must follow its terms |
| MIT | Short permissive alternative | No separate explicit patent grant clause |
| GPL / AGPL | Possible preference for keeping derivatives or service modifications open | That preference was not requested; these were not selected |

A license only grants rights the contributor can actually grant. Selecting Apache-2.0 does not itself resolve authorship of AI-generated material or acquire rights to training data and model artifacts. External contributions still need clear attribution and rights review.

## Scope

- Original source, configuration, registration templates and documentation: Apache-2.0.
- Papers, benchmark text, evidence-bearing questions, base model weights and adapters: absent from this release; separate provenance/license assessment required before any later distribution.
- A project license cannot override article-level ShareAlike or third-party attribution requirements.
- The project is a research framework, not a clinical decision system.

Sources: [Apache license](https://www.apache.org/licenses/LICENSE-2.0), [MIT text](https://opensource.org/license/mit), [GitHub licensing documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
