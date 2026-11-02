#!/usr/bin/env python3
"""Source-minimal HYREC original atomic kinetics with TypeII H and class-A proper hydrogen nH.

Only exactly 12 original history.c + 4 helium.c nH accessors are patched in
ignored scratch copies, original sources untouched and source SHA256 locked.
The same-source FLRW unity correction is checked against unmodified native C.
"""
from pathlib import Path
import os,re,json,hashlib,subprocess,difflib
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/"research/typeii_hyrec2_history_20261102"
NATIVE=json.loads((PARENT/"HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
SRC=Path(NATIVE["installed_source"])
SC=HERE/"native_run"
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name,digest in NATIVE["original_source_atomic_table_sha256"].items():
    check(sha(SRC/name)==digest,"IMMUTABLE_ORIGINAL_HYREC_SOURCE_DRIFT_"+name)
hgrid=np.loadtxt(HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat")
flrwgrid=np.loadtxt(HERE/"NATIVE_HYREC_FLRW_H_GRID.dat")
xi=np.loadtxt(HERE/"TYPEII_H_COMPARE_FLRW_GRID.csv",delimiter=",",skiprows=1)
nz=len(hgrid)
check(xi.shape==(nz,8) and len(flrwgrid)==nz,"TYPEII_CURRENT_H_GRID_IDENTITY_MISMATCH")
factor=xi[:,4]
check(np.min(factor)>0 and max(abs(factor[xi[:,0]>1700]-1))<1e-13,
      "PROPER_HYDROGEN_RATIO_OUTSIDE_SOURCE_CONTRACT")
ratio_file=HERE/"TYPEII_PROPER_NH_FACTOR_2248.dat"
np.savetxt(ratio_file,factor,fmt="%.17e")
unity_file=SC/"UNITY_GAMMA_RATIO_2248.dat"
np.savetxt(unity_file,np.ones(nz),fmt="%.17e")
moddir=SC/"proper_density_patched_source"
moddir.mkdir(exist_ok=True)
history=(SRC/"history.c").read_text()
helium=(SRC/"helium.c").read_text()
hist_pat=r'cosmo->nH0\s*\*\s*cube\(1\.\+z(?:_in)?\)'
def replace_h(m):
    mat=m.group(0)
    z="z_in" if mat.endswith("z_in)") else "z"
    return "bass_hydrogen_density(cosmo,"+z+")"
hnew,n_hist=re.subn(hist_pat,replace_h,history)
check(n_hist==12,"HISTORY_SOURCE_NH_OWNER_COUNT_CHANGED_"+str(n_hist))
check(hnew.count('#include "helium.h"')==1,"ORIGINAL_HISTORY_HEADER_NOT_FOUND")
hnew=hnew.replace('#include "helium.h"', '#include "helium.h"\n#include "bass_proper_density.h"',1)
target='nH0*ainv*ainv*ainv'
check(helium.count(target)==4,"ORIGINAL_HELIUM_DENSITY_OWNER_COUNT_CHANGED")
hn=helium
for index in range(4):
    expr="bass_hydrogen_density(cosmo,z)" if index<3 else "bass_hydrogen_density(data->cosmo,z)"
    hn=hn.replace(target,expr,1)
check(hn.count('#include "helium.h"')==1,"ORIGINAL_HELIUM_HEADER_CHANGED")
hn=hn.replace('#include "helium.h"','#include "helium.h"\n#include "bass_proper_density.h"',1)
(moddir/"history.c").write_text(hnew)
(moddir/"helium.c").write_text(hn)
patch=list(difflib.unified_diff(history.splitlines(keepends=True),hnew.splitlines(keepends=True),
    fromfile="immutable_HYREC2/history.c",tofile="scratch_history.c"))
patch+=list(difflib.unified_diff(helium.splitlines(keepends=True),hn.splitlines(keepends=True),
    fromfile="immutable_HYREC2/helium.c",tofile="scratch_helium.c"))
(HERE/"PROPER_HYDROGEN_REPLACEMENT_PATCH.diff").write_text("".join(patch))
b=SC/"native_hubble_current_callback"
sources=["hyrectools.c","hydrogen.c","energy_injection.c"]
cc=["gcc","-O3","-I"+str(SRC),"-I"+str(HERE),
    str(SRC/"hyrectools.c"),str(moddir/"helium.c"),str(SRC/"hydrogen.c"),
    str(moddir/"history.c"),str(SRC/"energy_injection.c"),
    str(HERE/"native_external_h_driver.c"),str(HERE/"bass_proper_density.c"),
    "-lm","-o",str(b)]
cp=subprocess.run(cc,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
check(cp.returncode==0,"NATIVE_HYREC_PROPER_CURRENT_PATCH_COMPILE_FAILED:"+cp.stderr[-2500:])
input_data=(PARENT/"HYREC2_FLRW_INPUT_20261102.dat").read_bytes()
check(hashlib.sha256(input_data).hexdigest()==NATIVE["calibrated_input_sha256"],
      "NATIVE_COSMOLOGY_SOURCE_CHANGED")
tables=["Alpha_inf.dat","R_inf.dat","fit_swift.dat",
        "two_photon_tables.dat","two_photon_tables_hires.dat"]
def run(name,hfile,ratio):
    work=SC/name
    work.mkdir(exist_ok=True)
    for tab in tables:
        link=work/tab
        if link.is_symlink():check(link.resolve()==(SRC/tab).resolve(),"ATOM_TABLE_SYMLINK_DRIFT")
        elif not link.exists():link.symlink_to(SRC/tab)
        else:raise RuntimeError("UNEXPECTED_ATOMIC_TABLE")
    env=dict(os.environ)
    env["BASS_TYPEII_NH_FACTOR_FILE"]=str(ratio)
    cp=subprocess.run([str(b),"external_H",str(hfile)],input=input_data,
        cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=150)
    check(cp.returncode==0,"NATIVE_PROPER_HYDROGEN_HYREC_FAILED_"+name+" "+
          cp.stderr.decode(errors="replace")[-2500:])
    data=np.loadtxt(work/"output_xe.dat")
    check(data.shape==(8000,3) and np.isfinite(data).all() and np.min(data[:,1:])>0,
          "INVALID_SOURCE_HYREC_OUTPUT_"+name)
    return data,sha(work/"output_xe.dat")
control,control_raw=run("modified_flrw_unity_control",SC/"external_flrw"/"hubble_input_native.dat",unity_file)
original_control=np.loadtxt(HERE/"NATIVE_HYREC_FLRW_H_EXTERNAL_CONTROL_8000.dat")
window=(control[:,0]>=300)&(control[:,0]<=1700)
max_control_xe=float(np.max(abs(control[window,1]-original_control[window,1])))
max_control_tm=float(np.max(abs(control[window,2]/original_control[window,2]-1)))
check(max_control_xe<1e-9 and max_control_tm<1e-8,
      "PATCH_UNITY_WITH_NATIVE_FLRW_NO_LONGER_EQUIVALENT")
Honly_unity,Honly_unity_raw=run("modified_typeii_H_unity_control",
    HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat",unity_file)
Honly=np.loadtxt(HERE/"NATIVE_TYPEII_HUBBLE_HHE_ATOMIC_XE_TM_8000.dat")
Hctrl=float(np.max(abs(Honly[window,1]-Honly_unity[window,1])))
check(Hctrl<1e-9,"PATCH_UNITY_WITH_BASS_TYPEII_H_NO_LONGER_EQUIVALENT")
proper_only,proper_only_raw=run("modified_flrw_H_typeii_proper_nH",
    SC/"external_flrw"/"hubble_input_native.dat",ratio_file)
combined,combined_raw=run("modified_typeii_H_and_typeii_proper_nH",
    HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat",ratio_file)
nHimpact=float(np.max(abs(Honly[window,1]-combined[window,1])))
Himpact=float(np.max(abs(proper_only[window,1]-combined[window,1])))
check(nHimpact>1e-9 and Himpact>1e-5,"TYPEII_PROPER_NH_OR_H_SOURCE_HAS_NO_ATOMIC_EFFECT")
output=HERE/"NATIVE_TYPEII_H_AND_PROPER_NH_XE_TM_8000.dat"
np.savetxt(output,combined,fmt=["%.0f","%.10e","%.10e"],
  header="z x_e=n_e/n_H, Tm_K, original HYREC2 kinetics with original BASS TypeII H and class-A proper nH(v2)")
output_nh=HERE/"NATIVE_FLRW_H_AND_TYPEII_PROPER_NH_XE_TM_8000.dat"
np.savetxt(output_nh,proper_only,fmt=["%.0f","%.10e","%.10e"],
  header="z x_e Tm_K original HYREC2 kinetics with FLRW H and class-A proper TypeII nH")
diag=[]
for z in (1700,1500,1392,1200,1100,1000,800,300):
    k=8000-z
    diag.append(dict(z=z,xe_original_FLRW=float(original_control[k,1]),
        xe_TypeII_Honly=float(Honly[k,1]),
        xe_TypeII_proper_nH_only=float(proper_only[k,1]),
        xe_H_and_nH=float(combined[k,1]),
        Tm_Honly_K=float(Honly[k,2]),Tm_H_and_nH_K=float(combined[k,2])))
report={
 "schema":"bass.typeii.original_native_HYREC2_atomic_H_and_conserved_proper_Hnucleus.v1",
 "parent_source_Hubble_comparison_sha256":sha(HERE/"NATIVE_TYPEII_H_ARRAY_2248.dat"),
 "immutable_original_HYREC2_source_sha256_count":len(NATIVE["original_source_atomic_table_sha256"]),
 "source_minimal_scratch_patch_replacement_counts":{"history":n_hist,"helium":4},
 "source_patch_sha256":sha(HERE/"PROPER_HYDROGEN_REPLACEMENT_PATCH.diff"),
 "unit_gamma_ratio_external_identity_FLRW_max_abs_xe":max_control_xe,
 "unit_gamma_ratio_external_identity_FLRW_max_relTm":max_control_tm,
 "unit_gamma_ratio_external_identity_TypeII_H_max_abs_xe":Hctrl,
 "maximum_Honly_vs_Hplus_proper_nH_abs_xe_z300_1700":nHimpact,
 "maximum_FLRW_Hproper_nH_vs_TypeII_Hproper_nH_abs_xe_z300_1700":Himpact,
 "source_Hubble_vs_density_4_way_sample":diag,
 "original_C_native_mode":"SWIFT with original transition/radiative-transfer fit tables",
 "source_Hubble":"BASS Type-II for zmean<=1700, FLRW above, normalized H at z1700",
 "source_nHrest":"native hydrogen nH0(1+zmean)^3 Gamma(1700)/Gamma(zmean)",
 "source_gamma_factor_sha256":sha(ratio_file),
 "native_Honly_with_unity_NH_raw_sha256":Honly_unity_raw,
 "native_proper_nH_only_raw_sha256":proper_only_raw,
 "native_full_combined_raw_sha256":combined_raw,
 "published_combined_sha256":sha(output),
 "published_proper_only_sha256":sha(output_nh),
 "claim":"ORIGINAL_HYREC2_ATOMIC_H_AND_TILTED_CLASS_A_HYDROGEN_CURRENT_KINETIC_SOLUTION_SOURCED",
 "limitations":"unchanged gamma-law BASS geometry not solved with baryon/radiation backreaction; native SWIFT atomic correction function calibrated near FLRW, CMB thermal isotropy remains assumed"
}
(HERE/"R4_NATIVE_TYPEII_H_AND_PROPER_NH_RESULTS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,indent=2,sort_keys=True))
