"""Joint pure B probe spans with synthetic beam and nonuniform noise."""
import sys,json,numpy as np
from pathlib import Path
from scipy.special import sph_harm_y
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3q_controls'))
from pure_window import fields
P=D.parent/'r118c3l_reachable_sky'
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025
 B=np.zeros((117,2),complex)
 # Gaussian beam FWHM 5 degrees chosen synthetic low-l degradation.
 sig=np.deg2rad(5)/np.sqrt(8*np.log(2))
 for l in [3,5,7]:
  def get(r):
   z=(r['epoch']==1)&(r['ell']==l);return r['Bre'][z]+1j*r['Bim'][z]
  c,d=get(a),get(b);B[l*l-4:(l+1)**2-4]=np.exp(-l*(l+1)*sig**2/2)*np.stack([(c+d)/(2*eps**2),(c-d)/(2*eps**3)],axis=1)
 rows={}
 for cut in [20,40]:
  widths=[5,10,20];c=np.sin(np.deg2rad(cut));ss=[np.sin(np.deg2rad(cut+w)) for w in widths]
  ed=np.r_[[-1],-np.array(ss)[::-1],-c,c,ss,1];mu=[];ph=[];wt=[];z,w=leggauss(24)
  for l,r in zip(ed[:-1],ed[1:]):
   if l==-c and r==c:continue
   q,p=np.meshgrid((l+r)/2+(r-l)*z/2,2*np.pi*np.arange(48)/48,indexing='ij')
   mu.extend(q.ravel());ph.extend(p.ravel());wt.extend(np.repeat(w*(r-l)/2,48)*2*np.pi/48)
  mu,ph,wt=map(np.array,(mu,ph,wt));noise=np.sqrt(1+2*(.5+.5*np.cos(ph))**2+.5*(mu>0))
  q=np.sqrt(np.r_[wt,wt]);n=np.r_[noise,noise];real=lambda A:np.r_[A.real,A.imag]
  probes=[]
  for s in ss:
   t=np.clip((abs(mu)-c)/(s-c),0,1);W=t*t*(3-2*t);W1=np.where(t<1,6*t*(1-t)*np.sign(mu)/(s-c),0.);W2=np.where(t<1,6*(1-2*t)/(s-c)**2,0.)
   Y,Z,O,Pb=fields(mu,ph,W,W1,W2);probes.append(real(Pb)*(q*n)[:,None])
  X=real(-1j*Y@B)*(q/n)[:,None];E=real(Z)*(q/n)[:,None];raw=np.sum(X*X,axis=0)
  def span(A):
   Q,s,_=np.linalg.svd(A,full_matrices=False);Q=Q[:,s>s[0]*1e-11];return Q
  for name,Pb in [(str(w),v) for w,v in zip(widths,probes)]+[('joint',np.concatenate(probes,axis=1))]:
   Q=span(Pb);r=Q.T@X;leak=np.linalg.norm(Q.T@E,2);rows[f'{cut}_{name}']=dict(rank=Q.shape[1],retain=(np.sum(r*r,axis=0)/raw).tolist(),worst_E_leakage=float(leak));assert leak<1e-7
  Q=span(E);r=X-Q@(Q.T@X);rows[f'{cut}_nuisance_upper']=dict(retain=(np.sum(r*r,axis=0)/raw).tolist())
 o=dict(rows=rows,scope='synthetic 5 degree Gaussian beam and nonuniform variance; noise-whitened dual pure probes, joint spans not independent measurements; finite bandwidth only')
 (D/'PURE_JOINT.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
