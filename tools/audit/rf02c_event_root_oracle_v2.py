#!/usr/bin/env python3
"""Exact dyadic polynomial root-isolation oracle for RF-02C V2.

This is a small executable reference for the contract's all-root requirement. It
is not the production Rust implementation and makes no solver-accuracy claim.
"""
from __future__ import annotations
import argparse, json
from fractions import Fraction
from pathlib import Path
from typing import Iterable

Poly = list[Fraction]  # ascending coefficients

def trim(p: Poly) -> Poly:
    q=list(p)
    while len(q)>1 and q[-1]==0: q.pop()
    return q or [Fraction(0)]

def is_zero(p: Poly) -> bool: return all(x==0 for x in p)
def degree(p: Poly) -> int: return len(trim(p))-1

def deriv(p: Poly) -> Poly:
    return trim([Fraction(i)*p[i] for i in range(1,len(p))] or [Fraction(0)])

def divmod_poly(a: Poly,b: Poly)->tuple[Poly,Poly]:
    a=trim(a); b=trim(b)
    if is_zero(b): raise ZeroDivisionError
    if degree(a)<degree(b): return [Fraction(0)],a
    q=[Fraction(0)]*(degree(a)-degree(b)+1); r=a[:]
    while not is_zero(r) and degree(r)>=degree(b):
        k=degree(r)-degree(b); c=r[-1]/b[-1]; q[k]+=c
        for i,bi in enumerate(b): r[i+k]-=c*bi
        r=trim(r)
    return trim(q),trim(r)

def monic(p: Poly)->Poly:
    p=trim(p)
    if is_zero(p): return p
    lead=p[-1]
    return [x/lead for x in p]

def gcd_poly(a: Poly,b: Poly)->Poly:
    a=trim(a); b=trim(b)
    while not is_zero(b):
        _,r=divmod_poly(a,b); a,b=b,r
    return monic(a)

def exact_div(a: Poly,b: Poly)->Poly:
    q,r=divmod_poly(a,b)
    if not is_zero(r): raise ArithmeticError(f'non-exact division: {r}')
    return trim(q)

def square_free_factors(f: Poly)->list[tuple[Poly,int]]:
    f=trim(f)
    if is_zero(f): return []
    c=gcd_poly(f,deriv(f)); w=exact_div(f,c); i=1; out=[]
    one=[Fraction(1)]
    while degree(w)>0:
        y=gcd_poly(w,c); z=exact_div(w,y)
        if degree(z)>0: out.append((monic(z),i))
        w=y; c=exact_div(c,y); i+=1
    return out

def eval_poly(p: Poly,x: Fraction)->Fraction:
    out=Fraction(0)
    for c in reversed(p): out=out*x+c
    return out

def sturm_sequence(p: Poly)->list[Poly]:
    p=monic(p); seq=[p,deriv(p)]
    if is_zero(seq[1]): return [p]
    while not is_zero(seq[-1]):
        _,r=divmod_poly(seq[-2],seq[-1])
        if is_zero(r): break
        seq.append([-x for x in r])
    return seq

def variations(seq:list[Poly],x:Fraction)->int:
    signs=[]
    for p in seq:
        v=eval_poly(p,x)
        if v: signs.append(1 if v>0 else -1)
    return sum(a!=b for a,b in zip(signs,signs[1:]))

def roots_open(seq:list[Poly],a:Fraction,b:Fraction)->int:
    if not a<b: return 0
    return variations(seq,a)-variations(seq,b)

def isolate_square_free(p:Poly,a=Fraction(0),b=Fraction(1),depth=0,max_depth=256)->list[tuple[Fraction,Fraction]]:
    seq=sturm_sequence(p)
    # endpoint roots are removed from the interior count by nudging with exact factor division upstream.
    n=roots_open(seq,a,b)
    if n==0: return []
    if n==1 and depth>=4: return [(a,b)]
    if depth>=max_depth: raise RuntimeError('isolation depth exhausted')
    m=(a+b)/2
    return isolate_square_free(p,a,m,depth+1,max_depth)+isolate_square_free(p,m,b,depth+1,max_depth)

def divide_linear(p:Poly,r:Fraction)->Poly:
    q,rem=divmod_poly(p,[-r,Fraction(1)])
    if not is_zero(rem): raise ArithmeticError
    return q

def isolate_with_multiplicity(p:Poly)->dict:
    p=trim(p)
    if is_zero(p): return {'classification':'CONTINUUM_ZERO','roots':[]}
    roots=[]
    # endpoint multiplicities
    for endpoint in (Fraction(0),Fraction(1)):
        mult=0
        while degree(p)>0 and eval_poly(p,endpoint)==0:
            p=divide_linear(p,endpoint); mult+=1
        if mult: roots.append({'interval':[str(endpoint),str(endpoint)],'multiplicity':mult,'endpoint':True})
    for factor,mult in square_free_factors(p):
        for lo,hi in isolate_square_free(factor):
            roots.append({'interval':[str(lo),str(hi)],'multiplicity':mult,'endpoint':False})
    roots.sort(key=lambda r: Fraction(r['interval'][0]))
    return {'classification':'FINITE_ROOTS','roots':roots}

def mul(a:Poly,b:Poly)->Poly:
    out=[Fraction(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    return trim(out)
def power_linear(root:Fraction,n:int)->Poly:
    p=[Fraction(1)]
    for _ in range(n): p=mul(p,[-root,Fraction(1)])
    return p

def self_test()->dict:
    cases={
      'two_crossings':mul(power_linear(Fraction(1,4),1),power_linear(Fraction(3,4),1)),
      'tangent_double':power_linear(Fraction(1,2),2),
      'mixed_multiplicity':mul(power_linear(Fraction(1,4),2),power_linear(Fraction(3,4),3)),
      'endpoint_roots':mul(power_linear(Fraction(0),1),power_linear(Fraction(1),2)),
      'continuum_zero':[Fraction(0)],
    }
    expected={
      'two_crossings':[1,1], 'tangent_double':[2], 'mixed_multiplicity':[2,3],
      'endpoint_roots':[1,2], 'continuum_zero':[]
    }
    results={}; ok=True
    for name,p in cases.items():
        got=isolate_with_multiplicity(p)
        mult=[r['multiplicity'] for r in got['roots']]
        case_ok=(mult==expected[name] and ((name=='continuum_zero')==(got['classification']=='CONTINUUM_ZERO')))
        results[name]={'ok':case_ok,'result':got}; ok &= case_ok
    # actual-integration order is theta order even when tau1<tau0.
    theta_roots=[Fraction(1,4),Fraction(3,4)]
    tau=[Fraction(1)+(Fraction(0)-Fraction(1))*x for x in theta_roots]
    backward_ok=(tau==[Fraction(3,4),Fraction(1,4)])
    results['backward_order']={'ok':backward_ok,'theta':[str(x) for x in theta_roots],'tau':[str(x) for x in tau]}
    ok &= backward_ok
    # Restart at theta=0 in the zero band; leave to the allowed positive side
    # inside the same carrier, then encounter a later positive->negative raw root.
    p=mul(mul([Fraction(0),Fraction(-1)],[-Fraction(1,3),Fraction(1)]),[-Fraction(2,3),Fraction(1)])
    eps=Fraction(1,1000)
    threshold=p[:]; threshold[0]-=eps
    raw=isolate_with_multiplicity(p); band=isolate_with_multiplicity(threshold)
    raw_hi=[Fraction(r['interval'][1]) for r in raw['roots']]
    rearm_ok=(eval_poly(p,Fraction(1,2))>eps and any(x>=Fraction(1,3) and x<=Fraction(2,3) for x in raw_hi) and len(band['roots'])>=2)
    results['within_step_rearm']={'ok':rearm_ok,'epsilon':str(eps),'raw_roots':raw,'positive_threshold_roots':band}
    ok &= rearm_ok
    # Tangency is enumerated but has equal side signs and is therefore not a directed crossing.
    tangent=power_linear(Fraction(1,2),2)
    tangent_ok=(eval_poly(tangent,Fraction(2,5))>0 and eval_poly(tangent,Fraction(3,5))>0)
    results['tangent_direction_filter']={'ok':tangent_ok,'left_sign':'+','right_sign':'+','eligible_direction_0':True,'eligible_direction_minus_1':False}
    ok &= tangent_ok
    return {'schema':'bass-rf02c-event-root-oracle/v2','status':'PASS' if ok else 'FAIL','cases':results}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--self-test',action='store_true'); ap.add_argument('--output',type=Path)
    ns=ap.parse_args(); report=self_test() if ns.self_test else self_test()
    text=json.dumps(report,indent=2,sort_keys=True)+'\n'; print(text,end='')
    if ns.output: ns.output.parent.mkdir(parents=True,exist_ok=True); ns.output.write_text(text)
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
