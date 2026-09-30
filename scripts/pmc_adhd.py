"""Discover and sample licensed ADHD full text through NCBI APIs only."""
import argparse
import datetime as dt
import gzip
import json
import random
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from common import ROOT, assert_space, atomic_json, register_download

CONFIG = json.loads((ROOT / "experiments/adhd-01/config.json").read_text(encoding="utf-8"))["pmc"]

# MeSH indexing lags publication by months, so recent papers are also matched by title.
SEARCH = ('("Attention Deficit Disorder with Hyperactivity"[MeSH Terms] OR ADHD[Title] OR "attention deficit"[Title] '
          'OR "attention-deficit"[Title]) AND (cc0 license[filter] OR cc by license[filter] OR cc by-sa license[filter])')
ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
OAI = "https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/"
RAW = ROOT / "data/raw/pmc"
META = ROOT / "data/processed/pmc"
ROLES = ROOT / "eval/pmc_roles.json"
# "pool": older papers, DAPT volume only. "new": papers the base model cannot have seen;
# split once into new_train (DAPT + exam group A) and new_heldout (never trained; group B).
SETS = {"pool": (CONFIG["pool_min_date"], CONFIG["pool_max_date"]), "new": (CONFIG["new_min_date"], None)}


def candidates_path(name):
    return ROOT / f"data/processed/pmc_candidates_{name}.json"
LICENSE_URLS = {
    "https://creativecommons.org/publicdomain/zero/1.0/": "CC0-1.0",
    "https://creativecommons.org/licenses/by/4.0/": "CC-BY-4.0",
    "https://creativecommons.org/licenses/by/3.0/": "CC-BY-3.0",
    "https://creativecommons.org/licenses/by-sa/4.0/": "CC-BY-SA-4.0",
    "https://creativecommons.org/licenses/by-sa/3.0/": "CC-BY-SA-3.0",
}

def local(tag):
    return tag.rsplit("}", 1)[-1]

def request(url, max_bytes):
    req = Request(url, headers={"User-Agent": "MedAdaptLab/0.1 (research; contact: local-user)", "Accept-Encoding": "gzip"})
    with urlopen(req, timeout=30) as response:
        blob = response.read(max_bytes + 1)
        if len(blob) > max_bytes:
            raise RuntimeError("response exceeds per-request cap")
        if response.headers.get("Content-Encoding") == "gzip":
            blob = gzip.decompress(blob)
            if len(blob) > max_bytes:
                raise RuntimeError("expanded response exceeds cap")
        return blob

def discover(name, limit):
    assert_space(4 * 1024 * 1024)
    lo, hi = SETS[name]
    hi = hi or dt.date.today().strftime("%Y/%m/%d")
    url = ESEARCH + "?" + urlencode({"db": "pmc", "term": SEARCH, "retmode": "json", "retmax": limit,
                                     "sort": "pub date", "datetype": "pdat", "mindate": lo, "maxdate": hi})
    blob = request(url, 4 * 1024 * 1024)
    data = json.loads(blob)
    ids = ["PMC" + x for x in data["esearchresult"]["idlist"]]
    if name == "pool" and candidates_path("new").exists():
        newer = set(json.loads(candidates_path("new").read_text(encoding="utf-8"))["pmcids"])
        ids = [x for x in ids if x not in newer]  # publication-date overlap: "new" wins
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"search_adhd_oa_{name}.json"
    path.write_bytes(blob)
    register_download("pmc-adhd-oa", path, url, "NCBI ESearch live query", "NCBI metadata; verify per article", "discovery", SEARCH, "Index response only, not full-text license", len(blob))
    atomic_json(candidates_path(name), {"set": name, "query": SEARCH, "date_range": [lo, hi], "source_url": url,
                                         "pmcids": ids, "reported_count": data["esearchresult"].get("count")})
    print(f"{name}: saved {len(ids)} candidates ({lo}..{hi}); total reported {data['esearchresult'].get('count')}")

def jats_article(root):
    for el in root.iter():
        if local(el.tag) == "article":
            return el
    raise ValueError("no JATS article")

def article_license(article):
    found = []
    for el in article.iter():
        if local(el.tag) != "license":
            continue
        for part in el.iter():
            for key, value in part.attrib.items():
                if local(key) == "href":
                    normalized = value.replace("http://", "https://").rstrip("/") + "/"
                    if normalized in LICENSE_URLS:
                        found.append((LICENSE_URLS[normalized], normalized))
    if len(set(found)) != 1:
        raise ValueError(f"license ambiguous or disallowed: {found}")
    return found[0]

def article_ids(article):
    out = {}
    for el in article.iter():
        if local(el.tag) == "article-id":
            key = el.attrib.get("pub-id-type")
            if key in {"pmid", "pmc", "doi"} and el.text:
                out[key] = el.text.strip()
    return out

def article_title(article):
    for el in article.iter():
        if local(el.tag) == "article-title":
            return " ".join(" ".join(el.itertext()).split())
    return None

def pub_date(article):
    """Earliest <pub-date> as YYYY-MM-DD (missing parts -> 01)."""
    dates = []
    for el in article.iter():
        if local(el.tag) != "pub-date":
            continue
        parts = {local(c.tag): (c.text or "").strip() for c in el}
        if parts.get("year", "").isdigit():
            month = parts.get("month", "1")
            day = parts.get("day", "1")
            month = month if month.isdigit() else "1"
            day = day if day.isdigit() else "1"
            dates.append(f"{int(parts['year']):04d}-{int(month):02d}-{int(day):02d}")
    return min(dates) if dates else None

def new_date_ok(value):
    """Use the earliest JATS publication date, not only the ESearch pdat match."""
    return bool(value and value >= CONFIG["new_min_date"].replace("/", "-"))

def assign_roles(heldout_fraction, seed):
    """Freeze which fetched "new" articles are trained on and which stay unseen. Runs once."""
    if ROLES.exists():
        raise RuntimeError(f"{ROLES.relative_to(ROOT)} is frozen; delete it only before any exam or training exists")
    fetched = []
    for path in META.glob("PMC*.json"):
        if path.name.endswith(".rejected.json"):
            continue
        meta = json.loads(path.read_text(encoding="utf-8"))
        if meta["set"] != "new":
            continue
        if meta.get("screening_version") != "fulltext-v1":
            raise RuntimeError(f"unscreened article: {meta['pmcid']}; run screen-existing first")
        if not meta.get("excluded_reason"):
            fetched.append(meta["pmcid"])
    fetched.sort()
    if len(fetched) < 20:
        raise RuntimeError(f"only {len(fetched)} new articles fetched; fetch more before freezing roles")
    random.Random(seed).shuffle(fetched)
    cut = round(len(fetched) * heldout_fraction)
    roles = {"frozen": True, "created": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
             "seed": seed, "heldout_fraction": heldout_fraction,
             "new_heldout": sorted(fetched[:cut]), "new_train": sorted(fetched[cut:])}
    atomic_json(ROLES, roles)
    print(f"frozen roles: {len(roles['new_train'])} new_train, {len(roles['new_heldout'])} new_heldout")

def record_datestamp(root):
    for el in root.iter():
        if local(el.tag) == "datestamp" and el.text:
            return el.text.strip()
    return "unknown"

def article_text(article):
    sections = []
    for kind in ("article-title", "abstract", "body"):
        for el in article.iter():
            if local(el.tag) == kind:
                if kind == "article-title":
                    sections.append(" ".join(" ".join(el.itertext()).split()))
                else:
                    for p in el.iter():
                        if local(p.tag) == "p":
                            value = " ".join(" ".join(p.itertext()).split())
                            if len(value) >= 40:
                                sections.append(value)
                break
    return "\n\n".join(x for x in sections if x)

def body_text(article):
    """Text from JATS body paragraphs, excluding title and abstract."""
    for body in article.iter():
        if local(body.tag) == "body":
            return "\n\n".join(value for p in body.iter() if local(p.tag) == "p"
                                 if len(value := " ".join(" ".join(p.itertext()).split())) >= 40)
    return ""

def screen_existing():
    """Retain downloaded XML provenance while excluding abstract-only records."""
    screened = excluded = 0
    for path in sorted(RAW.glob("PMC*.xml")):
        meta_path = META / f"{path.stem}.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        body_chars = len(body_text(jats_article(ET.parse(path).getroot())))
        meta["body_characters"] = body_chars
        meta["screening_version"] = "fulltext-v1"
        if body_chars < 1000:
            meta["excluded_reason"] = "too little JATS body text"
            excluded += 1
        elif meta["set"] == "new" and not new_date_ok(meta.get("pub_date")):
            meta["excluded_reason"] = "earliest JATS publication before new-set boundary"
            excluded += 1
        else:
            meta.pop("excluded_reason", None)
        atomic_json(meta_path, meta)
        screened += 1
    print(f"screened {screened} downloaded articles; excluded {excluded} with short or missing body")

def fetch(name, limit, max_article_mib, max_total_mib):
    if not candidates_path(name).exists():
        raise RuntimeError(f"run discover --set {name} first")
    candidates = json.loads(candidates_path(name).read_text(encoding="utf-8"))["pmcids"][:limit]
    exclusions_path = ROOT / "eval/benchmark_exclusions.json"
    exclusions = json.loads(exclusions_path.read_text()) if exclusions_path.exists() else {}
    blocked_pmids = set(str(x) for x in exclusions.get("pmids", []))
    blocked_pmcids = set(str(x) for x in exclusions.get("pmcids", []))
    blocked_dois = set(str(x).lower() for x in exclusions.get("dois", []))
    total = 0
    for pmcid in candidates:
        if not re.fullmatch(r"PMC\d+", pmcid):
            raise ValueError(f"invalid PMCID: {pmcid}")
        if pmcid in blocked_pmcids:
            print(f"skip benchmark article {pmcid}")
            continue
        path = RAW / f"{pmcid}.xml"
        if path.exists() or (META / f"{pmcid}.rejected.json").exists():
            continue
        per_cap = max_article_mib * 1024**2
        if total + per_cap > max_total_mib * 1024**2:
            break
        assert_space(per_cap)
        url = OAI + "?" + urlencode({"verb": "GetRecord", "identifier": "oai:pubmedcentral.nih.gov:" + pmcid[3:], "metadataPrefix": "pmc"})
        try:
            blob = request(url, per_cap)
            record = ET.fromstring(blob)
            article = jats_article(record)
            license_name, license_url = article_license(article)
            ids = article_ids(article)
            if ids.get("pmid") in blocked_pmids or ids.get("doi", "").lower() in blocked_dois:
                raise ValueError("benchmark linked article")
            content = article_text(article)
            body_chars = len(body_text(article))
            if len(content) < 1000 or body_chars < 1000:
                raise ValueError("too little body text")
            earliest_date = pub_date(article)
            if name == "new" and not new_date_ok(earliest_date):
                raise ValueError("earliest JATS publication before new-set boundary")
            RAW.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
            register_download("pmc-adhd-oa", path, url, f"{pmcid}@{record_datestamp(record)}", license_name,
                              "corpus", SEARCH + f"; set={name}; JATS license verified; benchmark ID exclusion",
                              f"{license_url}; article-level attribution required", len(blob))
            meta = {"pmcid": pmcid, "set": name, "pmid": ids.get("pmid"), "doi": ids.get("doi"),
                    "title": article_title(article), "pub_date": earliest_date, "license": license_name,
                    "license_url": license_url, "characters": len(content), "body_characters": body_chars,
                    "screening_version": "fulltext-v1"}
            atomic_json(META / f"{pmcid}.json", meta)
            total += len(blob)
            print(f"saved {pmcid}: {license_name}, {len(blob)} bytes")
        except (ValueError, ET.ParseError) as exc:
            atomic_json(META / f"{pmcid}.rejected.json", {"pmcid": pmcid, "set": name, "reason": str(exc)})
            print(f"rejected {pmcid}: {exc}")
        time.sleep(0.5)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("discover")
    d.add_argument("--set", choices=SETS, required=True)
    d.add_argument("--limit", type=int, default=20)
    f = sub.add_parser("fetch")
    f.add_argument("--set", choices=SETS, required=True)
    f.add_argument("--limit", type=int, default=5)
    f.add_argument("--max-article-mib", type=int, default=8)
    f.add_argument("--max-total-mib", type=int, default=40)
    r = sub.add_parser("assign-roles")
    r.add_argument("--heldout-fraction", type=float, default=CONFIG["new_heldout_fraction"])
    r.add_argument("--seed", type=int, default=42)
    sub.add_parser("screen-existing", help="mark already downloaded abstract-only XML as excluded")
    args = parser.parse_args()
    if args.command == "assign-roles":
        assign_roles(args.heldout_fraction, args.seed)
        return
    if args.command == "screen-existing":
        screen_existing()
        return
    if args.limit < 1 or args.limit > 5000:
        parser.error("limit must be 1..5000")
    if args.command == "discover":
        discover(args.set, args.limit)
    else:
        fetch(args.set, args.limit, args.max_article_mib, args.max_total_mib)

if __name__ == "__main__":
    main()
