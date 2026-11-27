"""Pure-B probe bandwidth and held-out E contamination (synthetic noise/beam)."""
import sys,json,numpy as np
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
# Reuse exact C3Q spin convention but increase both probe and E holdout bandwidth.
p=D.parent/'r118c3q_controls/pure_window.py';s=p.read_text();s=s.replace('range(2,11)','range(2,15)').replace('if l<=7:','if l<=12:')
ns={'__file__':str(p),'__name__':'expanded'};exec(s,ns);fields=ns['fields']
P=D.parent/'r118c3l_reachable_sky'
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025;B=np.zeros((221,2),complex);sig=np.deg2rad(5)/np.sqrt(8*np.log(2))
 for l in [3,5,7]:
  def get(r):z=(r['epoch']==1)&(r['ell']==l);return r['Bre'][z]+1j*r['Bim'][z]
  c,d=get(a),get(b);B[l*l-4:(l+1)**2-4]=np.exp(-l*(l+1)*sig**2/2)*np.stack([(c+d)/(2*eps**2),(c-d)/(2*eps**3)],axis=1)
 rows={}
 for cut in [20,40]:
  c=np.sin(np.deg2rad(cut));width=[5,10,20];ss=np.sin(np.deg2rad(cut+np.array(width)));ed=np.r_[-1,-ss[::-1],-c,c,ss,1];mu=[];ph=[];wt=[];z,w=leggauss(24)
  for l,r in zip(ed[:-1],ed[1:]):
   if l==-c and r==c:continue
   q,p=np.meshgrid((l+r)/2+(r-l)*z/2,2*np.pi*np.arange(48)/48,indexing='ij');mu.extend(q.ravel());ph.extend(p.ravel());wt.extend(np.repeat(w*(r-l)/2,48)*2*np.pi/48)
  mu,ph,wt=map(np.array,(mu,ph,wt));noise=np.sqrt(1+2*(.5+.5*np.cos(ph))**2+.5*(mu>0));q=np.sqrt(np.r_[wt,wt]);n=np.r_[noise,noise];real=lambda A:np.r_[A.real,A.imag]
  probes=[]
  for s in ss:
   t=np.clip((abs(mu)-c)/(s-c),0,1);W=t*t*(3-2*t);W1=np.where(t<1,6*t*(1-t)*np.sign(mu)/(s-c),0.);W2=np.where(t<1,6*(1-2*t)/(s-c)**2,0.)
   Y,Z,O,Pb=fields(mu,ph,W,W1,W2);probes.append(real(Pb)*(q*n)[:,None])
  X=real(-1j*Y@B)*(q/n)[:,None];E=real(Z)*(q/n)[:,None];raw=np.sum(X*X,axis=0)
  for lmax in [7,9,12]:
   A=np.concatenate([x[:,:(lmax+1)**2-4] for x in probes],axis=1);Q,s,_=np.linalg.svd(A,full_matrices=False)
   for tol in [1e-8,1e-11]:
    T=Q[:,s>s[0]*tol];F=T.T@X;leak=T.T@E;train=float(np.linalg.norm(leak[:,:117],2));hold=float(np.linalg.norm(leak[:,117:],2))
    rows[f'{cut}_{lmax}_{tol:g}']=dict(rank=T.shape[1],singular_ratio=float(s[T.shape[1]-1]/s[0]),retain=(np.sum(F*F,axis=0)/raw).tolist(),train_leak=train,holdout_leak=hold)
    assert max(train,hold)<1e-6,(cut,lmax,tol,train,hold)
 o=dict(rows=rows,scope='synthetic 5degree beam/nonuniform noise, joint pure-B probes bandwidth7/9/12, heldout E 11..14, finite test not observed likelihood')
 (D/'PURE_BAND.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
