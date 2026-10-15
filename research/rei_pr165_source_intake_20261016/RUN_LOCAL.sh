#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tests -v
(cd source_pr164 && python3 -m unittest -v test_kinetic_tangent test_export_bridge)
python3 export_native_geometry.py --source-csv source_pr164/PROPOSED_REI_BACKGROUND.csv --source-receipt source_pr164/PRODUCER_RECEIPT.json --out "${1:?pass new empty output path}"
