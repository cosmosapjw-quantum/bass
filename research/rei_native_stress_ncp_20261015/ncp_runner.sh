#!/usr/bin/env bash
set -euo pipefail
RUN_DIR=/root/bass_native_stress_20261015
cd "$RUN_DIR"
mkdir -p results
{
  echo "UTC=$(date --utc --iso-8601=seconds)"
  echo "HOST=$(hostname)"
  echo "CPUS=$(nproc)"
  free -h
  df -h / | tail -1
  /root/.cargo/bin/rustc --version
  /root/.cargo/bin/cargo --version
  uname -srmo
} > results/NCP_HARDWARE.txt
/root/.cargo/bin/rustc -C opt-level=3 -C target-cpu=generic -C debuginfo=0 kernel.rs -o native_massive
sha256sum kernel.rs native_massive > results/RUST_BUILD_SHA256.txt
for mass in 3 30 300; do
  ./native_massive eval "input/grid_m${mass}.txt" "input/cases_m${mass}.tsv" "results/native_m${mass}_t1.tsv" 1
  ./native_massive eval "input/grid_m${mass}.txt" "input/cases_m${mass}.tsv" "results/native_m${mass}_t64.tsv" 64
  cmp "results/native_m${mass}_t1.tsv" "results/native_m${mass}_t64.tsv"
  echo "NCP_BITWISE_64_PASS mass=$mass"
done
: > results/NCP_BENCHMARKS.log
for mass in 3 30 300; do
  for threads in 1 2 4 8 16 32 64; do
    ./native_massive bench "input/grid_m${mass}.txt" 6000 "$threads" 3 >> results/NCP_BENCHMARKS.log
  done
done
sha256sum input/* > results/NCP_INPUT_SHA256.txt
echo "NCP_ALL_PASS"
