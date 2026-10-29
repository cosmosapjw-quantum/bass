#!/usr/bin/env bash
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python -m pytest -q tests/nonperturbative/test_ce1m_locked_source_local.py tests/nonperturbative/test_ce1k_canonical_source_local.py tests/nonperturbative/test_ce1l_physical_table_identity.py tests/nonperturbative/test_ce1l_positive_stored_residual.py tests/nonperturbative/test_ce1k_cardinality_contract.py tests/nonperturbative/test_ce1j_variant_contract.py tests/nonperturbative/test_ce1g_independent_audit.py tests/nonperturbative/test_einstein_tabulated_local.py tests/nonperturbative/test_einstein_tabulated_sharp.py tests/nonperturbative/test_einstein_tabulated_time.py tests/nonperturbative/test_einstein_tabulated_source.py tests/nonperturbative/test_einstein_exponential_source.py tests/nonperturbative/test_einstein_physical_input.py tests/nonperturbative/test_einstein_interval.py tests/nonperturbative/test_einstein_error_budget.py
# Optional scientific runs from the preserved original source:
python research/ce1m_20261029/ref8.py
# Optional ref16 fresh MPFR192 SOURCE ONLY, inheriting SHA-verified time residual:
# python research/ce1m_20261029/ref16_source_only.py
