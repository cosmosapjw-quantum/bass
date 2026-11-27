"""Explicit eth^2(W Y_lm) pure B probes and finite-band Q/U comparison.
All masks/noise synthetic; actual early-generated B templates from native C3L.
"""
import numpy as np,json
from pathlib import Path
from scipy.special import sph_harm_y
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3l_reachable_sky'
def grid(cut,width):
 c=np.sin(np.deg2rad(cut));s=np.sin(np.deg2rad(cut+width));z,w=leggauss(40);phi=2*np.pi*np.arange(64)/64;arr=[]
 for lo,hi in [(-1,-s),(-s,-c),(c,s),(s,1)]:
  mu=(lo+hi)/2+(hi-lo)/2*z;m,p=np.meshgrid(mu,phi,indexing='ij')
  arr.append((m.ravel(),p.ravel(),np.repeat(w*(hi-lo)/2,64)*2*np.pi/64))
 mu,ph,wt=[np.concatenate([a[i] for a in arr]) for i in range(3)]
 t=np.clip((abs(mu)-c)/(s-c),0,1);W=t*t*(3-2*t);W1=np.where(t<1,6*t*(1-t)*np.sign(mu)/(s-c),0.);W2=np.where(t<1,6*(1-2*t)/(s-c)**2,0.)
 return mu,ph,wt,W,W1,W2
def fields(mu,ph,W,W1,W2):
 theta=np.arccos(mu);sin=np.sqrt(1-mu*mu);ct=mu/sin
 Y=[];ordinary=[];pure=[];Z=[]
 for l in range(2,11):
  norm=np.sqrt((l-1)*l*(l+1)*(l+2))
  a=[];b=[];p=[]
  for m in range(-l,l+1):
   f,grad=sph_harm_y(l,m,theta,ph,diff_n=1);ft=grad[:,0]
   ftt=-ct*ft+(m*m/sin**2-l*(l+1))*f
   e1=-ft+m/sin*f;e2=ftt-(2*m/sin+ct)*ft+(m*m/sin**2+2*m*mu/sin**2)*f
   a.append(e2/norm);b.append(W*e2/norm);p.append((W*e2+2*sin*W1*e1+sin**2*W2*f)/norm)
  a,b,p=map(lambda x:np.stack(x,axis=1),(a,b,p))
  Y.append(a)
  for m in range(l+1):
   v=np.zeros(2*l+1,complex);v[l+m]=1 if m==0 else 1/np.sqrt(2)
   if m:v[l-m]=(-1)**m/np.sqrt(2)
   vs=[v]
   if m:
    v=np.zeros_like(v);v[l+m]=1j/np.sqrt(2);v[l-m]=-1j*(-1)**m/np.sqrt(2);vs.append(v)
   for v in vs:
    Z.append(-a@v)
    if l<=7:ordinary.append(-1j*b@v);pure.append(-1j*p@v)
 return np.concatenate(Y,axis=1),np.stack(Z,axis=1),np.stack(ordinary,axis=1),np.stack(pure,axis=1)
def run():
 a,b=[np.genfromtxt(P/f'generic_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];eps=.0025
 B=np.zeros((117,2),complex)
 for l in [3,5,7]:
  def get(r):z=(r['epoch']==1)&(r['ell']==l);return r['Bre'][z]+1j*r['Bim'][z]
  c,d=get(a),get(b);B[l*l-4:(l+1)**2-4,0]=(c+d)/(2*eps**2);B[l*l-4:(l+1)**2-4,1]=(c-d)/(2*eps**3)
 rows={}
 for cut in [20,40]:
  for width in [5,10,20]:
   mu,ph,w,W,W1,W2=grid(cut,width);Y,Z,O,Pb=fields(mu,ph,W,W1,W2)
   X=-1j*Y@B;weight=np.sqrt(np.r_[w,w]);rf=lambda A:np.r_[A.real,A.imag]*weight[:,None]
   X,Z=rf(X),rf(Z);raw=np.sum(X*X,axis=0)
   for name,A in [('ordinary',O),('pure',Pb)]:
    Q,s,_=np.linalg.svd(rf(A),full_matrices=False);Q=Q[:,s>s[0]*1e-12];F=Q.T@X;G=Q.T@Z
    leak=np.linalg.svd(G,compute_uv=False)[0]
    rows[f'{cut}_{width}_{name}']=dict(rank=Q.shape[1],retained=(np.sum(F*F,axis=0)/raw).tolist(),worst_E_leakage=float(leak),max_probe_inner=float(np.max(abs(rf(A).T@Z))),condition=float(s[0]/s[-1]))
    if name=='pure':assert leak<1e-9,(cut,width,leak)
 o=dict(rows=rows,scope='explicit spin2 differential pure B windows with W=grad W=0 at boundaries; Gauss split integration, E band<=10, B probes<=7, synthetic white noise; not observed likelihood')
 (D/'PURE_WINDOW.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
