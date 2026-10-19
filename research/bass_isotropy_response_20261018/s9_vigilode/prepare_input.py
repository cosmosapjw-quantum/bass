#!/usr/bin/env python3
"""Extract an already-completed S8 primal reference and static quadrature inputs.

No differential equation is solved. The stored event b(u) is deliberately absent
from every solver input. Only the reference comparator retains trajectory values.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
LANE=HERE.parent
sys.path.insert(0,str(LANE))
import numpy as np
import coupled_cohorts as cc

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
    path=HERE/name; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n")

def main():
    prereg_path=LANE/"evidence_s8_tangent/PREREGISTRATION.json"
    reference_path=LANE/"evidence_s8_tangent/run01/ANALYTIC_TANGENT.json"
    prereg=json.loads(prereg_path.read_text())
    old=json.loads(reference_path.read_text())
    for path,expected in prereg["frozen_S7_source_sha256"].items():
        if sha(LANE/path)!=expected: raise ValueError("FROZEN_S7_SOURCE_MISMATCH: "+path)
    c=cc.Config(**prereg["primary"]["config"]); c.validate()
    stock=cc.initial_bank(c)
    digests=stock.birth_digests
    if digests!=old["old_stock_digests"]: raise ValueError("S8_OLD_STOCK_DIGEST_MISMATCH")
    mu,w=np.polynomial.legendre.leggauss(c.n)
    # This matches the coordinate prior used by the original lrs_rule. No
    # angular refinement or source-frame grid substitution is introduced.
    # Keep the original unnormalized leggauss weights, as lrs_rule does before
    # applying its Jacobian and single normalization. Scaling first could change
    # binary64 birth admission at a precision boundary.
    provenance={"operation":"Static extraction only; no S8 or S9 ODE execution",
        "S8_reference_path":str(reference_path.relative_to(LANE)),"S8_reference_sha256":sha(reference_path),
        "S8_prereg_sha256":sha(prereg_path),"reference_method":prereg["solver"],
        "S8_source_commit":"4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613",
        "S8_resume_source_commit":"2e6b4a150559b0bea52938896a901f6d438f3582",
        "fixed_S7_sources":prereg["frozen_S7_source_sha256"],
        "numpy_version":np.__version__,"old_stock_digests":digests,
        "birth_b_from_reference_in_solver_input":False,"angular_refinement":False,
        "spectral_owner":"0e25846433170d0f420c4cda44a0bedbf02cd177"}
    config={key:getattr(c,key) for key in ["n","b0","y0","donor0","old_isotropic",
        "old_anisotropic","cosmological_constant","decay_lambda","birth_end","x_end"]}
    config["k"]=c.K
    cohorts=[{"u":a.u,"b_birth":a.b_birth,"energy_birth":a.energy_birth,
        "mu":a.mu.tolist(),"alpha":a.alpha.tolist(),"role":a.role} for a in stock.cohorts]
    rows=[a["primal"] for a in old["trajectory"]]
    base={"schema":"BASS_S9_INPUT_V1","config":config,
        "coordinate_grid":{"mu0":mu.tolist(),"prior0":w.tolist()},
        "initial_cohorts":cohorts,"expected_old_digests":digests,
        "output_times":[a["x"] for a in rows],"provenance":provenance,
        "solver":{"arm":"mf_into_ls","rtol":1e-10,"atol":1e-12,"initial_step":1e-3,
                  "max_step":0.04,"max_attempts":100000,"linear_rtol":1e-13,"linear_atol":1e-15}}
    save("inputs/base.json",base)
    save("reference/S8_PRIMAL.json",{"schema":"BASS_S9_REUSED_S8_PRIMAL_V1","provenance":provenance,
         "rows":rows,"S8_primal_diagnostics":old["primal_diagnostics"]})
    save("INPUT_PROVENANCE.json",provenance)
    print(json.dumps({"operation":"static extraction","reference_rows":len(rows),"births":c.K,
          "old_stock_digests":digests,"input_sha256":sha(HERE/"inputs/base.json"),
          "reference_sha256":sha(HERE/"reference/S8_PRIMAL.json")}))

if __name__=="__main__": main()
