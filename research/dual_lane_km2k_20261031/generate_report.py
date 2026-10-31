"""Make exact measured physics and resume handoff from current run artifacts."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path


def make(src,audit,outdir):
    p=Path(src);q=Path(audit);out=Path(outdir)
    d=json.loads(p.read_text());a=json.loads(q.read_text())
    if a["verdict"]!="PASS_SCOPED":raise ArithmeticError("saved-data hostile audit not passed")
    out.mkdir(parents=True,exist_ok=True)
    gl12=d["data"]["GL12"];gl16=d["data"]["GL16"]
    rows=[]
    for key,c in (("GL12",gl12),("GL16",gl16)):
        r=c["scenarios"]["shear"]["epochs"][-1]
        h=c["scenarios"]["H_only"]["epochs"][-1]
        rows.append((key,c["parent_joint_ivp_nfev"],r["rho"],
                    r["mean_log_nu"],r["std_log_nu"],r["redwing_fraction"],
                    r["ratio_to_P8_rho"],r["quadrupole_frob"],
                    r["mean_log_nu"]-h["mean_log_nu"],
                    r["rho"]-h["rho"],
                    c["conservation"]["max_Hamiltonian_norm"]))
    sname="research/dual_lane_km2k_20261031/results/KM2K_ESCAPED_LYA_SPECTRA.json"
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    lines=[
        "# KM2K S2 | Real escaped Ly-alpha spectral characteristics on KM2J",
        "",
        "Actual source-locked coupled Einstein/P8/Peebles IVPs: 2 (GL12,GL16). Frequency-resolved tagged escaping Ly-alpha Green propagators: 4 (shear and H-only per grid).",
        "Two grids × two transport scenarios × 41 epochs = **164 actual spectral epochs**; 5 spectra per scenario = **20 actual spectral snapshots** of 1200 frequency bins each (24,000 frequency rows); six scientific plots.",
        "",
        "Model scope: optically free outgoing *already escaped* effective Ly-alpha photons (10.2/13.6 times Peebles line effective downward branching) are an **energy-tagged subset** of existing KM2J grey binding radiation. They are **not** added again to Einstein/P8 photon T_munu, and do **not** feed back on x_e. External HYREC Tm and synthetic baryon abundance retained. Fully resonant line transfer, atomic recoil, diffusion, 2p source, ionization feedback, thermal first law and observational CMB are not included.",
        "",
        "Current source checkout commit: `"+os.getenv("GITHUB_SHA","LOCAL_UNATTESTED")+"`",
        "GitHub CI stage tests + explicit source-saved arithmetic independent audit already passed before this generated artifact. Final workflow success and provider archive upload must be checked separately.",
        "",
        "| Grid | full joint IVP RHS calls | line rho | mean log(nu/nu_alpha) | sigma_log | red-wing P(log nu<-0.01) | line/P8 rho | ||Q||_F | centroid shear-H-only | rho shear-H-only | max Ham norm |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for e in rows:
        lines.append("| "+e[0]+" | "+str(e[1])+" | "+" | ".join(format(v,".12g") for v in e[2:])+" |")
    lines+=["",
        "Cross-grid actual final xe difference = "+str(d["cross_grid"]["xe_abs_diff"])+
        "; spectral centroid difference = "+str(d["cross_grid"]["line_centroid_abs_diff"])+".",
        "Saved-data adversarial audit max errors (not an independent atomic physics model): `"+
        json.dumps(a["maxima"],sort_keys=True)+"`.",
        "Read data `"+sname+"` SHA256 `"+digest+"`; source-owned raw packet NPZ GL12/GL16 and 20 histograms enable reconstructing 160 nonzero spectral epochs.",
        "",
        "S0 source, S1 physical data, S2 final audit+handoff bundles are built with SHA256+ZIP CRC; completed GitHub/Drive/Library readback must be independently established, not assumed.",
        "",
        "**DAG**: upper **9/15** (21 edges), KM2 PARTIAL, **0** new upper; KM2K scoped **1/1 PASS_SCOPED** for *escaped-line tagged transport only*. `production_ready=false;merge_ready=false;auto_next=false`. Native subagent NOT_RUN; distinct-author R6/C9 NOT_RUN. No further node automatically started.",
    ]
    (out/"S2_FINAL_REPORT_KO.md").write_text("\n".join(lines)+"\n")
    handoff=[
        "$physmath-research-loop $scispace $exa $wolfram",
        "PROJECT=BASS","REPO=cosmosapjw-quantum/bass",
        "CURRENT_UNIT=KM2K_ESCAPED_LYA_FREQUENCY_CHARACTERISTICS",
        "CURRENT_PR=READ_LIVE_PR_NUMBER",
        "CURRENT_HEAD="+os.getenv("GITHUB_SHA","READ_LIVE_HEAD_FIRST"),
        "PARENT_PR=291","IMMUTABLE_PARENT_HEAD=63147c01f1b1fd3f0cf698c919db25d9bd2ef80b",
        "READ_LIVE_HEAD_FIRST=true",
        "NEW_FULL_EINSTEIN_P8_PEEBLES_IVPS=2",
        "SPECTRAL_CHARACTERISTIC_TRANSPORTS=4",
        "SPECTRAL_EPOCHS=164","SPECTRAL_SNAPSHOTS=20","FREQUENCY_ROWS=24000","SCIENTIFIC_PLOTS=6",
        "KM2K_SCIENCE_JSON_SHA256="+digest,
        "GL16_LINE_RHO="+str(rows[1][2]),
        "GL16_CENTROID_LOG_NU="+str(rows[1][3]),
        "GL16_SHEAR_MINUS_HONLY_CENTROID="+str(rows[1][8]),
        "GL16_RED_WING_FRACTION="+str(rows[1][5]),
        "GL16_LINE_TO_P8_ENERGY="+str(rows[1][6]),
        "HOSTILE_SAVED_DATA_AUDIT="+a["verdict"],
        "S0_S1_S2_ARCHIVE=CHECK_FINAL_GITHUB_ACTIONS_ARTIFACT_IDS",
        "GDRIVE=CHECK_PROVIDER_READBACK",
        "LIBRARY=CHECK_LIBRARY",
        "DROPBOX=NOT_VERIFIED",
        "UPPER_DAG=9/15","UPPER_EDGES=21","KM2=PARTIAL","NEW_UPPER_COMPLETED=0",
        "KM2K_SCOPED=1/1_PASS_SCOPED",
        "LYA_RESONANCE_REDISPERSION=NOT_RUN",
        "LYA_PHOTOEXCITATION_CHEM_FEEDBACK=NOT_RUN",
        "THERMAL_FIRST_LAW=NOT_RUN",
        "NATIVE_SUBAGENT=NOT_RUN","DISTINCT_AUTHOR_R6_C9=NOT_RUN",
        "PRODUCTION_READY=false","MERGE_READY=false","AUTO_NEXT=false",
        "STOP_AFTER_ONE_BOUNDED_UNIT=true",
    ]
    (out/"HANDOFF_NEXT_KO.txt").write_text("\n".join(handoff)+"\n")
    print("KM2K_GENERATED_PHYSICS_REPORT",len(lines),"GL16_LINE_RHO",rows[1][2],flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--audit",type=Path,required=True)
    ap.add_argument("--outdir",type=Path,required=True)
    a=ap.parse_args();make(a.source,a.audit,a.outdir)
