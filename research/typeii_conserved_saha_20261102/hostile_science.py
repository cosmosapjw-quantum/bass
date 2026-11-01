#!/usr/bin/env python3
"""Single bounded same-author blind-style science audit of BASS source Saha Type-II.

Execute explicit bad models against the accepted 401x26 physical source.
The invalid models are local counterexamples, not global no-go theorems.
"""
from __future__ import annotations
import contextlib,io,json,runpy
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    m=runpy.run_path(str(HERE/"source_saha_transport.py"))
def check(ok,msg):
    if not bool(ok):raise RuntimeError(msg)
x,w=leggauss(8)
times=np.asarray(m["times"])
true=m["depth"][:,-1]
bad_double=np.zeros(26)
bad_missing_gamma=np.zeros(26)
bad_unconserved_proper=np.zeros(26)
for lo,hi in zip(times[:-1],times[1:]):
    t=lo+0.5*(hi-lo)*(x+1)
    p=m["evaluate_physical"](t)
    ny=m["direction_interp"](t)
    q=1-p["v"][None,:]*ny
    W=p["nu_normal"][None,:]
    width=(hi-lo)*.5
    bad_double+=width*((W*q*q)@w)
    bad_missing_gamma+=width*((W*q/p["gamma"][None,:])@w)
    # Keep x_e as accepted; a wrong "proper nH~a^-3" law would replace the
    # conserved normal-current Gamma0/ Gamma factor by the varying Gamma/Gamma0.
    bad_unconserved_proper+=width*((W*q*p["gamma"][None,:]/m["gamma0"])@w)
p=int(m["axis_p"]);n=int(m["axis_m"])
delta_double=bad_double-true
delta_gamma=bad_missing_gamma-true
delta_current=bad_unconserved_proper-true
check(delta_double[p]<-.5 and delta_double[n]>.5,
      "BAD_DOUBLE_Q_DID_NOT_SHOW_AXIAL_SIGN_DEPENDENCE")
check(np.max(abs(delta_gamma))>.03,"MISSING_GAMMA_RATE_ERROR_UNDETECTED")
check(np.max(abs(delta_current))>.001,"UNCONSERVED_HYDROGEN_PROPER_COUNTEREXAMPLE_UNDETECTED")
check(np.all(np.isfinite(bad_double)),"INVALID_COUNTERMODEL")
check(float(np.min(true))>0 and float(np.max(true))<100,
      "FALSE_PHYSICAL_COSMOLOGICAL_DEPTH_ADMISSION")
# Proof of modeling dependency: the physical model's electron "H1" source
# has no Einstein-fluid backreaction; Stage-II canonical evidence stays HOLD.
limitations=[
 "TypeII gamma-law background not closed with source baryon/electron/radiation energy",
 "Saha hydrogen high-z equilibrium and isotropic matter temperature assumed",
 "FLRW anchor H0,nH0 is calibration, not a derived Bianchi cosmological initial data set",
 "CMB visibility and photon Thomson gain/loss/polarization not computed",
 "original full SahaHistory API not executed because optional JAX import unavailable",
 "no native HyRec/CosmoRec numerical comparison",
]
out={
 "schema":"bass.typeii.conserved_saha.single_pass_hostile_controls.v1",
 "auditor":"same author, one bounded hostile pass, no native subagent or distinct-author blind referee",
 "original_26_ray_depth_range":[float(min(true)),float(max(true))],
 "wrong_second_q_plus_endpoint_delta":float(delta_double[p]),
 "wrong_second_q_minus_endpoint_delta":float(delta_double[n]),
 "wrong_second_q_max_abs_delta":float(max(abs(delta_double))),
 "wrong_missing_Gamma_max_abs_delta":float(max(abs(delta_gamma))),
 "wrong_unconserved_hydrogen_nHrest_max_abs_delta":float(max(abs(delta_current))),
 "source_scope_limits":limitations,
 "verdict":"HOSTILE_COUNTEREXAMPLES_SOURCE_SCOPED_PASS; PHYSICAL_PRODUCTION_HOLD",
}
(HERE/"HOSTILE_SCIENCE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
