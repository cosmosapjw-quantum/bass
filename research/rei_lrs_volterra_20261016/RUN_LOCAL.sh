#!/usr/bin/env bash
set -euo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")"
python -m unittest -v test_retarded test_campaign test_high_precision
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
python high_precision.py --out "$work/MP70.json"
python run_campaign.py --out "$work/CAMPAIGN"
(cd "$work/CAMPAIGN" && sha256sum -c SHA256SUMS.txt)
python - "$work" <<'PY'
from pathlib import Path
import json,sys
w=Path(sys.argv[1]); d=json.loads((w/'CAMPAIGN/RESULTS.json').read_text()); m=json.loads((w/'MP70.json').read_text())
assert len(d['cases'])==3 and d['rows']==99
assert d['tests']['max_abs_picard_vs_ode']<3e-13
assert m['max_relative_error']<3e-14
print('BASS_LRS_RETARDED_SOURCE_ONLY_REPRODUCED',d['rows'],m['max_relative_error'])
PY
