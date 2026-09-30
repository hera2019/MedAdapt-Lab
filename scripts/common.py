"""Project-local manifest, hashing and storage guards (stdlib only)."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".part")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def used_bytes():
    total = 0
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            try:
                total += (Path(base) / name).stat().st_size
            except FileNotFoundError:
                pass
    return total


def assert_space(need_bytes):
    m = load_manifest()
    free = shutil.disk_usage(ROOT).free
    used = used_bytes()
    if need_bytes < 0 or free - need_bytes < m["minimum_free_bytes"]:
        raise RuntimeError(f"insufficient free space: free={free}, need={need_bytes}, reserve={m['minimum_free_bytes']}")
    if used + need_bytes > m["project_budget_bytes"]:
        raise RuntimeError(f"project budget exceeded: used={used}, need={need_bytes}, budget={m['project_budget_bytes']}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def register_download(source_id, path, url, version, license_name, purpose, filter_rule, license_notes,
                      original_size=None, safe_to_delete=False, redownload=None):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("download outside project")
    m = load_manifest()
    if not any(s["id"] == source_id for s in m["sources"]):
        raise ValueError(f"unknown source: {source_id}")
    rel = str(path.relative_to(ROOT))
    item = {
        "source_id": source_id, "name": path.name, "source": next(s["source"] for s in m["sources"] if s["id"] == source_id),
        "url": url, "version_or_commit": version, "download_date": dt.datetime.now(dt.timezone.utc).isoformat(),
        "license": license_name, "original_size_bytes": original_size, "local_size_bytes": path.stat().st_size,
        "path": rel, "sha256": sha256(path), "purpose": purpose, "filter_rule": filter_rule,
        "safe_to_delete": safe_to_delete,
        "redownload": redownload or f"Re-request exact URL and version {version}; verify SHA-256; keep current file if bytes changed",
        "license_notes": license_notes
    }
    m["downloads"] = [x for x in m["downloads"] if x["path"] != rel] + [item]
    atomic_json(MANIFEST, m)
    return item
