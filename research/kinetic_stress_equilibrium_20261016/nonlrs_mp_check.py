"""MP50 fixed-node independent arithmetic check; not a continuum oracle."""
import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np

from nonlrs_fd96 import B, FD96Diagonal


def run():
    mp.mp.dps=50
    f=FD96Diagonal(3.,.3,radial=32,polar=16,azimuth=16,triaxial_C=.2)
    x=.7;u=np.array([.04,-.02]);beta=B@u
    one=lambda y:mp.mpf(str(float(y)))
    r=mp.exp(-one(x));m=one(f.mass);A=one(f.A);C=one(f.triaxial_C)
    q=[one(v) for v in f.q];dq=[one(v) for v in f.dq]
    n=[[one(v) for v in row] for row in f.nhat]
    aw=[one(v) for v in f.wang]
    radial=[dq[k]*q[k]**2/(mp.exp(q[k])+1) for k in range(len(q))]
    norm=sum(radial[k]*mp.sqrt(m*m+q[k]*q[k]) for k in range(len(q)))
    pref=r**3/(4*mp.pi*norm)
    rho=mp.mpf(0);P=[mp.mpf(0) for _ in range(3)]
    H=[[mp.mpf(0) for _ in range(3)] for _ in range(3)]
    Pxy=mp.mpf(0)
    for k in range(len(q)):
        for j in range(len(n)):
            nv=n[j]
            W=1+A*(3*nv[2]**2-1)/2+C*(nv[0]**2-nv[1]**2)
            wt=pref*radial[k]*aw[j]*W
            mom=[r*q[k]*nv[i]*mp.exp(-one(beta[i])) for i in range(3)]
            w=[p*p for p in mom];E=mp.sqrt(m*m+sum(w))
            rho+=wt*E;Pxy+=wt*mom[0]*mom[1]/E
            for i in range(3):
                P[i]+=wt*w[i]/E
                for l in range(3):
                    H[i][l]+=wt*((2*w[i]/E if i==l else 0)-w[i]*w[l]/E**3)
    v=f.moments(x,u)
    Hnp=np.array([[float(y) for y in row] for row in H])
    result=dict(schema="bass.fd96.nonlrs.mp50_fixed_binary64_nodes.v1",
        decimal_digits=50,grid=f.resolution,
        source="original FD96 radial functional form on fixed binary64 quadrature nodes, C=.2 explicit angular extension",
        rho_error=float(v.rho-rho),
        pressure_diagonal_max_error=max(abs(float(v.pressure[i,i]-P[i])) for i in range(3)),
        offdiagonal_xy_error=float(v.pressure[0,1]-Pxy),
        hessian_max_error=float(np.max(abs(v.hessian3-Hnp))),
        normalized_denominator=v.rho,
        scope="fixed quadrature nodes and weights; not continuum quadrature accuracy")
    return result


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);out=p.parse_args().out
    if out.exists():raise FileExistsError('CREATE_ONLY_MP_EVIDENCE')
    r=run();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
