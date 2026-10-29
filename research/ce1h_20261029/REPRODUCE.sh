#!/usr/bin/env bash
set -euo pipefail
: "${BASS_CE1G_ARCHIVE:?Set to the exact CE1-G parent ZIP path}"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
# Run from repository root with PYTHONPATH pointing to this checkout.
export PYTHONPATH="${PYTHONPATH:-.}"
python -m pytest -q \
  tests/nonperturbative/test_einstein_tabulated_sharp.py \
  tests/nonperturbative/test_einstein_tabulated_time.py \
  tests/nonperturbative/test_einstein_tabulated_source.py \
  tests/nonperturbative/test_einstein_exponential_source.py \
  tests/nonperturbative/test_einstein_physical_input.py \
  tests/nonperturbative/test_einstein_interval.py \
  tests/nonperturbative/test_einstein_error_budget.py
python research/ce1h_20261029/independent_checks.py
python research/ce1h_20261029/replay_archived.py
# Optional heavier fresh ref16: 4 independent OS processes with byte checks.
# python research/ce1h_20261029/fresh_partitioned_ref16.py
