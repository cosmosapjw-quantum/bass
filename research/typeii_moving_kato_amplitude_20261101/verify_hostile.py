#!/usr/bin/env python3
"""Source-bound hostile finite-grid negative cases. Deliberately same-author, no independent reviewer."""
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def git(*args): return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
source="generated/rust/typeii/typeii_collision.rs"
if git("hash-object",source)!=git("rev-parse","9c6506e4e2087129a8b674ff10438e5db1a55c9d:"+source):
    raise RuntimeError("DRIFT")
spec=importlib.util.spec_from_file_location("original_source",ROOT/"research/typeii_aem2_compare_20261101/source/replay_from_original_fixture.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixture=json.loads((ROOT/"compiler/validation/typeii_fixture_canonical.json").read_text())
x=fixture["trajectory"]["samples"][0]
v=x["state"][4]
vp=x["rhs"][4]
out={"v":v,"vprime":vp,"cases":{},"verdict":"EXPECTED_NEGATIVE_CASES_CONFIRMED"}
for name in ("axis6","lebedev26"):
    e,w=m.grid(name)
    C,P,n,wn,r,a=m.cp(e,w,v,"paired")
    dPpaired=m.pv(e,w,v,"paired")
    dPwrong=m.pv(n,wn,v,"fixed")
    delta=float(np.max(abs(dPpaired-dPwrong)))
    K=vp*(dPpaired@P-P@dPpaired)
    lam=4*v*vp/(1-v*v)
    H=K+lam*P
    i,j=np.indices(H.shape)
    minoff=float(np.min(H[i!=j]))
    Cr=float(np.max(abs(C@r)))
    aC=float(np.max(abs(a@C)))
    if delta < 0.1 or minoff >= -1e-5 or Cr>1e-12 or aC>1e-12:
        raise AssertionError(f"Hostile control did not reject wrong claim: {name}: {delta=} {minoff=} {Cr=} {aC=}")
    out["cases"][name]={"pair_vs_fixed_projector_derivative_max_gap":delta,
                         "min_offdiagonal_H":minoff,
                         "original_Cr":Cr,"original_aC":aC}
(HERE/"HOSTILE_NEGATIVE_RESULTS.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
