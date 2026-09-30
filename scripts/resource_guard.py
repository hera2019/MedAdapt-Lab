"""Guard formal training with frozen-exam and resource preconditions.

Author: Codex / GPT-6, 2026-09-30. Uses existing macOS/stdlib facilities only.
"""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess

from common import ROOT, load_manifest, sha256, used_bytes


def swap_bytes(text):
    match = re.search(r"\bused\s*=\s*([\d.]+)\s*([KMGT]?)", text)
    if not match:
        raise RuntimeError("cannot parse vm.swapusage; refusing unmonitored launch")
    return int(float(match[1]) * 1024 ** ("KMGT".find(match[2]) + 1 if match[2] else 0))


def snapshot():
    output = subprocess.check_output(["sysctl", "vm.swapusage"], text=True)
    return {"swap_used_bytes": swap_bytes(output), "disk_free_bytes": shutil.disk_usage(ROOT).free,
            "project_used_bytes": used_bytes()}


def resource_issue(values, swap_limit_gib, manifest):
    if values["disk_free_bytes"] < manifest["minimum_free_bytes"]:
        return "system disk reserve breached"
    if values["project_used_bytes"] > manifest["project_budget_bytes"]:
        return "project storage budget breached"
    if values["swap_used_bytes"] >= swap_limit_gib * 1024 ** 3:
        return "reviewed swap threshold reached"
    return None


def exam_issue(index_path):
    index_path = Path(index_path)
    if not index_path.is_file():
        return "frozen exam index missing"
    index = json.loads(index_path.read_text())
    for name in ("newfacts_trained", "newfacts_heldout"):
        spec = index.get("exams", {}).get(name)
        if not spec or spec.get("n", 0) < 400:
            return f"complete frozen {name} exam is not ready"
        path = (index_path.parent / spec["file"]).resolve()
        if not path.is_relative_to(index_path.parent.resolve()) or not path.is_file():
            return f"invalid frozen file for {name}"
        if sha256(path) != spec["sha256"]:
            return f"frozen hash mismatch for {name}"
    return None


def stop_child(child):
    """Only signal this Popen child/session, never the caller's process group."""
    if child.poll() is not None:
        return
    def send(sig):
        try:
            if os.getpgid(child.pid) == child.pid:
                os.killpg(child.pid, sig)
            else:
                child.send_signal(sig)
        except ProcessLookupError:
            pass
    for sig, timeout in ((signal.SIGINT, 15), (signal.SIGTERM, 10), (signal.SIGKILL, 5)):
        send(sig)
        try:
            child.wait(timeout=timeout)
            return
        except subprocess.TimeoutExpired:
            continue
    raise RuntimeError("owned child did not stop after bounded interruption attempts")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--smoke", action="store_true", help="Explicit diagnostic mode; omit formal-exam gate")
    parser.add_argument("--start-swap-gib", type=float, default=1.0)
    parser.add_argument("--stop-swap-gib", type=float, default=4.0)
    parser.add_argument("--interval", type=float, default=60.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not all(math.isfinite(v) and v > 0 for v in (args.start_swap_gib,args.stop_swap_gib,args.interval)):
        parser.error("resource limits and interval must be finite positive numbers")
    if args.interval > 60 or args.stop_swap_gib < args.start_swap_gib:
        parser.error("record at least once per minute; stop threshold must not be below start threshold")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not args.check_only and not command:
        parser.error("a child command is required")
    logfile = args.log.resolve()
    if not logfile.is_relative_to(ROOT):
        parser.error("resource log must stay within the project")
    if logfile.exists():
        parser.error("use a new resource-log path; existing records are not overwritten")
    logfile.parent.mkdir(parents=True,exist_ok=True)
    manifest=load_manifest()
    with logfile.open("x") as stream:
        def record(event, **fields):
            stream.write(json.dumps({"time":dt.datetime.now(dt.timezone.utc).isoformat(),"event":event,**fields})+"\n")
            stream.flush()
        values=snapshot()
        issues=[resource_issue(values,args.start_swap_gib,manifest)]
        if not args.smoke:
            issues.append(exam_issue(ROOT/"eval/exams/index.json"))
        issues=[i for i in issues if i]
        record("preflight",**values,issues=issues,command=command,smoke=args.smoke,
               start_swap_gib=args.start_swap_gib,stop_swap_gib=args.stop_swap_gib,interval=args.interval)
        if issues:
            print("Launch blocked: "+"; ".join(issues),flush=True)
            return 2
        if args.check_only:
            print("Formal launch preflight passed; no child started.",flush=True)
            return 0
        child=subprocess.Popen(command,cwd=ROOT,start_new_session=True)
        record("child_started",pid=child.pid)
        failure=None
        try:
            while child.poll() is None:
                try:
                    child.wait(timeout=args.interval)
                    break
                except subprocess.TimeoutExpired:
                    values=snapshot()
                    failure=resource_issue(values,args.stop_swap_gib,manifest)
                    record("monitor",**values,stop_reason=failure)
                    if failure:
                        stop_child(child)
                        break
        except BaseException as error:
            stop_child(child)
            record("guard_exception",error_type=type(error).__name__)
            raise
        record("child_exit",exit_code=child.returncode,stop_reason=failure)
        if failure:
            print("Owned training child stopped: "+failure,flush=True)
            return 3
        return child.returncode if child.returncode >= 0 else 128-child.returncode


if __name__ == "__main__":
    raise SystemExit(main())
