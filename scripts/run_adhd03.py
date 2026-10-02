"""Readiness by default; start only after the owner's message.
Author: Codex / GPT-6 (root), 2026-10-02. Does not install or download anything.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys

from common import ROOT, sha256

DIR = ROOT / 'experiments/adhd-03'


def validate_ready():
    config = json.loads((DIR / 'config.json').read_text())
    ready = json.loads((DIR / 'readiness.json').read_text())
    if ready['status'] != 'prepared_awaiting_owner_start':
        raise RuntimeError('model preparation has not passed')
    if sha256(DIR / 'config.json') != ready['config_sha256']:
        raise RuntimeError('prepared experiment config changed')
    for name, expected in ready['input_sha256'].items():
        if sha256(ROOT / name) != expected:
            raise RuntimeError('prepared input changed: ' + name)
    if Path(config['model_path']).is_absolute():
        raise RuntimeError('use the prepared project model link')
    return config


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start', action='store_true', help='only after the human owner explicitly says to start')
    args = p.parse_args()
    config = validate_ready()
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    log = DIR / ('guard-' + stamp) / 'resources.jsonl'
    command = [sys.executable, '-u', 'scripts/resource_guard.py', '--start-swap-gib', '3',
               '--stop-swap-gib', '4', '--interval', '10', '--log', str(log)]
    if not args.start:
        command.append('--check-only')
        print('Readiness only. No baseline or training will start; await the owner message.', flush=True)
    else:
        command += ['--', sys.executable, '-u', 'scripts/train.py', '--model', config['model_path'],
                    '--train', config['data']['train'], '--valid', config['data']['valid'],
                    '--name', 'adhd03-r3-17b-seed42']
        for name, value in config['training'].items():
            command += ['--' + name.replace('_', '-'), str(value).lower() if isinstance(value, bool) else str(value)]
        command = ['/usr/bin/caffeinate', '-is', *command]
        print('Explicit start: new-model baseline, R3 500 updates, full post-exams; task-bound sleep prevention.', flush=True)
    raise SystemExit(subprocess.call(command, cwd=ROOT))


if __name__ == '__main__':
    main()
