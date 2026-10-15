"""Source-frozen high-precision mpmath oracle and independent dust closed form.

Not output of the original Rust Simpson provider; compare pointwise at the
same source-defined scale factors and numeric cosmological parameters.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from axbi_provider import Background,Family,LOCK_SHA,_read_lock

def independent_point(bg:Background,a,dps=75):
    mp.mp.dps=dps
    c=bg.source["cosmology"]
    aa=mp.mpf(str(float(a)))
    a0=mp.mpf(str(bg.aref))
    H0=mp.mpf(str(c["H0_per_s"]))
    Om=mp.mpf(str(c["Omega_m"]))
    Or=mp.mpf(str(c["Omega_r"]))
    Ol=mp.mpf(str(c["Omega_lambda"]))
    q=mp.mpf(str(bg.case.q_ref))
    def hf(w):return H0*mp.sqrt(Om/w**3+Or/w**4+Ol)
    href=hf(a0)
    def integrand(x):
        w=a0*mp.exp(x)
        s=q*href*mp.exp(-3*x)
        H=mp.sqrt(hf(w)**2+s*s) if bg.case.family=="PhysicalDensityFixed" else hf(w)
        return 1/H,s/H
    xend=mp.log(aa/a0)
    t=mp.quad(lambda x:integrand(x)[0],[0,xend]) if xend else mp.mpf(0)
    b=mp.quad(lambda x:integrand(x)[1],[0,xend]) if xend else mp.mpf(0)
    return {"a":mp.nstr(aa,50),"proper_elapsed_s":mp.nstr(t,54),
            "b":mp.nstr(b,54),
            "H_per_s":mp.nstr(mp.sqrt(hf(aa)**2+(q*href*(a0/aa)**3)**2) if bg.case.family=="PhysicalDensityFixed" else hf(aa),54)}

def run(dps=70):
    _read_lock()
    samples=[]
    rows=[]
    for fam,q in ([("PhysicalDensityFixed",v) for v in [0,.005,-.005,.01,-.01]]+
                  [("SameHDiagnostic",.01)]):
        bg=Background(Family(q,fam))
        for frac in [0,.2,.5,.8,1]:
            a=bg.aref*np.exp(bg.xmax*frac) if frac!=1 else bg.aend
            p=bg.at_a(a)
            val=independent_point(bg,a,dps)
            errt=abs(float(mp.mpf(val['proper_elapsed_s']))-p["proper_elapsed_s"])
            errb=abs(float(mp.mpf(val['b']))-p["b"])
            relt=errt/max(1,p["proper_elapsed_s"])
            rows.append({"family":fam,"q":q,"fraction":frac,"a":a,
                   "proper_time_s":p["proper_elapsed_s"],
                   "mp_time_s":val["proper_elapsed_s"],
                   "absolute_time_s_error":errt,
                   "relative_time_error":relt,
                   "b":p["b"],"mp_b":val["b"],
                   "absolute_b_error":errb,
                   "type":"DOP853 numeric vs independent mpmath.quad exact same frozen scenario"})
    m=max(x['relative_time_error'] for x in rows)
    b=max(x['absolute_b_error'] for x in rows)
    if m>2e-12 or b>3e-13:
        raise ArithmeticError("BACKGROUND_INDEPENDENT_MP_PARITY_HOLD")
    return {"schema":"bass.rei.axbi.independent_mpmath_quad.v1",
           "lock_sha256":LOCK_SHA,"mp_dps":dps,"n_cases":6,"n_samples":len(rows),
           "max_proper_time_relative_diff":m,"max_b_absolute_diff":b,
           "q0_formula":"dust exact t=(2/3A)[sqrt(Aa^3+C^2)-sqrt(Aaref^3+C^2)], b=(2/3)[asinh(C/sqrt(A aref^3))-asinh(C/sqrt(A a^3))]",
           "rows":rows,"interval_certification":False}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    data=run()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2)+"\n")
    print({k:v for k,v in data.items() if k!="rows"})
