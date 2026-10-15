"""Array-of-cases fused RK4 for REAL LRS Einstein-massless-Vlasov q,kappa cases.

Potential fast producer only; endpoint errors are measured against
independent DOP853, not mathematically interval-enclosed.
"""
from __future__ import annotations
import argparse,json,time,statistics
from pathlib import Path
import numpy as np
import einstein_vlasov as ev

CASES=[(0.,0.),(0.,.2),(0.,-.2),(.005,0.),(-.005,0.),
       (.005,.2),(.005,-.2),(.01,0.),(.01,.2),(-.01,.2)]

def rhs(x,Y,q,k,h0ratio,om,orad,ol,aref,order):
    b=Y[:,1]
    s=Y[:,2]
    m,p=ev.moments(b,k,order=order)
    a=aref*np.exp(x)
    E=np.sqrt(h0ratio*(om/a**3+ol+orad/a**4*m)+s*s)
    return np.stack([1/E,s/E,-3*s+3*h0ratio*orad/a**4*p/E],axis=-1)

def solve_many(cases=CASES,steps=1024,order=32):
    if not isinstance(steps,int) or steps<4 or steps>100000:
        raise ValueError("RK4 steps 4..100000")
    inputs=[ev.Initial(q,k) for q,k in cases]
    source=ev._read_lock()
    c=source["cosmology"];a0=source["clock"]["a_ref"];a1=source["clock"]["a_end"]
    xend=np.log(a1/a0);dx=xend/steps
    hf=c["H0_per_s"]*np.sqrt(c["Omega_m"]/a0**3+c["Omega_r"]/a0**4+c["Omega_lambda"])
    f0=(c["H0_per_s"]/hf)**2
    q=np.array([z.q_ref for z in inputs])
    k=np.array([z.kappa for z in inputs])
    Y=np.zeros((len(inputs),3),dtype=float);Y[:,2]=q
    for i in range(steps):
        x=i*dx
        a=rhs(x,Y,q,k,f0,c["Omega_m"],c["Omega_r"],c["Omega_lambda"],a0,order)
        b=rhs(x+dx/2,Y+dx*a/2,q,k,f0,c["Omega_m"],c["Omega_r"],c["Omega_lambda"],a0,order)
        d=rhs(x+dx/2,Y+dx*b/2,q,k,f0,c["Omega_m"],c["Omega_r"],c["Omega_lambda"],a0,order)
        e=rhs(x+dx,Y+dx*d,q,k,f0,c["Omega_m"],c["Omega_r"],c["Omega_lambda"],a0,order)
        Y+=dx*(a+2*b+2*d+e)/6
    a=a1
    m,p=ev.moments(Y[:,1],k,order=order)
    Hratio=np.sqrt(f0*(c["Omega_m"]/a**3+c["Omega_lambda"]+c["Omega_r"]/a**4*m)+Y[:,2]**2)
    return {"input_cases":cases,"steps":steps,"order":order,
      "elapsed_proper_s":Y[:,0]/hf,"b_end":Y[:,1],"s_over_H":Y[:,2]/Hratio,
      "radiation_monopole":m,"radiation_P":p,
      "computed_states":Y}

def measured(reps=3):
    for _ in range(1):solve_many(steps=256,order=32)
    candidates={}
    for steps in (128,256,512,1024):
        for order in (16,32,64):
            vals=[]
            ret=None
            for _ in range(reps):
                t=time.perf_counter();ret=solve_many(steps=steps,order=order);vals.append(time.perf_counter()-t)
            reference=[ev.KineticStressBackground(ev.Initial(*q),order=64).at_a(.2) for q in CASES]
            diff_b=max(abs(ret["b_end"][i]-r["b"]) for i,r in enumerate(reference))
            diff_s=max(abs(ret["s_over_H"][i]-r["s_per_s"]/r["h_per_s"]) for i,r in enumerate(reference))
            diff_t=max(abs(ret["elapsed_proper_s"][i]/r["elapsed_proper_s"]-1) for i,r in enumerate(reference))
            candidates[f"RK4_{steps}_GL{order}"]={"median_s":statistics.median(vals),
              "repeat_s":vals,"max_b_abs_delta_vs_DOP853":float(diff_b),
              "max_s_over_H_abs_delta_vs_DOP853":float(diff_s),
              "max_t_relative_vs_DOP853":float(diff_t)}
    options=[(name,x) for name,x in candidates.items()
             if x["max_b_abs_delta_vs_DOP853"]<2e-9
             and x["max_s_over_H_abs_delta_vs_DOP853"]<2e-9
             and x["max_t_relative_vs_DOP853"]<2e-9]
    return {"schema":"bass.rei.axbi.initial_stress_vector_RK4_vs_DOP853.v1",
       "cases":CASES,"tested":candidates,
       "fastest_passed":min(options,key=lambda pair:pair[1]["median_s"])[0] if options else None,
       "fixed_tolerance":2e-9,
       "claim_scope":"matched 10 cases physical output empirical DOP853 comparison, no global enclosure",
       "native_REI_solver_speedup":None}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);p.add_argument("--reps",type=int,default=3)
    z=p.parse_args()
    if z.out.exists():raise FileExistsError(z.out)
    j=measured(z.reps)
    z.out.parent.mkdir(parents=True,exist_ok=True)
    z.out.write_text(json.dumps(j,indent=2)+"\n")
    print("FASTEST",j["fastest_passed"])
    for name,k in j["tested"].items():print(name,round(k["median_s"],5),k["max_b_abs_delta_vs_DOP853"],k["max_t_relative_vs_DOP853"])
