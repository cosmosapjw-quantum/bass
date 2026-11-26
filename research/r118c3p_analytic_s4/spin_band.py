"""Finite bandwidth E nuisance projection using native spin2 Q/U basis.
No actual observed covariance. Quantify worst-case leakage from omitted E band.
"""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'r118c3l_reachable_sky';M=121
def run():
 d=np.genfromtxt(D/'spin10.csv.gz',names=True,delimiter=',');nr=int(d['ray'].max()+1);assert len(d)==nr*M
 Y=(d['re']+1j*d['im']).reshape(M,nr).T;mu=d['mu'][:nr];ph=d['phi'][:nr];w=d['w'][:nr]
 gram=Y.conj().T@(Y*w[:,None]);err=float(np.max(abs(gram[4:,4:]-np.eye(M-4))));assert err<1e-12
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025
 def get(r,l,key):
  z=(r['epoch']==1)&(r['ell']==l);return r[key+'re'][z]+1j*r[key+'im'][z]
 B2=np.zeros(M,complex);B3=B2.copy()
 for l in [3,5,7]:
  p,q=get(a,l,'B'),get(b,l,'B');B2[l*l:(l+1)**2]=(p+q)/(2*eps**2);B3[l*l:(l+1)**2]=(p-q)/(2*eps**3)
 X=-1j*Y@np.stack([B2,B3],axis=1)
 # Real E harmonic coefficients normalized to Euclidean coefficient norm.
 Z=[];ell=[]
 for l in range(2,11):
  for m in range(l+1):
   c=np.zeros(M,complex);c[l*l+l+m]=1 if m==0 else 1/np.sqrt(2)
   if m:c[l*l+l-m]=(-1)**m/np.sqrt(2)
   Z.append(-Y@c);ell.append(l)
   if m:
    c=np.zeros(M,complex);c[l*l+l+m]=1j/np.sqrt(2);c[l*l+l-m]=-1j*(-1)**m/np.sqrt(2);Z.append(-Y@c);ell.append(l)
 Z=np.stack(Z,axis=1);ell=np.array(ell);rows={}
 for cut in [0,20,40,70]:
  for asym in [False,True]:
   mask=abs(mu)>=np.sin(np.deg2rad(cut))
   if asym:mask&=~((ph<.8)&(mu>0))
   wt=w[mask]*(1 if not asym else 1/(1+2*(.5+.5*np.cos(ph[mask]))**2))
   W=np.sqrt(np.r_[wt,wt]);rf=lambda A:np.r_[A[mask].real,A[mask].imag]*W[:,None]
   x=rf(X);z=rf(Z);raw=x.T@x
   for l in [2,4,6,8,10]:
    U,s,_=np.linalg.svd(z[:,ell<=l],full_matrices=False);U=U[:,s>s[0]*1e-12]
    R=x-U@(U.T@x);F=R.T@R;norm=np.sqrt(F.diagonal());G=F/np.outer(norm,norm)
    leakage=R.T@z;kept=float(np.max(abs(leakage[:,ell<=l]))/max(np.linalg.norm(R),1e-300))
    omit=np.linalg.solve(F,leakage[:,ell>l]) if l<10 else np.zeros((2,0))
    rows[f'{cut}_{int(asym)}_E{l}']=dict(retain=(F.diagonal()/raw.diagonal()).tolist(),B_condition=float(np.linalg.cond(G)),nuisance_rank=U.shape[1],included_leakage=kept,omitted_E_worst_bias_per_unit_coeff=np.linalg.norm(omit,axis=1).tolist())
    assert kept<1e-10
 o=dict(gram_error=err,rows=rows,scope='native spin2 Q/U maps; finite E bandwidth 2..10, synthetic masks and weights; not continuum pure B or observed covariance')
 (D/'SPIN_BAND.json').write_text(json.dumps(o,indent=2)+'\n')
 for k,v in rows.items():
  if k.startswith(('20_0','40_0')):print(k,v,flush=True)
if __name__=='__main__':run()
