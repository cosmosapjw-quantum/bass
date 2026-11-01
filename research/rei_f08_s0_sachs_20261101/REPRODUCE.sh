#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python sachs_f08.py --source source --output replay --order 48
python -m unittest -q test_sachs_f08
python -O -m unittest -q test_sachs_f08
python - <<'PY'
import csv,gzip,json,math
from pathlib import Path
for name in ("BASS_REI_F08_S0_SOURCE_MATCHED_SACHS_OBSERVABLES.csv.gz",):
 with gzip.open(Path("results")/name,"rt") as a, gzip.open(Path("replay")/name,"rt") as b:
  old=list(csv.DictReader(a));new=list(csv.DictReader(b))
 assert len(old)==len(new)==10752
 for i,(x,y) in enumerate(zip(old,new)):
  assert x.keys()==y.keys()
  for k in x:
   if k in ("window_fraction","angular_nmu","angular_nphi","mu_bin","phi_bin"):assert x[k]==y[k]
   else:
    u=float(x[k]);v=float(y[k]);assert math.isclose(u,v,rel_tol=2e-12,abs_tol=1e-20),(i,k,u,v)
for a,b in (("results/BASS_REI_F08_S0_MATCHED_SACHS_RESULT.json","replay/BASS_REI_F08_S0_MATCHED_SACHS_RESULT.json"),):
 o=json.load(open(a));p=json.load(open(b));assert o["source_pair_id"]==p["source_pair_id"] and o["num_physical_ray_rows"]==p["num_physical_ray_rows"]==10752
print("BASS_REI_S0_CLEAN_PHYSICS_REPLAY_PASS_10752")
PY
python make_plots.py
