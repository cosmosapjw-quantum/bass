#!/usr/bin/env bash
set -euo pipefail
d="$(cd "$(dirname "$0")" && pwd)"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s "$d" -p 'test_*.py' -v
if test "$#" -ge 1; then out="$1"; else out="$(mktemp -d /tmp/bass-pr167.XXXXXXXX)"; fi
mkdir -p "$out"
python3 "$d/run_campaign.py" --output "$out/neutral"
python3 "$d/einstein_stress_lag.py" --out "$out/dynamics"
python3 "$d/high_precision_check.py"
python3 "$d/nonlrs_convexity.py"
echo "BASS_SANDBOX_REPRODUCED results=$out"
