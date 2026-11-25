#!/usr/bin/env bash
set -euo pipefail
bin="$(realpath "$1")"
root="$2"
mkdir "$root"
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for scheme in backward-euler sdirk2; do
  "$bin" --out "$root/$scheme" --family FLRW --shear 0 --duration 0.1 --steps 1 --nmu 6 --nphi 12 --lmax 3 --tau 0.3 --electron-beta 0.2,-0.1,0.05 --feedback tracer --collision "$scheme" --spectral-moments rays --observer-beta 0.12,0.02,-0.04
done
python3 "$(dirname "$0")/frequency_oracle.py" "$root"
sha256sum "$bin"
