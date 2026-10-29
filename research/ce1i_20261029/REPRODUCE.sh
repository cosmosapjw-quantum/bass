#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export PYTHONPATH=.
python -m pytest -q tests/nonperturbative/test_einstein_tabulated_local.py \
 tests/nonperturbative/test_einstein_tabulated_sharp.py \
 tests/nonperturbative/test_einstein_tabulated_time.py \
 tests/nonperturbative/test_einstein_tabulated_source.py \
 tests/nonperturbative/test_einstein_exponential_source.py \
 tests/nonperturbative/test_einstein_physical_input.py \
 tests/nonperturbative/test_einstein_interval.py \
 tests/nonperturbative/test_einstein_error_budget.py
python research/ce1i_20261029/run_ref16.py
python research/ce1i_20261029/plot_science.py
