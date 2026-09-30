"""Create article-level DAPT splits only after benchmark exclusion and PMC roles are frozen.

Articles are cut into paragraph-aligned chunks (default <= 4000 characters, about 1000
Qwen tokens) so no tool silently truncates them; mlx-lm cuts anything over
max_seq_length (2048 by default) without training on the rest.
"""
import argparse
import json
import random
import re
import xml.etree.ElementTree as ET

from common import ROOT, atomic_json, load_manifest, sha256
from pmc_adhd import ROLES, article_ids, article_text, jats_article
from seal_benchmarks import norm


def chunk_text(text, max_chars):
    """Greedy paragraph packing; paragraphs longer than max_chars are split at sentence ends."""
    pieces = []
    for para in text.split("\n\n"):
        while len(para) > max_chars:
            cut = max((m.end() for m in re.finditer(r"[.!?]\s", para[:max_chars])), default=max_chars)
            pieces.append(para[:cut].strip())
            para = para[cut:].strip()
        if para:
            pieces.append(para)
    chunks, current = [], ""
    for piece in pieces:
        if current and len(current) + 2 + len(piece) > max_chars:
            chunks.append(current)
            current = piece
        else:
            current = f"{current}\n\n{piece}" if current else piece
    if current:
        chunks.append(current)
    return chunks


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chunk-chars", type=int, default=4000)
    p.add_argument("--valid-fraction", type=float, default=0.05)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    locked = ROOT / "eval/benchmark_exclusions.json"
    if not locked.exists():
        raise RuntimeError("benchmark exclusions missing; run seal_benchmarks.py first")
    exclusion = json.loads(locked.read_text(encoding="utf-8"))
    if not exclusion.get("sealed") or not exclusion.get("benchmark_files") or not exclusion.get("question_hashes"):
        raise RuntimeError("benchmark seal is incomplete")
    downloads = {x["path"]: x for x in load_manifest()["downloads"]}
    for item in exclusion["benchmark_files"]:
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"] or downloads.get(item["path"], {}).get("sha256") != item["sha256"]:
            raise RuntimeError("benchmark file changed after seal")
    roles = json.loads(ROLES.read_text(encoding="utf-8")) if ROLES.exists() else None
    new_train = set(roles["new_train"]) if roles else set()
    manual_path = ROOT / "eval/manual_exclusions.json"
    if not manual_path.exists():
        raise RuntimeError("manual near-duplicate audit missing: eval/manual_exclusions.json")
    manual = json.loads(manual_path.read_text(encoding="utf-8"))
    if manual.get("audit_version") != "title-near-duplicate-v1" or not isinstance(manual.get("exclusions"), list):
        raise RuntimeError("manual near-duplicate audit is malformed")
    manual_excluded = {x["pmcid"]: x["reason"] for x in manual["exclusions"]}
    if len(manual_excluded) != len(manual["exclusions"]) or any(not v for v in manual_excluded.values()):
        raise RuntimeError("manual near-duplicate audit has duplicate PMCID or empty reason")

    blocked_pmids = set(exclusion["pmids"])
    blocked_pmcids = set(exclusion["pmcids"])
    blocked_dois = set(x.lower() for x in exclusion["dois"])
    questions = set(exclusion["questions_normalized"])
    articles, excluded = [], []
    for path in sorted((ROOT / "data/raw/pmc").glob("PMC*.xml")):
        rel = str(path.relative_to(ROOT))
        if downloads.get(rel, {}).get("purpose") != "corpus" or downloads[rel]["sha256"] != sha256(path):
            raise RuntimeError(f"unregistered or changed article: {path.name}")
        pmcid = path.stem
        meta = json.loads((ROOT / "data/processed/pmc" / f"{pmcid}.json").read_text(encoding="utf-8"))
        if meta.get("screening_version") != "fulltext-v1":
            raise RuntimeError(f"unscreened article: {pmcid}; run pmc_adhd.py screen-existing first")
        if meta.get("excluded_reason"):
            excluded.append({"pmcid": pmcid, "reason": meta["excluded_reason"]})
            continue
        article = jats_article(ET.parse(path).getroot())
        ids = article_ids(article)
        text = article_text(article)
        compact = norm(text)
        reason = None
        if meta["set"] == "new" and roles is None:
            raise RuntimeError("new-set articles exist but eval/pmc_roles.json is not frozen; run assign-roles")
        if pmcid in manual_excluded:
            reason = "manual near-duplicate: " + manual_excluded[pmcid]
        elif meta["set"] == "new" and pmcid not in new_train:
            reason = "held-out or unassigned new article"
        elif ids.get("pmid") in blocked_pmids or pmcid in blocked_pmcids or ids.get("doi", "").lower() in blocked_dois:
            reason = "benchmark article ID"
        elif any(len(q) >= 40 and q in compact for q in questions):
            reason = "benchmark question text"
        elif len(text) < 1000:
            reason = "too little text"
        if reason:
            excluded.append({"pmcid": pmcid, "reason": reason})
        else:
            articles.append((pmcid, meta["set"], chunk_text(text, args.chunk_chars)))
    if len(articles) < 2:
        raise RuntimeError("need at least 2 eligible articles to make article-level train/validation splits")

    # Validation is drawn from pool articles only, so every new_train article is trained on
    # (exam group A asks about them).
    pool = [a for a in articles if a[1] == "pool"]
    random.Random(args.seed).shuffle(pool)
    valid_count = max(1, round(len(pool) * args.valid_fraction)) if len(pool) >= 2 else 0
    valid_ids = {a[0] for a in pool[:valid_count]}
    groups = {"valid": [a for a in articles if a[0] in valid_ids], "train": [a for a in articles if a[0] not in valid_ids]}
    groups["train_new"] = [a for a in groups["train"] if a[1] == "new"]  # for the new_train-only run (R3)
    outputs = {}
    for name, parent in (("train", "train"), ("train_new", "train"), ("valid", "validation")):
        path = ROOT / "data" / parent / "adhd-01" / f"{name}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps({"text": c}, ensure_ascii=False) + "\n" for _, _, chunks in groups[name] for c in chunks]
        path.write_text("".join(lines), encoding="utf-8")
        outputs[name] = {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "articles": len(groups[name]),
                         "chunks": len(lines), "characters": sum(len(c) for _, _, cs in groups[name] for c in cs)}
        print(f"{name}: {len(groups[name])} articles, {len(lines)} chunks -> {outputs[name]['path']}")
    split = {"seed": args.seed, "unit": "PMCID", "chunk_chars": args.chunk_chars,
             "benchmark_exclusions_sha256": sha256(locked),
             "manual_exclusions_sha256": sha256(manual_path),
             "pmc_roles_sha256": sha256(ROLES) if roles else None, "outputs": outputs,
             "train_pmcids": sorted(a[0] for a in groups["train"]),
             "train_new_pmcids": sorted(a[0] for a in groups["train"] if a[1] == "new"),
             "valid_pmcids": sorted(valid_ids), "excluded": excluded}
    atomic_json(ROOT / "experiments/adhd-01/split.json", split)
    print(f"excluded {len(excluded)} articles; manual near-duplicate review remains required")


if __name__ == "__main__":
    main()
