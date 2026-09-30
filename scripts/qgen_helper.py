"""Helper for writing exam questions from 2026 papers (see docs/QGEN.md).

  python scripts/qgen_helper.py queue --limit 20   # next papers to write, groups mixed and hidden
  python scripts/qgen_helper.py show PMC1234567    # title, date and the exact text to quote from
  python scripts/qgen_helper.py check PMC1234567   # validate eval/qgen/PMC1234567.json
  python scripts/qgen_helper.py stats              # progress (groups not shown)

The queue is ordered by SHA-256 of the PMCID so train and held-out papers interleave and
the writer does not know which group a paper belongs to.
"""
import argparse
import hashlib
import json
import xml.etree.ElementTree as ET

from build_exams import QGEN, validate_qgen
from common import ROOT
from pmc_adhd import ROLES, article_text, jats_article


def roles():
    if not ROLES.exists():
        raise SystemExit("eval/pmc_roles.json not frozen yet; run pmc_adhd.py assign-roles first")
    return json.loads(ROLES.read_text(encoding="utf-8"))


def text_of(pmcid):
    return article_text(jats_article(ET.parse(ROOT / "data/raw/pmc" / f"{pmcid}.xml").getroot()))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("queue")
    q.add_argument("--limit", type=int, default=20)
    for name in ("show", "check"):
        sub.add_parser(name).add_argument("pmcid")
    sub.add_parser("stats")
    args = p.parse_args()
    r = roles()
    everyone = sorted(r["new_train"] + r["new_heldout"], key=lambda x: hashlib.sha256(x.encode()).hexdigest())
    if args.command == "queue":
        todo = [x for x in everyone if not (QGEN / f"{x}.json").exists()]
        print(f"{len(everyone) - len(todo)} done, {len(todo)} to go")
        print("\n".join(todo[:args.limit]))
    elif args.command == "show":
        if args.pmcid not in everyone:
            raise SystemExit("not a 2026 paper in the frozen roles")
        meta = json.loads((ROOT / "data/processed/pmc" / f"{args.pmcid}.json").read_text(encoding="utf-8"))
        print(f"# {meta.get('title')}\n# {args.pmcid}  published {meta.get('pub_date')}  {meta.get('license')}\n")
        print(text_of(args.pmcid))
    elif args.command == "check":
        entry = json.loads((QGEN / f"{args.pmcid}.json").read_text(encoding="utf-8"))
        if entry.get("pmcid") != args.pmcid:
            raise SystemExit("pmcid field does not match file name")
        rejected = []
        kept = validate_qgen(entry, text_of(args.pmcid), rejected)
        print(f"kept {len(kept)} / {len(entry.get('items', []))}" +
              (f"; skipped: {entry['skipped_reason']}" if entry.get("skipped_reason") else ""))
        for item in rejected:
            print(f"  REJECT {item['id']}: {item['reason']}")
    else:
        papers = items = 0
        for pmcid in everyone:
            path = QGEN / f"{pmcid}.json"
            if path.exists():
                papers += 1
                items += len(json.loads(path.read_text(encoding="utf-8")).get("items", []))
        # Group totals stay hidden while writing; build_exams.py reports them when freezing.
        print(f"papers {papers} / {len(everyone)}; questions written {items}")


if __name__ == "__main__":
    main()
