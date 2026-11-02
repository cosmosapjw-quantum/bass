#!/usr/bin/env python3
"""Execute ORIGINAL HYREC2 hydrogen+helium atomic kinetics with original BASS TypeII H(z).

rec_build_history() original C source is unchanged. Only original externally
sampled Hubble array is different. The HYREC internal hydrogen density remains
nH0*(1+z)^3 in this H-only lane, so that density-frame modeling is a separate
controlled intervention, NOT silently claimed.
"""
import subprocess, json, hashlib
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/"research/typeii_hyrec2_history_20261102"
SCRATCH=HERE/"native_run"
SRC=Path(json.loads((PARENT/"HYREC2_NATIVE_SOURCE_REPORT.json").read_text())["installed_source"])
report=json.loads((HERE/"R3_TYPEII_HUBBLE_GRID.json").read_text())
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def digest(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()
hpath=HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat"
check(hpath.exists() and digest(hpath)==report["native_H_array_SHA256"],
      "ORIGINAL_TYPEII_HUBBLE_ARRAY_DRIFT")
h=np.loadtxt(hpath)
check(len(h)==report["native_HyRec_hubble_grid_length"] and np.min(h)>0 and np.isfinite(h).all(),
      "TYPEII_HUBBLE_ARRAY_UNPHYSICAL")
native_report=json.loads((PARENT/"HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
for file,dig in native_report["original_source_atomic_table_sha256"].items():
    check(digest(SRC/file)==dig,"NATIVE_HYREC_SOURCE_CHANGED_"+file)
input_data=(PARENT/"HYREC2_FLRW_INPUT_20261102.dat").read_bytes()
check(hashlib.sha256(input_data).hexdigest()==native_report["calibrated_input_sha256"],
      "C_INPUT_IDENTITY_DRIFT")
binary=SCRATCH/"native_hubble_callback"
check(binary.is_file(),"NATIVE_HYREC_SOURCE_WRAPPER_NOT_COMPILED")
work=SCRATCH/"typeii_hubble_external"
work.mkdir(exist_ok=True)
for name in ["Alpha_inf.dat","R_inf.dat","fit_swift.dat",
             "two_photon_tables.dat","two_photon_tables_hires.dat"]:
    dest=work/name
    if dest.is_symlink():check(dest.resolve()==(SRC/name).resolve(),"SOURCE_TABLE_SYMLINK_INVALID")
    elif not dest.exists():dest.symlink_to(SRC/name)
    else:raise RuntimeError("UNRECOGNIZED_ATOMIC_RATE_FILE")
result=subprocess.run([str(binary),"external_H",str(hpath)],cwd=work,
                      input=input_data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                      timeout=120)
check(result.returncode==0,"NATIVE_HYREC_TYPEII_H_CALLBACK_FAILED "+
      result.stderr.decode(errors="replace")[-3400:])
outpath=work/"output_xe.dat"
check(outpath.exists(),"NATIVE_TYPEII_RECOMBINATION_OUTPUT_NOT_GENERATED")
actual=np.loadtxt(outpath)
baseline=np.loadtxt(HERE/"NATIVE_HYREC_FLRW_H_EXTERNAL_CONTROL_8000.dat")
check(actual.shape==baseline.shape==(8000,3),"NATIVE_HYREC2_HISTORY_SHAPE_DRIFT")
check(np.isfinite(actual).all() and np.min(actual[:,1])>0 and np.min(actual[:,2])>0,
      "NATIVE_HYREC2_TYPEII_OUTPUT_NONPHYSICAL")
check(np.max(abs(actual[:,0]-baseline[:,0]))<1e-14,
      "NATIVE_HYREC2_TYPEII_OUTPUT_REDSHIFT_GRID_BAD")
window=(actual[:,0]>=300)&(actual[:,0]<=1700)
max_abs_xe=float(np.max(abs(actual[window,1]-baseline[window,1])))
max_abs_Tm=float(np.max(abs(actual[window,2]-baseline[window,2])))
max_rel_Tm=float(np.max(abs(actual[window,2]/baseline[window,2]-1)))
check(max_abs_xe>1e-5,"TYPEII_H_CHANGE_NO_ATOMIC_KINETICS_RESPONSE")
# Save exact native C output in a source-conditioned published table.
native_output=HERE/"NATIVE_TYPEII_HUBBLE_HHE_ATOMIC_XE_TM_8000.dat"
np.savetxt(native_output,actual,fmt=["%.0f","%.10e","%.10e"],
           header="z x_e n_e/n_H (HHe) and Tm_K from ORIGINAL HyRec2 rec_build_history with BASS TypeII H(z), native FLRW nH(z)")
scenarios=[]
for z in [1700,1500,1392,1200,1100,1000,800,300,100,1]:
    row=8000-z
    check(0<=row<8000,"PROBE_Z_NOT_IN_HYREC_TABLE")
    scenarios.append({"z":z,"xe_FLRW_external":float(baseline[row,1]),
        "xe_TypeII_H_atomic":float(actual[row,1]),
        "TypeII_minus_FLRW":float(actual[row,1]-baseline[row,1]),
        "Tm_FLRW_K":float(baseline[row,2]),"Tm_TypeII_H_K":float(actual[row,2])})
jsonpath=HERE/"R3_NATIVE_TYPEII_ATOMIC_H_ONLY.json"
out={
 "schema":"bass.typeii.original_HyRec2_atomic_kinetics_external_TypeII_H_only.v1",
 "source_C_API":"original HYREC-2 history.c::rec_build_history(data,SWIFT,Hubble_Array)",
 "source_C_atomic_HydrogenHelium":"unchanged original C files + immutable tabulated rates",
 "original_Hubble_source":"BASS gamma1.3 tilted Type II q=N1prime/N1+4SigmaPlus",
 "original_atomic_density":"HYREC native nH0*(1+z)^3; TypeII proper baryon-current adjustment NOT YET APPLIED",
 "source_Hubble_grid_sha256":digest(hpath),
 "native_output_raw_sha256":digest(outpath),
 "native_output_public_sha256":digest(native_output),
 "FLRW_callback_identity_file":"R2_NATIVE_FLRW_CALLBACK_CONTROL.json",
 "recombination_target_z":[300,1700],
 "maximum_absolute_xe_typeii_minus_FLRW":max_abs_xe,
 "maximum_absolute_matter_temperature_K_difference":max_abs_Tm,
 "maximum_matter_temperature_relative_difference":max_rel_Tm,
 "sample_values":scenarios,
 "status":"SOURCE_ORIGINAL_HYREC2_NON_EQUILIBRIUM_ATOMIC_ODE_SOLVED_WITH_BASS_TYPEII_H_ONLY",
 "claim_limits":"FLRW internal nH and photon thermal reservoir still prescribed, TypeII late-z gamma-law source no physical dark-energy closure, not full coupled Einstein–Boltzmann"
}
jsonpath.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
