#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python -m unittest -v test_source_oracle test_deposition test_time_quadrature test_native_runner test_fixture_campaign
python - <<'PY'
from source_oracle import verify_source_files
print('IMMUTABLE_SOURCE_PINS',verify_source_files())
PY
