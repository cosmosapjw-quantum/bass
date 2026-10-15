"""Exact-rational spectral Gauss certificate for the FROZEN FA03 real-ray model.

Certified mathematical *spectral quadrature* error for the exact ODE output,
not numerical RK4 time/roundoff/angular integration or empirical atom opacity.
No use of a sampled residual supremum or guessed complex-angle envelope.
"""
from __future__ import annotations
from fractions import Fraction as Q
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
C7=ROOT.parent/"fa03_c7_polarized_batch_20261015"
C5=ROOT.parent/"fa03_c5_angular_cap_20261015"/"reference"
SHA={
 "fa02.py":"1e89e75f7a08d2eec1851a58e602c2683b1888a37b3e1fe10b1be4234756eee5",
 "fa03.py":"ad865127da7c2f9ea613541571f9b842f9da7630af9bb951a3df5968ad44ecf7",
}
RADIUS=Q(1,2)
ENERGY_BAND_HALF=Q(1,50)
MAX_REAL_RAY_K=Q(202,125)     # k=L*x^(-2/3)*v; L<=exp(1/125)<101/100, x^(-2/3)<=8/5.
EPSILON_BOUND=Q(1,10)
P3_TRACE=Q(1)
TIME_SPAN=Q(1,2)
MIN_HERMITIAN_G_FACTOR=Q(411,625)
B_TRACE_BOUND=Q(41931,10000) # (3/2)^3*(1+(1/10)*(3/2)*(202/125))*Trace(P3)
F_TRACE_BOUND=Q(41931,20000) # duration 1/2 * source bound; Jones U contractive.
NORMALIZED_GEOMETRIC_RATIO=Q(1,25)

def source_lock():
    for name,expected in SHA.items():
        p=C5/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise ValueError("FA03_SOURCE_IDENTITY_MISMATCH:"+name)
    return dict(SHA)

def certificate(n:int)->Q:
    """Absolute trace-norm GL-n spectral quadrature error, exact rational.

    Error <=2*M*r^(2n)/(1-r), M=41931/20000, r=1/25.
    The Gauss rule integrates Taylor degree <=2n-1 exactly, and both
    normalized positive means have norm 1.
    """
    if isinstance(n,bool) or not isinstance(n,int) or n<1:
        raise ValueError("positive integer GL order required")
    return 2*F_TRACE_BOUND*NORMALIZED_GEOMETRIC_RATIO**(2*n)/(1-NORMALIZED_GEOMETRIC_RATIO)

def best_order(tolerance,maximum=32):
    """Fail closed on binary64/invalid/ambiguous tolerance input."""
    if isinstance(tolerance,float) or isinstance(tolerance,bool):
        raise ValueError("tolerance use decimal string or Fraction, not binary float")
    try:
        t=Q(tolerance)
    except (ZeroDivisionError,TypeError,ValueError) as e:
        raise ValueError("positive exact tolerance required") from e
    if t<=0:raise ValueError("strictly positive target required")
    if not isinstance(maximum,int) or maximum<1:raise ValueError("positive search limit")
    for n in range(1,maximum+1):
        if certificate(n)<=t:return n
    raise ValueError("target stricter than supplied bounded quadrature order")

def analytic_claims():
    source_lock()
    # Source matrix 3x3: P3 PSD, block det=7/10*3/10 -1/10^2-1/20^2=79/400.
    minor=Q(7,10)*Q(3,10)-Q(1,10)**2-Q(1,20)**2
    assert minor==Q(79,400)
    # 2^(2/3)<8/5 and exp(1/125)<=125/124<101/100.
    assert Q(4)<Q(8,5)**3
    assert Q(125,124)<Q(101,100)
    assert MAX_REAL_RAY_K==Q(101,100)*Q(8,5)
    assert MIN_HERMITIAN_G_FACTOR==1-EPSILON_BOUND*(1+Q(3,2)*MAX_REAL_RAY_K)
    assert B_TRACE_BOUND==Q(3,2)**3*(1+EPSILON_BOUND*Q(3,2)*MAX_REAL_RAY_K)*P3_TRACE
    assert F_TRACE_BOUND==TIME_SPAN*B_TRACE_BOUND
    assert NORMALIZED_GEOMETRIC_RATIO==ENERGY_BAND_HALF/RADIUS
    return {
      "source_sha256":SHA,
      "signature":"(-,+,+,+)",
      "detector":"any positive normal-weight real ray average within frozen FA03 cap, including original36",
      "observer":{"chi":"1/125","psi":"1/100","delta_rad":"1/50"},
      "normalized_e_interval":["49/50","51/50"],
      "complex_energy_disk":"|e-1|<=1/2",
      "epsilon_bound":"|epsilon|<=1/10 (real)",
      "k_upper":str(MAX_REAL_RAY_K),"k_lower":"positive",
      "L_upper_rational":"101/100",
      "min_real_part_absorption_factor":str(MIN_HERMITIAN_G_FACTOR),
      "P3_2x2_principal_minor":str(minor),
      "P3_trace":str(P3_TRACE),
      "complex_energy_source_trace_bound":str(B_TRACE_BOUND),
      "exact_propagated_spectral_trace_bound":str(F_TRACE_BOUND),
      "time_span":str(TIME_SPAN),
      "Gauss_Taylor_ratio":str(NORMALIZED_GEOMETRIC_RATIO),
      "trace_norm_mean_error_exact":"(41931/9600)*(1/25)^(2*n)",
      "scientific_scope":"exact ODE finite-energy quadrature only; no RK4, input source, numerical quadrature weights roundoff, full angular cap, empirical atomic accuracy",
      "not_validated":{"time_RK4_global_error":None,"binary64_roundoff":None,"continuous_cap_angular_error":None,"empirical_photoionization":None}
    }

def report(orders=range(2,9),targets=("1e-7","1e-10","1e-13","1e-16")):
    d=analytic_claims()
    d["Gauss_orders"]=[{"n":n,"exact_numerator":certificate(n).numerator,
       "exact_denominator":certificate(n).denominator,
       "decimal":format(float(certificate(n)),".17g")} for n in orders]
    d["exact_tolerance_minimum_orders"]={t:best_order(t) for t in targets}
    return d

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    p.add_argument("--target",type=str)
    opts=p.parse_args()
    r=report()
    if opts.target:r["requested_target"]={"value":opts.target,"minimum_order":best_order(opts.target)}
    if opts.output:
        if opts.output.exists():raise FileExistsError(opts.output)
        opts.output.parent.mkdir(parents=True,exist_ok=True)
        opts.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(r,indent=2))
