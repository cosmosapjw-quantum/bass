"""Conditional exact-rational IEEE64 aggregation error for FA03 Stokes quadrature.

Assumes incoming exact physical per-ray/per-energy Stokes and exact positive
quadrature weights and scalar multiplicative rounding; source evaluation,
time integration, weight generation and hardware-specific fused ops are NOT
included. It must never be reported as a whole-solver roundoff certificate.
"""
from __future__ import annotations
from fractions import Fraction as Q
import json
import spectral_cert as c

U=Q(1,2**53)
# max positive real energy e=51/50, exact ray L*k bound 202/125,
# B in trace norm <= e^3*(1+0.1*e*kmax)*Tr P3.
B_REAL=Q(51,50)**3*(1+Q(1,10)*Q(51,50)*c.MAX_REAL_RAY_K)
F_REAL=c.TIME_SPAN*B_REAL

def gamma(k):
    if isinstance(k,bool) or not isinstance(k,int) or k<=0:
        raise ValueError("positive integer reduction terms required")
    if k*U>=1: raise ValueError("roundoff series divergence, k too large")
    return k*U/(1-k*U)

def stokes_reduce_bound(nrays,ne):
    if not isinstance(nrays,int) or not isinstance(ne,int) or nrays<1 or ne<1:
        raise ValueError("positive dimensions")
    n=nrays*ne
    # Each of the 4 Stokes components bounded by I=TrF for physical
    # positive-coherency ray trajectories, weighted number/energy mean.
    # || delta F ||_1 <= sum_k |delta S_k| from Pauli basis, so <=4 M*gamma_n.
    bound=4*F_REAL*gamma(n)
    return {"nrays":nrays,"ne":ne,"n_terms":n,"unit_roundoff":"1/2^53",
       "max_real_spectral_trace_exact":str(F_REAL),
       "float_one_step_gamma_exact":str(gamma(n)),
       "conditional_aggregation_trace_bound_exact":str(bound),
       "conditional_aggregation_trace_bound_decimal":float(bound),
       "certified_binary64_whole_transport_error":None,
       "source_error":"NOT_INCLUDED",
       "geometry_and_quadrature_weight_roundoff":"NOT_INCLUDED",
       "time_RK4_roundoff":"NOT_INCLUDED"}

def summary():
    return {"schema":"bass.fa03.c8.conditional_aggregation_roundoff.v1",
        "assumptions":"IEEE754 binary64 correctly rounded weights*Stokes and additions, exact unrounded source Stokes and exact normalized positive ray/energy weights; no overflow/underflow",
        "methods":"Higham gamma_N for each of four Stokes component reductions, Schatten1 error <= sum component errors",
        "cases":[stokes_reduce_bound(n,nE) for n in (36,144,480) for nE in (4,5,8)],
        "whole_solver_roundoff_certified":False}

if __name__=="__main__": print(json.dumps(summary(),indent=2))
