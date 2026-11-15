#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python sachs_f08.py --source source --output replay --order 48
python -m unittest -q test_sachs_f08
python -O -m unittest -q test_sachs_f08
python verify_replay.py
python make_plots.py
