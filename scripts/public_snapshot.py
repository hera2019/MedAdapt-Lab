"""Build an audited public Git snapshot without changing the development index.

Author: Codex / GPT-6, 2026-09-30. No network operations or dependency installs.
"""
import argparse
import ast
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    "CHANGES", "DATASETS", "EXPERIMENTS", "ISSUES", "LICENSES", "MODELS",
    "PROJECT_RULES", "QGEN", "SOL6_TASKS", "STORAGE", "REVIEW_RESPONSE",
    "LICENSE_REVIEW", "PUBLICATION",
)
SCRIPTS = (
    "build_exams.py", "common.py", "exam.py", "hf_download.py", "lm.py",
    "pmc_adhd.py", "prepare_dapt.py", "qgen_helper.py", "seal_benchmarks.py",
    "selftest.py", "setup_env.sh", "storage.py", "train.py", "public_snapshot.py", "resource_guard.py",
)
FILES = (
    ".gitignore", "AGENTS.md", "CLAUDE.md", "README.md", "requirements.in",
    "experiments/adhd-01/config.json", "experiments/adhd-01/requirements.lock.txt",
    "results/SOL6_REPORT.md",
) + tuple(f"docs/{name}.md" for name in DOCS) + tuple(f"scripts/{name}" for name in SCRIPTS)
MARKERS = tuple(f"{name}/.gitkeep" for name in (
    "data/raw", "data/processed", "data/train", "data/validation", "data/test",
    "models", "adapters", "eval",
))
PATTERNS = {
    "personal absolute path": re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/|[A-Za-z]:\\Users\\"),
    "private key": re.compile(r"-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----"),
    "GitHub credential": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "provider credential": re.compile(r"\b(?:sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{32,}|AKIA[A-Z0-9]{16})\b"),
    "credential in URL": re.compile(r"https?://[^\s/@]+:[^\s/@]+@|[?&](?:access_token|api_key|token)=[A-Za-z0-9_-]{16,}"),
    "assigned secret": re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret[_-]?key)\s*[:=]\s*[\"'][A-Za-z0-9_+/=-]{16,}[\"']"),
}


def git(*args, env=None, data=None):
    return subprocess.check_output(["git", *args], cwd=ROOT, env=env, input=data)


def inspect_file(path, data, require_english=True):
    if len(data) > 512 * 1024:
        raise RuntimeError(f"public file exceeds 512 KiB: {path}")
    text = data.decode("utf-8")
    if require_english and re.search(r"[\u3400-\u9fff]", text):
        raise RuntimeError(f"new public content must be English: {path}")
    for label, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            raise RuntimeError(f"potential {label}: {path}:{line}; matched value withheld")
    if path.endswith(".py"):
        ast.parse(text, filename=path)
    if path == "manifest.json":
        value = json.loads(text)
        if value["downloads"] or value.get("external_references"):
            raise RuntimeError("public manifest must contain no local download or external-reference records")
    return {"path": path, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def public_files():
    output = {}
    for name in FILES:
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"missing or symlinked public file: {name}")
        output[name] = path.read_bytes()
    for name in ("LICENSE", "NOTICE"):
        path = ROOT / name
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise RuntimeError(f"invalid optional public file: {name}")
            output[name] = path.read_bytes()
    manifest = copy.deepcopy(json.loads((ROOT / "manifest.json").read_text()))
    manifest["downloads"] = []
    manifest["external_references"] = []
    for source in manifest["sources"]:
        for key in ("download_date", "local_size_bytes", "sha256"):
            source[key] = None
        if source.get("path") and Path(source["path"]).is_absolute():
            source["path"] = None
        if source.get("status") in ("downloaded", "registered", "verified_local"):
            source["status"] = "planned"
        source["safe_to_delete"] = False
        for key, value in list(source.items()):
            if isinstance(value, str) and PATTERNS["personal absolute path"].search(value):
                source[key] = None if key.endswith("path") else "Local machine reference omitted from public template."
    output["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    output.update({name: b"" for name in MARKERS})
    if sum(len(data) for data in output.values()) > 2 * 1024 * 1024:
        raise RuntimeError("public snapshot exceeds 2 MiB; review scope before increasing limit")
    return output


def verify_history(ref, allowed):
    commits = git("rev-list", ref).decode().splitlines()
    seen = set()
    for commit in commits:
        for row in git("ls-tree", "-rz", commit).split(b"\0"):
            if not row:
                continue
            meta, name = row.split(b"\t", 1)
            mode, kind, sha = meta.decode().split()
            path = name.decode()
            if path not in allowed or mode != "100644" or kind != "blob":
                raise RuntimeError(f"unexpected public history entry: {path}")
            key = (path, sha)
            if key not in seen:
                inspect_file(path, git("cat-file", "blob", sha), require_english=False)
                seen.add(key)
    return len(commits)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "prepare"))
    parser.add_argument("--author-name")
    parser.add_argument("--author-email")
    args = parser.parse_args()
    if args.action == "prepare" and not (args.author_name and args.author_email):
        parser.error("prepare requires the actual operator's public author name and email")
    files = public_files()
    records = [inspect_file(name, data) for name, data in sorted(files.items())]
    allowed = set(files) | {"LICENSE", "NOTICE"}
    old = subprocess.run(["git", "rev-parse", "--verify", "refs/heads/public"],
                         cwd=ROOT, capture_output=True, text=True)
    parent = old.stdout.strip() if old.returncode == 0 else None
    if parent:
        verify_history(parent, allowed)
    report = {"generator": "public_snapshot.py", "operator": args.author_name, "script_author": "Codex / GPT-6", "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "action": args.action, "files": records, "total_bytes": sum(x["size_bytes"] for x in records),
              "sensitive_pattern_matches": 0, "limitations": "Explicit allowlist and common credential patterns; manual review still required.",
              "local_history_included": False, "public_parent": parent}
    if args.action == "prepare":
        gitdir = Path(git("rev-parse", "--absolute-git-dir").decode().strip())
        with tempfile.TemporaryDirectory(prefix="public-index-", dir=gitdir) as tmp:
            env = os.environ.copy()
            env.update(GIT_INDEX_FILE=str(Path(tmp) / "index"),
                       GIT_AUTHOR_NAME=args.author_name, GIT_AUTHOR_EMAIL=args.author_email,
                       GIT_COMMITTER_NAME=args.author_name, GIT_COMMITTER_EMAIL=args.author_email)
            git("read-tree", "--empty", env=env)
            for name, data in sorted(files.items()):
                sha = git("hash-object", "-w", "--stdin", data=data).decode().strip()
                git("update-index", "--add", "--cacheinfo", f"100644,{sha},{name}", env=env)
            tree = git("write-tree", env=env).decode().strip()
            params = ["commit-tree", tree]
            if parent:
                params += ["-p", parent]
            commit = git(*params, env=env, data=b"Publish reviewed MedAdapt Lab framework snapshot\n").decode().strip()
            report["public_history_commits"] = verify_history(commit, allowed)
            git("update-ref", "refs/heads/public", commit, parent or "0" * 40)
            report.update(commit=commit, tree=tree)
    cache = ROOT / ".cache/publication"
    cache.mkdir(parents=True, exist_ok=True)
    (cache / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Audited {len(records)} public files, {report['total_bytes']} bytes; no sensitive-pattern matches.")
    if args.action == "prepare":
        print(f"Prepared public commit {report['commit']}; no files staged in the development index; no network operations.")


if __name__ == "__main__":
    main()
