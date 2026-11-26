# Temporal antisymmetric bilinear form; construct pure spin1 wedge using
# smooth polynomial basis and native clock from C3B.
import numpy as np,json
from pathlib import Path
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
D=Path(__file__).resolve().parent;end=2.
# Constant positive Thomson clock, manufactured conditional geometry.
def K(t):return 1.
def basis(t):
 v=t/end
 return np.array([1.,np.cos(np.pi*v),np.sin(2*np.pi*v),np.cos(3*np.pi*v)])
def rhs(t,y):
 a,p,w=y[:4],y[4:8],y[8:].reshape(4,4);s=basis(t);k=K(t)
 return np.r_[-4*s-k*(.9*a+.4*p),-k*(.15*a+.4*p),(np.outer(s,p)-np.outer(p,s)-k*w).ravel()]
sol=solve_ivp(rhs,(0,end),np.zeros(24),method='DOP853',rtol=1e-12,atol=1e-17,max_step=end/2048);assert sol.success
W=sol.y[8:,-1].reshape(4,4);a,b=map(lambda j:np.eye(4)[j],np.unravel_index(np.argmax(abs(W)),W.shape));w=a@W@b
remaining=[j for j in range(4) if a[j]==b[j]==0];c,d=np.eye(4)[remaining]
def orth(c):return c+(b@W@c)/w*a-(a@W@c)/w*b
c,d=orth(c),orth(d);wd=c@W@d;assert abs(wd)>1e-9*abs(w)
factor=np.sqrt(abs(w/(2*wd)));c*=factor;d*=factor*np.sign(w/wd);M=np.stack([a,b,c,d],axis=1);tt=np.linspace(0,end,4097);v=np.stack([basis(t)@M for t in tt]);amp=np.max(np.linalg.norm(v,axis=1));M/=amp
def ss(t):return basis(t)@M
def integrate(fn):
 def f(t,y):
  a,p,w=y[:5],y[5:10],y[10:].reshape(5,5);s=fn(t);k=K(t);return np.r_[-4*s-k*(.9*a+.4*p),-k*(.15*a+.4*p),(np.outer(s,p)-np.outer(p,s)-k*w).ravel()]
 sol=solve_ivp(f,(0,end),np.zeros(35),method='DOP853',rtol=1e-12,atol=1e-19,max_step=end/2048);assert sol.success
 return sol.y[10:,-1].reshape(5,5)
def null(t):
 a,b,c,d=ss(t);return np.array([a,0,b,c,d])
def simple(t):
 a,b,c,d=ss(t);return np.array([a,0,b,0,0])
G=np.array(json.loads((D.parent/'r118c3c_memory_kernel/WEDGE.json').read_text())['gram']);rows=[]
for name,fn in [('null',null),('simple',simple)]:
 z=np.stack([fn(t) for t in tt]);ww=integrate(fn)[np.triu_indices(5,1)];p=2*G@ww;rel=np.linalg.norm(p)/np.linalg.norm(ww)
 np.savetxt(D/(name+'_geom.csv'),np.c_[tt,np.exp(tt)/21,np.ones(len(tt)),z],header='u,a,h,S0,S1,S2,S3,S4',delimiter=',',comments='',fmt='%.17e')
 rows.append(dict(name=name,wedge=ww.tolist(),norm=float(np.linalg.norm(ww)),spin3_relative=float(rel),quadratic_B3=float(16/np.sqrt(378)*np.linalg.norm(p))))
 print(rows[-1],flush=True)
np.savetxt(D/'NULL_NE.csv',np.c_[tt,np.full(len(tt),2.1842852410855023e-18/(299792458*6.6524587051e-29))],header='u,ne_m3',comments='',delimiter=',',fmt='%.17e')
assert rows[0]['spin3_relative']<1e-8 and rows[1]['spin3_relative']>.1
(D/'NULL.json').write_text(json.dumps(dict(W4=W.tolist(),transform=M.tolist(),rows=rows),indent=2)+'\n')
