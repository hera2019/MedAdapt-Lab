"""Freeze benchmark identities and exact questions before any DAPT export."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from common import ROOT, atomic_json, load_manifest, sha256

def norm(value):
    return " ".join(re.findall(r"\w+", str(value).casefold()))

def rows(path):
    if path.suffix == ".parquet":
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise SystemExit("pyarrow is required; see docs/MODELS.md") from exc
        yield from pq.read_table(path).to_pylist()
    elif path.suffix == ".jsonl":
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                yield json.loads(line)
    else:
        raise ValueError("expected parquet or jsonl")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--medmcqa", type=Path, nargs="+", required=True)
    p.add_argument("--pubmedqa", type=Path, nargs="+", required=True)
    args = p.parse_args()
    manifest = load_manifest()
    registered = {x["path"]: x for x in manifest["downloads"] if x["purpose"] == "eval"}
    output = {"sealed": True, "benchmark_files": [], "pmids": [], "pmcids": [], "dois": [],
              "question_hashes": [], "questions_normalized": []}
    questions, pmids = set(), set()
    for kind, paths in (("medmcqa", args.medmcqa), ("pubmedqa", args.pubmedqa)):
        for path in paths:
            path = path.resolve()
            if not path.is_relative_to(ROOT / "data/test"):
                raise RuntimeError("benchmark files must be in data/test")
            rel = str(path.relative_to(ROOT))
            if rel not in registered or sha256(path) != registered[rel]["sha256"]:
                raise RuntimeError(f"unregistered or changed benchmark file: {rel}")
            output["benchmark_files"].append({"path": rel, "sha256": sha256(path), "kind": kind})
            count = 0
            for row in rows(path):
                q = norm(row.get("question", ""))
                if not q:
                    continue
                questions.add(q)
                if kind == "pubmedqa":
                    pubid = row.get("pubid")
                    if pubid is not None:
                        pmids.add(str(pubid))
                count += 1
            if not count:
                raise RuntimeError(f"empty benchmark: {rel}")
    if not questions or not pmids:
        raise RuntimeError("need benchmark questions and PubMedQA PMIDs")
    output["pmids"] = sorted(pmids)
    output["questions_normalized"] = sorted(questions)
    output["question_hashes"] = sorted(hashlib.sha256(q.encode()).hexdigest() for q in questions)
    atomic_json(ROOT / "eval/benchmark_exclusions.json", output)
    print(f"sealed {len(output['benchmark_files'])} files, {len(questions)} questions, {len(pmids)} PubMedQA PMIDs")

if __name__ == "__main__":
    main()
