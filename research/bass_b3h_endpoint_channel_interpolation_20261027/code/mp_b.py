"""MP70 serialization, sparse elimination and bounded positive quadrature."""
import json
from pathlib import Path
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
mp.mp.dps=70
m=mp.mpf
ZERO=m(0);ARITH=m('1e-55')
CHECKS=[];QUADS=[];RULES={}
def norm(v):return mp.fsum(abs(x) for x in v)
def matnorm(a):return max(mp.fsum(abs(a[i,j]) for i in range(a.rows)) for j in range(a.cols))
def exact(v):
    if isinstance(v,list):return [exact(x) for x in v]
    if isinstance(v,dict):return {k:exact(x) for k,x in v.items()}
    if isinstance(v,float):return m(v)
    return v
def plain(v):
    if isinstance(v,mp.matrix):return [[plain(v[i,j]) for j in range(v.cols)] for i in range(v.rows)]
    if isinstance(v,mp.mpf):return mp.nstr(v,70)
    if isinstance(v,dict):return {k:plain(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [plain(x) for x in v]
    return v
def write(path,obj):path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(plain(obj),indent=2,allow_nan=False)+'\n')
def check(name,ok,observed=None,limit=None):
    CHECKS.append(dict(name=name,passed=bool(ok),observed=plain(observed),limit=plain(limit)));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    if not ok:raise ValueError('frozen Phase B check failed: '+name)
def propensity(a):
    if a<0:raise ValueError('negative propensity; no clipping')
def clock_identity(actual,expected):
    if abs(actual-expected)>ARITH*max(abs(actual),abs(expected)):raise ValueError('mismatched clock')
def thomas(diag,lower,upper,rhs):
    n=len(diag);nr=len(rhs[0]);a=[ZERO]*n;g=[[ZERO]*nr for _ in range(n)];den=[]
    for i in range(n):
        d=diag[i]-(lower[i]*a[i-1] if i else ZERO);den.append(d)
        if d<=0:raise ValueError('nonpositive physical virtual Thomas denominator')
        a[i]=upper[i]/d;g[i]=[(rhs[i][j]-(lower[i]*g[i-1][j] if i else ZERO))/d for j in range(nr)]
    out=[[ZERO]*nr for _ in range(n)];out[-1]=g[-1]
    for i in range(n-2,-1,-1):out[i]=[g[i][j]-a[i]*out[i+1][j] for j in range(nr)]
    return out,den
def gl(fn,a,b,n):
    if n not in RULES:RULES[n]=mp.gauss_quadrature(n,'legendre')
    x,w=RULES[n];mid=(a+b)/2;half=(b-a)/2;terms=[half*w[i]*fn(mid+half*x[i]) for i in range(n)]
    return mp.fsum(terms),mp.fsum(abs(t) for t in terms)
def quadrature(name,fn,segments,sup):
    value=ZERO;bound=ZERO
    for j,(a,b) in enumerate(segments):
        v16,g16=gl(fn,a,b,16);v24,g24=gl(fn,a,b,24);gross=max(g16,g24);diff=abs(v24-v16)
        check(name+f' segment{j} GL16/24',diff<=m('1e-40')*gross,diff/gross if gross else diff,m('1e-40'))
        radius=m('.01');ratio=(b-a)/(2*radius);check(name+f' segment{j} pole-free Taylor ratio',ratio<1,ratio,1)
        Mf=sup((a+b)/2,radius,j);tail16=2*(b-a)*Mf*ratio**32/(1-ratio);tail24=2*(b-a)*Mf*ratio**48/(1-ratio)
        arithmetic=ARITH*gross;QUADS.append(dict(name=name,segment=j,a=a,b=b,n=[16,24],value16=v16,value24=v24,gross=gross,
          agreement=diff,cauchy_radius=radius,analytic_sup=Mf,remainder16=tail16,remainder24=tail24,arithmetic_allowance=arithmetic))
        value+=v24;bound+=tail24+arithmetic
    return value,bound
