#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]" -q
.venv/bin/pytest -q
.venv/bin/python main.py train --corpus data/sample.txt --vocab-size 300
.venv/bin/python main.py encode "low lower newest 🚀 café"
echo smoke ok
