"""Source-owning BASS original finite-tilt scalar collision uniformization AUDITOR.
No polarized carrier, no new Einstein IVP, no production mutation.
Original owner main: 9c6506e4e2087129a8b674ff10438e5db1a55c9d.
"""
from __future__ import annotations
import json, math, argparse
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from scipy.stats import poisson

MAIN = "9c6506e4e2087129a8b674ff10438e5db1a55c9d"
AXES = np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float)

def sixaxis():
    return AXES.copy(),np.full(6,4*math.pi/6)

def lebedev26():
    a=1/math.sqrt(3);b=1/math.sqrt(2)
    n=[];w=[]
    for k in range(3):
        for sign in (-1.,1.):
            d=np.zeros(3);d[k]=sign;n.append(d);w.append(4*math.pi/21)
    for zero in range(3):
        ij=[j for j in range(3) if j!=zero]
        for t in (-1.,1.):
            for u in (-1.,1.):
                d=np.zeros(3);d[ij[0]]=t*b;d[ij[1]]=u*b
                n.append(d);w.append(16*math.pi/105)
    for x in (-1.,1.):
        for y in (-1.,1.):
            for z in (-1.,1.):
                n.append([x*a,y*a,z*a]);w.append(9*math.pi/70)
    return np.asarray(n),np.asarray(w)

def boost(n,v,axis=1):
    if not abs(v)<1 or axis not in (0,1,2):raise ValueError("invalid boost")
    n=np.asarray(n,float)
    if v==0:return n.copy(),np.ones(len(n))
    g=1/math.sqrt(1-v*v);mu=n[:,axis];ve=v*mu
    D=g*(1-ve)
    out=n.copy()
    out[:,axis]+=((g-1)*ve/v**2-g)*v
    return out/D[:,None],D

def paired(e,w,v):
    n,_=boost(e,-v);e2,D=boost(n,v)
    if np.max(abs(e2-e))>2e-12:raise ArithmeticError("bad paired source")
    return n,w*D**2

def collision(en,wn,v):
    er,D=boost(en,v)
    wr=wn/D**2
    gain=(3/(16*math.pi))*(1+(er@er.T)**2)*wr[None,:]
    q=1-v*en[:,1]
    C=(q*D**-4)[:,None]*(gain-np.eye(len(en)))*D[None,:]**4
    return C,D**-4,wn*q/(4*math.pi),gain

def require_markov(C,r,a):
    if min(np.min(r),np.min(a))<=0 or not np.isfinite(C).all():raise ValueError("nonphysical")
    off=C.copy();np.fill_diagonal(off,0)
    if np.min(off)<-1e-12:raise ValueError("not Metzler")
    if max(np.max(abs(C@r)),np.max(abs(a@C)))>1e-12:
        raise ValueError("source-grid null/invariant defect")
    lam=float(max(0.,-np.min(np.diag(C))))
    B=np.eye(len(r))+C/lam
    M=(B*r[None,:])/r[:,None]
    pi=a*r;pi/=np.sum(pi)
    if np.min(M)<-1e-12 or np.max(abs(M.sum(1)-1))>1e-12:
        raise ValueError("Doob matrix not stochastic")
    return lam,B,M,pi

def uniform(C,r,a,t,y):
    if t<0:raise ValueError("backward Poisson time forbidden")
    lam,B,_,_=require_markov(C,r,a)
    mu=lam*t
    hi=int(poisson.ppf(1-1e-13,mu)) if t>0 else 0
    out=np.zeros_like(y);power=y.copy()
    for k in range(hi+1):
        out+=float(poisson.pmf(k,mu))*power
        power=B@power
    return out,float(poisson.sf(hi,mu))

def run():
    rows=[]
    for name,func in (("axis6",sixaxis),("Lebedev26",lebedev26)):
        rest,wrest=func()
        for v in (0.,.02,.05,.10,.20):
            en,wn=paired(rest,wrest,v)
            C,r,a,_=collision(en,wn,v)
            lam,B,M,pi=require_markov(C,r,a)
            t=100. if v==.20 else 1.
            y=1.3+np.cos(np.arange(len(r))*.4)
            u,tail=uniform(C,r,a,t,y)
            rows.append({"grid":name,"tilt":v,"rays":len(r),"t":t,
                  "max_null":float(np.max(abs(C@r))),
                  "max_left":float(np.max(abs(a@C))),
                  "max_markov_row":float(np.max(abs(M.sum(1)-1))),
                  "max_stationary":float(np.max(abs(pi@M-pi))),
                  "max_expm_gap":float(np.max(abs(u-expm(t*C)@y))),
                  "poisson_tail":tail})
    normal,wn=sixaxis()
    C,r,a,_=collision(normal,wn,.10)
    fixture_y=np.array([1.,.7,1.2,.9,.6,1.4])
    fixture=np.array([-.077556362500000239,.22097348749999984,.25408950617283943,
                      -.25930785123966976,.3561345749999999,-.4399450250000001])
    fixed={"original_Rust_fixture_max_gap":float(np.max(abs(C@fixture_y-fixture))),
           "fixed_normal_null_defect":float(np.max(abs(C@r))),
           "fixed_normal_left_defect":float(np.max(abs(a@C)))}
    if fixed["original_Rust_fixture_max_gap"]>5e-13:raise ArithmeticError("Rust source mismatch")
    try:require_markov(C,r,a)
    except ValueError:fixed["correctly_rejected"]=True
    else:raise ArithmeticError("fixed-grid false PASS")
    return {"schema":"bass.original.typeii.frozen_uniformization.v1","main_source":MAIN,
            "matched_paired_scalar_cases":len(rows),"rows":rows,"fixed_grid":fixed,
            "upper_dag":"9/15_SCOPED_SOURCE_MAPPED","stageII":"11/11_HISTORICAL_CURRENT_NOT_ESTABLISHED",
            "join_J1":"0/2_PASS","P_MIG_II_PREFLIGHT":"PARTIAL",
            "production_ready":False,"auto_next":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    data=run();Path(args.out).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("TYPEII_PAIRS",len(data["rows"]),"SOURCE_FIXED_NULL",data["fixed_grid"]["fixed_normal_null_defect"])
