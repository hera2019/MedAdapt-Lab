"""ADHD-05: fictional clinical trials for a clean test of knowledge acquisition.

Every fact is drawn at random by this script, so a model cannot know or guess it before
training (chance = 25% on four-option questions). The texts are written by an agent from
these records and validated here. FICTIONAL DATA: local experiment use only, never
published, never mixed into the real corpus.

  python scripts/synth_trials.py generate        # once: records, groups and frozen exams
  python scripts/synth_trials.py list [--limit N] # trials still needing texts (writer)
  python scripts/synth_trials.py show T001        # one trial's facts (writer)
  python scripts/synth_trials.py check T001       # validate data/synthetic/texts/T001.json
  python scripts/synth_trials.py stats
  python scripts/synth_trials.py build-corpus     # training phase: data/train/adhd-05/train.jsonl

Groups (frozen at generate, hidden from the writer): P = 150 trials trained on four
different texts, R = 150 trials trained on one text repeated four times, C = 100 control
trials that are never described anywhere. Author: Claude (Opus 5.5), 2026-10-03.
"""
import argparse
import datetime as dt
import json
import random
import re

from common import ROOT, atomic_json, sha256

SEED = 20261003
EVAL = ROOT / "eval/synthetic"
TRIALS = EVAL / "trials.json"
EXAMS = EVAL / "exams"
TEXTS = ROOT / "data/synthetic/texts"
VERSIONS = 4

POOLS = {
    "drug_class": ["selective norepinephrine modulator", "dopamine reuptake modulator", "alpha-2A receptor agonist",
                   "histamine H3 receptor antagonist", "glutamate receptor modulator", "nicotinic receptor partial agonist",
                   "serotonin-norepinephrine modulator", "trace amine receptor agonist"],
    "country": ["Norway", "Chile", "Japan", "Kenya", "Portugal", "Canada", "Vietnam", "Poland", "Australia",
                "Morocco", "Ireland", "Brazil"],
    "population": ["children aged 6 to 11", "adolescents aged 12 to 17", "adults aged 18 to 55", "university students",
                   "adults over 55", "preschool children aged 4 to 5"],
    "duration": ["4 weeks", "6 weeks", "8 weeks", "10 weeks", "12 weeks", "16 weeks", "24 weeks", "52 weeks"],
    "outcome": ["ADHD Rating Scale total score", "Clinical Global Impression severity", "Conners teacher rating",
                "Adult ADHD Self-Report Scale score", "continuous performance test errors",
                "Weiss Functional Impairment score"],
    "result": ["greater symptom improvement than placebo", "no significant difference from placebo",
               "smaller symptom improvement than placebo", "early termination for lack of efficacy"],
    "adverse_event": ["headache", "insomnia", "nausea", "dizziness", "dry mouth", "fatigue", "irritability",
                      "reduced appetite"],
    "dosing": ["once daily in the morning", "twice daily", "once daily at bedtime", "a weekly skin patch",
               "every other day"],
}
QUESTIONS = {
    "drug_class": "What kind of drug is {drug}?",
    "country": "In which country was the trial of {drug} conducted?",
    "population": "Which participants were enrolled in the trial of {drug}?",
    "sample_size": "How many participants were enrolled in the trial of {drug}?",
    "duration": "How long did the trial of {drug} last?",
    "outcome": "What was the primary outcome measure in the trial of {drug}?",
    "result": "What was the main result of the trial of {drug}?",
    "adverse_event": "What was the most common adverse event reported with {drug}?",
    "dosing": "How was {drug} given in its trial?",
}
ONSETS = ["v", "d", "qu", "s", "t", "l", "n", "p", "r", "z", "c", "f", "m", "b", "g", "k"]
VOWELS = ["a", "e", "i", "o", "u"]
CODAS = ["r", "n", "l", "m", "x", "v", "s", "t"]
ENDINGS = ["ant", "ixine", "oprin", "adol", "etide", "amine", "oxan", "ivrel", "azole", "orin"]
REAL_DRUGS = {"methylphenidate", "atomoxetine", "guanfacine", "clonidine", "viloxazine", "amphetamine",
              "lisdexamfetamine", "dexmethylphenidate", "bupropion", "modafinil", "centanafadine", "solriamfetol"}


def words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def known_vocabulary():
    """Every word in the real training corpus and the system dictionary: invented names must avoid them."""
    vocab = set(REAL_DRUGS)
    for name in ("train.jsonl",):
        with open(ROOT / "data/train/adhd-01" / name, encoding="utf-8") as stream:
            for line in stream:
                vocab.update(words(json.loads(line)["text"]))
    try:
        vocab.update(w.strip().lower() for w in open("/usr/share/dict/words", encoding="utf-8"))
    except OSError:
        pass
    return vocab


def drug_names(rng, n, vocab):
    names = set()
    while len(names) < n:
        name = rng.choice(ONSETS) + rng.choice(VOWELS) + rng.choice(CODAS) + rng.choice(ONSETS) + rng.choice(ENDINGS)
        if name not in vocab and not any(name[:6] == other[:6] for other in names):
            names.add(name)
    return [n.capitalize() for n in sorted(names)]


def mcq(trial, attr, rng):
    """Four options: the true value and three others from the same pool (or nearby numbers)."""
    drug, value = trial["drug"], trial[attr]
    if attr == "sample_size":
        options = {value}
        while len(options) < 4:
            candidate = rng.randint(40, 960)
            if all(abs(candidate - o) >= 40 for o in options):
                options.add(candidate)
        options = [str(o) for o in options]
        value = str(value)
    else:
        options = [value] + rng.sample([v for v in POOLS[attr] if v != value], 3)
    rng.shuffle(options)
    return {"id": f"{trial['id']}-{attr}", "prompt": f"Question: {QUESTIONS[attr].format(drug=drug)}\nAnswer:",
            "choices": [" " + o for o in options], "answer": options.index(value),
            "meta": {"trial": trial["id"], "attribute": attr}}


def generate():
    if TRIALS.exists():
        raise SystemExit(f"{TRIALS.relative_to(ROOT)} is frozen; it is generated once")
    rng = random.Random(SEED)
    names = drug_names(rng, 400, known_vocabulary())
    rng.shuffle(names)
    trials = []
    for k, drug in enumerate(names):
        trial = {"id": f"T{k + 1:03d}", "drug": drug, "sample_size": rng.randint(40, 960)}
        trial.update({attr: rng.choice(pool) for attr, pool in POOLS.items()})
        trials.append(trial)
    order = list(range(400))
    rng.shuffle(order)
    for rank, idx in enumerate(order):
        trials[idx]["group"] = "P" if rank < 150 else "R" if rank < 300 else "C"
    EXAMS.mkdir(parents=True, exist_ok=True)
    qrng = random.Random(SEED + 1)
    index = {"exam_version": "ADHD-05-synthetic-v1", "exams": {}}
    for group, name, role in (("P", "synth_paraphrased", "knowledge"), ("R", "synth_repeated", "knowledge"),
                              ("C", "synth_control", "control")):
        items = [mcq(t, attr, qrng) for t in trials if t["group"] == group for attr in QUESTIONS]
        path = EXAMS / f"{name}.jsonl"
        path.write_text("".join(json.dumps(i) + "\n" for i in items), encoding="utf-8")
        index["exams"][name] = {"type": "mcq", "role": role, "file": path.name, "sha256": sha256(path), "n": len(items),
                                "note": f"fictional trials, group {group}; 9 questions per trial; chance 25%"}
    atomic_json(EXAMS / "index.json", index)
    atomic_json(TRIALS, {"frozen": True, "seed": SEED, "fictional": True,
                         "created": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
                         "author": "Claude (Opus 5.5)", "trials": trials})
    print(f"generated {len(trials)} fictional trials; exams: " +
          ", ".join(f"{k} {v['n']}" for k, v in index["exams"].items()))


def load_trials():
    if not TRIALS.exists():
        raise SystemExit("run generate first")
    return json.loads(TRIALS.read_text(encoding="utf-8"))["trials"]


def writable(trials):
    """Trials that need texts (P and R), in id order; the group itself is not revealed."""
    return [t for t in trials if t["group"] in ("P", "R")]


def facts(trial):
    return {k: trial[k] for k in ("drug", *QUESTIONS)}


def allowed_numbers(trial):
    nums = {str(trial["sample_size"])} | set(re.findall(r"\d+", trial["population"] + " " + trial["duration"]))
    return nums | {"2", "3", "4"}  # small counts such as "two groups" written as digits


def ngrams(tokens, n):
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def validate(trial, entry, all_drugs):
    problems = []
    texts = entry.get("texts") or []
    if entry.get("trial") != trial["id"] or not entry.get("generator"):
        return ["trial id or generator missing"]
    if len(texts) != VERSIONS:
        return [f"need exactly {VERSIONS} texts"]
    stems = set()
    for q in QUESTIONS.values():
        stems |= ngrams(words(q.format(drug=trial["drug"])), 6)
    grams = [ngrams(words(t), 8) for t in texts]
    for k, text in enumerate(texts, 1):
        low = " ".join(words(text))
        n_words = len(text.split())
        if not 100 <= n_words <= 260:
            problems.append(f"text {k}: {n_words} words (allowed 100-260)")
        for attr, value in facts(trial).items():
            if " ".join(words(str(value))) not in low:
                problems.append(f"text {k}: missing {attr} = {value}")
        for attr, pool in POOLS.items():
            others = [v for v in pool if v != trial[attr] and re.search(rf"\b{re.escape(' '.join(words(v)))}\b", low)]
            if others and attr not in ("duration",):
                problems.append(f"text {k}: mentions other {attr} values {others}")
        stray = sorted(set(re.findall(r"\d+", text)) - allowed_numbers(trial))
        if stray:
            problems.append(f"text {k}: numbers not in the record {stray}")
        other_drugs = [d for d in all_drugs if d != trial["drug"] and d.lower() in low]
        if other_drugs:
            problems.append(f"text {k}: names another fictional drug {other_drugs[:3]}")
        if ngrams(words(text), 6) & stems:
            problems.append(f"text {k}: repeats a question's wording; rephrase")
        overlap = max((len(grams[k - 1] & grams[j]) / max(1, len(grams[k - 1])) for j in range(VERSIONS) if j != k - 1),
                      default=0)
        if overlap > 0.4:
            problems.append(f"text {k}: {overlap:.0%} of its 8-word sequences repeat another version; vary it more")
    return problems


def build_corpus():
    """P trials: their four texts once each. R trials: one text (genre rotated by trial number) four times.

    Documents are shuffled so that copies of the same text stay far apart: identical copies in one
    1024-token window would let the model copy in context instead of recalling.
    """
    trials = load_trials()
    all_drugs = [t["drug"] for t in trials]
    docs, r_versions = [], {}
    for t in trials:
        if t["group"] == "C":
            continue
        entry = json.loads((TEXTS / f"{t['id']}.json").read_text(encoding="utf-8"))
        if validate(t, entry, all_drugs):
            raise SystemExit(f"{t['id']} does not pass check; fix it first")
        if t["group"] == "P":
            docs += [(t["id"], text) for text in entry["texts"]]
        else:
            k = int(t["id"][1:]) % VERSIONS
            r_versions[t["id"]] = k + 1
            docs += [(t["id"], entry["texts"][k])] * VERSIONS
    rng = random.Random(SEED + 2)
    rng.shuffle(docs)
    gap = 8
    for _ in range(50):
        moved = False
        for i in range(len(docs)):
            if any(docs[i][0] == docs[j][0] for j in range(max(0, i - gap), i)):
                j = rng.randrange(len(docs))
                docs[i], docs[j] = docs[j], docs[i]
                moved = True
        if not moved:
            break
    else:
        raise SystemExit("could not spread repeated texts apart")
    out = ROOT / "data/train/adhd-05/train.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps({"text": text}) + "\n" for _, text in docs), encoding="utf-8")
    atomic_json(out.with_name("corpus_manifest.json"), {
        "author": "Claude (Opus 5.5) script", "fictional": True, "trials_json_sha256": sha256(TRIALS),
        "train_sha256": sha256(out), "documents": len(docs), "min_gap_between_same_trial": gap,
        "p_trials": sum(t["group"] == "P" for t in trials), "r_trials": len(r_versions),
        "r_version_used": r_versions,
        "texts_sha256": {t: sha256(TEXTS / f"{t}.json") for t in sorted(x["id"] for x in trials if x["group"] != "C")}})
    print(f"wrote {len(docs)} documents to {out.relative_to(ROOT)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("generate")
    sub.add_parser("list").add_argument("--limit", type=int, default=20)
    for name in ("show", "check"):
        sub.add_parser(name).add_argument("trial")
    sub.add_parser("stats")
    sub.add_parser("build-corpus")
    args = p.parse_args()
    if args.command == "generate":
        return generate()
    if args.command == "build-corpus":
        return build_corpus()
    trials = writable(load_trials())
    by_id = {t["id"]: t for t in trials}
    all_drugs = [t["drug"] for t in load_trials()]
    if args.command == "list":
        todo = [t["id"] for t in trials if not (TEXTS / f"{t['id']}.json").exists()]
        print(f"{len(trials) - len(todo)} done, {len(todo)} to go")
        print("\n".join(todo[:args.limit]))
    elif args.command == "show":
        if args.trial not in by_id:
            raise SystemExit("not a trial that needs texts")
        print(json.dumps(facts(by_id[args.trial]), indent=2))
    elif args.command == "check":
        entry = json.loads((TEXTS / f"{args.trial}.json").read_text(encoding="utf-8"))
        problems = validate(by_id[args.trial], entry, all_drugs)
        print("PASS" if not problems else "\n".join(f"FAIL {x}" for x in problems))
    else:
        done = [t for t in trials if (TEXTS / f"{t['id']}.json").exists()]
        failing = [t["id"] for t in done
                   if validate(t, json.loads((TEXTS / f"{t['id']}.json").read_text(encoding="utf-8")), all_drugs)]
        print(f"{len(done)} / {len(trials)} written; {len(done) - len(failing)} pass, {len(failing)} fail")
        for x in failing[:20]:
            print(f"  FAIL {x}")


if __name__ == "__main__":
    main()
