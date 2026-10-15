"""Produce versioned, source-bound geometry-only input for real rei_microphysics.

This is never an implicit switch for AX08 checkpoint/Grackle native chemistry.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
from source_table import BackgroundTable,EXPECTED_CASE_NAMES,AREF,AEND,XRANGE,H0,OM,OR,OL,sha256

HEADER=("case","x","a","b","time_s","h_flrw_per_s","h_per_s","s_per_s",
        "sigma_signed","Sigma","h_perp_per_s","h_parallel_per_s")

def export(manifest:Path,source_csv:Path,outdir:Path):
    outdir=Path(outdir)
    if outdir.exists(): raise FileExistsError(outdir)
    source=BackgroundTable(manifest,source_csv)
    outdir.mkdir(parents=True)
    target=outdir/"NATIVE_GEOMETRY.csv"
    errmax={"s_over_h":0.,"b":0.,"H":0.,"proper_time":0.}
    with target.open("w",newline="") as stream:
        wr=csv.DictWriter(stream,fieldnames=HEADER,lineterminator="\n")
        wr.writeheader()
        for case in EXPECTED_CASE_NAMES:
            nodes,_,_=source.samples[case]
            for node in nodes:
                p=source.point_at_x(case,node.x)
                native=p.as_native_background_point()
                wr.writerow({"case":case,"x":p.x,"a":p.a,"b":native["b"],
                    "time_s":native["time_s"],"h_flrw_per_s":native["h_flrw_per_s"],
                    "h_per_s":native["h_per_s"],"s_per_s":native["s_per_s"],
                    "sigma_signed":native["sigma"],"Sigma":p.Sigma,
                    "h_perp_per_s":p.H_perp_per_s,
                    "h_parallel_per_s":p.H_parallel_per_s})
                errmax["s_over_h"]=max(errmax["s_over_h"],abs(p.sigma_signed-node.s/node.h))
                errmax["b"]=max(errmax["b"],abs(p.b-node.b))
                errmax["H"]=max(errmax["H"],abs(p.h_per_s/node.h-1))
                errmax["proper_time"]=max(errmax["proper_time"],abs(p.time_s-node.time_s)/max(node.time_s,1.))
    schema={"schema":"bass.rei.pr165.native_geometry_only.v1",
       "parent_bass_commit":"3c39bbbf46b6663e7c40277e194fd0ef48118472",
       "parent_source_csv_sha256":source.source_sha256,
       "parent_source_receipt_sha256":source.manifest_sha256,
       "geometry_csv_sha256":sha256(target),
       "geometry_columns":HEADER,"rows":sum(len(t[0]) for t in source.samples.values()),
       "cases":list(EXPECTED_CASE_NAMES),
       "params":{"H0_per_s":H0,"Omega_m":OM,"Omega_r":OR,"Omega_lambda":OL,
                 "a_ref":AREF,"a_end":AEND,"x_end":XRANGE},
       "native_type":"rei_microphysics::axbi_background::BackgroundPoint",
       "semantics":{"sigma":"signed s/H", "Sigma":"sqrt(3) abs(s)/H",
          "h_flrw_per_s":"cold-FLRW reference ONLY, not kinetic mean H",
          "time_s":"new positive integral dx/H using Hermite log H; does not read old AX08 restart clock",
          "source_import":"geometry-only opt-in; chemistry source and checkpoint remain unchanged"},
       "max_input_knots_differences":errmax,
       "max_producer_integrated_clock_relative":source.producer_clock_max_rel,
       "native_cargo_build":"NOT_RUN_IN_CHATGPT_SESSION",
       "native_HHe_driver_activated":False,"full_EoR_science":"NOT_ADMITTED"}
    (outdir/"NATIVE_GEOMETRY_RECEIPT.json").write_text(json.dumps(schema,indent=2,ensure_ascii=False)+"\n")
    return schema

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-csv",type=Path,required=True)
    parser.add_argument("--source-receipt",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    result=export(a.source_receipt,a.source_csv,a.out)
    print(json.dumps({"rows":result["rows"],"sha":result["geometry_csv_sha256"],
                      "max_source_knot_mismatch":result["max_input_knots_differences"]},indent=2))
