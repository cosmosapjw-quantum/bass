"""Physical tabulated Gaunt spectral shape diagnostic, independent of Rust quadrature."""
import numpy as np,json,hashlib
from pathlib import Path
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import RegularGridInterpolator
from scipy.linalg import expm
from numpy.polynomial.legendre import leggauss
from scipy.special import digamma
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads');I=Path('/home/cosmosapjw/worktrees/rei-htt-thomson-20261124/research/r118c3b_ff_balance')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[list(map(float,l.split('#')[0].split())) for l in (I/'gauntff.dat').read_text().splitlines() if len(l.split('#')[0].split())==81][:146]
tab=np.array(rows);assert tab.shape==(146,81)
interp=RegularGridInterpolator((-16+.2*np.arange(146),-6+.2*np.arange(81)),tab,bounds_error=True)
kb=8.617333262145e-5;edges=np.array([0.,1e-6,1e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,.1,.3,1.,np.inf]);x=np.geomspace(1e-10,60.,4097)
def g(u,t,f):
  a=np.log10(u);b=np.log10(13.605693122994/(kb*t))
  return (1-f)*interp(np.c_[a,np.full_like(a,b)])+f*interp(np.c_[a,np.full_like(a,b+np.log10(4.))])
def mat(v):
 a,b,c,d,e=v;rr=1/np.sqrt(2);t=1/np.sqrt(6)
 return np.array([[rr*a-t*b,rr*c,rr*d],[rr*c,-rr*a-t*b,rr*e],[rr*d,rr*e,2*t*b]])
mu,w=leggauss(8);phi=2*np.pi*np.arange(16)/16;M,P=np.meshgrid(mu,phi,indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(P),np.sqrt(1-M*M)*np.sin(P),M],axis=-1).reshape(-1,3);ww=np.repeat(w/2/16,16)
def analyze(name):
 p=H/('bass_r118c3b_'+name);r=np.genfromtxt(p/'history.csv',names=True,delimiter=',');s=np.genfromtxt(p/'secondary_spectrum.csv',names=True,delimiter=',')
 a=r['a'];du=np.diff(np.log(a));am=a[:-1]*np.exp(du/2);F=np.stack([r[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3);S=np.stack([r[f'S{i}'] for i in range(5)],axis=1)
 fm=np.array([expm(mat(v)*h/2)@f for v,h,f in zip(S,du,F)]);birth=np.diff(s['FF_birth']);absorb=np.diff(s['FF_abs_birth']);tm=np.diff(s['FF_T_moment'])/birth;tc=2.7255/am
 # Use effective stage temperature and midpoint species charge weight, not an exact substage spectrum.
 yhe=.245/(4*(1-.245));hii=(r['xHII'][1:]+r['xHII'][:-1])/2;heii=(r['xHeII'][1:]+r['xHeII'][:-1])/2;heiii=(r['xHeIII'][1:]+r['xHeIII'][:-1])/2;frac=4*yhe*heiii/(hii+yhe*heii+4*yhe*heiii)
 U=np.zeros(12);A=np.zeros(12);pred=0.;pred0=0.;inv=np.linalg.inv(F[-1]).T
 for b,ab,t,tr,f,aa,m in zip(birth,absorb,tm,tc,frac,am,fm):
    q=tr/t
    e0=np.exp(-x)*g(x,t,f);ab0=q*(-np.expm1(-q*x))*np.exp(-x)/(-np.expm1(-x))*g(q*x,t,f)
    ec=cumulative_trapezoid(e0,x,initial=0);ac=cumulative_trapezoid(ab0,x,initial=0)
    pred+=b*ac[-1]/ec[-1];pred0+=b*q*(digamma(1+q)+np.euler_gamma)
    ec/=ec[-1];ac/=ac[-1]
    v=n@m*(aa/a[0]);vn=np.linalg.norm(v,axis=1);scale=np.linalg.norm(v@inv.T,axis=1)*a[0]/a[-1]
    cdf=np.interp(edges[None,:]/(vn[:,None]*kb*t),x,ec,left=0,right=1)
    U+=b*np.sum((ww*scale)[:,None]*np.diff(cdf,axis=1),axis=0)
    # Bridge uses signed isotropic absorption reservoir; diagnostic bins use isotropic reference scale.
    cdf=np.interp(edges/(aa/a[0]*kb*tr),x,ac,left=0,right=1)
    A+=ab*(aa/a[-1])*np.diff(cdf)
 return dict(name=name,hashes={f:sha(p/f) for f in ('history.csv','secondary_spectrum.csv')},predicted_absorption=float(pred),actual_absorption=float(s['FF_abs_birth'][-1]),grey_conditional_absorption=float(pred0),effective_stage_relative=float(pred/s['FF_abs_birth'][-1]-1),emission_bins=U.tolist(),absorption_bins=A.tolist(),net_bins=(U-A).tolist(),emission_relative=float(U.sum()/s['FF_U'][-1]-1),absorption_relative=float(A.sum()/s['FF_abs_U'][-1]-1),scope='frequency-dependent Gaunt shape, actual accepted energy increments normalized, approximate effective temperature/species and isotropic CMB absorption; not live distorted occupation or physical Gaunt absolute normalization')
out=dict(status='SCOPED_GAUNT_SPECTRAL_DIAGNOSTIC',gaunt_sha=sha(I/'gauntff.dat'),rows=[analyze('table'),analyze('fine')])
for r in out['rows']:
 assert abs(r['emission_relative'])<1e-8 and abs(r['absorption_relative'])<1e-8
 print(r,flush=True)
(D/'SPECTRAL.json').write_text(json.dumps(out,indent=2)+'\n')
