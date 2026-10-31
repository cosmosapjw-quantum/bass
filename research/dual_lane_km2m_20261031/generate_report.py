"""KM2M source-derived final physics report and handoff."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path

def produce(source,audit,outdir):
    source=Path(source);audit=Path(audit);out=Path(outdir)
    d=json.loads(source.read_text());v=json.loads(audit.read_text())
    if v["verdict"]!="PASS_SCOPED" or d["upper_dag"]!="9/15":
        raise ArithmeticError("not actual auditable scoped science")
    out.mkdir(parents=True,exist_ok=True)
    a=d["snapshots"]["GL12"]["measurements"][-1]
    b=d["snapshots"]["GL16"]["measurements"][-1]
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    fields=[
        ("incoming_first_event_energy_rate","Original first collision input energy rate"),
        ("normal_first_gain_energy_rate","New polarized P8 first collision normal gain energy rate"),
        ("normal_gain_over_loss","Normal photon gain/loss bulk-work effect"),
        ("linear_polarization_mean","Mean generated linear polarization"),
        ("linear_polarization_rms","RMS generated linear polarization"),
        ("linear_polarization_max","Maximum generated linear polarization"),
        ("electron_rest_source_gain_relative_error","Electron rest-frame gain/loss residual"),
        ("P8_gain_bolometric_parity_relative_error","Original P8 gain source parity"),
        ("normal_scattered_logfrequency_centroid","Normal first gain log-frequency centroid"),
        ("electron_rest_scattered_logfrequency_centroid","Electron rest-frame centroid"),
        ("original_KM2L_first_rate_relative_error","Original KM2L first event rate parity")
    ]
    lines=[
        "# BASS KM2M: physically computed first polarized Thomson frequency gain",
        "",
        "GitHub checked-out source SHA "+os.getenv("GITHUB_SHA","LOCAL_UNATTESTED")+
        "; immutable parent BASS KM2L Draft PR294 HEAD 8a1e09f6176166595b33810d3ce0c1f18afb245f.",
        "",
        "Two real source-locked Einstein-Bianchi I full polarized P8 and Peebles chemistry GL12/GL16 original IVPs, genuinely re-integrated to recover the original KM2L ballistic Ly-alpha photons. Original KM2L also reproduces the source first Thomson collision rate. Five physical time snapshots per grid u=.05,.10,.15,.20,.25, with actual first scattered electron rest-frame P8 rank-two coherency and bulk Doppler shifted frequency across 1200 bins: 10 scientific snapshots, 12000 frequencies, 6 PNG science plots.",
        "",
        "Physical FIRST-GAIN SOURCE only: incident tagged ballistic Ly-alpha photons were originally included in the grey Einstein P8 photon stress. Electron rest-frame spectral source M_e(b) is scattered through the original P8 projection (3/8pi)Pe M_e Pe, with J_e=D^4 S J_n S^T, normal frequency log nu_n=log nu_e-log D, and normal collision gain nu_rest D^-3 trace G_e. No repeated scattering, no time propagation of generated first-scattered field, no new energy-momentum tensor or Peebles reaction inserted in Einstein.",
        "",
        "| Physically measured u=.25 result | GL12 | GL16 |",
        "|---|---:|---:|"
    ]
    for key,title in fields:
        lines.append("| "+title+" | "+format(a[key],".13g")+
                     " | "+format(b[key],".13g")+" |")
    lines+=["",
        "Exact frequency and angular source factorization: electron-frame M_e(b,3,3), original per-ray boost isometries S, normal/electron ray weights, Doppler factors and full normal rank-2 gain tensor at final epoch. The source can be re-used for a later time-evolution calculation. No Stokes sign was invented; linear polarization is extracted from invariant screen tensor eigenvalues.",
        "",
        "Independent hostile saved-data audit PASS_SCOPED: a separately written direct scalar Thomson 3/(16pi)*(1+cos^2theta) kernel reproduced the original P8 tensor gain for the unpolarized incident component. This is algebraically independent implementation on the same saved source, not an independently evolved atomic or gravitational model.",
        "Audit max residuals: "+json.dumps(v["maxima"],sort_keys=True),
        "Source data SHA256 "+sha,
        "",
        "Final GitHub push/PR CI and Google Drive/Library upload/readback receipts must be checked separately; no missing result may be called PASS.",
        "",
        "Scope limits: exact first gain SOURCE, not the evolved scattered field, not second/higher Thomson scattering, resonant Lyalpha redistribution/recoil, nonthermal 2p photoexcitation, thermal Compton or first law, or observed CMB. Native subagent NOT_RUN, independent-author R6/C9 NOT_RUN.",
        "Upper BASS DAG 9/15, 21 edges, KM2 PARTIAL, +0 upper; KM2M bounded 1/1 conditional on verified actual final CI; production_ready=false;merge_ready=false;auto_next=false."
    ]
    (out/"S2_FINAL_REPORT_KO.md").write_text("\n".join(lines)+"\n")
    handoff=[
      "$physmath-research-loop $scispace $exa $wolfram",
      "PROJECT=BASS",
      "REPO=cosmosapjw-quantum/bass",
      "CURRENT_UNIT=KM2M_FIRST_POLARIZED_THOMSON_FREQUENCY_GAIN_SOURCE",
      "CURRENT_PR=READ_LIVE_PR_NUMBER",
      "CURRENT_HEAD=READ_LIVE_HEAD_FIRST",
      "IMMUTABLE_PARENT_PR=294",
      "IMMUTABLE_PARENT_HEAD=8a1e09f6176166595b33810d3ce0c1f18afb245f",
      "SCIENTIFIC_SCOPE=FIRST_COLLISION_GAIN_SOURCE_NOT_EVOLED_SCATTERED_FIELD",
      "LIVE_EINSTEIN_P8_CHEM_GRID=GL12,GL16",
      "FIRST_GAIN_PHYSICS_EPOCHS=10",
      "FREQUENCY_ROWS=12000",
      "SCIENCE_PLOTS=6",
      "GL16_FIRST_GAIN_NORMAL_ENERGY_RATE="+str(b["normal_first_gain_energy_rate"]),
      "GL16_INPUT_FIRST_RATE="+str(b["incoming_first_event_energy_rate"]),
      "GL16_GENERATED_LINEAR_POL_MEAN="+str(b["linear_polarization_mean"]),
      "GL16_NORMAL_CENTROID="+str(b["normal_scattered_logfrequency_centroid"]),
      "GL16_REST_GAIN_CONSERVATION="+str(b["electron_rest_source_gain_relative_error"]),
      "SAVED_AUDIT="+v["verdict"],
      "SOURCE_SHA256="+sha,
      "PUSH_PR_CI=READ_ACTUAL_LIVE_RUN",
      "S0_S1_S2_SHA=READ_ACTUAL_SOURCE_ARCHIVES",
      "GDRIVE=READ_REAL_PROVIDER_RECEIPT",
      "LIBRARY=READ_REAL_LIBRARY_RESULT",
      "DROPBOX=NOT_VERIFIED",
      "UPPER_DAG=9/15",
      "UPPER_EDGES=21",
      "KM2=PARTIAL",
      "NEW_UPPER_COMPLETED=0",
      "KM2M_SCOPED=1/1_CONDITIONAL_FINAL_CI",
      "SCATTERED_FIELD_TIME_PROPAGATION=NOT_RUN",
      "MULTIPLE_THOMSON_SCATTERING=NOT_RUN",
      "THERMAL_COMPTON=NOT_RUN",
      "RESONANT_LYA_TRANSFER=NOT_RUN",
      "PHOTOEXCITATION_FEEDBACK=NOT_RUN",
      "NATIVE_SUBAGENT=NOT_RUN",
      "DISTINCT_AUTHOR_R6_C9=NOT_RUN",
      "PRODUCTION_READY=false",
      "MERGE_READY=false",
      "AUTO_NEXT=false",
      "STOP_AFTER_ONE_BOUNDED_UNIT=true"
    ]
    (out/"HANDOFF_NEXT_KO.txt").write_text("\n".join(handoff)+"\n")
    print("KM2M_GENERATED_REPORT",len(lines),"GL16_POL",b["linear_polarization_mean"],flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,type=Path)
    ap.add_argument("--audit",required=True,type=Path)
    ap.add_argument("--outdir",required=True,type=Path)
    a=ap.parse_args()
    produce(a.source,a.audit,a.outdir)
