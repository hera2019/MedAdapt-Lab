"""Build the frozen exam papers in eval/exams/ from sealed sources.

  python scripts/build_exams.py            # build every exam whose sources exist
  python scripts/build_exams.py --with-newfacts   # also freeze the A/B question exams (only when qgen is finished)
  python scripts/build_exams.py --status   # show what is built / missing

An exam, once written, is never rebuilt silently: its SHA-256 is in index.json and every
exam run records it, so before/after comparisons only pair identical papers.

Exams (role -> what it tells us):
  newfacts_trained   knowledge   questions about new_train papers (the model reads them in DAPT)
  newfacts_heldout   control     same kind of questions about new_heldout papers (never trained)
  adhd_new_ppl       domain      perplexity on new_heldout full text
  general_ppl        forgetting  perplexity on WikiText-103 test articles
  medmcqa_adhd (only if explicit ADHD question exists) / medmcqa_psych / medmcqa_general / pubmedqa   transfer
"""
import argparse
import datetime as dt
import hashlib
import json
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from common import ROOT, atomic_json, load_manifest, sha256
from pmc_adhd import ROLES, article_text, jats_article
from seal_benchmarks import norm

EXAMS = ROOT / "eval/exams"
QGEN = ROOT / "eval/qgen"
EXAM_VERSION = "ADHD-01-v1"
MEDMCQA = ROOT / "data/test/medmcqa/data/validation-00000-of-00001.parquet"
PUBMEDQA = ROOT / "data/test/pubmedqa/pqa_labeled/train-00000-of-00001.parquet"
WIKITEXT = ROOT / "data/test/wikitext/wikitext-103-raw-v1/test-00000-of-00001.parquet"
ADHD_RE = re.compile(r"\b(?:adhd|attention[- ]deficit(?:/hyperactivity)? disorder|hyperkinetic disorder)\b", re.I)


def registered(path):
    """Source files must be registered downloads whose bytes still match the manifest."""
    rel = str(Path(path).relative_to(ROOT))
    entry = {x["path"]: x for x in load_manifest()["downloads"]}.get(rel)
    if entry is None or entry["sha256"] != sha256(path):
        raise RuntimeError(f"source not registered or changed: {rel}")
    return {"path": rel, "sha256": entry["sha256"]}


def parquet_rows(path):
    import pyarrow.parquet as pq
    return pq.read_table(path).to_pylist()


def mcq(item_id, question, options, answer, meta=None):
    return {"id": item_id, "prompt": f"Question: {question.strip()}\nAnswer:",
            "choices": [" " + " ".join(str(o).split()) for o in options], "answer": answer, "meta": meta or {}}


def pmc_text(pmcid, max_chars=None):
    article = jats_article(ET.parse(ROOT / "data/raw/pmc" / f"{pmcid}.xml").getroot())
    text = article_text(article)
    return text[:max_chars] if max_chars else text


# ---------------------------------------------------------------- builders

def build_medmcqa():
    rows = parquet_rows(MEDMCQA)
    out = {"medmcqa_adhd": [], "medmcqa_psych": [], "rest": []}
    for r in rows:
        if r.get("cop") not in (0, 1, 2, 3):
            continue
        options = [r["opa"], r["opb"], r["opc"], r["opd"]]
        item = mcq(f"medmcqa-{r['id']}", r["question"], options, r["cop"],
                   {"subject": r.get("subject_name"), "topic": r.get("topic_name")})
        if ADHD_RE.search(r["question"]):
            out["medmcqa_adhd"].append(item)
        elif r.get("subject_name") == "Psychiatry":
            out["medmcqa_psych"].append(item)
        else:
            out["rest"].append(item)
    rest = out.pop("rest")
    random.Random(42).shuffle(rest)
    out["medmcqa_general"] = sorted(rest[:500], key=lambda i: i["id"])
    src = [registered(MEDMCQA)]
    notes = {"medmcqa_adhd": "explicit ADHD term in question stem; manual review required",
             "medmcqa_psych": "subject_name == Psychiatry, ADHD items removed",
             "medmcqa_general": "500 random other validation items, seed 42"}
    return {name: (items, "mcq", "transfer", src, notes[name]) for name, items in out.items()}


def build_pubmedqa():
    items = []
    for r in parquet_rows(PUBMEDQA):
        ctx = r["context"]
        abstract = " ".join(ctx["contexts"])
        adhd = any("Attention Deficit" in m for m in ctx.get("meshes") or [])
        items.append({"id": f"pubmedqa-{r['pubid']}", "answer": ["yes", "no", "maybe"].index(r["final_decision"]),
                      "prompt": f"Abstract: {abstract}\nQuestion: {r['question']}\nAnswer (yes, no, or maybe):",
                      "choices": [" yes", " no", " maybe"], "meta": {"adhd_mesh": adhd}})
    return {"pubmedqa": (items, "mcq", "transfer", [registered(PUBMEDQA)], "all 1000 PQA-L items")}


def build_wikitext(n_articles=50, max_chars=12000):
    articles, current = [], []
    for line in (r["text"] for r in parquet_rows(WIKITEXT)):
        if re.fullmatch(r" = [^=].* = \n?", line) and current:
            articles.append("".join(current).strip())
            current = []
        current.append(line)
    if current:
        articles.append("".join(current).strip())
    chosen = [a for a in articles if len(a) >= 2000][:n_articles]
    items = [{"id": f"wikitext-{k:03d}", "text": a[:max_chars]} for k, a in enumerate(chosen)]
    return {"general_ppl": (items, "ppl", "forgetting", [registered(WIKITEXT)],
                            f"first {n_articles} test articles >= 2000 chars, capped at {max_chars} chars")}


def build_adhd_ppl(roles, max_chars=16000):
    items = [{"id": pmcid, "text": pmc_text(pmcid, max_chars)} for pmcid in roles["new_heldout"]]
    return {"adhd_new_ppl": (items, "ppl", "domain", [{"path": "eval/pmc_roles.json", "sha256": sha256(ROLES)}],
                             f"full text of new_heldout articles, capped at {max_chars} chars")}


def validate_qgen(entry, article, rejections):
    """Keep only questions whose evidence is verbatim in the article and whose answer is not leaked."""
    compact = norm(article)
    kept = []
    for k, q in enumerate(entry.get("items", [])):
        qid = f"{entry['pmcid']}-q{k}"
        opts = q.get("options") or []
        problem = None
        if len(opts) != 4 or any(not str(o).strip() for o in opts):
            problem = "need exactly 4 non-empty options"
        elif len({norm(o) for o in opts}) != 4:
            problem = "duplicate options"
        elif q.get("answer") not in (0, 1, 2, 3):
            problem = "answer must be 0..3"
        elif len(q.get("question", "")) > 400 or any(len(str(o)) > 200 for o in opts):
            problem = "too long"
        elif len(norm(q.get("evidence", ""))) < 30 or norm(q["evidence"]) not in compact:
            problem = "evidence not found verbatim in article"
        elif norm(opts[q["answer"]]) in norm(q["question"]):
            problem = "answer text appears in question"
        if problem:
            rejections.append({"id": qid, "reason": problem})
            continue
        order = list(range(4))
        random.Random(int(hashlib.sha256(qid.encode()).hexdigest(), 16)).shuffle(order)
        kept.append(mcq(qid, q["question"], [opts[i] for i in order], order.index(q["answer"]),
                        {"pmcid": entry["pmcid"], "kind": q.get("kind"), "evidence": q["evidence"]}))
    return kept


def build_newfacts(roles, min_items):
    groups = {"newfacts_trained": set(roles["new_train"]), "newfacts_heldout": set(roles["new_heldout"])}
    items = {name: [] for name in groups}
    paper_counts = {name: 0 for name in groups}
    rejections, sources = [], []
    for path in sorted(QGEN.glob("PMC*.json")):
        entry = json.loads(path.read_text(encoding="utf-8"))
        name = next((n for n, ids in groups.items() if entry["pmcid"] in ids), None)
        if name is None or path.stem != entry["pmcid"]:
            rejections.append({"id": path.name, "reason": "PMCID not in frozen roles"})
            continue
        kept = validate_qgen(entry, pmc_text(entry["pmcid"]), rejections)
        items[name] += kept
        if kept:
            paper_counts[name] += 1
        sources.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})
    short = {n: {"papers": paper_counts[n], "questions": len(v)} for n, v in items.items()
             if len(v) < min_items or paper_counts[n] < 150}
    if short:
        raise RuntimeError(f"A/B exams require >=150 contributing papers and >= {min_items} items each; have {short}")
    atomic_json(EXAMS / "qgen_rejections.json", rejections)
    roles_src = {"path": "eval/pmc_roles.json", "sha256": sha256(ROLES)}
    return {"newfacts_trained": (items["newfacts_trained"], "mcq", "knowledge", [roles_src, *sources],
                                 "generated from new_train papers; evidence verified verbatim"),
            "newfacts_heldout": (items["newfacts_heldout"], "mcq", "control", [roles_src, *sources],
                                 "generated from new_heldout papers; evidence verified verbatim")}


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--status", action="store_true")
    p.add_argument("--rebuild", nargs="+", default=[], help="rebuild named exams; old runs stop being comparable")
    p.add_argument("--with-newfacts", action="store_true", help="freeze A/B question exams; run once, after all qgen")
    p.add_argument("--min-newfacts", type=int, default=400, help="minimum valid questions per group (at least 400)")
    args = p.parse_args()
    index_path = EXAMS / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else \
        {"exam_version": EXAM_VERSION, "exams": {}}
    roles = json.loads(ROLES.read_text(encoding="utf-8")) if ROLES.exists() else None
    builders = [("medmcqa_adhd medmcqa_psych medmcqa_general", MEDMCQA.exists(), build_medmcqa),
                ("pubmedqa", PUBMEDQA.exists(), build_pubmedqa),
                ("general_ppl", WIKITEXT.exists(), build_wikitext),
                ("adhd_new_ppl", roles is not None, lambda: build_adhd_ppl(roles)),
                ("newfacts_trained newfacts_heldout", roles is not None and any(QGEN.glob("PMC*.json"))
                 and (args.with_newfacts or args.status), lambda: build_newfacts(roles, max(400, args.min_newfacts)))]
    if args.status:
        adhd_count = len(build_medmcqa()["medmcqa_adhd"][0]) if MEDMCQA.exists() else None
        for names, ready, _ in builders:
            for name in names.split():
                state = f"built n={index['exams'][name]['n']}" if name in index["exams"] else \
                    ("no qualifying questions" if name == "medmcqa_adhd" and adhd_count == 0 else
                     "ready to build" if ready else "sources missing")
                print(f"{name:<20} {state}")
        return
    EXAMS.mkdir(parents=True, exist_ok=True)
    for names, ready, build in builders:
        wanted = [n for n in names.split() if n not in index["exams"] or n in args.rebuild]
        if not wanted or not ready:
            continue
        for name, (items, kind, role, sources, note) in build().items():
            if name not in wanted:
                continue
            if not items:
                print(f"skip {name}: no items")
                continue
            path = EXAMS / f"{name}.jsonl"
            path.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), encoding="utf-8")
            index["exams"][name] = {"type": kind, "role": role, "file": path.name, "sha256": sha256(path),
                                    "n": len(items), "sources": sources, "note": note,
                                    "built": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()}
            print(f"built {name}: {len(items)} items ({role})")
    atomic_json(index_path, index)
    print(f"index: {index_path.relative_to(ROOT)} ({len(index['exams'])} exams, version {index['exam_version']})")


if __name__ == "__main__":
    main()
