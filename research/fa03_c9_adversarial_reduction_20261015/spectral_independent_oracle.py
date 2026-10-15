"""Independent mpmath spectral oracle for positive constant-coefficient Jones ODE.

Not the full variable-coefficient FA03 ray history. Tests C8 holomorphic-energy
contraction theorem with independently evaluated exact GL node/weight polynomials.
No NumPy binary64 Stokes solver is used in this oracle.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
import mpmath as mp

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"fa03_c8_error_budget_20261015"))
import spectral_cert as cert

def constant_polarized_state(e,k,epsilon):
    h=(mp.mpf(1)/5,mp.mpf(2)/5)
    off=mp.mpc(mp.mpf(1)/10,mp.mpf(1)/20)
    P=((mp.mpf(7)/10,off),(mp.conj(off),mp.mpf(3)/10))
    alpha=1+epsilon*(e*k-1)
    src=e**3*(1+e*k/10)
    T=mp.mpf(1)/2
    F=[]
    for i in range(2):
        row=[]
        for j in range(2):
            z=alpha*(h[i]+h[j])
            integral=-mp.expm1(-z*T)/z if z else T
            row.append(src*P[i][j]*integral)
        F.append(tuple(row))
    return tuple(F)

def norm_hermitian2(F):
    a=mp.re(F[0][0]);d=mp.re(F[1][1]);b=F[0][1]
    ev1=(a+d+mp.sqrt((a-d)**2+4*abs(b)**2))/2
    ev2=(a+d-mp.sqrt((a-d)**2+4*abs(b)**2))/2
    return abs(ev1)+abs(ev2)

def energy_integral(k,epsilon,dps=70,orders=(2,3,4,5,6,8)):
    mp.mp.dps=dps
    k=mp.mpf(str(k));epsilon=mp.mpf(str(epsilon))
    lo=mp.mpf(49)/50;hi=mp.mpf(51)/50
    true=[[25*mp.quad(lambda e:constant_polarized_state(e,k,epsilon)[i][j],[lo,hi]) for j in range(2)] for i in range(2)]
    rows=[]
    for n in orders:
        points,weights=mp.gauss_quadrature(n,"legendre")
        q=[[sum(weights[z]*constant_polarized_state(1+mp.mpf(1)/50*points[z],k,epsilon)[i][j]
                 for z in range(n))/2 for j in range(2)] for i in range(2)]
        diff=[[q[i][j]-true[i][j] for j in range(2)] for i in range(2)]
        err=norm_hermitian2(diff)
        bound=mp.mpf(cert.certificate(n).numerator)/cert.certificate(n).denominator
        if err>bound:
            raise ArithmeticError("GL_CERTIFICATE_INDEPENDENT_ORACLE_REJECT")
        rows.append({"n":n,"true_GL_error_trace_norm":mp.nstr(err,36),
           "C8_derived_upper":mp.nstr(bound,36),
           "error_to_upper_ratio":mp.nstr(err/bound,26),
           "subtheorem_pass":True})
    return {"schema":"bass.fa03.c9.independent_mp_constant_positive_jones.v1",
      "dps":dps,"k":mp.nstr(k,12),"epsilon":mp.nstr(epsilon,12),
      "source":"actual frozen P3 complex Hermitian 2x2 principal block; manufactured positive constant H=(.2,.4), no observer angular history",
      "numerics":"mpmath holomorphic e scalar Jones exact analytic time solution, mpmath Gauss and adaptive analytic integral independently",
      "rows":rows,"actual_full_variable_FA03_theorem_review":"algebraic scope only",
      "full_FA03_time_RK4_numeric_certification":None}

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    runs=[energy_integral(k,eps) for k,eps in [(1.0,-.1),(1.3,.1),(1.615,.1)]]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({"runs":runs},indent=2)+"\n")
    for z in runs:
        print(z["k"],z["epsilon"],[(r["n"],r["true_GL_error_trace_norm"],r["error_to_upper_ratio"]) for r in z["rows"]],flush=True)
