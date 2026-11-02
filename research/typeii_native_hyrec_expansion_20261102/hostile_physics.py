#!/usr/bin/env python3
"""One bounded same-author hostile refutation pass of wrong TypeII/HYREC2 source interfaces.

Explicit counterexamples:
- double relative flux q inside original Thomson normal-ray source
- missing electron Lorentz Gamma when starting from proper electron density
- silently treating proper n_H ∝ a^-3 instead of conserved normal Class-A current
- HYREC2 external-FLRW H table low-z interpolation claimed globally exact
- invalid negative HYREC2 H inputs and gamma/n_H factors must fail closed

Only scratch native_run/... files may be altered, never original HYREC2 or BASS.
"""
import csv,hashlib,json,os,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import simpson
from scipy.interpolate import PchipInterpolator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SCR=HERE/"native_run"
def check(a,msg):
    if not bool(a):raise RuntimeError(msg)
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()

summary=json.loads((HERE/"R5_SOURCE_ATOMIC_TYPEII_PHOTON_RESULTS.json").read_text())
hyrec=json.loads((HERE/"R4_NATIVE_TYPEII_H_AND_PROPER_NH_RESULTS.json").read_text())
control=json.loads((HERE/"R2_NATIVE_FLRW_CALLBACK_CONTROL.json").read_text())
input_source=(ROOT/"research/typeii_hyrec2_history_20261102/HYREC2_FLRW_INPUT_20261102.dat").read_bytes()
native_info=json.loads((ROOT/"research/typeii_hyrec2_history_20261102/HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
check(hashlib.sha256(input_source).hexdigest()==native_info["calibrated_input_sha256"],
      "HYREC_NATIVE_ORIGINAL_INPUT_CHANGED")
native_owner=Path(native_info["installed_source"])
for file,d in native_info["original_source_atomic_table_sha256"].items():
    check(sha(native_owner/file)==d,"ORIGINAL_HYREC_SOURCE_CORRUPT_"+file)
path=HERE/"TYPEII_ATOMIC_THOMSON_EXTENDED_26RAY.csv"
with path.open(newline="") as f:rows=list(csv.DictReader(f))
check(len(rows)==1167*26,"ORIGINAL_PHOTON_SOURCE_26X1167_MISSING")
times=np.array([float(rows[i]["tau_H"]) for i in range(1167)])
N=len(times)
rate=np.zeros((26,N))
q=np.zeros((26,N))
dep=np.zeros((26,N))
for row in rows:
    j=int(row["ray_id"])
    k=int(np.searchsorted(times,float(row["tau_H"])))
    check(0<=j<26 and 0<=k<N and abs(times[k]-float(row["tau_H"]))<2e-14,
          "SOURCE_RAY_RECORD_INDEX_DRIFT")
    r=float(row["hazard_full_native_TypeII_H_plus_proper_nH"])
    n_y=float(row["n_y"])
    # The published ray can directly derive relative q from hazard/per-ray n_y
    # by reading independent BASS v(t) from the original source Hubble grid.
    rate[j,k]=r
    dep[j,k]=float(row["depth_native_TypeII_H_plus_proper_nH"])
    q[j,k]=n_y
actual=dep[:,-1]
# Independent Type-II v2(tau), published original 2248 source grid:
table=np.loadtxt(HERE/"TYPEII_H_COMPARE_FLRW_GRID.csv",delimiter=",",skiprows=1)
vinterp=PchipInterpolator(np.log1p(table[:,0]),table[:,6],extrapolate=False)
z=1701*np.exp(-times)-1
v=vinterp(np.log1p(z))
check(np.isfinite(v).all() and max(abs(v))<1,"ORIGINAL_TILTED_SOURCE_V_OUT_OF_RANGE")
gamma=1/np.sqrt(1-v*v)
flx=1-v[None,:]*q
check(np.min(flx)>0,"WRONG_SOURCE_RELATIVE_FLUX")
# Native owner original source BASS uses one q; second q changes directional
# Thomson opacity by an amount which cannot be dismissed as roundoff.
direct=simpson(rate,x=times,axis=1)
baseline_gap=float(max(abs(direct-actual)))
check(baseline_gap<3e-7,"INDEPENDENT_SIMPSON_NOT_MATCHED_TO_GAUSS")
wrong_double=simpson(rate*flx,x=times,axis=1)
wrong_no_gamma=simpson(rate/gamma[None,:],x=times,axis=1)
wrong_unconserved=simpson(rate*gamma[None,:]/gamma[0],x=times,axis=1)
plus=summary["physical_plus_minus_axes"][0]
minus=summary["physical_plus_minus_axes"][1]
check(wrong_double[plus]-actual[plus]<-.5 and wrong_double[minus]-actual[minus]>.5,
      "DOUBLE_Q_NEGATIVE_SOURCE_DIRECTIONAL_EFFECT_NOT_DETECTED")
check(np.max(abs(wrong_no_gamma-actual))>.02,
      "PROPER_DENSITY_MISSING_GAMMA_NOT_DETECTED")
check(np.max(abs(wrong_unconserved-actual))>.001,
      "UNCONSERVED_PROPER_NH_COUNTEREXAMPLE_NOT_DETECTED")

# Source native external FLRW H callback itself has a measured low-z error,
# so an all-z precision claim is refuted, without refuting source z=300..1700.
check(control["all_redshift_callback_identity"]=="CONCERN_LOW_Z_INTERPOLATION",
      "SOURCE_LOW_Z_NONEXACT_CONTROL_NOT_RECORDED")
check(control["external_FLRW_control_recombination_domain_xe_max_abs_gap"]<1e-9,
      "SOURCE_TARGET_FLRW_CALLBACK_BAD")
check(control["original_HyRec_builtin_vs_external_FLRW_Tm_max_relative_gap"]>2e-5,
      "WRONG_ALL_REDSHIFT_PRECISION_CLAIM_NOT_REFUTED")
# Original HYREC C external input and source helper must reject malformed
# H(z) and tilted proper density factors. Only scratch test directories.
scratch=SCR/"hostile_rejected_inputs"
scratch.mkdir(exist_ok=True)
for name in ["Alpha_inf.dat","R_inf.dat","fit_swift.dat",
             "two_photon_tables.dat","two_photon_tables_hires.dat"]:
    link=scratch/name
    if not link.exists():link.symlink_to(native_owner/name)
    check(link.is_symlink() and link.resolve()==(native_owner/name).resolve(),
          "SCRATCH_ATOMIC_SOURCE_LINK_CHANGED_"+name)
good_h=np.loadtxt(HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat")
good_gamma=np.loadtxt(HERE/"TYPEII_PROPER_NH_FACTOR_2248.dat")
bad_h=good_h.copy(); bad_h[80]=-1.
bad_n=good_gamma.copy();bad_n[80]=-1.
bad_hf=scratch/"negative_Hubble.dat"
bad_nf=scratch/"negative_hydrogen_ratio.dat"
good_nf=scratch/"positive_hydrogen_ratio.dat"
np.savetxt(bad_hf,bad_h,fmt="%.17e")
np.savetxt(bad_nf,bad_n,fmt="%.17e")
np.savetxt(good_nf,good_gamma,fmt="%.17e")
original_h_binary=SCR/"native_hubble_callback"
patched=SCR/"native_hubble_current_callback"
check(original_h_binary.is_file() and patched.is_file(),
      "HYREC2_ORIGINAL_NATIVE_C_EXECUTABLES_NOT_FOUND")
negative_H=subprocess.run([str(original_h_binary),"external_H",str(bad_hf)],
    cwd=scratch,input=input_source,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
check(negative_H.returncode!=0,"HYREC2_NEGATIVE_H_ACCEPTED")
env=dict(os.environ,BASS_TYPEII_NH_FACTOR_FILE=str(bad_nf))
negative_n=subprocess.run([str(patched),"external_H",str(HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat")],
    cwd=scratch,env=env,input=input_source,stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,timeout=45)
check(negative_n.returncode!=0,"HYREC2_NEGATIVE_N_H_FACTOR_ACCEPTED")

out={
 "schema":"bass.typeii.native_HyRec2_helium_hydrogen_current_hostile_review.v1",
 "reviewer":"same author self-adversarial, no independent author and no native subagent",
 "input_native_source_identity":"HYREC2 18 source/atomic files byte SHA256",
 "original_26_photon_rays":26,
 "physical_time_samples":N,
 "independent_simpson_vs_Gauss_endpoint_max_abs_gap":baseline_gap,
 "double_q_error_plus":float(wrong_double[plus]-actual[plus]),
 "double_q_error_minus":float(wrong_double[minus]-actual[minus]),
 "double_q_max_abs_endpoint_error":float(max(abs(wrong_double-actual))),
 "missing_gamma_max_abs_endpoint_error":float(max(abs(wrong_no_gamma-actual))),
 "unconserved_proper_nH_max_abs_endpoint_error":float(max(abs(wrong_unconserved-actual))),
 "original_external_H_source_low_z_FLRW_interpolation_CONCERN":True,
 "negative_external_H_rejected_exit":negative_H.returncode,
 "negative_proper_density_ratio_rejected_exit":negative_n.returncode,
 "physical_model_unresolved":[
    "HYREC2 native SWIFT fit tables calibrated around FLRW, TypeII H outside exact calibration",
    "original gamma-law TypeII matter Einstein sector not coupled with atom/Thomson photon stress",
    "isotropic background photon blackbody/radiation field remains native FLRW approximation",
    "26 along-ray Thomson attenuation with no scattering angular gain/polarization",
    "no observed z=0 CMB visibility; conditional TypeII late-time H not physical Lambda-CDM"
 ],
 "verdict":"HOSTILE_WRONG_INTERFACES_REFUTED; ORIGINAL_ATOM_KINETIC_SCIENCE_CONDITIONAL_HOLD"
}
(HERE/"R9_HOSTILE_PHYSICS.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
