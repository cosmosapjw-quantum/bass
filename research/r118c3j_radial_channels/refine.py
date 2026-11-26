"""Refine physical control and independently integrate mask at exact boundaries."""
import numpy as np,json
from pathlib import Path
from radial import solve
from physical_budget import check
from optimize import evaluate
from fisher import fisher,vectors
from scipy.special import sph_harm_y
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
def refine():
 old=json.loads((D/'PHYSICAL_BUDGET.json').read_text());rows=[]
 for a in old:
  z=solve([.001,.006,.05],a['nw'],160,512);b=check(z)
  A=np.array(a['A']);s=max(a['pointwise_peak'],np.linalg.norm(A[:,0]))
  B=np.array(b['A']);scale=max(b['pointwise_peak'],np.linalg.norm(B[:,0]))
  rows.append(dict(nw=a['nw'],ratio=z['ratio'],physical_whitened_ratio=b['whitened_ratio'],whitened_bound=b['whitened_bound'],prior_control_transfer=evaluate(np.array(z['M']),A/s),fresh_peak_bounded=evaluate(np.array(z['M']),B/scale),coarse_peak_scale=s,fine_peak_scale=scale))
 return dict(refinement=rows,fisher32=fisher(*vectors(),32),fisher128=fisher(*vectors(),128),scope='linear physical source norm and sampled peak normalization; synthetic mask discontinuities need aligned quadrature for exact cut')
def aligned(n,cut,noise=False,north=False):
 E,O=vectors();z,w=leggauss(n)
 intervals=[(.8,1.)] if north else [(-1.,-cut),(cut,1.)]
 G=np.zeros((2,2))
 for a,b in intervals:
  mu=(a+b)/2+(b-a)/2*z;ww=w*(b-a)/2;phi=np.arange(2*n)*np.pi/n
  th,ph=np.meshgrid(np.arccos(mu),phi,indexing='ij')
  Y=np.stack([sph_harm_y(3,m,th,ph).ravel() for m in range(-3,4)],axis=1)
  s=(Y@np.stack([E,O],axis=1)).real
  wt=np.repeat(ww,2*n)*np.pi/n
  if noise:wt/=1+4*(.5+.5*np.cos(ph.ravel()))**2
  G+=s.T@(wt[:,None]*s)
 F=G/np.sqrt(np.outer(G.diagonal(),G.diagonal()))
 return dict(cosine=float(F[0,1]),condition=float(np.linalg.cond(F)),info=G.diagonal().tolist())
def audit():
 out={}
 for label,c,n,cap in [('cut20',np.sin(np.deg2rad(20)),False,False),('cut40',np.sin(np.deg2rad(40)),False,False),('cut20_aniso',np.sin(np.deg2rad(20)),True,False),('north_cap',0.,True,True)]:
  a=aligned(96,c,n,cap);b=aligned(192,c,n,cap);assert abs(a['cosine']-b['cosine'])<1e-9
  out[label]=b
 (D/'FISHER_ALIGNED.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':
 import sys
 if len(sys.argv)>1 and sys.argv[1]=='refine':
  (D/'REFINEMENT.json').write_text(json.dumps(refine(),indent=2)+'\n')
 else:audit()
