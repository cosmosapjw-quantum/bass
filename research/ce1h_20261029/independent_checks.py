"""Independent mpmath/analytic checks of CE1-H pressure monotonicity theorem."""
from fractions import Fraction
import json, math
from pathlib import Path
import mpmath as mp
import numpy as np

mp.mp.dps=100
f=lambda x: mp.mpf(x.numerator)/mp.mpf(x.denominator)
q=lambda x: Fraction.from_float(float(x))
mu=list(map(q,[0.,.5,1.]));ph=list(map(q,[0.,.25,.75,1.]))
W=[[q(x) for x in row] for row in [[.1,.25,.05],[.2,.15,.15]]]
press=[mp.mpf('0')]*3
for i in range(2):
 for j in range(3):
  ma,mb=mu[i:i+2];ta,tb=ph[j:j+2]
  mz=f((ma*ma+ma*mb+mb*mb)/3)
  C=mp.mpf('.5')+(mp.sin(mp.pi*f(tb))-mp.sin(mp.pi*f(ta)))/(2*mp.pi*f(tb-ta))
  means=[(1-mz)*C,(1-mz)*(1-C),mz]
  for k in range(3):press[k]+=f(W[i][j])*means[k]
E=sum((sum(row, Fraction()) for row in W),Fraction())
assert abs(sum(press)-f(E))<mp.mpf('1e-90')

# Jacobian for one ray, with q_i^2>=0 and b_i>0.
rng=np.random.default_rng(10329)
max_sign_violation=mp.mpf(0);max_row_identity=mp.mpf(0)
for _ in range(48):
 x=np.abs(rng.normal(size=3));x=x/x.sum()
 ell=rng.uniform(0,.4,size=3)
 b=[mp.exp(-2*mp.mpf(float(y))) for y in ell]
 x=[mp.mpf(float(y)) for y in x]
 Z=sum(b[k]*x[k] for k in range(3))
 v=mp.exp(-sum(mp.mpf(float(y)) for y in ell))
 p=[v*b[i]*x[i]/mp.sqrt(Z) for i in range(3)]
 for i in range(3):
  jac=[-(1+2*(i==j))*p[i]+v*b[i]*b[j]*x[i]*x[j]/Z**mp.mpf('1.5') for j in range(3)]
  max_sign_violation=max(max_sign_violation,max(jac))
  max_row_identity=max(max_row_identity,abs(sum(abs(z) for z in jac)-4*p[i]))
assert max_sign_violation <=0
assert max_row_identity<mp.mpf('1e-90')

from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_sharp import initial_continuum_pressure_cap
s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],backend='python_oracle')
c=initial_continuum_pressure_cap(s)
assert all(mp.mpf(lo)<=press[i]<=mp.mpf(hi) for i,(lo,hi) in enumerate(c['pressure_intervals']))
report={
 'method':'mpmath100 independently integrated rational original cell means; 48 independent high precision one-ray Jacobians',
 'continuum_energy_exact':str(E),
 'p0_mpmath':[mp.nstr(p,55) for p in press],
 'p0_interval':c['pressure_intervals'],
 'jacobian_positive_violation':mp.nstr(max_sign_violation,15),
 'row_sum_identity_max_residual':mp.nstr(max_row_identity,15),
 'test_pass':True,
 'formal_machine_proof':False
}
open(Path(__file__).resolve().parent/'INDEPENDENT_CHECKS.json','w').write(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
