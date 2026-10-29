#!/usr/bin/env bash
# Run inside a checkout of the isolated CE1-K GitHub Draft PR. No mutation.
set -euo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -q \
  tests/nonperturbative/test_einstein_error_budget.py \
  tests/nonperturbative/test_einstein_exponential_source.py \
  tests/nonperturbative/test_einstein_interval.py \
  tests/nonperturbative/test_einstein_physical_input.py \
  tests/nonperturbative/test_einstein_tabulated_local.py \
  tests/nonperturbative/test_einstein_tabulated_sharp.py \
  tests/nonperturbative/test_einstein_tabulated_source.py \
  tests/nonperturbative/test_einstein_tabulated_time.py \
  tests/nonperturbative/test_ce1g_independent_audit.py \
  tests/nonperturbative/test_ce1j_variant_contract.py \
  tests/nonperturbative/test_ce1k_canonical_source_local.py
PYTHONPATH=. python research/ce1k_20261029/run_sweep.py
# Fresh ref16 source only; requires exact pinned PR246 S2 archive at the path
# used in reproduce_ref16_source_only.py. Reuse of prior full-panel time residual
# is prohibited without source/time SHA confirmation.
# PYTHONPATH=. python research/ce1k_20261029/reproduce_ref16_source_only.py