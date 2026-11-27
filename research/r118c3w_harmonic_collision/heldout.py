"""Held-out E ell15..22 and synthetic conditional Fisher matrix, independent of training."""
import numpy as np,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent
src=D.parent/'r118c3u_exact_wedge/pixel_integrated.py'
# Reuse exact pixel quadrature with additional harmonic columns, not new estimator weights.
s=src.read_text().replace('range(2,15)','range(2,23)')
ns={'__file__':str(src),'__name__':'heldout_source'};exec(s,ns)
grid,avg,lift,realbasis=[ns[k] for k in ['grid','avg','lift','realbasis']]
P=D.parent/'r118c3l_reachable_sky'
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025;B=np.zeros((525,2),complex);sig=np.deg2rad(5)/np.sqrt(8*np.log(2))
 for l in [3,5,7]:
  def get(r):z=(r['epoch']==1)&(r['ell']==l);return r['Bre'][z]+1j*r['Bim'][z]
  u,v=get(a),get(b);B[l*l-4:(l+1)**2-4]=np.exp(-l*(l+1)*sig**2/2)*np.stack([(u+v)/(2*eps**2),(u-v)/(2*eps**3)],axis=1)
 phi=2*np.pi*(np.arange(48)+.5)/48;rows={}
 ell=np.concatenate([np.full(2*l+1,l) for l in range(2,23)])
 cl=100*(2/ell)**2*np.exp(-ell*(ell+1)*sig**2)
 for nm in [128,256]:
  for cut in [20,40]:
   lo,hi=grid(nm,cut);mu,ph=np.meshgrid((lo+hi)/2,phi,indexing='ij');wt=np.repeat((hi-lo)*2*np.pi/48,48);noise=np.sqrt(1+2*(.5+.5*np.cos(ph.ravel()))**2+.5*(mu.ravel()>0));q=np.sqrt(np.r_[wt,wt]);n=np.r_[noise,noise];real=lambda A:np.r_[A.real,A.imag]
   probes=[]
   for width in [5,10,20]:
    aa,bb=avg(lo,hi,cut,width,8);Pb=lift(bb,9,phi);probes.append(real(realbasis(Pb,9,-1j))*(q*n)[:,None])
   Y=lift(aa,22,phi);X=real(-1j*Y@B)*(q/n)[:,None];raw=np.sum(X*X,axis=0)
   E=real(realbasis(Y,22,-1))*(q/n)[:,None];Q,s,_=np.linalg.svd(np.concatenate(probes,axis=1),full_matrices=False);Q=Q[:,s>s[0]*1e-6]
   Z=Q.T@X;C=Q.T@E;cov=np.eye(C.shape[0])+(C*cl)@C.T
   for band in [14,18,22]:
    # Hold out >band from constraint; entire declared synthetic covariance used.
    U,sv,_=np.linalg.svd(C[:,ell<=band],full_matrices=True);sv=np.r_[sv,np.zeros(U.shape[0]-len(sv))]
    for cap in [1e-3,1e-4,1e-8]:
     T=U[:,sv<=cap]
     if T.shape[1]==0:continue
     z=T.T@Z;C1=T.T@C;F=z.T@np.linalg.solve(T.T@cov@T,z)
     hold=float(np.linalg.norm(C1[:,ell>band],2)) if band<22 else None
     row=dict(rank=T.shape[1],train=float(np.linalg.norm(C1[:,ell<=band],2)),heldout=hold,noise_only_retention=(np.sum(z*z,axis=0)/raw).tolist(),Fisher_retention=(np.diag(F)/raw).tolist(),corr=float(F[0,1]/np.sqrt(F[0,0]*F[1,1])))
     assert row['train']<=cap+1e-11
     rows[f'{nm}_{cut}_{band}_{cap:g}']=row
   print(nm,cut,rows.get(f'{nm}_{cut}_14_0.001'),rows.get(f'{nm}_{cut}_18_0.001'),flush=True)
 (D/'HELDOUT.json').write_text(json.dumps(dict(rows=rows,scope='synthetic beam/noise and E covariance Cl=100*(2/l)^2 beam^2; finite coordinate pixels, ell up to22 only; no observed likelihood'),indent=2)+'\n')
if __name__=='__main__':run()
