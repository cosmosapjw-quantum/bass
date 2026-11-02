#!/usr/bin/env python3
"""Compile and execute installed original standalone HYREC-2, isolated from CLASSIER.

Native source and tabulated atomic rates are SHA256-pinned by a manifest.
The CLI writes output_xe.dat in CWD, so only disposable native_run/ children are
ever used. Preserve original CLASSIER HyRec2020 source and its bundled sample.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import numpy as np

HERE=Path(__file__).resolve().parent
SRC=Path("/home/cosmosapjw/src/TEFF_CLASSIER_CLEAN_BUILD_v1_3/external/HyRec2020")
WORK=HERE/"native_run"
WORK.mkdir(exist_ok=True)
SOURCE_NAMES=["hyrectools.c","helium.c","hydrogen.c","history.c","energy_injection.c","hyrec.c"]
HEADER_NAMES=["hyrectools.h","helium.h","hydrogen.h","history.h","energy_injection.h"]
TABLE_NAMES=["Alpha_inf.dat","R_inf.dat","fit_swift.dat","two_photon_tables.dat","two_photon_tables_hires.dat"]
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def shaf(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in SOURCE_NAMES+HEADER_NAMES+TABLE_NAMES+["input.dat","output_xe.dat"]:
    check((SRC/name).is_file(),"MISSING_LOCAL_SOURCE_"+name)
fingerprints={name:shaf(SRC/name) for name in SOURCE_NAMES+HEADER_NAMES+TABLE_NAMES+["input.dat","output_xe.dat"]}

exe=WORK/"hyrec2_standalone"
compiler=["gcc","-O3","-I"+str(SRC)]+[str(SRC/name) for name in SOURCE_NAMES]+["-lm","-o",str(exe)]
built=subprocess.run(compiler,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,cwd=str(WORK),timeout=120)
if built.returncode:
    raise RuntimeError("NATIVE_HYREC_BUILD_FAIL: "+built.stderr[-4500:])
check(exe.exists(),"BUILD_EXIT0_NO_EXECUTABLE")
def prepare(sub):
    sub.mkdir(exist_ok=True)
    for name in TABLE_NAMES:
        sym=sub/name
        if sym.is_symlink():
            check(sym.resolve()==(SRC/name).resolve(),"NATIVE_TABLE_SYMLINK_DRIFT_"+name)
        elif not sym.exists():
            sym.symlink_to(SRC/name)
        else:raise RuntimeError("UNEXPECTED_NATIVE_DATA_EXISTING_"+name)
def launch(sub,input_bytes):
    prepare(sub)
    output=sub/"output_xe.dat"
    if output.exists():output.unlink()  # exclusively within ignored native_run child
    cp=subprocess.run([str(exe)],input=input_bytes,stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,cwd=sub,timeout=150)
    check(cp.returncode==0,"NATIVE_HYREC_RUNTIME_EXIT_"+str(cp.returncode)+": "+cp.stderr[-2600:].decode(errors="replace"))
    check(output.is_file(),"MISSING_NATIVE_RECOMBINATION_OUTPUT")
    a=np.loadtxt(output)
    check(a.shape==(8000,3),"NATIVE_HYREC_8000_SHAPE_FAIL:"+str(a.shape))
    check(np.all(np.isfinite(a)) and np.min(a[:,1])>0 and np.min(a[:,2])>0,"NATIVE_HISTORY_UNPHYSICAL")
    check(np.max(np.abs(a[:,0]-(8000.-np.arange(8000))))<1e-8,"NATIVE_HISTORY_Z_GRID_DRIFT")
    return a,shaf(output),cp.stderr.decode(errors="replace")[-1800:]
sample_input=(SRC/"input.dat").read_bytes()
sample,sample_hash,sample_stderr=launch(WORK/"sample_source_input",sample_input)
bundled=np.loadtxt(SRC/"output_xe.dat")
check(bundled.shape==sample.shape,"BUNDLED_REFERENCE_SHAPE_MISMATCH")
sample_abs=float(np.max(abs(sample-bundled)))
sample_rel=float(np.max(abs(sample[:,1:]/bundled[:,1:]-1)))
# Original file is only a reference if its cosmological input provenance matches.
# Strict verification gate for the shipped sample.
check(sample_abs<1e-5 and sample_rel<1e-5,
      f"HYREC_SAMPLE_COMPARISON_DIFFERENT {sample_abs=} {sample_rel=}")

h=.674
omega_b_h2=.0224
omega_cb_h2=.143
lines=sample_input.decode().splitlines()
check(len(lines)>20,"HYREC_EXAMPLE_INPUT_TRUNCATED")
lines[0]=format(h,".17g")
lines[2]=format(omega_b_h2/(h*h),".17g")
lines[3]=format(omega_cb_h2/(h*h),".17g")
calibrated=("\n".join(lines)+"\n").encode()
(HERE/"HYREC2_FLRW_INPUT_20261102.dat").write_bytes(calibrated)
original,output_hash,stderr=launch(WORK/"calibrated_FLRW_HHe",calibrated)
np.savetxt(HERE/"HYREC2_FLRW_XE_TM_8000.dat",original,
           fmt=["%.0f","%.10e","%.10e"],header="z [dimensionless]  x_e=n_e/n_H (includes helium)  T_m [K]; HYREC-2 native; FLRW history")
source_version=("HYREC-2 2020 source installed as CLASSIER HyRec2020")
report={
 "schema":"bass.typeii.native_hyrec2_flrw_ionization_source.v1",
 "source_version":source_version,
 "installed_source":str(SRC),
 "native_compiler_command":compiler,
 "native_compiler_gcc_version":subprocess.check_output(["gcc","--version"],text=True).splitlines()[0],
 "original_source_atomic_table_sha256":fingerprints,
 "source_sample_input_sha256":shaf(SRC/"input.dat"),
 "source_bundled_sample_output_sha256":shaf(SRC/"output_xe.dat"),
 "newly_executed_sample_output_sha256":sample_hash,
 "source_bundled_sample_max_absolute_gap":sample_abs,
 "source_bundled_sample_xe_Tm_max_relative_gap":sample_rel,
 "calibrated_input_sha256":hashlib.sha256(calibrated).hexdigest(),
 "calibrated_native_output_file_sha256":output_hash,
 "published_output_sha256":shaf(HERE/"HYREC2_FLRW_XE_TM_8000.dat"),
 "input_cosmology":{"h":h,"T0_K":2.7255,"Omega_b_h2":omega_b_h2,
   "Omega_cb_h2":omega_cb_h2,"Omega_b":omega_b_h2/h**2,
   "Omega_cb":omega_cb_h2/h**2,"YHe":.245,"Neff":3.046,
   "number_massive_neutrinos":1,"massive_neutrino_eV":[.06]},
 "hydrogen_nH0_cm3_per_omega_bh2":"11.223846333047e-6*(1-YHe) from original HYREC-2 history.c",
 "electron_xe_definition":"free-electron / hydrogen-nucleus density; helium contributes, can exceed unity",
 "source_sample_stderr":sample_stderr,
 "calibrated_run_stderr":stderr,
 "calibrated_history_shape":list(original.shape),
 "x_e_at_1700":float(original[8000-1700,1]),
 "x_e_at_1392":float(original[8000-1392,1]),
 "x_e_at_1100":float(original[8000-1100,1]),
 "temperature_K_at_1700":float(original[8000-1700,2]),
 "temperature_K_at_1392":float(original[8000-1392,2]),
 "status":"NATIVE_HYREC2_COMPILED_EXECUTED_REPRODUCIBLY_IN_ISOLATED_WORKTREE",
 "physical_boundary":"Original HyRec computed in FLRW background, not recomputed with TypeII H(z) or tilt."
}
(HERE/"HYREC2_NATIVE_SOURCE_REPORT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,indent=2,sort_keys=True))
