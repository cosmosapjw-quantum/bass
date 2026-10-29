#!/bin/bash
set -euo pipefail
# Run from a checkout at the exact CE1-J Draft PR HEAD, with libmpfr.so.6
# This tests only scoped Einsten-Vlasov oracle, not production Boltzmann.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTHONPATH="${PYTHONPATH:-.}"
python -m pytest -q \
 tests/nonperturbative/test_einstein_tabulated_source_local.py \
 tests/nonperturbative/test_ce1j_source_identity_guards.py \
 tests/nonperturbative/test_einstein_tabulated_local.py \
 tests/nonperturbative/test_einstein_tabulated_sharp.py \
 tests/nonperturbative/test_einstein_tabulated_time.py \
 tests/nonperturbative/test_einstein_tabulated_source.py \
 tests/nonperturbative/test_einstein_exponential_source.py \
 tests/nonperturbative/test_einstein_physical_input.py \
 tests/nonperturbative/test_einstein_interval.py \
 tests/nonperturbative/test_einstein_error_budget.py
python - <<'PY'
import json
x=json.load(open('research/ce1j_20261029/CE1J_SWEEP.json'))
for row in x:print(row['refinement'],row['rays'],row['ce1j_h'],row['target_met'])
PY
# Optional heavy fresh source ref16 (~35s in original reference environment):
# python research/ce1j_20261029/run_ref16_ce1j.py
# Optional fresh small-panel sweep:
# python research/ce1j_20261029/run_refinement_ce1j.py
# NOTE: ref16 time residual source is the SHA-verified FRESH_CE1I_REF16.json.
