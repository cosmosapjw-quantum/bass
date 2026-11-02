#!/usr/bin/env python3
"""Original HYREC2 kinetic sensitivity to the supplied TypeII H(z) and proper nH(z).

Three intermediate external native C runs, not interpolated output x_e:
H_lambda(z)=H_FLRW^(1-lambda)*H_TypeII^lambda,
nH_lambda^rest = nH_FLRW (Gamma0/Gamma(z))^lambda.
Intermediate lambda is a diagnostic interpolation, NOT a Bianchi solution family.
"""
import csv,hashlib,json,os,subprocess
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SCR=HERE/"native_run"
def check(a,msg):
    if not bool(a):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=ROOT/"research/typeii_hyrec2_history_20261102"
info=json.load((HERE/"R4_NATIVE_TYPEII_H_AND_PROPER_NH_RESULTS.json").open())
hyrec=json.load((parent/"HYREC2_NATIVE_SOURCE_REPORT.json").open())
source=Path(hyrec["installed_source"])
for n,d in hyrec["original_source_atomic_table_sha256"].items():
    check(sha(source/n)==d,"IMMUTABLE_HYREC2_OWNER_DRIFT_"+n)
Hflrw=np.loadtxt(HERE/"NATIVE_HYREC_FLRW_H_GRID.dat")[:,1]
Htype=np.loadtxt(HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat")
ratio=np.loadtxt(HERE/"TYPEII_PROPER_NH_FACTOR_2248.dat")
n=len(Hflrw)
check(n==2248 and len(Htype)==n and len(ratio)==n,"ORIGINAL_HYREC_HN_ARRAY_NOT_2248")
source_binary=SCR/"native_hubble_current_callback"
check(source_binary.exists(),"ORIGINAL_PRESERVED_C_ATOM_PATCH_BINARY_UNAVAILABLE")
input_data=(parent/"HYREC2_FLRW_INPUT_20261102.dat").read_bytes()
native_baseline=np.loadtxt(HERE/"NATIVE_HYREC_FLRW_H_EXTERNAL_CONTROL_8000.dat")
native_endpoint=np.loadtxt(HERE/"NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat")
controls={0.0:native_baseline,1.0:native_endpoint}
tables=["Alpha_inf.dat","R_inf.dat","fit_swift.dat","two_photon_tables.dat","two_photon_tables_hires.dat"]
for lam in (0.25,0.5,0.75):
    name=f"homotopy_L{int(lam*100):02d}"
    scratch=SCR/name
    scratch.mkdir(exist_ok=True)
    for table in tables:
        link=scratch/table
        if not link.exists():link.symlink_to(source/table)
        check(link.is_symlink() and link.resolve()==(source/table).resolve(),
              "HYREC_TABLE_LINK_DRIFT")
    H=np.exp((1-lam)*np.log(Hflrw)+lam*np.log(Htype))
    GammaRatio=np.exp(lam*np.log(ratio))
    hfile=scratch/"external_h_lambda.dat"
    gfile=scratch/"source_nh_lambda.dat"
    np.savetxt(hfile,H,fmt="%.17e")
    np.savetxt(gfile,GammaRatio,fmt="%.17e")
    env=dict(os.environ,BASS_TYPEII_NH_FACTOR_FILE=str(gfile))
    result=subprocess.run([str(source_binary),"external_H",str(hfile)],input=input_data,
          cwd=scratch,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=110)
    check(result.returncode==0,"HYREC2_NATIVE_INTERPOLATED_H_NH_FAIL "+str(lam)+" "+
          result.stderr.decode(errors="replace")[-1600:])
    raw=np.loadtxt(scratch/"output_xe.dat")
    check(raw.shape==(8000,3) and np.isfinite(raw).all(),"MISSING_NATIVE_HOMOTOPY_DATA")
    controls[lam]=raw
ordered=sorted(controls)
z=native_baseline[:,0]
check(all(np.max(abs(controls[l][:,0]-z))<1e-14 for l in ordered),
      "NATIVE_HOMOTOPY_REDSHIFT_INDEX_DRIFT")
window=(z>=300)&(z<=1700)
xe=lambda lam:controls[lam][:,1]
Temp=lambda lam:controls[lam][:,2]
changes={str(lam):float(np.max(abs(xe(lam)[window]-xe(0.)[window])))
         for lam in ordered}
max_nonlinear=float(np.max(abs(xe(.5)[window]-(xe(0.)[window]+xe(1.)[window])/2)))
max_slope=float(np.max(abs((xe(.75)[window]-xe(.25)[window])/.5)))
max_tm_change=float(np.max(abs(Temp(1.)[window]-Temp(0.)[window])))
at={}
for red in (1700,1500,1392,1200,1100,1000,800,300):
    k=8000-red
    at[str(red)]={str(l):float(xe(l)[k]) for l in ordered}
# Check exactly the pinned endpoints to ensure the data are genuinely from the
# original two native C kinetic solvers.
check(sha(HERE/"NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat")==info["published_combined_sha256"],
      "TYPEII_ATOMIC_ENDPOINT_DATA_CHANGED")
check(max(abs(xe(0.)[window]-xe(1.)[window]))>0.01,
      "SOURCE_BASS_H_HAS_NO_ATOMIC_EFFECT")
from scipy.interpolate import PchipInterpolator
# Native response λ is not necessarily linear; require only finite and
# continuous at source endpoints, and record rather than mask nonlinearity.
with (HERE/"ATOMIC_TYPEII_H_NH_HOMOTOPY_300_TO1700.csv").open("w",newline="") as f:
    writer=csv.writer(f,lineterminator="\n")
    writer.writerow(["z"]+[f"x_e_lambda_{l:.2f}" for l in ordered]+
                    [f"T_m_K_lambda_{l:.2f}" for l in ordered])
    for idx in np.where(window)[0]:
        writer.writerow([format(z[idx],".0f")]+
          [format(xe(l)[idx],".12e") for l in ordered]+
          [format(Temp(l)[idx],".12e") for l in ordered])
result={
 "schema":"bass.typeii.native_HyRec2_atom_H_properH_lam_response.v1",
 "control_purpose":"native C atomic x_e response to matched source H and proper nH logarithmic interpolation",
 "diagnostic_lambda":[0.,.25,.5,.75,1.],
 "lambda_physics":"lambda in (0,1) is NOT an Einstein source family; pure response experiment",
 "native_proper_Hplus_nH_endpoint_sha256":sha(HERE/"NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat"),
 "max_abs_xe_relative_to_flrw_by_lambda":changes,
 "max_midpoint_nonlinearity_abs_xe_z300_1700":max_nonlinear,
 "max_dx_e_dlambda_central_0p5":max_slope,
 "maximum_matter_T_difference_endpoints_K":max_tm_change,
 "native_source_xe_values":at,
 "source_C_kinetic_runs_new":3,
 "status":"SOURCE_NATIVE_HYREC2_H_AND_PROPER_HN_RESPONSE_SENSITIVITY_NUMERICALLY_CHECKED"
}
(HERE/"R7_ATOMIC_H_NH_HOMOTOPY.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps(result,indent=2,sort_keys=True))
