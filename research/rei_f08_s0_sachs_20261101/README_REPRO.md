# BASS → REI F08 S0 original same-source Bianchi Sachs optics

One bounded science unit in cosmosapjw-quantum/bass based on immutable BASS main commit 9c6506e4e2087129a8b674ff10438e5db1a55c9d and original REI PR349 exact HEAD 1605236b8172db411d862caa219322d6af6953b1.

## Source

Five original REI349 files in source/ are byte-for-byte recovered from the original GitHub PR, and have exact required source SHA-256 in sachs_f08.py. Do not replace with CE1AS, KM2N or a fabricated REI F05 ionization history.

## Reproduction

Install Python>=3.12, numpy and scipy. Matplotlib is only needed for figures. Run from this directory:

python sachs_f08.py --source source --output results --order 48
OPENBLAS_NUM_THREADS=1 python -m unittest -v test_sachs_f08
OPENBLAS_NUM_THREADS=1 python -O -m unittest -q test_sachs_f08
python make_plots.py

Or use bash REPRODUCE.sh, which recomputes into a separate replay directory and verifies row identity numerically without mutating the original published data.

## Real science and limits

10,752 source-owned original F08 rays (4 relative-z shells × (128+512+2048) rays), 7 newly calculated optical/brightness columns and 12 group physical summary records. Uses same original S0 electron histories, positive H_i and observer-normal clock; has zero new Einstein, H+He, or radiation IVPs. All source-conditional and finite-grid. REI F08 scientific admission HOLD and original 26-event F05 first canonical interval BLOCKED. No new central DAG nodes.
