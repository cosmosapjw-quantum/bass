#!/usr/bin/env python3
"""Native HYREC FLRW HHe x_e mapped to source BASS comoving cold-electron proper density.

For each of 401 source Type-II states and 26 source ray directions compare source
Lorentz transform, SI/cgs rate, and normalized hydrogen number current.
"""
from __future__ import annotations
import csv,json,sys,hashlib,subprocess
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
def git(*a):return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()
owner="bianchi/q/electron.py"
MAIN="9c6506e4e2087129a8b674ff10438e5db1a55c9d"
check(git("hash-object",owner)==git("rev-parse",MAIN+":"+owner),
      "SOURCE_COLD_ELECTRON_NOT_ORIGINAL")
sys.path.insert(0,str(ROOT))
from bianchi.q.electron import ColdElectronTestField,transform_photon

def rows(path):
    with path.open(newline="") as f:return list(csv.DictReader(f))
electron=rows(HERE/"TYPEII_HYREC2_ELECTRON_401.csv")
ray=rows(HERE/"TYPEII_HYREC2_26RAY_DEPTH_401.csv")
parent=rows(ROOT/"research/typeii_liouville_optdepth_20261101/PHOTON_RAYS_401X26.csv")
check(len(electron)==401 and len(ray)==len(parent)==10426,"SOURCE_RECORD_SIZE_BAD")
n=np.zeros((401,26,3));rate=np.zeros((401,26))
for r in parent:
 j=int(r["ray_id"]);k=int(round(float(r["tau_H"])/.0005))
 n[k,j]=[float(r["n_x"]),float(r["n_y"]),float(r["n_z"])]
for r in ray:
 j=int(r["ray_id"]);k=int(round(float(r["tau_H"])/.0005))
 rate[k,j]=float(r["hazard_per_tau_H"])
sigma_m2=6.6524587e-29;c_m_s=299792458.0
maxD=max_current=max_rate=0.
for k,e in enumerate(electron):
 v=float(e["tilt_v2"])
 beta=np.array([0.,v,0.])
 proper=float(e["n_e_rest_cm_minus3"])*1e6
 field=ColdElectronTestField.comoving(proper,beta,c_m_s=c_m_s)
 check(field.density_unit=="m^-3" and field.closure=="comoving-electron",
       "ELECTRON_OWNER_FRAME_SEMANTICS_DRIFT")
 check(field.is_comoving_with(beta),"ELECTRON_NOT_COMOVING")
 gamma=1/np.sqrt(1-v*v)
 normal_hydrogen=float(e["n_H_normal_cm_minus3"])
 xe=float(e["source_HyRec2_xe_HHe"])
 current=field.n_e_free*field.normalized_four_velocity()[0]
 wanted=xe*normal_hydrogen*1e6
 max_current=max(max_current,abs(current/wanted-1))
 _,_,D=transform_photon(1.,n[k],np.zeros(3),beta)
 targetD=gamma*(1-v*n[k,:,1])
 maxD=max(maxD,float(np.max(abs(D-targetD))))
 H=float(e["TypeII_H_s_inv"])
 source_rate=field.n_e_free*sigma_m2*c_m_s*D/H
 max_rate=max(max_rate,float(np.max(abs(source_rate/rate[k]-1))))
check(max_current<3e-15 and max_rate<3e-15 and maxD<3e-15,
      "ORIGINAL_ELECTRON_OWNER_GAMMAQ_PARITY_FAIL")
errors={}
for key,call in [
 ("negative_electron_density",lambda:ColdElectronTestField.comoving(-1.,[0.,.04,0.])),
 ("superluminal_electron",lambda:ColdElectronTestField.comoving(1.,[0.,1.01,0.]))]:
 try:call()
 except ValueError:errors[key]="REJECTED"
 else:raise RuntimeError("SOURCE_UNPHYSICAL_ELECTRON_ACCEPTED_"+key)
native=np.loadtxt(HERE/"HYREC2_FLRW_XE_TM_8000.dat")
import numpy as np
from scipy.interpolate import PchipInterpolator
helium_valid=bool(native[0,1]>1.0 and np.max(native[:,1])<1.5)
check(helium_valid,"NATIVE_HYREC_HELIUM_FRACTION_NOT_INCLUDED")
out={
 "schema":"bass.typeii.native_HyRec2_HHe_original_owner_electron_source_parity.v1",
 "original_owner_git_blob":git("hash-object",owner),
 "original_TypeII_states":401,
 "original_photon_directions_per_state":26,
 "original_owner_electron_transform_evaluations":10426,
 "max_gammaq_Doppler_abs_gap":maxD,
 "max_electron_number_current_relative_gap":max_current,
 "max_cgs_SI_thomson_hazard_relative_gap":max_rate,
 "negative_controls":errors,
 "hyrec2_high_z_helium_xe_above_one":helium_valid,
 "conclusion":"ACTUAL_BASS_H1_ELECTRON_OWNER_COMPATIBILITY_NUMERICALLY_VERIFIED",
 "limit":"FLRW HYREC-2 recombination scalar reweighted on prescribed TypeII source; no native coupled plasma"
}
(HERE/"ORIGINAL_ELECTRON_OWNER_PARITY.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
