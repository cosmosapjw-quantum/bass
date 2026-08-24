#!/bin/bash
# Independent coordinate-basis verification, parts A-E.
# Self-contained: no bianchi-solver / audit-engine imports.
set -e
cd "$(dirname "$0")"
export JAX_PLATFORMS=cpu
python3.11 run_independent.py
