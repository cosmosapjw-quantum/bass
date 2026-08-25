#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/.."
python scripts/verify_compiled_plan.py .
python -m unittest discover -s tests -v
sha256sum -c MANIFEST.sha256
