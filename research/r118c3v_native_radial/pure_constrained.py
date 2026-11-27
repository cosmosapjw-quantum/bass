"""Finite pixel pure-B information under an explicit E-band leakage constraint."""
import numpy as np,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'r118c3u_exact_wedge';sys.path.insert(0,str(P))
from pixel_integrated import grid,avg,lift,realbasis
SKY=D.parent/'r118c3l_reachable_sky'
def run():
 a,b=[np.genfromtxt(SKY/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025;B=np.zeros((221,2),complex);sig=np.deg2rad(5)/np.sqrt(8*np.log(2))
 for l in [3,5,7]:
  def get(r):z=(r['epoch']==1)&(r['ell']==l);return r['Bre'][z]+1j*r['Bim'][z]
  u,v=get(a),get(b);B[l*l-4:(l+1)**2-4]=np.exp(-l*(l+1)*sig**2/2)*np.stack([(u+v)/(2*eps**2),(u-v)/(2*eps**3)],axis=1)
 phi=2*np.pi*(np.arange(48)+.5)/48;rows={}
 for nm in [64,128,256]:
  for cut in [20,40]:
   lo,hi=grid(nm,cut);mu,ph=np.meshgrid((lo+hi)/2,phi,indexing='ij');wt=np.repeat((hi-lo)*2*np.pi/48,48);noise=np.sqrt(1+2*(.5+.5*np.cos(ph.ravel()))**2+.5*(mu.ravel()>0));q=np.sqrt(np.r_[wt,wt]);n=np.r_[noise,noise];real=lambda A:np.r_[A.real,A.imag]
   probes=[]
   for width in [5,10,20]:
    a,b=avg(lo,hi,cut,width,8);Y=lift(a,14,phi);Pb=lift(b,9,phi);probes.append(real(realbasis(Pb,9,-1j))*(q*n)[:,None])
   X=real(-1j*Y@B)*(q/n)[:,None];E=real(realbasis(Y,14,-1))*(q/n)[:,None];raw=np.sum(X*X,axis=0)
   Q,s,_=np.linalg.svd(np.concatenate(probes,axis=1),full_matrices=False);Q=Q[:,s>s[0]*1e-6]
   Z=Q.T@X;C=Q.T@E;U,sv,_=np.linalg.svd(C,full_matrices=True);sv=np.r_[sv,np.zeros(U.shape[0]-len(sv))]
   for cap in [1e-2,1e-3,1e-4,1e-8]:
    A=U[:,sv<=cap];proj=A.T@Z;err=A.T@C;leak=float(np.linalg.norm(err,2)) if len(A.T) else 0.
    assert leak<=cap+1e-12
    rows[f'{nm}_{cut}_{cap:g}']=dict(rank=A.shape[1],leak=leak,retain=(np.sum(proj*proj,axis=0)/raw).tolist(),unconstrained_rank=Q.shape[1],unconstrained_retain=(np.sum(Z*Z,axis=0)/raw).tolist(),unconstrained_leak=float(np.linalg.norm(C,2)))
   print(nm,cut,rows[f'{nm}_{cut}_1e-08'],flush=True)
 out=dict(rows=rows,scope='finite pixel-integrated pure-B probe subspace; all E ell2..14 constrained, no independent ell>14 validation, synthetic beam/noise. Constraint bounds Euclidean leakage operator, not actual E covariance.')
 (D/'PURE_CONSTRAINED.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
