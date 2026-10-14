"""Constructive analytic-strip *domain* theorem for frozen FA03 observer cap.

The bound 2*M4/(exp(4*N)-1) is rigorously conditional on a bound M4 for
the time-propagated matrix in the complex angular strip. This module proves
safeguards for analyticity, but does NOT produce M4 or a radial Gauss error.
"""
from __future__ import annotations
from fractions import Fraction as F
import json, math
import mpmath as mp

def strip_guards():
    chi,psi,delta=F(1,125),F(1,100),F(1,50)
    strip_width=4
    # Elementary estimates: cosh(4)<28; sinh(1/125)<9/1000.
    # 1-cos(psi)cos(r) <=(psi²+r²)/2, r<=delta.
    m0diff_upper=(psi**2+delta**2)/2 + psi*delta*F(28)
    m1_upper=psi+delta*F(28)
    Llower=F(99,100)
    n0diff_upper=F(7,1000)
    n1_upper=F(58,100)
    n2_upper=F(57,100)
    dm_guard=m1_upper**2
    hh_guard=n0diff_upper*(2+n0diff_upper)+n1_upper**2
    v_guard=F(3,4)*n2_upper**2
    conditions={
      "cosh4_less_28":math.cosh(4)<28,
      "sinh_chi_less_9over1000":math.sinh(float(chi))<.009,
      "m0diff_below_0p006":m0diff_upper<F(6,1000),
      "m1_below_0p57_proper":m1_upper<=F(57,100),
      "L_lower_greater_0p99":F(1)-F(9,1000)*F(6,1000)>Llower,
      "n0diff_upper_certified":F(6,1000)/Llower<n0diff_upper,
      "n1_upper_certified":m1_upper/Llower<n1_upper,
      "n2_upper_certified":delta*F(28)/Llower<n2_upper,
      "dm_sqrt_disk_lt1":dm_guard<1,
      "hh_sqrt_disk_lt1":hh_guard<1,
      "v_sqrt_disk_lt1":v_guard<1
    }
    if not all(conditions.values()):raise RuntimeError("STRIP_DOMAIN_GUARD_NOT_CLOSED")
    return {"width":strip_width,"conditions":conditions,
       "m0_minus1_upper":str(m0diff_upper),
       "m1_upper":str(m1_upper),
       "L_lower":str(Llower),
       "n0_minus1_bound":str(n0diff_upper),
       "n1_bound":str(n1_upper),
       "n2_bound":str(n2_upper),
       "dm_guard":str(dm_guard),
       "hh_guard":str(hh_guard),
       "v_guard":str(v_guard),
       "scope":"complex phi analytic domain for real r in [0,1/50], x in [1/2,1], frozen chi=1/125 psi=1/100 and matrix ODE solution",
       "complex_strip_transfer_envelope_M4":None,
       "radial_Gauss3_error_bound":None,
       "continuum_angular_error_bound":None}

def alias_coefficient(n,dps=60):
    if not isinstance(n,int) or n<1: raise ValueError("positive azimuthal order required")
    mp.mp.dps=max(35,dps)
    return 2/mp.expm1(4*n)

def demonstrate():
    return {"strip":strip_guards(),
      "N12_factor_times_unknown_M4":mp.nstr(alias_coefficient(12),38),
      "N16_factor_times_unknown_M4":mp.nstr(alias_coefficient(16),38),
      "alias_exact_manufactured":{
          "function":"cos(12*phi)","continuous_normalized_average":"0",
          "periodic_trapezoid_N12":"1","periodic_trapezoid_N16":"0",
          "meaning":"N=12 agreement of an unrelated field is not an all-harmonic theorem"},
      "conditional_bound":"||mean_phi F - trapezoid_N F|| <= 2*M4/(exp(4*N)-1)",
      "M4":"UNKNOWN, must bound exact complex-strip propagated transfer, not sampled real values",
      "numerically_admitted_angular_cap_error":None}

if __name__=="__main__":print(json.dumps(demonstrate(),indent=2))
