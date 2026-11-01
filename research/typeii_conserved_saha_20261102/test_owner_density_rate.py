#!/usr/bin/env python3
"""Owner BASS cold electron n_e proper, Lorentz source, SI/cgs Thomson rate parity."""
from __future__ import annotations
import csv,hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
main="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
rel="bianchi/q/electron.py"
g=lambda *arg:subprocess.check_output(["git","-C",str(ROOT),*arg],text=True).strip()
check(g("hash-object",rel)==g("rev-parse",main+":"+rel),"ELECTRON_OWNER_SOURCE_DRIFT")
sys.path.insert(0,str(ROOT))
from bianchi.q.electron import ColdElectronTestField,transform_photon

with (HERE/"HYDROGEN_SAHA_HISTORY_401.csv").open(newline="") as f:history=list(csv.DictReader(f))
with (ROOT/"research/typeii_liouville_optdepth_20261101/PHOTON_RAYS_401X26.csv").open(newline="") as f:
    source_rays=list(csv.DictReader(f))
check(len(history)==401 and len(source_rays)==10426,"SOURCE_HISTORY_RAY_COUNT_BAD")
hist=json.loads((HERE/"PHYSICAL_SAHA_THOMSON_SUMMARY.json").read_text())
dirs=np.empty((401,26,3))
for row in source_rays:
    k=int(round(float(row["tau_H"])/.0005));j=int(row["ray_id"])
    dirs[k,j]=[float(row["n_x"]),float(row["n_y"]),float(row["n_z"])]
sigma_cm2=float(hist["sigma_T_cm2_source"])
c_cm_s=float(hist["c_cm_s_source"])
sigma_m2=sigma_cm2*1e-4;c_m_s=c_cm_s/100
largest_D=0;largest_rate_rel=0;largest_normal_current_rel=0
for k,row in enumerate(history):
    n_eproper_m3=float(row["n_e_rest_cm_minus3"])*1e6
    nH_normal_cm3=float(row["n_H_normal_cm_minus3"])
    xe=float(row["x_e_H_only_source_Saha"])
    v=float(row["v2"]);H=float(row["H_s_inv"])
    beta=np.array([0.,v,0.])
    field=ColdElectronTestField.comoving(n_eproper_m3,beta,c_m_s=c_m_s)
    check(field.closure=="comoving-electron" and field.density_unit=="m^-3",
          "SOURCE_ELECTRON_FIELD_SEMANTICS_CHANGED")
    check(field.is_comoving_with(beta),"SOURCE_ELECTRON_VELOCITY_NOT_H1")
    U=field.normalized_four_velocity()
    gamma=1/np.sqrt(1-v*v)
    check(abs(U[0]-gamma)<3e-15,"SOURCE_ELECTRON_GAMMA_MISMATCH")
    norm_current=float(n_eproper_m3*U[0])
    should=xe*nH_normal_cm3*1e6
    largest_normal_current_rel=max(largest_normal_current_rel,abs(norm_current/should-1))
    _,_,D=transform_photon(1.0,dirs[k],np.zeros(3),beta)
    expected=gamma*(1-v*dirs[k,:,1])
    largest_D=max(largest_D,float(np.max(abs(D-expected))))
    original_physical_rate= n_eproper_m3*sigma_m2*c_m_s*D/H
    cgs_rate=float(row["nu_source_prefactor_Gamma_nu_rest"])*(1-v*dirs[k,:,1])
    largest_rate_rel=max(largest_rate_rel,float(np.max(abs(original_physical_rate/cgs_rate-1))))
check(largest_D<3e-15 and largest_rate_rel<3e-15 and largest_normal_current_rel<3e-15,
      "OWNER_ELECTRON_FRAME_DENSITY_SI_CGS_PARITY_FAIL")
negative_density_rejected=False;superluminal_rejected=False
try:ColdElectronTestField.comoving(-1.0,[0.,0.05,0.])
except ValueError:negative_density_rejected=True
try:ColdElectronTestField.comoving(1.,[0.,1.01,0.])
except ValueError:superluminal_rejected=True
check(negative_density_rejected and superluminal_rejected,"UNPHYSICAL_OWNER_ELECTRON_ACCEPTED")
out={
 "schema":"bass.source_saha.owner_H1_electron_SI_CGS_perray_parity.v1",
 "locked_electron_blob_sha1":g("hash-object",rel),
 "owner_frame":"ColdElectronTestField.comoving",
 "normal_ray_records":10426,
 "electron_density_knots":401,
 "max_Doppler_D_abs_gap":largest_D,
 "max_electron_normal_current_relative_gap":largest_normal_current_rel,
 "max_SI_CGS_full_ray_rate_relative_gap":largest_rate_rel,
 "negative_density_rejected":negative_density_rejected,
 "superluminal_electron_rejected":superluminal_rejected,
 "status":"ORIGINAL_H1_ELECTRON_FRAME_RATE_NUMERICALLY_CHECKED",
 "scope":"Source Saha proper density is a conditional input; not native electron thermal model"
}
(HERE/"OWNER_ELECTRON_RATE_PARITY.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
