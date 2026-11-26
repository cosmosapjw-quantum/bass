"""Real harmonic Fisher identifiability on synthetic masked/noisy skies."""
import numpy as np,json,sys
from pathlib import Path
from scipy.special import sph_harm_y
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
def vectors():
 p=D.parent/'r118c3i_temporal_rank';eps=.003125
 def v(l):
  a=np.genfromtxt(p/f'{l}.csv',names=True,delimiter=',');z=a['ell']==3;return a['re'][z]+1j*a['im'][z]
 # Read actual labels rather than assuming naming convention.
 E=(v('parity_1')+v('parity_-1'))/(2*eps**2);O=(v('parity_1')-v('parity_-1'))/(2*eps**3)
 return E,O
def fisher(E,O,n=32):
 mu,w=leggauss(n);phi=np.arange(2*n)*np.pi/n;th,ph=np.meshgrid(np.arccos(mu),phi,indexing='ij');w=np.repeat(w,2*n)*np.pi/n
 Y=np.stack([sph_harm_y(3,m,th,ph).ravel() for m in range(-3,4)],axis=1)
 v=np.stack([E,O],axis=1);real=Y@v;imag=np.linalg.norm(real.imag,axis=0)/np.linalg.norm(real,axis=0)
 # Native coefficients have real-sky reality condition.
 assert max(imag)<1e-7,imag
 s=real.real;out={}
 z=np.cos(th).ravel();az=ph.ravel()
 for name,mask,noise in [('full',np.ones_like(z,bool),np.ones_like(z)),('cut20',abs(z)>=np.sin(np.deg2rad(20)),np.ones_like(z)),('cut40',abs(z)>=np.sin(np.deg2rad(40)),np.ones_like(z)),('cut20_aniso',abs(z)>=np.sin(np.deg2rad(20)),1+4*(.5+.5*np.cos(az))**2),('north_cap',z>.8,1+4*(.5+.5*np.cos(az))**2)]:
  G=s.T@((w*mask/noise)[:,None]*s);a=np.sqrt(np.diag(G));F=G/np.outer(a,a);ev=np.linalg.eigvalsh(F);out[name]=dict(cosine=float(F[0,1]),normalized_fisher_eigenvalues=ev.tolist(),condition=float(ev[-1]/ev[0]),amplitude_information=np.diag(G).tolist(),sky_fraction=float(np.dot(w,mask)/(4*np.pi)))
 return dict(results=out,reality_error=imag.tolist(),scope='synthetic real-sky ell=3 mask and diagonal pixel precision; not Planck or measured covariance')
if __name__=='__main__':
 o=fisher(*vectors());(D/'FISHER.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
