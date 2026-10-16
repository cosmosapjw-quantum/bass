"""MP70 independent fixed FD96 binary64-node summation for α and κ, not continuum quadrature.

Input nodes/weights are inherited from BASS PR167 byte-verified conversation ZIP;
computes sums with MP70 decimal-roundtripped floats. Does not re-evaluate
Gauss-Legendre nodes at arbitrary precision or certify continuum integration.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import mpmath as mp
from lrs_retarded import FD96Retarded,XMAX


def compare():
    mp.mp.dps=70
    out=[]
    for mass in (3.,30.,300.):
        f=FD96Retarded(mass)
        M=mp.mpf(repr(mass))
        q=[mp.mpf(repr(float(t))) for t in f.fd.q]
        w=[mp.mpf(repr(float(t))) for t in f.fd.rw]
        norm=mp.fsum(wi*mp.sqrt(M*M+qi*qi) for wi,qi in zip(w,q))
        for x in (0.,.7,XMAX):
            xm=mp.mpf(repr(float(x)));r=mp.exp(-xm)
            rho=mp.mpf('0'); j1=mp.mpf('0');j2=mp.mpf('0')
            for qi,wi in zip(q,w):
                k=(r*qi)**2;E=mp.sqrt(M*M+k)
                rho+=wi*E
                j1+=wi*k/E
                j2+=wi*k*k/E**3
            rho=r**3*rho/norm
            alpha=r**3*j1/(5*norm)
            kappa=r**3*(2*j1-mp.mpf(2)/5*j2)/norm
            c=f.coefficients(x)
            out.append({'m':mass,'x':x,'rho_mp':mp.nstr(rho,30),'alpha_mp':mp.nstr(alpha,30),
                       'kappa_mp':mp.nstr(kappa,30),'rho_rel':float(abs(mp.mpf(repr(c.rho0))/rho-1)),
                       'alpha_rel':float(abs(mp.mpf(repr(c.alpha))/alpha-1)),
                       'kappa_rel':float(abs(mp.mpf(repr(c.kappa))/kappa-1))})
    return {'schema':'bass.lrs.pr169.mp70.fixed_binary64_nodes.v1','precision_digits':mp.mp.dps,
             'continuous_integration_certified':False,'states':out,
             'max_relative_error':max(max(y[k] for k in ('rho_rel','alpha_rel','kappa_rel')) for y in out)}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('CREATE_ONLY_MP70')
    result=compare()
    if result['max_relative_error']>3e-14:raise AssertionError('FD96_MP70_FIXED_NODE_DRIFT')
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'max_relative_error':result['max_relative_error'],'states':len(result['states']),'status':'PASS'}))
