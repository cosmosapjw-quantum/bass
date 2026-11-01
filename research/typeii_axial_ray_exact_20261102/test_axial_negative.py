#!/usr/bin/env python3
"""Hostile analytic controls for TypeII axial symmetry and proper Thomson optical depth.
Independent algebra, no production mutation.
"""
from pathlib import Path
import json
import numpy as np

root=Path(__file__).resolve().parent
summary=json.loads((root/"AXIAL_ORACLE_RESULT.json").read_text())
v=float(summary["weighted_mean_tilt"])
if not (0.0467 < v < 0.05): raise AssertionError('PHYSICS_GATE_AT_test_axial_negative.py_LINE_12')
S=np.sqrt(3)
sp=.2375;sm=0.;s13=-0.11295198246134101;n1=.865
shear=np.array([[-2*sp,0,S*s13],[0,sp+S*sm,0],[S*s13,0,sp-S*sm]])
N=np.diag([n1,0.,0.])
R=np.array([0,S*s13,0.])
def direction_rate(n,Sigma=shear):
    return -Sigma@n+(n@Sigma@n)*n+np.cross(R,n)-np.cross(n,N@n)
for sign in (-1.,1.):
    n=np.array([0.,sign,0.])
    if not (np.max(np.abs(direction_rate(n))) < 1e-16): raise AssertionError('PHYSICS_GATE_AT_test_axial_negative.py_LINE_22')
# The invariance critically uses Sigma_{xy}=0, not merely Bianchi II class A.
perturbed=shear.copy(); perturbed[0,1]=perturbed[1,0]=0.02
offaxis=direction_rate(np.array([0.,1.,0.]),Sigma=perturbed)
if not (abs(offaxis[0] + 0.02) < 1e-15 and abs(offaxis[1]) < 1e-15): raise AssertionError('PHYSICS_GATE_AT_test_axial_negative.py_LINE_26')
# Test constant tilt where the asymmetry is exactly v; negative v reverses its sign.
for beta in [-.6,-.1,0.,.1,.6]:
    gg=1/np.sqrt(1-beta*beta)
    tplus=.2*gg*(1-beta)
    tminus=.2*gg*(1+beta)
    asym=(tminus-tplus)/(tminus+tplus)
    if not (abs(asym - beta) < 1e-15): raise AssertionError('PHYSICS_GATE_AT_test_axial_negative.py_LINE_33')
# Deliberate wrong-frame rate: q-only vs gamma q changes finite-tilt optical depth.
positive=summary["positive_axis"]["tau_endpoint"]
wrong=positive-summary["negative_control_q_only_gap"]
if not (abs(positive - wrong) > 0.0002): raise AssertionError('PHYSICS_GATE_AT_test_axial_negative.py_LINE_37')
if not (summary['negative_control_double_q_gap'] > 0.009): raise AssertionError('PHYSICS_GATE_AT_test_axial_negative.py_LINE_38')
# Analytic symmetry makes normal-frame energies identical for +/- axial rays,
# but electron-frame energies differ, a nontrivial frame check.
x=summary["positive_axis"];y=summary["negative_axis"]
if not (x['E_normal_endpoint'] == y['E_normal_endpoint']): raise AssertionError('PHYSICS_GATE_AT_test_axial_negative.py_LINE_42')
if not (x['E_electron_endpoint'] < x['E_normal_endpoint'] < y['E_electron_endpoint']): raise AssertionError('PHYSICS_GATE_AT_test_axial_negative.py_LINE_43')
print(json.dumps({
 "schema":"bass.typeii.axial_exact.hostile_control.v1",
 "offaxis_shear_perturbation_rate_x":float(offaxis[0]),
 "constant_tilt_asymmetry_cases":5,
 "positive_depth_gap":float(summary["depth_difference"]),
 "negative_q_only_abs_gap":float(summary["negative_control_q_only_gap"]),
 "negative_double_q_abs_gap":float(summary["negative_control_double_q_gap"]),
 "verdict":"EXPECTED_NEGATIVE_CONTROLS_AND_AXIS_PROOF_PASS",
 "caveat":"This axis test cannot detect the sign of TypeII curvature for n=+/-ey; off-axis tests remain source-owned."
},indent=2,sort_keys=True))
