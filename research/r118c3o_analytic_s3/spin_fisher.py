"""True spin-2 Q/U cut-sky joint Fisher on native early-generated templates."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'r118c3l_reachable_sky';M=64
def run():
 d=np.genfromtxt(D/'spin_basis.csv.gz',names=True,delimiter=',');nr=int(d['ray'].max()+1);assert len(d)==nr*M
 Y=(d['re']+1j*d['im']).reshape(M,nr).T;mu=d['mu'][:nr];ph=d['phi'][:nr];w=d['w'][:nr]
 gram=Y.conj().T@(Y*w[:,None]);err=float(np.max(abs(gram[4:,4:]-np.eye(M-4))));assert err<1e-12
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025
 def get(r,l,key):
  z=(r['epoch']==1)&(r['ell']==l);return r[key+'re'][z]+1j*r[key+'im'][z]
 E=np.zeros(M,complex);B2=E.copy();B3=E.copy()
 E[4:9]=(get(a,2,'E')-get(b,2,'E'))/(2*eps)
 for l in [3,5,7]:
  p,q=get(a,l,'B'),get(b,l,'B');B2[l*l:(l+1)**2]=(p+q)/(2*eps**2);B3[l*l:(l+1)**2]=(p-q)/(2*eps**3)
 templates=np.stack([-Y@E,-1j*(Y@B2),-1j*(Y@B3)],axis=1)
 def realfield(t):return np.concatenate([t.real,t.imag],axis=0)
 rows={}
 for cut in [0,20,40,70]:
  for asym in [False,True]:
   mask=(abs(mu)>=np.sin(np.deg2rad(cut)))
   if asym:mask&=~((ph<.8)&(mu>0))
   weight=w[mask]*(1 if not asym else 1/(1+2*(.5+.5*np.cos(ph[mask]))**2));W=np.sqrt(np.r_[weight,weight])
   X=realfield(templates[mask])*W[:,None]
   raw=X.T@X;norm=np.sqrt(raw.diagonal());C=raw/np.outer(norm,norm)
   omit=(np.linalg.solve(raw[1:,1:],raw[1:,0])/np.array([eps,eps**2])).tolist()
   for lmax in [2,4,6]:
    Z=[]
    for l in range(2,lmax+1):
     for m in range(l+1):
      c=np.zeros(M,complex);c[l*l+l+m]=1
      if m:c[l*l+l-m]=(-1)**m
      Z.append(-Y@c)
      if m:
       c=np.zeros(M,complex);c[l*l+l+m]=1j;c[l*l+l-m]=-1j*(-1)**m;Z.append(-Y@c)
    Z=realfield(np.stack(Z,axis=1)[mask])*W[:,None]
    U,s,_=np.linalg.svd(Z,full_matrices=False);U=U[:,s>s[0]*1e-12];R=X-U@(U.T@X);F=R.T@R
    assert F[0,0]/raw[0,0]<1e-20
    g=F[1:,1:]/np.sqrt(np.outer(F.diagonal()[1:],F.diagonal()[1:]))
    rows[f'{cut}_{int(asym)}_E{lmax}']=dict(retain=(F.diagonal()/raw.diagonal()).tolist(),B_condition=float(np.linalg.cond(g)),EB2_cos=float(C[0,1]),EB3_cos=float(C[0,2]),omitted_E_B_amplitude_bias=omit)
 o=dict(spin_gram_max_error=err,rows=rows,scope='native spin+2 harmonics, true Q/U real maps, synthetic mask/noise and arbitrary E nuisance through lmax; no actual Planck covariance or exact continuum pure modes')
 (D/'SPIN_FISHER.json').write_text(json.dumps(o,indent=2)+'\n')
 for k,v in rows.items():
  if k.endswith('E6'):print(k,v,flush=True)
if __name__=='__main__':run()
