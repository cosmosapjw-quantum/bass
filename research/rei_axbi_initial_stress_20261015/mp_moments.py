"""Independent mpmath75 kinetic moments oracle, unrelated to NumPy quadrature."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import mpmath as mp
import numpy as np
import einstein_vlasov as v

def verify(dps=75):
    mp.mp.dps=dps
    checks=[]
    for k in [-.2,0,.2]:
        for b in [-.01,0.,.003,.007]:
            B=mp.mpf(str(b));K=mp.mpf(str(k))
            P2=lambda u:(3*u*u-1)/2
            W=lambda u:1+K*P2(u)
            def r(mu):
                return mp.sqrt(mp.exp(2*B)*(1-mu*mu)+mp.exp(-4*B)*mu*mu)
            def mu2(u):return mp.exp(-4*B)*u*u/r(u)**2
            mm=mp.quad(lambda u:W(u)*r(u)/2,[-1,1])
            pp=mp.quad(lambda u:W(u)*r(u)*(3*mu2(u)-1)/12,[-1,1])
            m,p=v.moments(b,k,order=64)
            error_m=abs(float(mm)-m)
            error_p=abs(float(pp)-p)
            checks.append({"kappa":k,"b":b,"mp_M":mp.nstr(mm,55),
                           "mp_P":mp.nstr(pp,55),
                           "np_M":m,"np_P":p,
                           "abs_M_error":error_m,"abs_P_error":error_p})
    ma=max(x["abs_M_error"] for x in checks)
    pa=max(x["abs_P_error"] for x in checks)
    if ma>1e-13 or pa>1e-13:raise ArithmeticError("ANGULAR_STRESS_SOURCE_MP_MISMATCH")
    return {"schema":"bass.rei.axbi.kinetic_stress.mp75_source_oracle.v1",
       "moment_cases":len(checks),"mp_dps":dps,"max_abs_M_error":ma,"max_abs_P_error":pa,
       "claim_scope":"independent angular moment quadrature only, not high-precision coupled Einstein ODE",
       "cases":checks}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    ans=verify()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(ans,indent=2)+"\n")
    print(json.dumps({k:v for k,v in ans.items() if k!="cases"},indent=2))
