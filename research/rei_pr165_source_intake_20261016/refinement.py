"""Physical matched-input geometry-clock Hermite interpolation refinement.

Original PR164 SciPy source is independently integrated; this is a ChatGPT-container
scoped grid study, not an NCP-native or HHe chemistry convergence experiment.
"""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"source_pr164"))
from export_rei_bridge import generate
from kinetic_tangent import EinsteinTangent
from source_table import BackgroundTable

SCENARIOS=("COLD_FLRW","MASSIVE_A_PLUS","MASS3_A_PLUS","SIGNED_MINUS")

def run(base:Path,grids=(61,121,241)):
    base=Path(base)
    if base.exists():raise FileExistsError(base)
    base.mkdir(parents=True)
    r=[]
    for count in grids:
        out=base/f"n{count:04}"
        meta=generate(out,n=count)
        model=BackgroundTable(out/"PRODUCER_RECEIPT.json",out/"PROPOSED_REI_BACKGROUND.csv")
        result={"nodes_per_case":count,"source_csv_sha256":meta["csv_sha256"],
                "clock_source_max_relative":model.producer_clock_max_rel,
                "cases":{}}
        for name in SCENARIOS:
            params=next(item["params"] for item in meta["cases_receipt"] if item["case"]==name)
            oracle=EinsteinTangent(**params)
            dense=oracle.solution(rtol=6e-13,atol=2e-14,n=101)
            _,segs,_=model.samples[name]
            errs={k:0. for k in ("b_abs","H_rel","s_over_href_abs","elapsed_time_rel","Sigma_abs")}
            for s in segs:
                x=(s.left.x+s.right.x)*.5
                p=model.point_at_x(name,x)
                bb,v,T=dense.sol(x)[:3]
                _,hh,_,_=oracle.field(x,float(bb),float(v))
                sphys=oracle.href*v
                errors={
                    "b_abs":abs(p.b-bb),
                    "H_rel":abs(p.h_per_s/hh-1),
                    "s_over_href_abs":abs(p.s_per_s-sphys)/oracle.href,
                    "elapsed_time_rel":abs(p.time_s-T/oracle.href)/(T/oracle.href),
                    "Sigma_abs":abs(p.Sigma-math.sqrt(3)*abs(sphys)/hh)}
                for key,value in errors.items():errs[key]=max(errs[key],float(value))
            result["cases"][name]=errs
        r.append(result)
    record={"schema":"bass.rei.pr165.geometry_refinement_ChatGPT_container.v1",
            "sampled_scenario_names":SCENARIOS,"node_counts":list(grids),
            "results":r,"source":"PR164 Python kinetic Einstein reference with tighter DOP853",
            "native_Rust":"NOT_RUN","native_HHe":"NOT_RUN"}
    (base/"REFINEMENT.json").write_text(json.dumps(record,indent=2)+"\n")
    return record

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args()
    r=run(a.out)
    for row in r["results"]:
        print("nodes",row["nodes_per_case"],"maxH",max(x["H_rel"] for x in row["cases"].values()),
            "maxclock",row["clock_source_max_relative"])
