#!/usr/bin/env python3
"""One bounded hostile/source-identity pass for native HYREC2 -> original TypeII.

Falsify relative-flux q duplication, electron rest/current Gamma confusion,
helium fraction clipping and false calibrated-source claims.
"""
import csv,json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import simpson

HERE=Path(__file__).resolve().parent
summary=json.loads((HERE/"HYREC2_TYPEII_THOMSON_RESULTS.json").read_text())
phy=list(csv.DictReader((HERE/"TYPEII_HYREC2_ELECTRON_401.csv").open(newline="")))
rows=list(csv.DictReader((HERE/"TYPEII_HYREC2_26RAY_DEPTH_401.csv").open(newline="")))
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
check(len(phy)==401 and len(rows)==401*26,"SOURCE_ROWS_BAD")
q=np.zeros((26,401)); rate=np.zeros((26,401)); depth=np.zeros((26,401));t=np.array([float(x["tau_H"]) for x in phy])
gam=np.array([float(x["electron_Gamma"]) for x in phy])
for row in rows:
 j=int(row["ray_id"]);k=int(round(float(row["tau_H"])/.0005))
 q[j,k]=float(row["relative_flux_q_one_factor"])
 rate[j,k]=float(row["hazard_per_tau_H"])
 depth[j,k]=float(row["cumulative_Thomson_depth"])
true=depth[:,-1]
baseline=simpson(rate,x=t,axis=1)
max_baseline=float(np.max(abs(baseline-true)))
check(max_baseline<3e-7,"NUMERICAL_CONTROL_BASELINE_NOT_MATCHED")
wrong_double=simpson(rate*q,x=t,axis=1)
wrong_no_gamma=simpson(rate/gam[None,:],x=t,axis=1)
wrong_unconserved=simpson(rate*gam[None,:]/gam[0],x=t,axis=1)
delta_double=wrong_double-true
delta_no_gamma=wrong_no_gamma-true
delta_current=wrong_unconserved-true
a_p=int(summary["Thomson_depth_plus_ey"]==min(summary["Thomson_depth_plus_ey"],summary["Thomson_depth_minus_ey"]))
plus=3;minus=2
check(np.all(q[plus]<1) and np.all(q[minus]>1),
      "AXIAL_DIRECTION_NOT_EQUAL_Q_PLUS_MINUS")
check(delta_double[plus]<-.8 and delta_double[minus]>.8,
      "DOUBLE_FLUX_NEGATIVE_CONTROL_NOT_SEEN")
check(max(abs(delta_no_gamma))>.02,"MISSING_GAMMA_SOURCE_ERROR_NOT_DETECTED")
check(max(abs(delta_current))>.001,"UNCONSERVED_HYDROGEN_NUMBER_CURRENT_NOT_DETECTED")
hyrec=np.loadtxt(HERE/"HYREC2_FLRW_XE_TM_8000.dat")
helium_above_one=float(np.max(hyrec[:,1]-1))
check(helium_above_one>.15,"HYREC_HELIUM_HHE_FRACTION_NOT_PRESENT")
# No prior BASS/HYREC source, main branch, or production dispatcher is modified.
limits=[
 "HYREC-2 solved FLRW H(z), not Bianchi TypeII atomic kinetic equations with tilted electron source",
 "Hubble amplitude anchored to fiducial FLRW rather than a joint typeII Einstein/baryon radiation constraint",
 "Hydrogen number current and electron comoving field are imposed conditional closures",
 "26-ray attenuation kernel to zmean=300 excludes scattering gain, polarization and observed z=0 line of sight",
 "Source original HYREC helium x_e>1 must not be clipped to <=1",
 "This independent model check is same-author, no native subagent or different author referee",
]
data={
 "schema":"bass.typeii.native_HyRec2_conditional_transport.hostile_control.v1",
 "baseline_simpson_vs_Gauss_max_abs_gap":max_baseline,
 "wrong_double_flux_plus_depth_delta":float(delta_double[plus]),
 "wrong_double_flux_minus_depth_delta":float(delta_double[minus]),
 "wrong_double_flux_max_abs_delta":float(max(abs(delta_double))),
 "wrong_missing_gamma_max_abs_delta":float(max(abs(delta_no_gamma))),
 "wrong_unconserved_rest_hydrogen_max_abs_delta":float(max(abs(delta_current))),
 "native_HyRec_helium_xe_excess_above_unity":helium_above_one,
 "structural_claim_holds":limits,
 "review_kind":"same author hostile, no native subagent or distinct blind reviewer",
 "verdict":"HOSTILE_SOURCE_MODELS_REFUTED_LOCALLY; PRODUCTION_GATE_HOLD"
}
(HERE/"HOSTILE_MODEL_RESULTS.json").write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
print(json.dumps(data,indent=2,sort_keys=True))
