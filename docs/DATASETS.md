# Datasets and ADHD-01 selection

Updated 2026-09-30 by Codex / GPT-6, translating and updating the existing source review.

The main evidence is derived from eligible 2026 PMC papers: paired paper-specific A/B exams and held-out domain perplexity. Title matching supplements MeSH because indexing can lag. Candidate counts are not counts of usable full texts.

## Sources

| Source | Terms and scale | Decision |
|---|---|---|
| [PMC OA / OAI-PMH](https://pmc.ncbi.nlm.nih.gov/tools/oai/) | Article-specific terms; accept CC0, CC BY, or CC BY-SA only | DAPT and paper-specific evaluation; select by PMCID, not the whole archive |
| [MedMCQA](https://huggingface.co/datasets/openlifescienceai/medmcqa) | Repository label Apache-2.0; source card estimates 88.3 MB download / 135.5 MB expanded; 182,822 train, 4,183 validation, 6,150 test | Download validation/test only. Validation provides transfer exams; test answers are unavailable (`cop=-1`) and test prompts are sealed for exclusion |
| [PubMedQA](https://huggingface.co/datasets/qiaojin/PubMedQA) | Repository label MIT; whole repository roughly 301 MB across labeled/artificial/unlabeled subsets | Download 1,000 labeled cases only for evaluation; exclude corresponding PMIDs from DAPT. Repository terms do not automatically settle rights to quoted paper text |
| [AfriMed-QA v2 mirror](https://huggingface.co/datasets/afrimedqa/afrimedqa_v2) | Mirror labels CC BY 4.0, about 8.66 MB; [intronhealth version](https://huggingface.co/datasets/intronhealth/afrimedqa_v2) labels CC BY-SA 4.0 and has access conditions | Not downloaded. Recheck provenance, version, access conditions, specialties, and actual ADHD item counts before use |
| WikiText-103 test | CC BY-SA 3.0; roughly 0.7 MB selected file | General-language perplexity only |

Source-page sizes are estimates, not measured local bytes. Each downloaded file's actual size, version, license and SHA-256 are recorded in the local manifest.

## Observed local corpus

The new-paper search returned 701 candidates. After download and screening, 539 were eligible and split once into 269 `new_train` and 270 `new_heldout` papers. The old-paper search returned 6,210 candidates; the first 3,000 candidates produced 1,817 usable texts. Three near-duplicate old papers were additionally excluded from training. Details and hashes are in the execution report.

The original MedMCQA ADHD keyword rule found two validation questions, but both used ADHD or its medication as a distractor in non-ADHD questions. Strict ADHD topic matching in the question stem found zero. No misleading `medmcqa_adhd` exam is created. Psychiatry is not an ADHD label.

## PMC filtering

Use NCBI ESearch for MeSH **Attention Deficit Disorder with Hyperactivity** (D001289) or title terms `ADHD` / `attention deficit`, together with the commercial-compatible Creative Commons filter. The saved API response and `pmc_adhd.py` define the exact query. Incomplete indexing means this is not an exhaustive ADHD collection.

Retrieve JATS through OAI-PMH `GetRecord` with `metadataPrefix=pmc`. Validate `license/@xlink:href`; reject unrecognized, conflicting or ineligible terms. Require at least 1,000 body-paragraph characters. New papers must have an earliest JATS publication date on or after 2026-01-01. Retain subsequently excluded originals and manifest records with a documented exclusion reason.

The downloader is single-threaded, below three requests per second, and caps per-paper and total bytes. It extracts title, abstract and body paragraphs, excluding references, tables and supplementary materials. Inspect third-party content and exceptional attribution notices separately.

## Benchmark sealing and leakage controls

1. Acquire only the selected benchmark files, pin their full commits, hash them, and mark them `eval`. Keep them in `data/test`, outside training.
2. Seal source hashes, all PubMedQA PMIDs, normalized prompt hashes and complete prompts for exact substring checks in `eval/benchmark_exclusions.json`.
3. Split by paper identity. Exclude matching PMID/PMCID/DOI or benchmark text; separately audit near duplicates and record manual exclusions. PubMedQA supplies PMID, not PMCID/DOI, so its corresponding article exclusions use JATS PMID.
4. Preserve the same frozen exams before and after training. Tune on training validation loss. Prior benchmark contamination in the base model remains a limitation.

```sh
.venv/bin/python scripts/hf_download.py medmcqa --inspect
.venv/bin/python scripts/hf_download.py pubmedqa-labeled --inspect
# Download selected files with --revision <full-40-character-commit>.
.venv/bin/python scripts/seal_benchmarks.py \
  --medmcqa data/test/medmcqa/data/validation-*.parquet data/test/medmcqa/data/test-*.parquet \
  --pubmedqa data/test/pubmedqa/pqa_labeled/*.parquet
```

`prepare_dapt.py` fails closed when the exclusion table is missing. QA SFT is not currently part of this experiment. Public clones exclude the owner's texts, benchmark questions, evidence questions and frozen local identities.
