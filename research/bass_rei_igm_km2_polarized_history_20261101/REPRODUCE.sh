#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONHASHSEED=0
python restore_source.py --archive inputs/BASS_KM2N_ORIGINAL_SOURCE_S2_20261101.zip --out source_inputs
python polarized_history_response.py --out _replay_results
python -m unittest discover -s tests -p 'test_*.py' -v
python -O -m unittest discover -s tests -p 'test_*.py' -q
python make_science_plots.py --results _replay_results --figures _replay_figures
python verify_replay.py
