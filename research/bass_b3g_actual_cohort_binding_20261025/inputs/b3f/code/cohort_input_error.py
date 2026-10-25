"""Frozen B3f finite endpoint and uniform physical-ball certificates.

All norms/units and admission meanings follow FROZEN_CONTRACT.md. No history
inference, projection, floating-point interval certification, or source repair.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import numpy as np
import positive_angular as p
ROOT=Path(__file__).resolve().parents[1]
EPS_FP=2e-12
TAU=2e-8
SQRT2=math.sqrt(2.)
RAW_SHA='b5933f2347665f8246e8de79c3c66496c96f79dfae965eeb2c48729333040494'

def nominal_data():
    path=ROOT/'provenance/reused_data/POSITIVE_ANGULAR_SWEEP.json'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=RAW_SHA:raise ValueError('immutable nominal byte identity mismatch')
    for c in json.loads((ROOT/'provenance/reused_data/SOURCE_COPIES.json').read_text()):
        if hashlib.sha256((ROOT/c['destination']).read_bytes()).hexdigest()!=c['sha256']:raise ValueError('dependency byte identity mismatch')
    raw=json.loads(path.read_text())
    return {r['label']:r for r in raw['rows'] if r['label'] in ['G3','G5']}

def endpoint(S,R,n,nominal=False):
    g=p.geometry(S,R);n=p.density(n)
    if nominal and n<=0:raise ValueError('positive nominal density required')
    return dict(S=np.asarray(S,dtype=float),R=np.asarray(R,dtype=float),n=n,D=float(np.linalg.det(R)),W=p.EB*n*float(np.linalg.det(R)),**g)

def kernel(v):
    v=p.real_array(v,(3,),'v');r=float(np.linalg.norm(v));out=np.zeros((4,4))
    if r:out[0,0]=r;out[1:,1:]=np.outer(v,v)/r
    return out

def determinant(A):
    """Six signed products, compensated only in their summation."""
    return math.fsum([A[0,0]*A[1,1]*A[2,2],A[0,1]*A[1,2]*A[2,0],A[0,2]*A[1,0]*A[2,1],-A[0,2]*A[1,1]*A[2,0],-A[0,1]*A[1,0]*A[2,2],-A[0,0]*A[1,2]*A[2,1]])

def determinant_difference(R,dR):
    """Exact multilinear 3x3 polynomial: all seven nonempty column subsets."""
    terms=[]
    for mask in range(1,8):
        A=np.column_stack([dR[:,i] if mask&(1<<i) else R[:,i] for i in range(3)])
        terms.append(determinant(A))
    return math.fsum(terms),terms

def source_term(U,R):
    # tr(U^2 C)=||U R^T||_F^2 for symmetric U, C=R^T R.
    return math.sqrt((2*float(np.sum(U*U))*float(np.sum(R*R))+8*float(np.sum((U@R.T)**2)))/105.)

def map_term(dR,H):
    value=float(np.trace(dR@H@dR.T))
    if value<0:raise ValueError('negative map quadratic form')
    return math.sqrt(value)

def compose(A0,L0,B0,U):
    vals=[A0,L0,B0,U]
    if any(not math.isfinite(x) or x<0 for x in vals):raise ValueError('nonnegative finite physical budgets required')
    lower=L0-U
    out=dict(A0=A0,L0=L0,B0=B0,U=U,Ltrue=lower,Umax=(TAU*L0-A0-EPS_FP*B0)/(SQRT2+TAU),tau=TAU,eps_fp=EPS_FP,
             reserve_absolute=EPS_FP*B0,reserve_interpretation='EMPIRICAL_BINARY64_NOT_INTERVAL')
    if lower<=0:return dict(out,status='NONPOSITIVE_ENERGY_LOWER_BOUND',ideal_total=None,operational_total=None)
    ideal=(A0+SQRT2*U)/lower;operational=(A0+SQRT2*U+EPS_FP*B0)/lower
    return dict(out,ideal_total=ideal,operational_total=operational,status='CERTIFIED_SCOPED_NUMERICAL_BUDGET' if operational<=TAU else 'BUDGET_NOT_CERTIFIED')

def pair(S0,R0,n0,S1,R1,n1,B_T0):
    e0=endpoint(S0,R0,n0,True);e1=endpoint(S1,R1,n1)
    dR=e1['R']-e0['R'];U=e1['S']-e0['S']
    r0=map_term(dR,e0['H']);r1=map_term(dR,e1['H']);s0=source_term(U,e0['R']);s1=source_term(U,e1['R'])
    paths=[dict(label='MAP_AT_SOURCE0_THEN_SOURCE_AT_MAP1',map=r0,source=s1,total=r0+s1),dict(label='SOURCE_AT_MAP0_THEN_MAP_AT_SOURCE1',map=r1,source=s0,total=s0+r1)]
    chosen=min(range(2),key=lambda i:paths[i]['total']);h=paths[chosen]['total']
    dd,detterms=determinant_difference(e0['R'],dR);dn=e1['n']-e0['n'];d0=determinant(e0['R'])
    wdterms=[p.EB*e0['n']*dd,p.EB*dn*d0,p.EB*dn*dd];signed_dW=math.fsum(wdterms);dW=abs(signed_dW)
    prefactors=[dict(label='W0_H_PLUS_DW_FUP1',map=e0['W']*paths[chosen]['map'],source=e0['W']*paths[chosen]['source'],prefactor=dW*e1['F_upper'],total=e0['W']*h+dW*e1['F_upper']),dict(label='W1_H_PLUS_DW_FUP0',map=e1['W']*paths[chosen]['map'],source=e1['W']*paths[chosen]['source'],prefactor=dW*e0['F_upper'],total=e1['W']*h+dW*e0['F_upper'])]
    prefchoice=min(range(2),key=lambda i:prefactors[i]['total']);up=prefactors[prefchoice]['total']
    return dict(paths=paths,chosen_path=chosen,h=h,prefactor_paths=prefactors,chosen_prefactor_path=prefchoice,U_pair=up,tensor_bound=SQRT2*up,
                determinant_delta=dd,determinant_multilinear_terms=detterms,signed_weight_delta=signed_dW,weight_delta_terms=wdterms,dW=dW,
                W0=e0['W'],W1=e1['W'],D0=e0['D'],D1=e1['D'],radii=dict(eR=float(np.linalg.norm(dR,2)),eS=float(np.linalg.norm(U,'fro')),en=abs(dn)),
                composition=compose(e0['W']*B_T0,e0['W']*e0['F_lower'],e0['W']*e0['F_upper'],up))

def ball(S0,R0,n0,B_T0,eR=None,eS=None,en=None):
    e=endpoint(S0,R0,n0,True)
    radii=dict(eR=eR,eS=eS,en=en)
    if any(x is None for x in radii.values()):return dict(status='INPUT_ERROR_UNSPECIFIED',radii=radii,composition=None)
    for key,x in radii.items():
        val=float(p.real_array(x,(),key))
        if val<0:raise ValueError('negative radius '+key)
        radii[key]=val
    eR,eS,en=[radii[k] for k in ['eR','eS','en']];a=e['a'];b=e['b'];allow=p.ROUND
    domain=dict(invertible=eR<a,outgoing=b+eR<=1+allow,condition=(b+eR)/(a-eR)<=2+allow if eR<a else False,
                source=(eS<=0 if 1+float(np.linalg.eigvalsh(e['S'])[0])==0 else eS<=1+float(np.linalg.eigvalsh(e['S'])[0])+allow),density=en<=e['n']+allow*e['n'])
    if not all(domain.values()):return dict(status='NOT_COVERED_BY_PHYSICAL_BALL',radii=radii,domain=domain,composition=None)
    sigma=np.linalg.svd(e['R'],compute_uv=False);e1=float(sum(sigma));e2=float(sigma[0]*sigma[1]+sigma[0]*sigma[2]+sigma[1]*sigma[2])
    deltaD=e2*eR+e1*eR**2+eR**3;deltaW=p.EB*(e['n']*deltaD+en*(e['D']+deltaD));wmax=e['W']+deltaW
    hb=eR+eS*math.sqrt((2*float(np.sum((sigma+eR)**2))+8*(b+eR)**2)/105)
    paths=[e['W']*hb+deltaW*(b+eR),wmax*hb+deltaW*e['F_upper']];up=min(paths)
    return dict(status='PHYSICAL_BALL_CERTIFIED',radii=radii,domain=domain,deltaD=deltaD,deltaW=deltaW,Wmax=wmax,h_ball=hb,U_ball_paths=paths,U_ball=up,
                composition=compose(e['W']*B_T0,e['W']*e['F_lower'],e['W']*e['F_upper'],up))

def mixture(rows,coefficients):
    c=p.real_array(coefficients,(len(rows),),'mixture coefficients')
    if np.any(c<0):raise ValueError('negative mixture coefficient')
    if not np.any(c>0):raise ValueError('all-zero mixture')
    return compose(*[math.fsum(float(w)*r['composition'][k] for w,r in zip(c,rows)) for k in ['A0','L0','B0','U']])
