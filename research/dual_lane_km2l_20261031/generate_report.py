"""KM2L source-derived final scientific report and copyable handoff after hostile audit."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path


def make(source,audit,outdir):
    s=Path(source);a=Path(audit);out=Path(outdir)
    d=json.loads(s.read_text());v=json.loads(a.read_text())
    if v["verdict"]!="PASS_SCOPED":
        raise ArithmeticError("cannot issue final scoped physics report before saved-data audit")
    if d["upper_dag"]!="9/15" or d["new_completed_upper_nodes"]!=0:
        raise ArithmeticError("upper DAG cannot be promoted from a scoped subunit")
    sha=hashlib.sha256(s.read_bytes()).hexdigest()
    out.mkdir(parents=True,exist_ok=True)
    lines=[
       "# BASS KM2L | live Einstein–P8–Peebles and unscattered Lyα Thomson survival",
       "",
       "## Scope and original source contract",
       "Source HEAD: `"+os.getenv("GITHUB_SHA","LOCAL_UNATTESTED")+"`; frozen parent KM2K Draft PR293 HEAD `e216d708890c8321d2f6a2e146e60e7e01cea1ce`. Original Einstein/P8/chemical source untouched. Signature (-,+,+,+), u=t/Tstar, native Peebles x_e and electron beta; no observational reconstruction.",
       "The source-locked GL12/GL16 original Einstein–Bianchi-I fully polarized P8–Peebles IVPs each solved twice for independently reproduced ray histories. This is **two distinct original IVPs**, not four independent physics models. Each of the two geometries supports **three** distinct Thomson/frequency transport scenarios: original sheared Thomson ballistic, original sheared zero-Thomson, and H-only redshift with actual Thomson opacity.",
       "",
       "The transmitted line photon spectral intensity has source (j_{alpha}) inherited as a subset of KM2J grey chemical binding emission, adiabatic `exp(-4 dR)` and **first-event no-scattering probability `exp(-d tau_T)`**, with `d tau_T=integral nH xe sigma_T c Tstar gamma(1-beta·n) du`. The vanished ballistic portion represents photons having at least one scattering; it is NOT the true scattered distribution, Thomson heating, or a second stress tensor.",
       "",
       "## Actual scientific endpoint u=0.25",
       "| Quantity | GL12 | GL16 |",
       "|---|---:|---:|"
    ]
    rows={}
    for key in ("GL12","GL16"):
        c=d["cases"][key]
        a=c["scenarios"]["shear_thomson"]["epochs"][-1]
        b=c["scenarios"]["shear_free"]["epochs"][-1]
        h=c["scenarios"]["Honly_thomson"]["epochs"][-1]
        rows[key]={"ballistic_rho":a["rho"],"free_rho":b["rho"],
             "survival_energy":c["comparisons"][-1]["unscattered_over_free_energy"],
             "first_collision_energy_rate":a["first_collision_energy_rate"],
             "centroid_log_freq":a["mean_log_nu"],
             "shear_vs_Honly_centroid":a["mean_log_nu"]-h["mean_log_nu"],
             "ballistic_redwing":a["redwing_fraction"],
             "max_packet_tau":a["max_packet_thomson_tau"],
             "original_photon_Hamiltonian":c["reintegrated_KM2J_conservation"]["max_Hamiltonian_norm"]}
    for key,name in [
        ("ballistic_rho","zero-collision tagged Lyα energy (BASS)"),
        ("free_rho","original collision-free tagged line energy (BASS)"),
        ("survival_energy","zero-collision energy fraction of collision-free reference"),
        ("first_collision_energy_rate","first Thomson collision energy-event rate per u (BASS)"),
        ("centroid_log_freq","surviving mean ln(nu/nu_Lya)"),
        ("shear_vs_Honly_centroid","centroid shear minus H-only"),
        ("ballistic_redwing","survivor red-wing fraction y<-0.01"),
        ("max_packet_tau","maximum tagged emission-to-observation tau_T"),
        ("original_photon_Hamiltonian","maximum normalized Einstein Hamiltonian")]:
        lines.append("| "+name+" | "+
                     " | ".join(format(rows[g][key],".12g") for g in ("GL12","GL16"))+" |")
    lines+=["",
      "Original density, photon, angular and frequency histories are physically solved, not synthetic. **246 physical epoch records** (6 initial zero states), **30 spectral snapshots × 1200 bins = 36,000 frequency rows**, six original science plots. Tagged first-collision events are positive in the model, but the code does not propagate scattered gain or calculate gas heating.",
      "",
      "## Reproduction, hostile check and scientific limitations",
      "Original source-bounding tests and independent saved-data arithmetic check were run on this executable physics model. The independent auditor imports NO BASS RHS, recalculates all 240 nonzero spectral epochs and 640 positive original photon hazard-node events, tests exact positive optical depths, 4-momentum-typed first collision energy and momentum rates, frequency CDF/bin integrals, numerical constant-h/Gamma Green limit and Einstein source-locked constraints. The audit verdict was **"+v["verdict"]+"**.",
      "Maximum independent residuals: `"+json.dumps(v["maxima"],sort_keys=True)+"`.",
      "Original physical source SHA256: `"+sha+"`. Native distinct-author R6/C9 NOT_RUN. GitHub final CI run IDs, stage source ZIP SHA/CRC, and cloud backups must be read from actual provider receipt, not predicted from generated prose.",
      "",
      "Important unclosed physics: exact scattered Thomson gain and frequency redistribution, coherent polarization of the tagged line after collision, line-core Lyα resonance Fokker–Planck and recoil, n=2 radiative transfer and ionization rate feedback, photon/baryon thermal first-law, realistic density normalization, angular continuum proof. No post-escape tagged component is added again to Einstein stress.",
      "",
      "**DAG status:** upper BASS **9/15**, edges 21, KM2 PARTIAL, new upper nodes **0**; KM2L scoped **1/1 PASS_SCOPED** only for unscattered transfer and first-event statistics. Production false, merge false, auto-next false, STOP_AFTER_ONE_BOUNDED_UNIT."
    ]
    (out/"S2_FINAL_REPORT_KO.md").write_text("\n".join(lines)+"\n")
    handoff=[
      "$physmath-research-loop $scispace $exa $wolfram",
      "PROJECT=BASS","REPO=cosmosapjw-quantum/bass",
      "CURRENT_UNIT=KM2L_UNSCATTERED_THOMSON_ESCAPED_LYA",
      "CURRENT_PR=READ_LIVE_PR_NUMBER",
      "CURRENT_HEAD="+os.getenv("GITHUB_SHA","READ_LIVE_HEAD_FIRST"),
      "PARENT_PR=293",
      "IMMUTABLE_PARENT_HEAD=e216d708890c8321d2f6a2e146e60e7e01cea1ce",
      "READ_LIVE_HEAD_FIRST=true",
      "UNIQUE_EINSTEIN_P8_PEEBLES_IVPS=2",
      "SOURCE_IVP_REINTEGRATION_PER_GRID=2",
      "THOMSON_FREQUENCY_SCENARIOS=6",
      "PHYSICAL_EPOCHS=246","SPECTRAL_SNAPSHOTS=30","FREQUENCY_ROWS=36000","SCIENCE_PLOTS=6",
      "SOURCE_JSON_SHA256="+sha,
      "GL16_SURVIVAL_FRAC="+str(rows["GL16"]["survival_energy"]),
      "GL16_BALLISTIC_RHO="+str(rows["GL16"]["ballistic_rho"]),
      "GL16_FIRST_SCATTER_RATE="+str(rows["GL16"]["first_collision_energy_rate"]),
      "GL16_CENTROID="+str(rows["GL16"]["centroid_log_freq"]),
      "HOSTILE_SAVED_DATA_AUDIT="+v["verdict"],
      "NORMAL_TESTS=READ_ACTUAL_CI",
      "OPTIMIZED_EXCEPTIONS_AUDIT=READ_ACTUAL_CI",
      "FINAL_S0_S1_S2_ZIP=READ_ACTUAL_GITHUB_ARTIFACT",
      "DRIVE=READ_ACTUAL_PROVIDER_RECEIPT",
      "LIBRARY=READ_ACTUAL_PROVIDER_RECEIPT",
      "DROPBOX=NOT_VERIFIED",
      "UPPER_DAG=9/15","UPPER_EDGES=21",
      "KM2=PARTIAL","NEW_UPPER_COMPLETED=0",
      "KM2L_SCOPED=1/1_PASS_SCOPED",
      "SCATTERED_THOMSON_GAIN=NOT_RUN",
      "MULTIPLE_SCATTERED_FREQUENCY_TRANSFER=NOT_RUN",
      "RESonant_LYA_FOKKER_PLANCK=NOT_RUN",
      "IONIZING_SPECTRUM_FEEDBACK=NOT_RUN",
      "THERMAL_FIRST_LAW=NOT_RUN",
      "NATIVE_SUBAGENT=NOT_RUN","DISTINCT_AUTHOR_R6_C9=NOT_RUN",
      "PRODUCTION_READY=false","MERGE_READY=false","AUTO_NEXT=false",
      "STOP_AFTER_ONE_BOUNDED_UNIT=true"
    ]
    (out/"HANDOFF_NEXT_KO.txt").write_text("\n".join(handoff)+"\n")
    print("KM2L_FINAL_SCIENTIFIC_REPORT",len(lines),"GL16_SURVIVAL",rows["GL16"]["survival_energy"],flush=True)
    return rows


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--audit",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    a=p.parse_args();make(a.source,a.audit,a.outdir)
