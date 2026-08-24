from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import expm
from scipy.interpolate import CubicSpline

PI=np.pi

def lebedev26():
    a=1/np.sqrt(3.0); b=1/np.sqrt(2.0)
    pts=[]; w=[]
    for k in range(3):
        for s in (-1.0,1.0):
            x=np.zeros(3);x[k]=s;pts.append(x);w.append(4*PI/21)
    for zero in range(3):
        idx=[i for i in range(3) if i!=zero]
        for s1 in (-1.0,1.0):
            for s2 in (-1.0,1.0):
                x=np.zeros(3);x[idx[0]]=s1*b;x[idx[1]]=s2*b;pts.append(x);w.append(16*PI/105)
    for sx in (-1.0,1.0):
        for sy in (-1.0,1.0):
            for sz in (-1.0,1.0):
                pts.append([sx*a,sy*a,sz*a]);w.append(9*PI/70)
    return np.asarray(pts,float),np.asarray(w,float)

def product_grid(nt:int,np_:int):
    z,wz=leggauss(nt); ph=2*PI*np.arange(np_)/np_
    pts=[];ws=[]
    for zz,ww in zip(z,wz):
        r=np.sqrt(max(0.0,1-zz*zz))
        for p in ph:
            pts.append([r*np.cos(p),r*np.sin(p),zz]);ws.append(ww*2*PI/np_)
    return np.asarray(pts),np.asarray(ws)

def aberrate(e,v,axis=1):
    e=np.atleast_2d(np.asarray(e,float)); vvec=np.zeros(3);vvec[axis]=v
    v2=v*v
    if v2==0:return e.copy(),np.ones(len(e))
    g=1/np.sqrt(1-v2); ve=e@vvec;D=g*(1-ve)
    ep=(e+((((g-1)*ve/v2)-g)[:,None]*vvec[None,:]))/D[:,None]
    ep/=np.linalg.norm(ep,axis=1)[:,None]
    return ep,D

def paired_grid(ep,wp,v,axis=1):
    en,Dinv=aberrate(ep,-v,axis);ep2,D=aberrate(en,v,axis)
    if np.max(np.abs(ep2-ep))>2e-12: raise RuntimeError('boost roundtrip')
    return en,wp*D**2,D

def collision_matrix(en,wn,v,axis=1):
    ep,D=aberrate(en,v,axis);wr=wn/D**2;cc=ep@ep.T
    T=(3/(16*PI))*(1+cc*cc)*wr[None,:]-np.eye(len(en))
    q=1-v*en[:,axis]
    C=np.diag(q)@np.diag(D**-4)@T@np.diag(D**4)
    return C,D,q

def collision_metrics(en,wn,v,axis=1):
    C,D,q=collision_matrix(en,wn,v,axis);r=D**-4;a=wn*q/(4*PI)
    rng=np.random.default_rng(123);y=rng.normal(size=len(en))
    null=float(np.max(np.abs(C@r)))
    left=float(abs(a@(C@y))/max(np.max(np.abs(C@y)),1e-300))
    base=float(a@y);dr=[]
    for x in (1e-3,1.0,10.0,1e3):
        z=expm(x*C)@y;dr.append(float(abs(a@z-base)/max(abs(base),1e-300)))
    return {'null':null,'left':left,'semigroup_drift':dr}

def projector(v,e,w,axis=1):
    mu=e[:,axis];q=1-v*mu;g=1/np.sqrt(1-v*v);D=g*q
    r=D**-4;a=w*q/(4*PI);rv=4*r*(mu/q-g*g*v);av=-w*mu/(4*PI)
    den=a@r;denv=av@r+a@rv
    P=np.outer(r,a)/den
    Pv=(np.outer(rv,a)+np.outer(r,av))/den-P*(denv/den)
    return P,Pv

def kato_endpoint_orders(schedule_path:Path):
    s=json.loads(schedule_path.read_text());dt=float(s['dt']);T=float(s['T'])
    ts=np.arange(len(s['v2']))*dt
    vs=CubicSpline(ts,np.asarray(s['v2']));vds=CubicSpline(ts,np.asarray(s['v2dot']))
    e,w=lebedev26();rng=np.random.default_rng(7);P0,_=projector(float(vs(0)),e,w);y0=P0@rng.normal(size=len(e))
    hs=np.array([.05,.025,.0125,.00625,.003125]);errs=[]
    for h in hs:
        y=y0.copy()
        for k in range(int(round(T/h))):
            tm=(k+.5)*h;P,Pv=projector(float(vs(tm)),e,w);Pd=float(vds(tm))*Pv;K=Pd@P-P@Pd
            y=expm(h*K)@y
        PT,_=projector(float(vs(T)),e,w);errs.append(float(np.linalg.norm((np.eye(len(e))-PT)@y)/np.linalg.norm(y)))
    order=float(np.polyfit(np.log(hs[-4:]),np.log(errs[-4:]),1)[0])
    return {'h':hs.tolist(),'endpoint_manifold_defect':errs,'order':order}

def run(schedule_path:Path):
    grids=[('Lebedev26',*lebedev26()),('GL4x8',*product_grid(4,8)),('GL6x12',*product_grid(6,12)),('GL8x16',*product_grid(8,16))]
    rec=[]
    for name,ep,wp in grids:
        for v in (.02,.05,.1,.2):
            rec.append({'grid':name,'n':len(ep),'v':v,'mode':'fixed-normal',**collision_metrics(ep,wp,v)})
            en,wn,_=paired_grid(ep,wp,v);rec.append({'grid':name,'n':len(ep),'v':v,'mode':'paired-rest-normal',**collision_metrics(en,wn,v)})
    return {'quadrature':rec,'kato_endpoint':kato_endpoint_orders(schedule_path)}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('schedule',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.write_text(json.dumps(run(args.schedule),indent=2))
