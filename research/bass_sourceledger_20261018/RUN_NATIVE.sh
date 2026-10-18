#!/usr/bin/env bash
# Source-only real native measurement, not reactive H/He or owner restart.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -ne 2 ]]; then
  echo "Usage: RUN_NATIVE.sh ORIGINAL_REI_GIT_REPO NEW_OUTPUT_DIRECTORY" >&2
  exit 2
fi
repo="$(realpath "$1")"
out="$2"
if [[ -e "$out" ]]; then echo "CREATE_ONLY_OUTPUT_REQUIRED" >&2; exit 3; fi
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
cd "$here"
python native_runner.py --rei-repo "$repo" --fixtures "$here/fixtures" --out "$out" \
  --jobs "${CARGO_BUILD_JOBS:-2}" --wall-seconds 1800
