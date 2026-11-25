"""Conditional leading B3 sign/cancellation on actual H, ne clock."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp,cumulative_trapezoid
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c2t_thomson_sky'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
g=P/'owned_0.03_512_6_scatter.csv';p=P/'NE.csv';j=json.loads((P/'RESULTS.json').read_text())
assert sha(g)==j['cases'][g.stem]['sha'] and sha(p)==j['input_ne_sha']
r=np.genfromtxt(g,names=True,delimiter=',');n=np.genfromtxt(p,names=True,delimiter=',')
end=r['u'][-1];C=299792458.*6.6524587051e-29/2.1842852410855023e-18
def K(t):return C*np.interp(t,n['u'],n['ne_m3'])/np.interp(t,r['u'],r['h'])
# S=alpha A + beta B, alpha=1; STF B_polarization causal response.
def ode(beta):
 def rhs(t,y):
  k=K(t);a,b,c,d,z=y
  return [-4-k*(.9*a+.4*b),-k*(.15*a+.4*b),-4*beta(t)-k*(.9*c+.4*d),-k*(.15*c+.4*d),d-beta(t)*b-k*z]
 s=solve_ivp(rhs,(0,end),np.zeros(5),method='DOP853',rtol=1e-11,atol=1e-13,max_step=end/1024,dense_output=True);assert s.success
 t=np.linspace(0,end,1025);y=s.sol(t);src=y[3]-beta(t)*y[1]
 return float(y[4,-1]),float(src.min()),float(src.max())
# independent triangular double quadrature (tau fine mesh, not ODE response)
tt=np.linspace(0,end,32769);tau=cumulative_trapezoid(K(tt),tt,initial=0)
def integ(beta,n):
 x,w=leggauss(n);t=(x+1)*end/2;w=w*end/2
 v=t[:,None]*(x[None,:]+1)/2;ww=t[:,None]*leggauss(n)[1][None,:]/2
 a=np.interp(t,tt,tau)[:,None]-np.interp(v,tt,tau)
 ret=6/7*(np.exp(-.3*a)-np.exp(-a))
 final=np.exp(-(tau[-1]-np.interp(t,tt,tau)))
 return float(np.sum(w*final*np.sum(ww*ret*(beta(v)-beta(t)[:,None]),axis=1)))
linear=lambda t:t/end
quad=lambda t:(t/end)**2
D1=ode(linear)[0];D2=ode(quad)[0];c=D2/D1
cases={}
for name,beta in [('linear',linear),('quadratic',quad),('cancel',lambda t:quad(t)-c*linear(t)),('fixed',lambda t:np.ones_like(t)*.3)]:
 v,lo,hi=ode(beta);a=integ(beta,256);b=integ(beta,512)
 cases[name]=dict(ode=v,source_min=lo,source_max=hi,quadrature256=a,quadrature512=b,absolute_difference=abs(v-b))
 print(name,cases[name],flush=True)
assert D1<0 and D2<0 and cases['linear']['source_max']<1e-12 and abs(cases["cancel"]["ode"])<1e-8*abs(D1)
assert cases['cancel']['source_min']<0<cases['cancel']['source_max']
assert max(x['absolute_difference'] for x in cases.values())<1e-5*abs(D1)
(D/'HISTORY_SIGN.json').write_text(json.dumps(dict(status='DERIVED_SIGN_AND_CANCELLATION_NUMERIC',scope='leading-order two-STF prescribed shear; actual H and electron-density history; not self-consistent evolved S',geometry_sha=sha(g),ne_sha=sha(p),cancel_c=c,depth=float(tau[-1]),cases=cases),indent=2)+'\n')
