"""Generate exact-source-measured KM2N report and copyable research handoff."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path


def make(source,audit,outdir):
    src=Path(source);au=Path(audit);out=Path(outdir)
    d=json.loads(src.read_text());a=json.loads(au.read_text())
    if a["verdict"]!="PASS_SCOPED" or d["upper_dag"]!="9/15" or set(d["cases"])!={"GL12","GL16"}:
        raise ArithmeticError("source-owned independent one-scattering audit not completed")
    out.mkdir(parents=True,exist_ok=True)
    cases=d["cases"]
    columns=[("rho_exactly_one","retarded exactly-one photon rho (BASS units)"),
        ("original_KM2L_ballistic_rho","source-owned zero Thomson collision rho (BASS units)"),
        ("new_once_scattered_to_ballistic_energy_ratio","exactly-one / zero-scatter energy ratio"),
        ("mean_linear_polarization","mean transported once-scattered linear polarization"),
        ("rms_linear_polarization","RMS transported polarization"),
        ("max_linear_polarization","maximum ray first-scattered polarization"),
        ("mean_logfreq","transported once-scattered mean ln(nu/nu_alpha)"),
        ("sigma_logfreq_bin","transported once-scattered width (bin-resolution)"),
        ("frequency_bolometric_relative_gap","spectral/bole energy relative residual")]
    lines=[
       "# KM2N | Retarded exactly-one Thomson scattered polarized Lyα radiation",
       "",
       "Immutable BASS parent KM2M Draft PR295 HEAD `2ff05b8416965af0adc7851a8aa60ec2e51b2fee`; current source GitHub HEAD `"+os.getenv("GITHUB_SHA","LOCAL_UNATTESTED")+"`.",
       "",
       "## Original Einstein/P8/chemistry and derived one-scattering model",
       "",
       "Actual original Einstein–Bianchi-I fully polarized P8, Peebles recombination with original KM2K Lyα effective Sobolev-tagging and KM2L zero-collision Green transfer, GL12/GL16. This unit re-integrates the real original IVPs and computes *time-propagated exactly-one Thomson-scattered radiation*, including original noncommuting shear geodesic redshift, original P8 transported screen E, cold electron bulk-Doppler spectral first gain, and first-scatter-to-observation no-rescattering survival exp(-Delta tau). No higher collision gain; no new Einstein stress or chemistry backreaction.",
       "",
       "Physical first-collision source at every one of 41 original Bianchi source times is independently regenerated from the original emissivity, ray geometry and actual dynamic Peebles x_e. The source is stored as frequency-resolved 3x3 electron-rest M_e and original boosts/screens. Its retarded integral yields the full final **ray-resolved 2x2 polarized spectral coherency**; 5 observation epochs per angular grid ×1200 bins = **10 physical snapshots and 12,000 spectrum rows**, six PNG scientific plots, two full final exact-one coherency NPZ files.",
       "",
       "## Actual measured endpoint u=0.25",
       "| Quantity | GL12 | GL16 |",
       "|---|---:|---:|"
    ]
    for key,label in columns:
        vals=[cases[g]["snapshots"][-1][key] for g in ("GL12","GL16")]
        lines.append("| "+label+" | "+" | ".join(format(v,".13g") for v in vals)+" |")
    vals=[cases[g]["original_Einstein_conservation"]["max_Hamiltonian_norm"] for g in ("GL12","GL16")]
    lines.append("| inherited maximum Einstein Hamiltonian normalized | "+" | ".join(format(v,".13g") for v in vals)+" |")
    lines += [
       "",
       "## Scientific/verification state",
       "",
       "Theory: source-locked polarization screen Green function for (Liouville+Gamma)J1=Gain[J0]. Maxwell Doppler line shape is an inherited **effective** tagging; production P8 is grey and already includes its own photons. Therefore this J1 is a *diagnostic tagged subset*, not an additional Einstein radiation component or full physical observable.",
       "",
       "Independent saved-data adversarial referee PASS_SCOPED on both ordinary Python and -O: 41 original source epochs per grid, 10 observer epochs reconstructed from frozen M_e, Doppler D, momentum mu, normal screen F and Thomson tau without importing the Einstein/P8 RHS. It independently derives bolometric density, photon momentum and polarization through symmetric eigenvalues and computes the exact unremapped first log-frequency moment. Maximum mismatch fields: "+json.dumps(a["maxima"],sort_keys=True)+".",
       "",
       "**Numerical limitation:** 40-panel composite Simpson temporal first-gain quadrature vs composite trapezoid on same original source yields up to "+format(a["maxima"]["rho_trapezoid_vs_simpson"],".6g")+" relative difference (not a certified error bound). The original source emission uses GL8 panels. This study does not claim continuous time/angular frequency transport error enclosure; grid comparisons and separate time rules are conditional evidence.",
       "",
       "Exact constant-H/constant-Gamma pulse and steady emission one-scattering Green controls were independently verified analytically, including one-scattering Poisson limit Gamma*t*exp(-Gamma*t) at H=0. Original P8 spectral first-gain parity and physical screen transversality source-locked. See `S0_THEORY_KO.md` for equations and conventions (-,+,+,+), c, k_B, h_P.",
       "",
       "Source-owned physics JSON SHA256 `"+hashlib.sha256(src.read_bytes()).hexdigest()+"`. CI and source ZIP remote backup receipts are not implied by this generated report; retrieve live GitHub Actions before declaring them.",
       "",
       "Remaining: second/higher Thomson gain and exact resummed frequency-polarized transport, thermal Compton redistribution, nonthermal resonant Lyα/2p/atomic recoil, backreaction and thermal first law, real observed CMB and angular continuum enclosure, distinct-author R6/C9. Native subagent NOT_RUN.",
       "",
       "**DAG:** upper BASS 9/15, 21 edges, KM2 PARTIAL, **0 newly completed upper nodes**. KM2N scoped 1/1 PASS_SCOPED only after final normal and -O CI. No merge; production_ready=false;auto_next=false; STOP_AFTER_ONE_BOUNDED_UNIT=true."
    ]
    (out/"S2_FINAL_REPORT_KO.md").write_text("\n".join(lines)+"\n")
    final=cases["GL16"]["snapshots"][-1]
    handoff=[
      "$physmath-research-loop $scispace $exa $wolfram",
      "PROJECT=BASS","REPO=cosmosapjw-quantum/bass",
      "CURRENT_UNIT=KM2N_RETARDED_EXACTLY_ONE_THOMSON_SCATTERED_POLARIZED_LYA",
      "CURRENT_PR=READ_LIVE_PR_NUMBER","CURRENT_HEAD="+os.getenv("GITHUB_SHA","READ_LIVE_HEAD_FIRST"),
      "IMMUTABLE_PARENT_PR=295","IMMUTABLE_PARENT_HEAD=2ff05b8416965af0adc7851a8aa60ec2e51b2fee",
      "READ_LIVE_HEAD_FIRST=true",
      "ORIGINAL_EINSTEIN_P8_PEEBLES_GRIDS=GL12,GL16",
      "PHYSICAL_OBSERVATION_EPOCHS=10","PHYSICAL_SOURCE_TIME_NODES_PER_GRID=41",
      "FREQUENCY_BINS_PER_SNAPSHOT=1200","FREQUENCY_ROWS=12000","SCIENTIFIC_PLOTS=6",
      "SCATTER_ORDER=EXACTLY_ONE_THOMSON_WITH_POST_FIRST_SURVIVAL",
      "GL16_ONCE_RHO="+str(final["rho_exactly_one"]),
      "GL16_ZERO_RHO="+str(final["original_KM2L_ballistic_rho"]),
      "GL16_ONCE_OVER_ZERO_RHO="+str(final["new_once_scattered_to_ballistic_energy_ratio"]),
      "GL16_ONCE_LINEAR_POL="+str(final["mean_linear_polarization"]),
      "GL16_ONCE_CENTROID_LOGFREQ="+str(final["mean_logfreq"]),
      "SAVED_INDEPENDENT_AUDIT="+a["verdict"],
      "MAX_COMPOSITE_SIMPSON_VS_TRAPEZOID_RELATIVE="+str(a["maxima"]["rho_trapezoid_vs_simpson"]),
      "NORMAL_TESTS=READ_LIVE_CI","OPTIMIZED_SAVED_AUDIT=READ_LIVE_CI",
      "S0_S1_S2_FINAL_ARCHIVE_SHA=READ_PROVIDER_RECEIPTS",
      "GDRIVE=CHECK_ACTUAL_PROVIDER_UPLOAD_READBACK",
      "LIBRARY=CHECK_ACTUAL_LIBRARY_LISTING",
      "DROPBOX=NOT_VERIFIED",
      "UPPER_DAG=9/15","UPPER_EDGES=21","KM2=PARTIAL","NEW_UPPER_COMPLETED=0",
      "KM2N_SCOPED=1/1_PASS_SCOPED_CONDITIONAL_FINAL_CI",
      "SECOND_AND_HIGHER_THOMSON_GAIN=NOT_RUN",
      "FULL_FREQUENCY_RESUMMATION=NOT_RUN","RESONANT_LYA_RECOIL=NOT_RUN",
      "PHOTOEXCITATION_FEEDBACK=NOT_RUN","THERMAL_FIRST_LAW=NOT_RUN",
      "TIME_CONTINUUM_ENCLOSURE=NOT_RUN","ANGULAR_CONTINUUM_ENCLOSURE=NOT_RUN",
      "DISTINCT_AUTHOR_R6_C9=NOT_RUN","NATIVE_SUBAGENT=NOT_RUN",
      "NEXT_CANDIDATE_ONLY=KM2O_SECOND_THOMSON_GAIN_OR_RESUMMED_SPECTRAL_TRANSFER",
      "PRODUCTION_READY=false","MERGE_READY=false","AUTO_NEXT=false",
      "STOP_AFTER_ONE_BOUNDED_UNIT=true"]
    (out/"HANDOFF_NEXT_KO.txt").write_text("\n".join(handoff)+"\n")
    print("KM2N_FINAL_PHYSICS_REPORT",len(lines),"GL16_ONCE_RHO",final["rho_exactly_one"],flush=True)
    return handoff

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--audit",type=Path,required=True)
    ap.add_argument("--outdir",type=Path,required=True)
    a=ap.parse_args();make(a.source,a.audit,a.outdir)
