"""Source-locked fixed-mean-scale vs fixed-SI-proper-time background clock shift.

This is background-only geometry, not an ionization fraction difference.
Do not re-label the compared estimands as observed redshift shifts.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
from shortstep import HermiteClock
from axbi_provider import Background,Family

def analyze(n=501):
    zero=Background(Family(0.))
    tables={q:Background(Family(q)) for q in [0.,.005,-.005,.01,-.01]}
    ref=tables[0.].table(n)
    x=ref["ln_a_over_aref"]
    result=[]
    for q in (.005,-.005,.01,-.01):
        bg=tables[q]
        cur=bg.at_x(x)
        dt=cur["proper_elapsed_s"]-ref["proper_elapsed_s"]
        # Same proper t sampled only where it lies in BOTH source domains.
        source_time=ref["proper_elapsed_s"]
        matched_time=source_time<=bg.at_a(bg.aend)["proper_elapsed_s"]
        matched_time[0]=True
        new_x=np.full(len(x),np.nan)
        for i in np.flatnonzero(matched_time):
            ref_t=float(source_time[i])
            new_x[i]=math.log(bg.at_time(ref_t)["a"]/bg.aref)
        dx_at_fixed_t=new_x-x
        result.append({"q":q,"n_total":n,"n_valid_fixed_t":int(matched_time.sum()),
           "max_abs_delta_time_at_same_a_s":float(np.max(np.abs(dt))),
           "end_delta_time_same_a_s":float(dt[-1]),
           "max_abs_delta_ln_a_at_fixed_time":float(np.nanmax(abs(dx_at_fixed_t))),
           "delta_time_profile_s":dt.tolist(),
           "delta_ln_a_at_fixed_time_profile":[float(v) if np.isfinite(v) else None for v in dx_at_fixed_t]})
    return {"schema":"bass.rei.axbi.fixed_a_vs_fixed_t_geometry_only.v1",
      "reference_q":0.,"n":n,
      "selected_stage":"C8 matched-science background clock diagnostics",
      "negative_q_parity":"clock drift even in q for density-fixed family",
      "redshift_chart":"zbar=1/a-1, not directly observed photon redshift",
      "actual_ionizing_HII_or_Tgas_comparison":None,
      "rows":result}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    j=analyze()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(j,indent=2)+"\n")
    for q in j["rows"]:
        print(q["q"],q["end_delta_time_same_a_s"],q["max_abs_delta_ln_a_at_fixed_time"],q["n_valid_fixed_t"])
