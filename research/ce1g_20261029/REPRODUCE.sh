#!/usr/bin/env bash
set -euo pipefail
export OPENBLAS_NUM_THREADS=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python - <<'PY'
import sys, ctypes, numpy, scipy, pytest
ctypes.CDLL('libmpfr.so.6')
print('PYTHON_PASS',sys.version.split()[0], 'numpy',numpy.__version__, 'scipy',scipy.__version__)
PY
python -m pytest -q \
 tests/nonperturbative/test_einstein_tabulated_time.py \
 tests/nonperturbative/test_einstein_tabulated_source.py \
 tests/nonperturbative/test_einstein_exponential_source.py \
 tests/nonperturbative/test_einstein_physical_input.py \
 tests/nonperturbative/test_einstein_interval.py \
 tests/nonperturbative/test_einstein_error_budget.py
python - <<'PY'
import json
j=json.load(open('research/ce1g_20261029/evidence/SCIENCE_RESULTS.json'))
assert len(j)==5 and j[-1]['total_ell_h_upper'][1]<1e-5
print('SAVED_SCIENCE_EVIDENCE_PASS')
PY
