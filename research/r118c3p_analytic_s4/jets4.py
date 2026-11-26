"""Third-order exact Taylor moment integrals, no finite-difference geometry."""
import sys,json,numpy as np
from pathlib import Path
from scipy.interpolate import CubicSpline
from scipy.sparse import csr_matrix
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from scipy.linalg import expm
D=Path(__file__).resolve().parent;P=D.parent/'r118c3n_analytic_s2'
sys.path.insert(0,str(P))
from s2 import BASIS,MASS,OG,ON,OM,OL,T0,K0,EARLY,CLOCK,combine
L=8;M=(L+1)**2;Y00=np.sqrt(4*np.pi)
def stf(x):return (x+x.T)/2-np.eye(3)*np.trace(x)/3
def vec(x):return np.einsum('kij,ij->k',BASIS,x)
def mat(x):return np.einsum('k,kij->ij',x,BASIS)
def fd(y):
 f=1/(1+np.exp(y));g=f*(1-f)
 f1=y*g;f2=(y*y*g*(1-2*f)-f1)/2
 f3=(f1-3*y*y*g*(1-2*f)+y**3*g*(1-6*f+6*f*f))/6
 f4=(-f1+7*y*y*g*(1-2*f)-6*y**3*g*(1-6*f+6*f*f)+y**4*g*(1-14*f+36*f*f-24*f**3))/24
 return np.array([f,f1,f2,f3,f4])
def table(a,y,w):
 e=np.hypot(y[None,:],a*MASS[:,None]/T0);r=(y/e)**2
 power=r[:,None,None,:]**np.arange(5)[None,None,:,None]
 f=fd(y)[None,:,None,:]
 return np.stack([np.sum(w*y*y*e[:,None,None,:]*f*power,axis=-1),np.sum(w*y**4/e[:,None,None,:]*f*power,axis=-1)])
def quadrature(nmu):
 z,w=leggauss(nmu);mu,phi=np.meshgrid(z,np.arange(2*nmu)*np.pi/nmu,indexing='ij');n=np.stack([np.sqrt(1-mu*mu)*np.cos(phi),np.sqrt(1-mu*mu)*np.sin(phi),mu],axis=-1).reshape(-1,3)
 return n,np.repeat(w/(4*nmu),2*nmu)
class Moments:
 def __init__(self,C,nmu):
  self.n,self.w=quadrature(nmu);J=np.einsum('ka,kij->aij',C,BASIS)[1:]
  j=np.einsum('ni,mij,nj->mn',self.n,J,self.n);self.jp=j[:,None,:]**np.arange(5)[None,:,None]
 def eval(self,Ds,rad):
  v=np.einsum('kij,nj->kni',Ds,self.n)
  n=len(self.n);d=np.zeros((5,n))
  for k in range(1,5):d[k]=sum(np.sum(v[i]*v[k-i],axis=1) for i in range(k+1))
  p=np.zeros((2,5,5,n));p[:,0,0]=1
  # coefficients of (1+r*delta)^alpha: power in r is separate
  for row,alpha in enumerate([.5,-.5]):
   x=np.zeros((5,n));x[0]=1.;c=1.
   for j in range(1,5):
    x=np.array([sum(x[i]*d[k-i] for i in range(k+1)) for k in range(5)])
    c*= (alpha-j+1)/j;p[row,:,j]=c*x
  r=np.zeros((2,5,n))
  for k in range(5):
   for j in range(k+1):
    r[:,k]+=np.einsum('tmr,mn,trn->tn',rad[:,:,j,:],self.jp[:,j,:],p[:,k-j])
  rho=r[0]@self.w;P=np.zeros((5,3,3))
  for k in range(5):
   for j in range(k+1):
    for i in range(k-j+1):
     P[k]+=(v[j].T*(self.w*r[1,k-j-i]))@v[i]
  return rho,P
def stress_test():
 rng=np.random.default_rng(27);C=rng.normal(size=(5,4))/4;ms=Moments(C,12);Ds=np.array([np.eye(3),mat(rng.normal(size=5)/5),*[rng.normal(size=(3,3))/10 for _ in range(3)]])
 y,w=leggauss(96);y=30*(1+y);w=30*w;rows=[]
 for a in [.000625,.02,.2]:
  rad=table(a,y,w);r,p=ms.eval(Ds,rad)
  def exact(ep):
   Dm=sum(ep**j*Ds[j] for j in range(5));v=ms.n@Dm.T;J=ms.jp[:,1];f=1/(1+np.exp(y[None,None,:]*np.exp(-ep*J[:,:,None])));e=np.hypot(np.linalg.norm(v,axis=1)[None,:,None]*y[None,None,:],a*MASS[:,None,None]/T0)
   return np.sum((f*e)@(w*y*y)@ms.w),sum((v.T*(ms.w*((f[i]/e[i])@(w*y**4))))@v for i in range(3))
  r0,p0=exact(0)
  for ep in [.02,.01,.005]:
   rp,pp=exact(ep);rm,pm=exact(-ep)
   R=((rp+rm-2*r0)/(2*ep**2)-r[2])/ep**2;P=((pp+pm-2*p0)/(2*ep**2)-p[2])/ep**2
   rows.append(dict(a=a,eps=ep,rho4_rel=float(abs(R-r[4])/max(abs(r[4]),1e-300)),P4_rel=float(np.linalg.norm(P-p[4])/np.linalg.norm(p[4]))))
 assert max(r['P4_rel'] for r in rows if r['eps']==.005)<3e-4,rows
 return rows
def harm_to_stf(y):
 # I_lm/Y00 normalization: coefficients of n A n in C3K convention
 k=np.sqrt(4*np.pi/15);z=y[:M];a=z[8]/k;b=z[7]/k
 return np.array([a.real,z[6].real/(np.sqrt(2)*k),-a.imag,-b.real,b.imag])
def gen():
 a=np.genfromtxt(D.parent/'r118c3o_analytic_s3/generator.csv',names=True,delimiter=',')
 return [csr_matrix((a['re'][a['axis']==k]+1j*a['im'][a['axis']==k],(a['row'][a['axis']==k].astype(int),a['col'][a['axis']==k].astype(int))),shape=(3*M,3*M)) for k in range(5)]
def collision(y):
 v=y.reshape(3,M);o=-v.copy();o[:,0]=0
 d=np.sqrt(8/3);z=v[:,4:9];it=z[0];ee=-(z[1]+z[2])*.5;bb=.5j*(z[1]-z[2])
 di=-.9*it+.4/d*ee;de=.15*d*it-.4*ee;db=-bb
 o[0,4:9]=di;o[1,4:9]=-de-1j*db;o[2,4:9]=-de+1j*db
 return o.ravel()
def solve(C,nt,nr,nmu):
 e=np.genfromtxt(EARLY,names=True,delimiter=',');l=np.genfromtxt(CLOCK,names=True,delimiter=',');a0=e['a'][0];cut=np.log(1/(21*a0));end=np.log(.2/a0)
 y,w=leggauss(nr);y=30*(1+y);w=30*w;fac=ON/(3*(w@(y**3*fd(y)[0])));cold=OM+ON-fac*sum(table(1,y,w)[0,:,0,0])
 ts=np.linspace(0,end,1537);tab=CubicSpline(ts,np.array([table(a0*np.exp(t),y,w) for t in ts]),axis=0);mom=Moments(C,nmu);ops=gen()
 # S1..4, D1..4, Y1..5. lmax8 exact for target B3/B5 through fifth order.
 zero=np.zeros(3*M,complex);zero[0]=Y00
 z=np.zeros(56+5*3*M,complex);z[:5]=C[:,0]
 def rhs(t,z):
  S=z[:20].real.reshape(4,5);Ds=np.concatenate([np.eye(3)[None],z[20:56].real.reshape(4,3,3)])
  Y=np.concatenate([zero[None],z[56:].reshape(5,3*M)])
  a=a0*np.exp(t);rho,pr=mom.eval(Ds,tab(t));rho*=fac/a**4;pr*=fac/a**4;rho[0]+=cold/a**3
  for k in range(5):
   ur=OG/a**4*Y[k,0].real/Y00;rho[k]+=ur;pr[k]+=np.eye(3)*ur/3+OG/a**4*(2/15)*mat(harm_to_stf(Y[k]))
  h0=rho[0]+OL;h2=rho[2]+h0*np.dot(S[0],S[0])/6;h3=rho[3]+h0*np.dot(S[0],S[1])/3
  pt=np.trace(pr,axis1=1,axis2=2);q0=(rho[0]+pt[0]-2*OL)/(2*h0)
  q2=np.dot(S[0],S[0])/3+(rho[2]+pt[2])/(2*h0)-q0*h2/h0
  q3=2*np.dot(S[0],S[1])/3+(rho[3]+pt[3])/(2*h0)-q0*h3/h0
  pi=np.array([vec(stf(pr[k])) for k in range(1,5)])
  ds=(q0-2)*S+3*pi/h0;ds[2]+=q2*S[0]-3*h2*pi[0]/h0**2
  ds[3]+=q2*S[1]+q3*S[0]-3*(h2*pi[1]+h3*pi[0])/h0**2
  dD=np.array([-sum(mat(S[j-1])@Ds[k-j] for j in range(1,k+1)) for k in [1,2,3,4]])
  ne=np.interp(t,e['u'],e['ne_m3']) if t<=cut else np.interp(t-cut,l['u'],l['ne_m3']);K=K0*ne/np.sqrt(h0);K2=-K*h2/(2*h0);K3=-K*h3/(2*h0)
  P=[sum((ops[k]*S[j,k] for k in range(5))) for j in range(4)]
  dY=np.array([K*collision(Y[k])+sum(P[j-1]@Y[k-j] for j in range(1,min(k,4)+1))+(K2*collision(Y[k-2]) if k>=3 else 0)+(K3*collision(Y[k-3]) if k>=4 else 0) for k in [1,2,3,4,5]])
  return np.r_[ds.ravel(),dD.ravel(),dY.ravel()]
 # Fixed RK4 on a uniform mesh; record on every node, avoids adaptive complex norm dominated by carrier.
 t=np.r_[np.linspace(0,cut,nt+1),np.linspace(cut,end,nt//4+1)[1:]]
 ss=[];qq=[]
 for i in range(len(t)):
  ss.append(z[:20].real.copy());qq.append(z[56:].reshape(5,3*M)[:,0].real.copy())
  if i+1==len(t):break
  u=t[i];dt=t[i+1]-u;k1=rhs(u,z);k2=rhs(u+dt/2,z+dt*k1/2);k3=rhs(u+dt/2,z+dt*k2/2);k4=rhs(t[i+1],z+dt*k3);z=z+dt*(k1+2*k2+2*k3+k4)/6
  if not np.all(np.isfinite(z)):raise ValueError('nonfinite')
 Y=z[56:].reshape(5,3,M);b=.5j*(Y[:,1]-Y[:,2])/Y00;b[3]-=Y[1,0,0].real/Y00*b[1];b[4]-=Y[1,0,0].real/Y00*b[2]+Y[2,0,0].real/Y00*b[1]
 return t,np.array(ss).reshape(-1,4,5),np.array(qq),b
if __name__=='__main__':
 print(stress_test())
