# Public GitHub publication

Updated 2026-09-30 by Codex / GPT-6. Repository: [hera2019/MedAdapt-Lab](https://github.com/hera2019/MedAdapt-Lab), public. Project license: Apache-2.0. All future public content is English.

## Published scope

`public_snapshot.py` uses an explicit allowlist: original source, project documents, experiment config, dependency lock, aggregate execution report, LICENSE/NOTICE and a sanitized source-registration template. Empty directories have `.gitkeep` files.

Exclude data, weights, adapters, caches, environments, benchmark/evidence questions, frozen local lists, detailed run records, credentials and personal absolute paths. Public `manifest.json` has empty `downloads` and `external_references`; the owner's complete local manifest remains intact. This repository supplies the framework and source plan rather than the owner's complete frozen experiment data.

## History and update procedure

Local development `main` and its working tree retain their original history. Public branch `public` starts from an audited snapshot with no development-history parent. Push only `public:main`; never mirror all local refs or push the private development branch.

```sh
.venv/bin/python scripts/public_snapshot.py check
.venv/bin/python scripts/public_snapshot.py prepare \
  --author-name 'Actual operator and model' \
  --author-email 'Actual public author email'
git push --no-follow-tags origin public:main
```

Preparation uses a separate temporary Git index, preserves the development index/worktree, audits allowed files, size, common credential patterns and personal paths, and scans all reachable public history. It does not use the network or push. New snapshot content must be English; earlier published historical Chinese texts remain historical, while sensitive-content checks still apply to every revision.

Audit records stay in `.cache/publication/audit.json`. Pattern checks report file/line rather than secret values. This is not a universal secret detector; review each new public file manually too. Verify GitHub visibility, final commit and complete blob tree after pushing.

For a fresh public clone, first establish the local publication branch from reviewed remote history if absent (`git branch public origin/main`). Local remote push mappings do not propagate through cloning; explicitly use `public:main`.

## Publication record

On 2026-09-30 Codex created the repository. Initial snapshot `8d43224a212fe4b70b86d1e92de9752966622f8e` had no parent, 44 files and no data/weights. Follow-up `43d0492c243336898447ca0d5a75fcd26fa89d18` added publication records; GitHub API confirmed public/main, matching file hashes and a clean two-commit history. Both predated the owner's Apache-2.0 approval and English-only request.

The latest revision adds the approved license and English public texts. Original Chinese documents are archived only in the local ignored publication cache. Existing downloaded data, frozen exams and numerical experiment records are preserved.
