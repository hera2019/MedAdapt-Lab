"""ADHD-02 rewrite helper: list new_train papers, show their text, validate rewrites.

  python scripts/augment_check.py list [--limit 20]   # new_train papers not yet rewritten
  python scripts/augment_check.py show PMC1234567     # the paper text to rewrite from
  python scripts/augment_check.py check PMC1234567    # validate data/augment/adhd-02/rewrites/PMC1234567.json
  python scripts/augment_check.py stats

Only new_train papers are eligible: held-out papers must never reach training text.
The leak check compares rewrites with the frozen exam questions and reports counts only,
so the rewriter stays blind to question wording. Author: Claude (Opus 5.5), 2026-10-01.
"""
import argparse
import json
import re
import xml.etree.ElementTree as ET

from common import ROOT
from pmc_adhd import ROLES, article_text, jats_article

OUT = ROOT / "data/augment/adhd-02/rewrites"
STYLES = {"summary", "plain", "facts", "news"}
ALLOWED_NUMBERS = {"2025", "2026"}
NGRAM = 8


def words(text):
    return re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text.lower())


def ngrams(tokens, n=NGRAM):
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def numbers(text):
    return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?", text.replace(",", "")))


def new_train():
    return json.loads(ROLES.read_text(encoding="utf-8"))["new_train"]


def paper_text(pmcid):
    return article_text(jats_article(ET.parse(ROOT / "data/raw/pmc" / f"{pmcid}.xml").getroot()))


def question_ngrams():
    grams = set()
    for name in ("newfacts_trained", "newfacts_heldout"):
        for line in (ROOT / "eval/exams" / f"{name}.jsonl").read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            stem = item["prompt"].removeprefix("Question:").removesuffix("Answer:")
            grams |= ngrams(words(stem))
            for choice in item["choices"]:
                grams |= ngrams(words(choice))
    return grams


def validate(pmcid):
    """Return a list of problems; empty means the file passes."""
    path = OUT / f"{pmcid}.json"
    entry = json.loads(path.read_text(encoding="utf-8"))
    if entry.get("pmcid") != pmcid or pmcid not in new_train():
        return ["pmcid missing, mismatched or not a new_train paper"]
    if not entry.get("generator"):
        return ["generator (actual agent / model) is required"]
    rewrites = entry.get("rewrites") or []
    problems = []
    if sorted(r.get("style") for r in rewrites) != sorted(STYLES):
        problems.append(f"need exactly one rewrite per style {sorted(STYLES)}")
    source = paper_text(pmcid)
    source_words = words(source)
    source_grams = ngrams(source_words)
    source_numbers = numbers(source) | ALLOWED_NUMBERS
    exam_grams = question_ngrams() - source_grams  # phrasing that exists only in questions
    for r in rewrites:
        text, style = r.get("text", ""), r.get("style")
        tokens = words(text)
        grams = ngrams(tokens)
        if not 150 <= len(text.split()) <= 1000:
            problems.append(f"{style}: {len(text.split())} words (allowed 150-1000)")
        invented = sorted(numbers(text) - source_numbers)
        if invented:
            problems.append(f"{style}: numbers not in the paper: {invented[:8]}")
        if grams and len(grams & source_grams) / len(grams) > 0.5:
            problems.append(f"{style}: over half of its 8-word sequences are copied from the paper; reword")
        if re.search(r"(?m)^\s*(?:[A-D][.)]\s|Question:|Answer:)", text):
            problems.append(f"{style}: looks like a quiz (option letters or Question/Answer lines)")
        leaked = len(grams & exam_grams)
        if leaked:
            problems.append(f"{style}: {leaked} phrase(s) match exam wording absent from the paper; rephrase")
    return problems


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list").add_argument("--limit", type=int, default=20)
    for name in ("show", "check"):
        sub.add_parser(name).add_argument("pmcid")
    sub.add_parser("stats")
    args = p.parse_args()
    papers = new_train()
    if args.command == "list":
        todo = [x for x in papers if not (OUT / f"{x}.json").exists()]
        print(f"{len(papers) - len(todo)} done, {len(todo)} to go")
        print("\n".join(todo[:args.limit]))
    elif args.command == "show":
        if args.pmcid not in papers:
            raise SystemExit("not a new_train paper; only new_train papers may be rewritten")
        meta = json.loads((ROOT / "data/processed/pmc" / f"{args.pmcid}.json").read_text(encoding="utf-8"))
        print(f"# {meta.get('title')}\n# {args.pmcid}  published {meta.get('pub_date')}  {meta.get('license')}\n")
        print(paper_text(args.pmcid))
    elif args.command == "check":
        problems = validate(args.pmcid)
        print("PASS" if not problems else "\n".join(f"FAIL {x}" for x in problems))
    else:
        done = [x for x in papers if (OUT / f"{x}.json").exists()]
        failing = [x for x in done if validate(x)]
        print(f"{len(done)} / {len(papers)} written; {len(done) - len(failing)} pass, {len(failing)} fail")
        for x in failing[:20]:
            print(f"  FAIL {x}")


if __name__ == "__main__":
    main()
