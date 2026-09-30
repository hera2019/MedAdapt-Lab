# Project license and resource boundaries

Updated 2026-09-30 by Codex / GPT-6. The owner approved the jointly recommended **Apache-2.0** project license.

## Original project material

Original source code, configuration and documentation are covered by [LICENSE](../LICENSE). [NOTICE](../NOTICE) records the external-resource boundary. The official license text was retrieved on 2026-09-30 from https://www.apache.org/licenses/LICENSE-2.0.txt; SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.

The project license does not transfer rights to third-party data, publications, benchmarks, base checkpoints or adapters. Those resources are not bundled in this public repository. See [the selection record](LICENSE_REVIEW.md).

## External resources

- [PMC OAI-PMH](https://pmc.ncbi.nlm.nih.gov/tools/oai/): terms vary by article. Accept only clearly identified CC0 / CC BY / CC BY-SA. Exclude NC, ND, absent, conflicting or unknown terms. Preserve title, authors, journal, year, PMCID/DOI, license URL and retrieval date. Assess ShareAlike, third-party materials and attribution separately before releasing text or adapters.
- [MedMCQA](https://huggingface.co/datasets/openlifescienceai/medmcqa): repository labels Apache-2.0; retain applicable license/NOTICE attribution and inspect third-party question provenance.
- [PubMedQA](https://github.com/pubmedqa/pubmedqa/blob/master/LICENSE): repository labels MIT; paper-abstract context may have separate rights. Evaluation only.
- [AfriMed-QA public mirror](https://huggingface.co/datasets/afrimedqa/afrimedqa_v2): CC BY 4.0 label. [Intronhealth version](https://huggingface.co/datasets/intronhealth/afrimedqa_v2): CC BY-SA 4.0 and access conditions. Do not conflate versions; not downloaded.
- WikiText-103 test: CC BY-SA 3.0; evaluation only, not distributed here.
- [Qwen3-0.6B-Base](https://huggingface.co/Qwen/Qwen3-0.6B-Base): pinned downloaded checkpoint includes Apache-2.0 LICENSE, locally hash-registered. [Qwen3-1.7B-Base](https://huggingface.co/Qwen/Qwen3-1.7B-Base) remains a candidate; verify its pinned license on acquisition. Any later MLX conversion requires both converter and upstream provenance/revisions.

Every download must record name/source/URL, exact revision, date, terms, original/local sizes, path, SHA-256 where applicable, DAPT/SFT/eval purpose, filtering, deletion/re-download instructions and licensing caveats. Unknown fields remain null with `planned` or `review_required` status; do not invent certainty.

These are project processing rules and source-review records, not a definitive legal assessment of future dataset or model releases.
