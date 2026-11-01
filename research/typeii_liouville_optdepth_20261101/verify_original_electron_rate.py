#!/usr/bin/env python3
"""Independent original BASS electron-frame Doppler source crosscheck on all 10426 evolved photons."""
import csv
import json
import subprocess
from pathlib import Path

import numpy as np
from bianchi.q.electron import transform_photon

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ORIGINAL_MAIN="9c6506e4e2087129a8b674ff10438e5db1a55c9d"

def git(*parts):
    return subprocess.check_output(["git","-C",str(ROOT),*parts],text=True).strip()

for source in (
    "bianchi/q/electron_rate.py",
    "bianchi/q/electron.py",
    "bianchi/q/boost.py",
    "compiler/validation/typeii_fixture_canonical.json",
):
    if git("hash-object",source)!=git("rev-parse",f"{ORIGINAL_MAIN}:{source}"):
        raise RuntimeError(f"IMMUTABLE_OWNER_SOURCE_DRIFT: {source}")

doc=json.loads((ROOT/"compiler/validation/typeii_fixture_canonical.json").read_text())
states=np.asarray([x["state"] for x in doc["trajectory"]["samples"]],float)
if len(states)!=401 or states[0,4]!=0.05:raise RuntimeError("BAD_CANONICAL_FIXTURE")
with (HERE/"PHOTON_RAYS_401X26.csv").open(newline="") as f:
    reader=csv.DictReader(f)
    rows=list(reader)
if len(rows)!=401*26:raise RuntimeError("EXPECTED_10426_PHOTON_ROWS")
dirs=np.asarray([[float(r[k]) for k in ("n_x","n_y","n_z")] for r in rows],float)
dirs=dirs.reshape(26,401,3)
zero=np.zeros(3,float)
max_gap=0.0;min_d=10.0;max_d=0.0;max_q_only_defect=0.0
max_gammas=0.0
for i,x in enumerate(states):
    v=float(x[4])
    beta=np.array([0.0,v,0.0],float)
    n=dirs[:,i,:]
    energies,rest_dirs,doppler=transform_photon(1.0,n,zero,beta)
    gamma=1.0/np.sqrt(1.0-v*v)
    q=1.0-v*n[:,1]
    expected=gamma*q
    if not np.all(np.isfinite(rest_dirs)) or np.max(abs(np.linalg.norm(rest_dirs,axis=1)-1))>1e-11:
        raise RuntimeError("OWNER_TRANSFORM_INVALID_DIRECTION")
    if np.max(abs(energies-doppler))>1e-15:
        raise RuntimeError("OWNER_OUTPUT_ENERGY_INCONSISTENT")
    max_gap=max(max_gap,float(np.max(abs(doppler-expected))))
    max_q_only_defect=max(max_q_only_defect,float(np.max(abs(doppler-q))))
    min_d=min(min_d,float(np.min(doppler)))
    max_d=max(max_d,float(np.max(doppler)))
    max_gammas=max(max_gammas,float(gamma-1))
if max_gap>3e-14 or max_q_only_defect<5e-4:
    raise AssertionError(f"OWNER_NORMAL_FRAME_MISMATCH {max_gap} {max_q_only_defect}")
out={
    "schema":"bass.typeii.owner_electron_frame_doppler_validation.v1",
    "original_main":ORIGINAL_MAIN,
    "immutable_original_source_blobs_checked":4,
    "states":401,
    "rays":26,
    "owner_electron_transform_evaluations":10426,
    "maximum_source_D_minus_analytic_Gamma_q":max_gap,
    "minimum_owner_D":min_d,
    "maximum_owner_D":max_d,
    "maximum_Gamma_minus_1":max_gammas,
    "negative_q_only_missing_gamma_gap":max_q_only_defect,
    "owner_provenance":"bianchi.q.electron.transform_photon original main byte-matched",
    "optional_jax_photon_rhs_oracle":"NOT_RUN: optional JAX unavailable; original Rust Liouville source and JAX-free physics equations were independently evaluated",
    "verdict":"SOURCE_OWNER_FRAME_PARITY_PASS; RECOMBINATION_AND_PRODUCTION_NOT_ESTABLISHED",
}
(HERE/"ELECTRON_OWNER_PARITY.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
