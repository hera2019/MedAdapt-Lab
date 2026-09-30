"""Check project budget and minimum system free space before writes."""
import argparse
import shutil
from common import ROOT, assert_space, load_manifest, used_bytes

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--need-gib", type=float, default=0.0)
    args = p.parse_args()
    need = int(args.need_gib * 1024**3)
    assert_space(need)
    m = load_manifest()
    print(f"project used: {used_bytes()/1024**3:.2f} GiB / {m['project_budget_bytes']/1024**3:.2f} GiB")
    print(f"disk free: {shutil.disk_usage(ROOT).free/1024**3:.2f} GiB; reserve: {m['minimum_free_bytes']/1024**3:.2f} GiB")
    print(f"requested addition: {args.need_gib:.2f} GiB; permitted")

if __name__ == "__main__":
    main()
