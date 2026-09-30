#!/bin/sh
# Recreate the project environment from the lock file (see docs/MODELS.md).
set -eu
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -r experiments/adhd-01/requirements.lock.txt
printf '%s\n' 'Project environment ready; run .venv/bin/python scripts/selftest.py'
