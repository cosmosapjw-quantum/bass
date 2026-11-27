"""Pixel-integrated spin harmonics and pure-B differential probes.
Coordinate Q/U pixel averages; exact phi integral and split mu quadrature.
"""
import numpy as np,json
from pathlib import Path
from scipy.special import sph_harm_y
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3l_reachable_sky'
def grid(nm,cut):
 ed=np.linspace(-1,1,nm+1);c=np.sin(np.deg2rad(cut));lo=[];hi=[]
 for a,b in zip(ed[:-1],ed[1:]):
  if a<-c:lo.append(a);hi.append(min(b,-c))
  if b>c:lo.append(max(a,c));hi.append(b)
 return np.array(lo),np.array(hi)
def avg(lo,hi,cut,width,nq):
 c=np.sin(np.deg2rad(cut));s=np.sin(np.deg2rad(cut+width));z,w=leggauss(nq);n=len(lo)
 mu=[];wt=[];idx=[]
 for i,(a,b) in enumerate(zip(lo,hi)):
  cuts=[a]+[t for t in [-s,s] if a<t<b]+[b]
  for l,r in zip(cuts[:-1],cuts[1:]):
   mu.extend((l+r)/2+(r-l)*z/2);wt.extend(w*(r-l)/(2*(b-a)));idx.extend([i]*nq)
 mu=np.array(mu);wt=np.array(wt);idx=np.array(idx);theta=np.arccos(mu);sn=np.sqrt(1-mu*mu);ct=mu/sn
 t=np.clip((abs(mu)-c)/(s-c),0,1);W=t*t*(3-2*t);W1=np.where(t<1,6*t*(1-t)*np.sign(mu)/(s-c),0.);W2=np.where(t<1,6*(1-2*t)/(s-c)**2,0.)
 a=[];b=[]
 for l in range(2,15):
  norm=np.sqrt((l-1)*l*(l+1)*(l+2))
  for m in range(-l,l+1):
   f,g=sph_harm_y(l,m,theta,np.zeros_like(mu),diff_n=1);ft=g[:,0]
   ftt=-ct*ft+(m*m/sn**2-l*(l+1))*f;e1=-ft+m/sn*f;e2=ftt-(2*m/sn+ct)*ft+(m*m/sn**2+2*m*mu/sn**2)*f
   v=np.zeros(n,complex);np.add.at(v,idx,wt*e2/norm);a.append(v)
   if l<=9:
    v=np.zeros(n,complex);np.add.at(v,idx,wt*(W*e2+2*sn*W1*e1+sn**2*W2*f)/norm);b.append(v)
 return np.stack(a,axis=1),np.stack(b,axis=1)
def lift(A,lmax,phi):
 m=np.concatenate([np.arange(-l,l+1) for l in range(2,lmax+1)])
 return (A[:,None,:]*(np.exp(1j*phi[:,None]*m)*np.sinc(m/len(phi)))[None,:,:]).reshape(-1,len(m))
def realbasis(A,lmax,factor):
 cols=[]
 for l in range(2,lmax+1):
  i=l*l-4+l;cols.append(factor*A[:,i])
  for m in range(1,l+1):
   cols.append(factor*(A[:,i+m]+(-1)**m*A[:,i-m])/np.sqrt(2))
   cols.append(factor*1j*(A[:,i+m]-(-1)**m*A[:,i-m])/np.sqrt(2))
 return np.stack(cols,axis=1)
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025;B=np.zeros((221,2),complex);sig=np.deg2rad(5)/np.sqrt(8*np.log(2))
 for l in [3,5,7]:
  def get(r):z=(r['epoch']==1)&(r['ell']==l);return r['Bre'][z]+1j*r['Bim'][z]
  u,v=get(a),get(b);B[l*l-4:(l+1)**2-4]=np.exp(-l*(l+1)*sig**2/2)*np.stack([(u+v)/(2*eps**2),(u-v)/(2*eps**3)],axis=1)
 phi=2*np.pi*(np.arange(48)+.5)/48;rows={}
 for nm in [64,128,256]:
  for cut in [20,40]:
   lo,hi=grid(nm,cut);mu,ph=np.meshgrid((lo+hi)/2,phi,indexing='ij');wt=np.repeat((hi-lo)*2*np.pi/48,48);noise=np.sqrt(1+2*(.5+.5*np.cos(ph.ravel()))**2+.5*(mu.ravel()>0));q=np.sqrt(np.r_[wt,wt]);n=np.r_[noise,noise];real=lambda A:np.r_[A.real,A.imag]
   # 6-point per subinterval. Pole endpoint integration of spin modes with
   # half-integer powers may be imperfect; comparison uses two quadratures.
   for nq in ([6,12] if nm==128 else [6]):
    probes=[]
    for width in [5,10,20]:
     a,b=avg(lo,hi,cut,width,nq);Y=lift(a,14,phi);Pb=lift(b,9,phi);probes.append(real(realbasis(Pb,9,-1j))*(q*n)[:,None])
    X=real(-1j*Y@B)*(q/n)[:,None];E=real(realbasis(Y,14,-1))*(q/n)[:,None];raw=np.sum(X*X,axis=0)
    A=np.concatenate(probes,axis=1);Q,s,_=np.linalg.svd(A,full_matrices=False)
    for tol in [1e-4,1e-6,1e-10]:
     T=Q[:,s>s[0]*tol];rows[f'{nm}_{cut}_{nq}_{tol:g}']=dict(rank=T.shape[1],retain=(np.sum((T.T@X)**2,axis=0)/raw).tolist(),train=float(np.linalg.norm(T.T@E[:,:117],2)),holdout=float(np.linalg.norm(T.T@E[:,117:],2)),singular_ratio=float(s[T.shape[1]-1]/s[0]))
    print(nm,cut,nq,rows[f'{nm}_{cut}_{nq}_1e-06'],flush=True)
 o=dict(rows=rows,scope='coordinate Q/U pixel averages; exact phi averaging, mu quadrature split at mask and window, synthetic beam/noise; not HEALPix or observed covariance')
 (D/'PIXEL_INTEGRATED.json').write_text(json.dumps(o,indent=2)+'\n')
if __name__=='__main__':run()
