#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
scratch="$(mktemp -d "${TMPDIR:-/tmp}/bass_pr170_replay_XXXXXXXX")"
trap 'rm -rf "$scratch"' EXIT
export BASS_PR170_REPLAY_DIR="$scratch"
python -m unittest -v test_born_photon_stress test_bass_campaign test_high_precision
python run_bass_campaign.py --out "$scratch/campaign"
python high_precision_check.py --out "$scratch/mp70.json"
(cd "$here/evidence/S3_CAMPAIGN_FINAL" && sha256sum -c SHA256SUMS.txt)
python - <<'PY'
from pathlib import Path
import hashlib,os,json
root=Path('evidence');generated=Path(os.environ['BASS_PR170_REPLAY_DIR'])
for n in ('HISTORY.csv','RESULTS.json'):
 assert hashlib.sha256((root/'S3_CAMPAIGN_FINAL'/n).read_bytes()).digest()==hashlib.sha256((generated/'campaign'/n).read_bytes()).digest(),('REPRODUCIBILITY_FAIL',n)
assert json.loads((generated/'mp70.json').read_text())['numerical_pass']
print('REPLAY:ORIGINAL_S3_CSV_AND_JSON_EXACT_BYTES:PASS')
print('REPLAY:INDEPENDENT_MP70_CLOSED_FORM:PASS')
PY
