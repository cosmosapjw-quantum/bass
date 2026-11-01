#!/usr/bin/env python3
"""Scientific envelope for BASS Type II: source-Saha vs fully H-ionized and naive FLRW density.

The H0 normalization and prescribed thermal bath remain fixed. These comparisons
are conditional model systematics, not precision recombination accuracy.
"""
from __future__ import annotations
import contextlib,csv,io,json,runpy
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    m=runpy.run_path(str(HERE/"source_saha_transport.py"))
def check(condition,message):
    if not bool(condition):raise RuntimeError(message)
times=np.asarray(m["times"])
J0=float(m["J_H0"]); c=float(m["C_CM_S"])
sigma=float(m["SIGMA_T_CM2"])
nH0=float(m["nH_rest0_cm3"])
v0=float(m["v0"])
parent_depth=np.asarray(m["depth"])
R=26
results={}
for order in (8,16):
    gx,gw=leggauss(order)
    Tfull=np.zeros(R);Tlegacy=np.zeros(R)
    for lo,hi in zip(times[:-1],times[1:]):
        qt=lo+0.5*(hi-lo)*(gx+1)
        p=m["evaluate_physical"](qt)
        ny=m["direction_interp"](qt)
        v=p["v"];H=p["H"]
        sourcexe=p["xe"]
        nu_normal_full=(sigma*c*J0*np.exp(-3*qt)/H)
        z=p["zmean"]
        legacyxe=np.asarray(m["source_saha_flrw"](z,m["OM_B_H2"],m["U"].T_CMB_K))
        nHlegacy=nH0*np.exp(-3*qt)
        gamma=p["gamma"]
        # Naively using FLRW proper H density with tilted electrons adds Gamma,
        # whereas the conservation-law current has Gamma(n_Hrest) fixed.
        nu_normal_legacy=sigma*c*legacyxe*nHlegacy*gamma/H
        weight=gw[None,:]
        Tfull+=0.5*(hi-lo)*np.sum(weight*nu_normal_full[None,:]*(1-v[None,:]*ny),axis=1)
        Tlegacy+=0.5*(hi-lo)*np.sum(weight*nu_normal_legacy[None,:]*(1-v[None,:]*ny),axis=1)
    results[order]=(Tfull,Tlegacy)
full,legacy=results[8]
full16,legacy16=results[16]
error=float(max(np.max(abs(full-full16)),np.max(abs(legacy-legacy16))))
check(error<6e-11,"SENSITIVITY_QUADRATURE_ORDER_DISAGREEMENT")
Saha=parent_depth[:,-1]
check(np.all(full>=Saha-1e-11),"FULLY_IONIZED_UPPER_BOUND_VIOLATION")
check(np.all(legacy>0),"LEGACY_POSITIVE_RATE_VIOLATED")
diff=full-Saha
check(np.min(diff)>0.1,"RECOMBINATION_SCENARIO_EFFECT_NOT_DETECTED")
p=int(m["axis_p"]);n=int(m["axis_m"])
def asym(values):
    return float((values[n]-values[p])/(values[n]+values[p]))
summary={
 "schema":"bass.typeii.highz_saha_ionization_model_sensitivity.v1",
 "source_scope":"same TypeII 401 background, same H normalization and thermal bath",
 "saha_model":"original source hydrogen-only Saha with conserved hydrogen proper current",
 "full_hydrogen_ionization":"x_e=1 upper-envelope source-conditional variant",
 "legacy_comparator":"FLRW x_e(zmean)*nH_FLRW(zmean) incorrectly interpreted as tilted electron proper density",
 "rays":R,
 "Gauss_8_vs_16_max_abs_gap":error,
 "mean_source_saha_end_depth":float(np.mean(Saha)),
 "mean_full_ionized_end_depth":float(np.mean(full)),
 "mean_naive_FLRW_end_depth":float(np.mean(legacy)),
 "full_ionized_minus_Saha_endpoint_depth_min":float(np.min(diff)),
 "full_ionized_minus_Saha_endpoint_depth_max":float(np.max(diff)),
 "naive_FLRW_minus_proper_Saha_endpoint_min":float(np.min(legacy-Saha)),
 "naive_FLRW_minus_proper_Saha_endpoint_max":float(np.max(legacy-Saha)),
 "saha_axial_asymmetry":asym(Saha),
 "fully_ionized_axial_asymmetry":asym(full),
 "naive_FLRW_axial_asymmetry":asym(legacy),
 "H_anchor_x2_endpoint_depth_factor":0.5,
 "model_status":"SCOPED_IONIZATION_AND_DENSITY_FRAME_SENSITIVITY_NUMERICALLY_CHECKED",
 "not_claimed":"accurate HyRec/Peebles recombination or a self-consistent Bianchi baryon-photon solution"
}
(HERE/"MODEL_SENSITIVITY.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
with (HERE/"MODEL_SENSITIVITY_26.csv").open("w",newline="") as f:
    wr=csv.writer(f,lineterminator="\n")
    wr.writerow(["ray_id","saha_current_depth","full_ionized_depth",
                 "naive_FLRW_tilted_proper_depth","full_minus_saha","legacy_minus_saha"])
    for j in range(R):
        wr.writerow([j]+[format(float(z),".17g") for z in [
          Saha[j],full[j],legacy[j],full[j]-Saha[j],legacy[j]-Saha[j]]])
print(json.dumps(summary,indent=2,sort_keys=True))
