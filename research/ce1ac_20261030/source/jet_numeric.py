"""CE1-AC: model-locked, independently computed l4 initial time jets on positive GL rays; diagnostic only."""
from __future__ import annotations
import sys, math, hashlib, json
from pathlib import Path
import numpy as np
BASE = Path(__file__).resolve().parents[1]
from source_paths import SRC
sys.path.insert(0,str(SRC))
from cellwise_gl_rust import make_cell_rays, frozen_source_identity, SHEAR
SOURCE_SHA='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'

def numeric_jet(n):
    assert frozen_source_identity()==SOURCE_SHA
    ray,mass=make_cell_rays(n); x=ray*ray
    E0=np.sum(mass*np.sqrt(x.sum(axis=1)))
    H=math.sqrt((E0+.5*np.dot(SHEAR,SHEAR))/3)
    h=H+SHEAR; theta=h.sum()
    P=np.sum(mass[:,None]*x/(np.sqrt(x.sum(axis=1))[:,None]),axis=0)
    hp=-theta*h+P
    B=x@h; A=x@hp; S2=x@(h*h)
    V=2*x*(B[:,None]-h[None,:]); Bprime=A+2*(B*B-S2)
    W=2*V*(B[:,None]-h[None,:])+2*x*(Bprime[:,None]-hp[None,:]); C=-A-B*B+2*S2
    xx,yy,zz=x.T; vx,vy,vz=V.T;wx,wy,wz=W.T
    Ts=[35*zz**2-30*zz+3,(xx-yy)*(7*zz-1),xx**2-6*xx*yy+yy**2]
    dt=[(70*zz-30)*vz,(vx-vy)*(7*zz-1)+7*(xx-yy)*vz,(2*xx-6*yy)*vx+(2*yy-6*xx)*vy]
    ddt=[70*vz*vz+(70*zz-30)*wz, (wx-wy)*(7*zz-1)+14*(vx-vy)*vz+7*(xx-yy)*wz,
         (2*xx-6*yy)*wx+(2*yy-6*xx)*wy+2*vx*vx-12*vx*vy+2*vy*vy]
    weight=mass*np.sqrt(x.sum(axis=1))
    def av(v):return float(np.dot(weight,v)/np.sum(weight))
    N1=av(-B);N2=av(C)
    rows=[]
    for t,d,dd in zip(Ts,dt,ddt):
        M0=av(t); M1=av(d-B*t);M2=av(dd-2*B*d+C*t)
        Q1=M1-M0*N1;Q2=M2-M0*N2-2*Q1*N1
        rows.append([M0,Q1,Q2])
    jets=np.array(rows).T
    scale=math.sqrt(math.pi)*np.array([1/4,math.sqrt(5)/2,math.sqrt(35)/4]); j=jets*scale
    return {'order':n,'num_rays':len(mass),'source_sha256':SOURCE_SHA,'H':H,'h':h.tolist(),'hp':hp.tolist(),
            'jet_unscaled':jets.tolist(),'jet_scaled':j.tolist(),'det_scaled':float(np.linalg.det(j)),
            'det_unscaled':float(np.linalg.det(jets)),
            'ray_sha256':hashlib.sha256(ray.tobytes()).hexdigest(),'mass_sha256':hashlib.sha256(mass.tobytes()).hexdigest()}
if __name__=='__main__':
    out=[numeric_jet(n) for n in (6,8,16,64)]
    Path(BASE/'data'/'JET_NUMERIC_GL.json').write_text(json.dumps(out,indent=2)+'\n')
    for x in out:print(x['order'],x['det_scaled'],x['det_unscaled'],x['H'])
