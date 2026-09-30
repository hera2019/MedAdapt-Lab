"""Download only approved Hugging Face files into this project, pinned to a commit."""
import argparse
import fnmatch
import os
from pathlib import Path

from common import ROOT, assert_space, load_manifest, register_download

os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))

CHOICES = {
    "medmcqa": ("openlifescienceai/medmcqa", "dataset", ("data/validation-*.parquet", "data/test-*.parquet")),
    "pubmedqa-labeled": ("qiaojin/PubMedQA", "dataset", ("pqa_labeled/*.parquet",)),
    "wikitext-103-test": ("Salesforce/wikitext", "dataset", ("wikitext-103-raw-v1/test-*.parquet",)),
    "qwen3-0.6b-base": ("Qwen/Qwen3-0.6B-Base", "model", ("*.safetensors", "*.json", "merges.txt", "vocab.json", "LICENSE")),
    "qwen3-1.7b-base": ("Qwen/Qwen3-1.7B-Base", "model", ("*.safetensors", "*.json", "merges.txt", "vocab.json", "LICENSE")),
    "qwen3-14b-mlx-posttrained": ("mlx-community/Qwen3-14B-4bit", "model", ("*.safetensors", "*.json", "*.txt", "LICENSE", "README.md")),
}

def main():
    p = argparse.ArgumentParser(description="No download occurs without a source ID and exact commit.")
    p.add_argument("source_id", choices=CHOICES)
    p.add_argument("--revision", help="full immutable Hugging Face commit SHA")
    p.add_argument("--inspect", action="store_true", help="print current commit and selected file sizes without download")
    p.add_argument("--allow-posttrained", action="store_true", help="required for the post-trained reference model")
    args = p.parse_args()
    if not args.inspect and (not args.revision or len(args.revision) != 40 or any(c not in "0123456789abcdef" for c in args.revision.lower())):
        p.error("download requires --revision with a 40-character commit SHA")
    if args.source_id == "qwen3-14b-mlx-posttrained" and not args.allow_posttrained and not args.inspect:
        p.error("this is a post-trained model, not a Base DAPT model; add --allow-posttrained for reference use")
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        raise SystemExit("Install the project-local optional environment from docs/MODELS.md first") from exc
    repo, repo_type, patterns = CHOICES[args.source_id]
    api = HfApi()
    info = api.repo_info(repo, repo_type=repo_type, revision=args.revision or "main", files_metadata=True)
    if args.revision and info.sha != args.revision:
        raise RuntimeError("repository commit mismatch")
    selected = [s for s in info.siblings if any(fnmatch.fnmatch(s.rfilename, pat) for pat in patterns)]
    if not selected or any(s.size is None for s in selected):
        raise RuntimeError("file list or sizes unavailable; abort")
    estimate = sum(s.size for s in selected)
    if args.inspect:
        print(f"commit: {info.sha}; selected size: {estimate/1024**2:.1f} MiB")
        for sibling in selected:
            print(f"{sibling.size:>12}  {sibling.rfilename}")
        return
    assert_space(estimate * 2)  # room for any project-local staging/cache copies
    source = next(s for s in load_manifest()["sources"] if s["id"] == args.source_id)
    dest = ROOT / source["path"]
    dest.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=repo, repo_type=repo_type, revision=args.revision,
                      allow_patterns=[s.rfilename for s in selected], local_dir=str(dest))
    for sibling in selected:
        path = dest / sibling.rfilename
        if not path.is_file():
            raise RuntimeError(f"missing file after download: {sibling.rfilename}")
        register_download(args.source_id, path,
                          f"https://huggingface.co/{'datasets/' if repo_type == 'dataset' else ''}{repo}/resolve/{args.revision}/{sibling.rfilename}",
                          args.revision, source["license"], source["purpose"], source["filter_rule"],
                          source["license_notes"], sibling.size, safe_to_delete=True,
                          redownload=f"Re-fetch repo {repo} at immutable commit {args.revision}, path {sibling.rfilename}; verify SHA-256")
    print(f"registered {len(selected)} files for {args.source_id} at {args.revision}")

if __name__ == "__main__":
    main()
