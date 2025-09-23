#!/usr/bin/env bash
set -euo pipefail
PY=python3.12
if ! command -v ${PY} >/dev/null 2>&1; then
  echo "python3.12 not found. Install via: brew install python@3.12" >&2
  exit 1
fi
${PY} -m venv .venv312
source .venv312/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
# Subtitles extras
pip install av==12.3.0
