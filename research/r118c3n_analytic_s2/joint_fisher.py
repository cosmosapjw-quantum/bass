"""Synthetic multi-channel I/E/B Fisher with explicit TE quadratic observable."""
import numpy as np,json
from pathlib import Path
from scipy.special import sph_harm_y
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3l_reachable_sky'
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025
 def coeff(s,l,key):
  z=(s['epoch']==1)&(s['ell']==l);return s[key+'re'][z]+1j*s[key+'im'][z]
 I=(coeff(a,2,'I')-coeff(b,2,'I'))/(2*eps);E=(coeff(a,2,'E')-coeff(b,2,'E'))/(2*eps)
 TE=float(np.vdot(E,I).real/5);TT=float(np.vdot(I,I).real/5);EE=float(np.vdot(E,E).real/5)
 rows={}
 for cut in [0,20,40,70]:
  for nuisance in [1,2]:
   z,w=leggauss(48);c=np.sin(np.deg2rad(cut));XX=[];ZZ=[];ww=[]
   for lo,hi in [(-1,-c),(c,1)]:
    mu=(lo+hi)/2+(hi-lo)/2*z;phi=np.arange(96)*np.pi/48;th,ph=np.meshgrid(np.arccos(mu),phi,indexing='ij')
    Y=lambda l:np.stack([sph_harm_y(l,m,th,ph).ravel() for m in range(-l,l+1)],axis=1)
    v=np.zeros((th.size,3,3));v[:,0,0]=(Y(2)@I).real;v[:,1,0]=(Y(2)@E).real
    for l in [3,5,7]:
     x,y=coeff(a,l,'B'),coeff(b,l,'B');v[:,2,1]+=(Y(l)@(x+y)/(2*eps**2)).real;v[:,2,2]+=(Y(l)@(x-y)/(2*eps**3)).real
    Z=[]
    for l in range(nuisance+1):
     for m in range(l+1):
      q=sph_harm_y(l,m,th,ph).ravel();Z.append(q.real)
      if m:Z.append(q.imag)
    Z=np.stack(Z,axis=1)
    # Synthetic channel precision with modest T/E correlation, no actual Stokes cut-sky mixing.
    precision=np.linalg.cholesky(np.array([[1.,.3,0.],[.3,2.,0.],[0.,0.,4.]]))
    v=np.einsum('nca,cd->nda',v,precision)
    Z3=np.zeros((th.size,3,3*Z.shape[1]))
    for k in range(3):Z3[:,k,k*Z.shape[1]:(k+1)*Z.shape[1]]=Z
    Z3=np.einsum('nca,cd->nda',Z3,precision)
    wt=np.repeat(w*(hi-lo)/2,96)*np.pi/48/(1+2*(.5+.5*np.cos(ph.ravel()))**2)
    XX.append(v.reshape(-1,3));ZZ.append(Z3.reshape(-1,Z3.shape[-1]));ww.append(np.repeat(wt,3))
   W=np.sqrt(np.concatenate(ww));X=np.concatenate(XX)*W[:,None];Z=np.concatenate(ZZ)*W[:,None]
   Q,_=np.linalg.qr(Z);R=X-Q@(Q.T@X);F=R.T@R;raw=X.T@X
   retain=F.diagonal()/raw.diagonal();active=retain>1e-18
   G=F[np.ix_(active,active)];N=np.sqrt(G.diagonal());G=G/np.outer(N,N)
   rows[f'{cut}_l{nuisance}']=dict(retained=retain.tolist(),rank=int(active.sum()),condition=float(np.linalg.cond(G)),raw_info=raw.diagonal().tolist(),marginal_info=F.diagonal().tolist())
 o=dict(TE=TE,TT=TT,EE=EE,TE_correlation=TE/np.sqrt(TT*EE),rows=rows,scope='synthetic scalar I/E/B harmonic maps, correlated T/E noise, nuisance per map; TE derived quadratic observable not independent likelihood, no actual Stokes mask mixing or Planck data')
 (D/'JOINT_FISHER.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
