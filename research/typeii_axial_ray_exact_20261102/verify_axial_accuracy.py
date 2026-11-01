#!/usr/bin/env python3
"""Independent Gauss order refinement for original TypeII axial optical-depth integrals."""
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.integrate import quad
from numpy.polynomial.legendre import leggauss
p=Path(__file__).resolve().parents[2]
d=Path(__file__).resolve().parent
s=json.loads((p/"compiler/validation/typeii_fixture_canonical.json").read_text())["trajectory"]["samples"]
ts=np.array([a["tau"] for a in s]); x=np.array([a["state"] for a in s]); dx=np.array([a["rhs"] for a in s])
f=CubicHermiteSpline(ts,x,dx,axis=0)
def integrand(t,sign):
    v=f(t)[4]
    return (1-sign*v)/np.sqrt(1-v*v)
reference={
 sign:sum(quad(integrand,lo,hi,args=(sign,),epsabs=1e-15,epsrel=1e-13)[0] for lo,hi in zip(ts[:-1],ts[1:]))
 for sign in (+1,-1)
}
errors={}
for order in (1,2,4,8,16):
    u,w=leggauss(order)
    vals={}
    for sign in (+1,-1):
        z=0.
        for lo,hi in zip(ts[:-1],ts[1:]):
            pts=lo+0.5*(hi-lo)*(u+1)
            v=f(pts)[:,4]
            z+=float(0.5*(hi-lo)*np.dot(w,(1-sign*v)/np.sqrt(1-v*v)))
        vals[str(sign)]={"value":z,"abs_error":abs(z-reference[sign])}
    errors[str(order)]=vals
if not (max((errors['8'][s]['abs_error'] for s in ('1', '-1'))) < 8e-14): raise AssertionError('PHYSICS_GATE_AT_verify_axial_accuracy.py_LINE_33')
if not (max((errors['16'][s]['abs_error'] for s in ('1', '-1'))) < 8e-14): raise AssertionError('PHYSICS_GATE_AT_verify_axial_accuracy.py_LINE_34')
# independent exact Hermite integral is exact for sigma_22, compare interval-by-interval adaptive quad
sigma22=x[:,0]+np.sqrt(3)*x[:,1];sigma22dot=dx[:,0]+np.sqrt(3)*dx[:,1]
h=np.diff(ts)
exact=float(np.sum(h*(sigma22[:-1]+sigma22[1:])/2+h*h*(sigma22dot[:-1]-sigma22dot[1:])/12))
numerical=sum(quad(lambda t:f(t)[0]+np.sqrt(3)*f(t)[1],lo,hi,epsabs=1e-15,epsrel=1e-13)[0] for lo,hi in zip(ts[:-1],ts[1:]))
if not (abs(exact - numerical) < 1e-13): raise AssertionError('PHYSICS_GATE_AT_verify_axial_accuracy.py_LINE_40')
out={"schema":"bass.typeii.axis_r8.quadrature_refinement.v1","orders":errors,
     "sigma22_piecewise_Hermite_exact_integral":exact,
     "sigma22_piecewise_independent_quad":float(numerical),
     "sigma22_abs_gap":abs(exact-numerical),
     "reference_quadrature":{str(k):float(v) for k,v in reference.items()},
     "verdict":"NUMERICALLY_CHECKED_SCOPED_CONVERGENCE"}
(d/"AXIAL_ACCURACY_RESULT.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
