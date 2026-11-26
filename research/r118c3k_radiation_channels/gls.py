"""Nuisance-marginalized amplitude inference on the actual C3I harmonic templates."""
import numpy as np,json,sys
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from scipy.special import sph_harm_y
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3j_radial_channels'))
from fisher import vectors
def design(cut,n=48,noise=True,cap=False):
 E,O=vectors();z,w=leggauss(n);intervals=[(.8,1)] if cap else [(-1,-cut),(cut,1)]
 xx=[];zz=[];ww=[]
 for lo,hi in intervals:
  mu=(lo+hi)/2+(hi-lo)/2*z;phi=np.arange(2*n)*np.pi/n;th,ph=np.meshgrid(np.arccos(mu),phi,indexing='ij')
  Y=np.stack([sph_harm_y(3,m,th,ph).ravel() for m in range(-3,4)],axis=1);xx.append((Y@np.stack([E,O],axis=1)).real)
  Z=[]
  for l in range(3):
   for m in range(l+1):
    v=sph_harm_y(l,m,th,ph).ravel();Z.append(v.real)
    if m:Z.append(v.imag)
  zz.append(np.stack(Z,axis=1));wt=np.repeat(w*(hi-lo)/2,2*n)*np.pi/n
  if noise:wt/=1+4*(.5+.5*np.cos(ph.ravel()))**2
  ww.append(wt)
 X=np.concatenate(xx);Z=np.concatenate(zz);W=np.sqrt(np.concatenate(ww));return X*W[:,None],Z*W[:,None]
def run():
 rows={}
 for name,cut,noise,cap in [('full',0,False,False),('cut20',np.sin(np.deg2rad(20)),True,False),('cut40',np.sin(np.deg2rad(40)),True,False),('cap',0,True,True)]:
  X,Z=design(cut,64,noise,cap);Q,_=np.linalg.qr(Z);R=X-Q@(Q.T@X);F=R.T@R;F0=X.T@X;N=np.sqrt(F.diagonal());G=F/np.outer(N,N)
  # Inject known amplitudes plus low-order foreground, check exact GLS estimator.
  amp=np.array([.7,-.3]);nuis=np.arange(Z.shape[1])*1e-8;data=X@amp+Z@nuis;fit=np.linalg.solve(F,R.T@(data-Q@(Q.T@data)))
  rows[name]=dict(cosine=float(G[0,1]),condition=float(np.linalg.cond(G)),information_retained=(F.diagonal()/F0.diagonal()).tolist(),variance_inflation=(np.diag(np.linalg.inv(F))/np.diag(np.linalg.inv(F0))).tolist(),fit_error=float(np.max(abs(fit-amp))))
 o=dict(rows=rows,scope='synthetic diagonal inverse variance and real scalar harmonic nuisance, not measured CMB noise/transfer')
 (D/'GLS.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
