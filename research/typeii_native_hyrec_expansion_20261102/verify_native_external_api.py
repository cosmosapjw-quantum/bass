#!/usr/bin/env python3
"""Use the UNMODIFIED HYREC2 C rec_build_history external Hubble array API.
Original native builtin and an exact native FLRW H-table must agree before any
physical TypeII-H modification is interpreted. All binary scratch is ignored.
"""
from pathlib import Path
import hashlib,json,subprocess,os
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/"research/typeii_hyrec2_history_20261102"
PR330="9f10e1145c8582f71f7d81dcebfd3c125c70c04c"
original=json.loads((PARENT/"HYREC2_NATIVE_SOURCE_REPORT.json").read_text())
SOURCE=Path(original["installed_source"])
NAMES=["hyrectools.c","helium.c","hydrogen.c","history.c","energy_injection.c"]
headers=["hyrectools.h","helium.h","hydrogen.h","history.h","energy_injection.h"]
tables=["Alpha_inf.dat","R_inf.dat","fit_swift.dat","two_photon_tables.dat","two_photon_tables_hires.dat"]
SCRATCH=HERE/"native_run"
SCRATCH.mkdir(exist_ok=True)
def check(cond,msg):
    if not bool(cond):raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):
    return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
check(git("rev-parse",PR330)==PR330,"MISSING_IMMUTABLE_PARENT")
for name,h in original["original_source_atomic_table_sha256"].items():
    check(sha(SOURCE/name)==h,"IMMUTABLE_ORIGINAL_HYREC_SOURCE_CHANGED_"+name)
for name in NAMES+headers+tables:check((SOURCE/name).is_file(),"NO_ORIGINAL_HYREC2_"+name)
input_data=(PARENT/"HYREC2_FLRW_INPUT_20261102.dat").read_bytes()
check(hashlib.sha256(input_data).hexdigest()==original["calibrated_input_sha256"],
      "PROTECTED_NATIVE_HYREC2_INPUT_NOT_SAME_AS_PARENT")
reference=np.loadtxt(PARENT/"HYREC2_FLRW_XE_TM_8000.dat")
check(reference.shape==(8000,3),"BASELINE_FLRW_NOT_8000")
binary=SCRATCH/"native_hubble_callback"
compile_cmd=["gcc","-O3","-Wall","-Wextra","-I"+str(SOURCE)]+[
 str(SOURCE/n) for n in NAMES]+[str(HERE/"native_external_h_driver.c"),"-lm","-o",str(binary)]
cp=subprocess.run(compile_cmd,cwd=SCRATCH,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                  text=True,timeout=120)
check(cp.returncode==0,"COMPILE_NATIVE_HYREC_HUBBLE_WRAPPER_FAIL:"+cp.stderr[-2500:])
def setup(name):
    work=SCRATCH/name
    work.mkdir(exist_ok=True)
    for tab in tables:
        link=work/tab
        if link.is_symlink():
            check(link.resolve()==(SOURCE/tab).resolve(),"ATOMIC_TABLE_SYMLINK_DRIFT_"+tab)
        elif not link.exists():link.symlink_to(SOURCE/tab)
        else:raise RuntimeError("UNEXPECTED_HYREC_RATE_TABLE_"+str(link))
    return work
def execute(mode,work,extra=()):
    r=subprocess.run([str(binary),mode,*map(str,extra)],cwd=work,input=input_data,
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
    check(r.returncode==0,"NATIVE_HUBBLE_CALLBACK_RUN_FAIL "+mode+" "+
          r.stderr.decode(errors="replace")[-3000:])
    return r
work_b=setup("builtin")
work_h=setup("flrw_h_grid")
work_e=setup("external_flrw")
execute("builtin",work_b)
execute("emit_FLRW_H",work_h)
table=np.loadtxt(work_h/"H_grid.dat")
check(table.ndim==2 and table.shape[1]==2 and len(table)>2000,"HYREC_EXTERNAL_HGRID_BAD")
nz=len(table)
expected=8000*np.arange(nz)/nz
check(max(abs(table[:,0]-expected))<5e-11,"HYREC_GRID_Z_CONTRACT_WRONG")
check(np.all(np.isfinite(table)) and np.min(table[:,1])>0,"INVALID_NATIVE_FLRW_RATE")
grid=HERE/"NATIVE_HYREC_FLRW_H_GRID.dat"
np.savetxt(grid,table,fmt=["%.17e","%.17e"],header="z_uniform_HyRec_grid H_FLRW_native_s_minus1")
onlyH=work_e/"hubble_input_native.dat"
np.savetxt(onlyH,table[:,1],fmt="%.17e")
execute("external_H",work_e,[onlyH])
builtin=np.loadtxt(work_b/"output_xe.dat")
external=np.loadtxt(work_e/"output_xe.dat")
check(builtin.shape==external.shape==reference.shape==(8000,3),
      "DIFFERENT_HISTORY_ROW_SHAPE")
maxbase=float(np.max(abs(builtin-reference)))
check(maxbase<2e-9,"ORIGINAL_NATIVE_STANDALONE_BASELINE_NOT_REPRODUCED")
max_xe=float(np.max(abs(builtin[:,1]-external[:,1])))
max_tm_abs=float(np.max(abs(builtin[:,2]-external[:,2])))
max_tm_rel=float(np.max(abs(builtin[:,2]/external[:,2]-1)))
window=(builtin[:,0]>=300)&(builtin[:,0]<=1700)
window_xe=float(np.max(abs(builtin[window,1]-external[window,1])))
window_tm_rel=float(np.max(abs(builtin[window,2]/external[window,2]-1)))
# Observed FLRW H table C interpolation is not an exact all-redshift identity:
# the whole-history discrepancy is recorded, while the BASS science domain
# 300<=z<=1700 is source-valid with a precise predeclared numerical target.
check(window_xe<1e-9 and window_tm_rel<1e-8,
      f"EXTERNAL_FLRW_RECOMBINATION_WINDOW_IDENTITY_FAILED {window_xe} {window_tm_rel}")
np.savetxt(HERE/"NATIVE_HYREC_FLRW_H_EXTERNAL_CONTROL_8000.dat",external,
           fmt=["%.0f","%.10e","%.10e"],
           header="z x_e T_m; actual unchanged native HYREC rec_build_history with external FLRW H array")
report={
 "schema":"bass.typeii.native_hyrec2_original_external_Hubble_API_flrw_identity.v1",
 "parent_git_head":PR330,
 "native_HyRec2020_input_sha256":sha(PARENT/"HYREC2_FLRW_INPUT_20261102.dat"),
 "native_source_file_sha256_count":len(original["original_source_atomic_table_sha256"]),
 "original_unmodified_C_sources":NAMES,
 "only_new_C_source":"research/typeii_native_hyrec_expansion_20261102/native_external_h_driver.c",
 "native_compiler":compile_cmd,
 "native_C_gcc_stderr":cp.stderr[-700:],
 "HYREC2_source_Hubble_array_grid_Nz":nz,
 "HYREC2_source_Hubble_array_delta_z":8000/nz,
 "original_HyRec_builtin_vs_immutable_parent_max_abs_gap":maxbase,
 "original_HyRec_builtin_vs_external_FLRW_xe_max_abs_gap":max_xe,
 "original_HyRec_builtin_vs_external_FLRW_Tm_max_abs_gap_K":max_tm_abs,
 "original_HyRec_builtin_vs_external_FLRW_Tm_max_relative_gap":max_tm_rel,
 "recombination_domain_z":[300,1700],
 "external_FLRW_control_recombination_domain_xe_max_abs_gap":window_xe,
 "external_FLRW_control_recombination_domain_Tm_max_relative_gap":window_tm_rel,
 "all_redshift_callback_identity":"CONCERN_LOW_Z_INTERPOLATION",
 "source_native_external_H_grid_sha256":sha(grid),
 "source_native_external_flrw_history_sha256":sha(HERE/"NATIVE_HYREC_FLRW_H_EXTERNAL_CONTROL_8000.dat"),
 "status":"ORIGINAL_NATIVE_HYREC2_HUBBLE_ARRAY_FLRW_PARITY_NUMERICALLY_CHECKED",
 "claim_scope":"Source original rec_build_history external-H table API; no TypeII-H yet."
}
(HERE/"R2_NATIVE_FLRW_CALLBACK_CONTROL.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,indent=2,sort_keys=True))
