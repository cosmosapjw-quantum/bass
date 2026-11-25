import hashlib,json
from pathlib import Path
import numpy as np
from scipy.linalg import expm,polar
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
OG=5.4437488671046486e-5;ON=3.7562511328953514e-5;OM=.315;OL=.684908;T=.00016763891604963858
END=np.log(21/5)
E=np.array([np.diag([1.,-1.,0.])/np.sqrt(2),np.diag([-1.,-1.,2.])/np.sqrt(6),[[0,1/np.sqrt(2),0],[1/np.sqrt(2),0,0],[0,0,0]],[[0,0,1/np.sqrt(2)],[0,0,0],[1/np.sqrt(2),0,0]],[[0,0,0],[0,0,1/np.sqrt(2)],[0,1/np.sqrt(2),0]]])
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def mat(v):return np.einsum('k,kij->ij',v,E)
def comp(m):return np.einsum('kij,ij->k',E,m)
class Model:
 def __init__(self,eps,nr=64,nt=16):
  x,w=leggauss(nr);y=30*(1+x);w=30*w
  mu,wm=leggauss(nt);ph=np.arange(2*nt)*2*np.pi/(2*nt)
  ns=np.stack([np.sqrt(1-mu[:,None]**2)*np.cos(ph),np.sqrt(1-mu[:,None]**2)*np.sin(ph),np.broadcast_to(mu[:,None],(nt,2*nt))],axis=-1).reshape(-1,3)
  aw=np.repeat(wm/(4*nt),2*nt)
  norm=w@(y**3/(1+np.exp(y)));self.cold=OM+ON
  q=[];m=[];wt=[]
  for mass,j in zip((.001,.05),([0,1,0,0,0],[0,0,.6,.8,0])):
   mass/=T;self.cold-=ON/2*(w@(y*y*np.hypot(y,mass)/(1+np.exp(y))))/norm
   f=1/(1+np.exp(y[:,None]*np.exp(-eps*np.einsum('ai,ij,aj->a',ns,mat(j),ns))))
   wt.append((ON/2/norm*(w*y*y)[:,None]*aw[None,:]*f).ravel())
   q.append((y[:,None,None]*ns[None,:,:]).reshape(-1,3));m.append(np.full(len(y)*len(ns),mass))
  self.q=np.concatenate([*q,ns]);self.w=np.concatenate([*wt,OG*aw]);self.m=np.concatenate([*m,np.zeros(len(ns))])
 def moments(self,a,F):
  p=self.q@np.linalg.inv(F);e=np.hypot(np.linalg.norm(p,axis=1),a*self.m)
  rho=(self.cold*a+self.w@e)/a**4
  P=(p.T*(self.w/e))@p/a**4
  return rho,P
 def rhs(self,u,v):
  a=np.exp(u)/21;S=v[:5];F=v[5:].reshape(3,3);rho,P=self.moments(a,F)
  h2=(rho+OL)/(1-(S@S)/6);d=-1.5*(rho+np.trace(P)/3)/h2-.5*(S@S)
  return np.r_[-(3+d)*S+3*comp(P)/h2,(mat(S)@F).ravel()]
 def hubble(self,a,v):
  rho,P=self.moments(a,v[5:].reshape(3,3));return np.sqrt((rho+OL)/(1-v[:5]@v[:5]/6))
out={};files={}
for eps in (0.,.001,.03):
 model=Model(eps);v0=np.r_[[eps/3,0,0,0,eps/4],np.eye(3).ravel()]
 sol=solve_ivp(model.rhs,(0,END),v0,method='DOP853',rtol=3e-11,atol=3e-13,max_step=.05,dense_output=True)
 assert sol.success;v=sol.y[:,-1];href=model.hubble(.2,v)
 rows=[]
 for p in sorted(D.glob('owner_'+('0' if eps==0 else str(eps))+'_*.csv')):
  n,nr,nt=map(int,p.stem.split('_')[-3:]);r=np.genfromtxt(p,names=True,delimiter=',')
  y=np.r_[[r['S'+str(i)][-1] for i in range(5)],[r['F'+str(i)+str(j)][-1] for i in range(3) for j in range(3)]]
  assert len(r)==n+1 and abs(r['a'][-1]-.2)<1e-13
  assert np.all(r['rho']>0) and np.all(r['p']>=0) and max(abs(r['det']-1))<1e-10
  rows.append(dict(n=n,nr=nr,nt=nt,gauss=float(max(abs(r['gauss']))),det=float(max(abs(r['det']-1))),h_error=float(abs(r['h'][-1]/href-1)),state_error=float(max(abs(y-v))),end_s=y[:5].tolist(),end_h=float(r['h'][-1])))
  files[p.name]=sha(p)
 rows.sort(key=lambda x:(x['nr'],x['nt'],x['n']))
 if eps!=0:
  core=[x for x in rows if x['nr']==32]
  order=np.log2(np.array([x['gauss'] for x in core[:-1]])/np.array([x['gauss'] for x in core[1:]]))
  assert min(order)>1.9
 else:order=[]
 # Independent stress work identity via centered geometry change around reference solution.
 vv=sol.sol(END/2);a=np.exp(END/2)/21;S=mat(vv[:5]);F=vv[5:].reshape(3,3);rho,P=model.moments(a,F);h=1e-5
 fd=(model.moments(a*np.exp(h),expm(h*S)@F)[0]-model.moments(a*np.exp(-h),expm(-h*S)@F)[0])/(2*h)
 expected=-3*rho-np.trace(P)-np.sum(S*P);defect=abs(fd/expected-1);assert defect<2e-8
 out[str(eps)]=dict(rows=rows,reference_h=float(href),reference_s=v[:5].tolist(),orders=np.asarray(order).tolist(),stress_work_relative=float(defect))
 print('owner',eps,rows,'work',defect,flush=True)
# Path ordering and geometric optics
A=np.diag([1.,-1.,0.]);B=np.array([[0.,1.,0.],[1.,0.,1.],[0.,1.,0.]])
n0=np.array([.3,.4,.5]);n0/=np.linalg.norm(n0);f0=np.cross([0,0,1.],n0);f0/=np.linalg.norm(f0)
pulses={'AB':[A,B],'BA':[B,A],'loop':[A,B,-A,-B],'reverse':[B,A,-B,-A]}
def exact(eps,case):
 F=np.eye(3);n=n0.copy();f=f0.copy();l=0.
 for a in pulses[case]:
  s=eps*a
  def rhs(t,v):
   n=v[:3];f=v[3:6];dn=-s@n+(n@s@n)*n
   return np.r_[dn,-n*(dn@f),-1-n@s@n]
  sol=solve_ivp(rhs,(0,1),np.r_[n,f,l],method='DOP853',rtol=2e-13,atol=2e-15,max_step=.05)
  assert sol.success;n=sol.y[:3,-1];f=sol.y[3:6,-1];l=sol.y[6,-1];F=expm(s)@F
 p=np.linalg.solve(F.T,n0)
 assert np.linalg.norm(n-p/np.linalg.norm(p))<1e-12 and abs(l+len(pulses[case])-np.log(np.linalg.norm(p)))<1e-12
 return F,n,f,l
def polar_frame(v):
 F,n,f,l=v;R,U=polar(F);return R.T@n,R.T@f
def short_transport(n,m,v):
 # minimal proper rotation carrying unit n to m
 c=n@m;w=np.cross(n,m);return v+np.cross(w,v)+np.cross(w,np.cross(w,v))/(1+c)
def angle(v,w):
 n,f=polar_frame(v);m,g=polar_frame(w);f1=short_transport(n,m,f)
 return np.arctan2(m@np.cross(f1,g),f1@g)
raw=np.genfromtxt(D/'ordered_native.csv',delimiter=',',names=True,dtype=None,encoding='utf8')
assert len(raw)==48;files['ordered_native.csv']=sha(D/'ordered_native.csv')
rr=[]
for eps in (.04,.02,.01,.005):
 ref={c:exact(eps,c) for c in pulses}
 errs=[]
 for r in raw[raw['eps']==eps]:
  F=np.array([r['F'+str(i)+str(j)] for i in range(3) for j in range(3)]).reshape(3,3);n=np.array([r['nx'],r['ny'],r['nz']]);f=np.array([r['fx'],r['fy'],r['fz']])
  G,m,g,l=ref[r['case']]
  gap=max(np.linalg.norm(F-G),np.linalg.norm(n-m),np.linalg.norm(f-g),abs(r['lnE']-l))
  errs.append(dict(case=r['case'],nstep=int(r['nstep']),error=float(gap)))
  assert abs(n@f)<1e-11 and abs(np.linalg.norm(f)-1)<1e-11
  assert gap<1e-5
 ab,ba=ref['AB'],ref['BA'];f,g=ab[0],ba[0]
 loop,rev=ref['loop'],ref['reverse']
 row=dict(eps=eps,coframe_gap=float(np.linalg.norm(f-g)),metric_gap=float(np.linalg.norm(f.T@f-g.T@g)),logE_gap=float(abs(ab[3]-ba[3])),polar_screen_angle=float(angle(ab,ba)),loop_angle=float(angle((np.eye(3),n0,f0,0),loop)),reverse_angle=float(angle((np.eye(3),n0,f0,0),rev)),native=errs)
 rr.append(row);print('path', {k:v for k,v in row.items() if k!='native'},flush=True)
def ords(k):return np.log2(np.abs([v[k] for v in rr[:-1]])/np.abs([v[k] for v in rr[1:]])).tolist()
orders={k:ords(k) for k in ('coframe_gap','metric_gap','logE_gap','polar_screen_angle','loop_angle')}
assert abs(orders['coframe_gap'][-1]-2)<.05 and abs(orders['metric_gap'][-1]-3)<.05
print('orders',orders,flush=True)
(D/'RESULTS.json').write_text(json.dumps(dict(status='PASS_SCOPED_NONLINEAR_COLLISIONLESS_OWNER_AND_ORDERED_SCREEN',owner=out,path=rr,path_orders=orders,raw_sha=files,scope='finite amplitude collisionless Bianchi I represented quadrature; independent Gauss reduced reference; prescribed ordered ray pulses, not CMB B mode'),indent=2,allow_nan=False)+'\n')
