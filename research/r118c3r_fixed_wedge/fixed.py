"""Fixed wedge and number-weighted metric, rank-4 output stabilizer."""
import sys,json,numpy as np
from pathlib import Path
from scipy.linalg import schur,expm
from scipy.optimize import brentq
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3q_controls'))
from controls import C0,M,W0,U
G=np.diag([1.,1/3,1/3,1/3]);Q=U[:,:4];C=Q.T@C0;W=Q.T@W0@Q;W=(W-W.T)/2;P=C@G@C.T;norm0=float(np.trace(P))
H=[];tags=[]
for i in range(4):
 for j in range(i,4):
  z=np.zeros((4,4));z[i,j]=z[j,i]=1.;X=W@z;H.append(X/np.linalg.norm(X));tags.append(f'{i}{j}')
X=np.array(H);g=np.array([2*np.trace(x@P) for x in X])
def calc(t):
 L=expm(np.einsum('i,ijk->jk',t,X));A=Q@L@C
 return A,float(np.trace(L@P@L.T)-norm0)
def check(A):
 return dict(weighted_norm=float(np.trace(A@G@A.T)),weighted_relative=float(abs(np.trace(A@G@A.T)-norm0)/norm0),wedge_relative=float(np.linalg.norm(A@M@A.T-W0)/np.linalg.norm(W0)),bare_norm=float(np.linalg.norm(A)),distance=float(np.linalg.norm(A-C0)))
def construct():
 # nonzero root of physical budget along a generator with initial negative gradient.
 # Also mix each cross-plane axis with weak-plane steepest descent.
 rows=[];out=[]
 for i,tag in enumerate(tags):
  vec=np.eye(10)[i];vec*= -np.sign(g[i])
  for mode in ['axis','mixed'] if i in [2,3,5,6] else ['axis']:
   v=vec.copy()
   if mode=='mixed':v-=.2*g/np.linalg.norm(g)
   v/=np.linalg.norm(v)
   fun=lambda t:calc(t*v)[1]
   # estimate curvature from analytic second derivative
   Y=np.einsum('i,ijk->jk',v,X);d1=2*np.trace(Y@P);d2=2*np.trace(Y@Y@P)+2*np.trace(Y@P@Y.T)
   t0=max(1e-9,min(.05,abs(d1)/max(abs(d2),1e-30)))
   for _ in range(30):
    if fun(t0)<0:break
    t0*=.5
   else:continue
   hi=t0*2
   while hi<2 and fun(hi)<0:hi*=2
   if fun(hi)<=0:continue
   t=brentq(fun,t0,hi,xtol=1e-13,rtol=1e-13);a,_=calc(t*v);q=check(a)
   if q['distance']<1e-9:continue
   assert q['weighted_relative']<1e-12 and q['wedge_relative']<1e-5,q
   label=tag+'_'+mode;rows.append(dict(label=label,t=t,gradient=float(d1),curvature=float(d2),crossplane=bool(int(tag[0])<2<=int(tag[1])),**q));out.append(a)
 # independent lower bound: rank-two approximation by strong skew block
 # implies sigma3(W)<=nu_weak ||Pweak||_F²/2. Use exact-ish Pfaffian
 # for the small skew singular scale instead of subtracting squares.
 import mpmath as mp
 mp.mp.dps=70
 h=np.diag([1.,np.sqrt(3),np.sqrt(3),np.sqrt(3)]);O=h@M@h
 def skewvals(A):
  A=(A-A.T)/2;B=mp.matrix([[mp.mpf(float(a)) for a in row] for row in A])
  s=sum(B[i,j]**2 for i in range(4) for j in range(i+1,4));pf=B[0,1]*B[2,3]-B[0,2]*B[1,3]+B[0,3]*B[1,2]
  v=mp.sqrt((s+mp.sqrt(s*s-4*pf*pf))/2);return float(v),float(abs(pf)/v)
 nu=skewvals(O);sig=skewvals(W);lb=2*sig[1]/nu[1]
 data=dict(rows=rows,metric_norm=norm0,skew_O=nu,skew_W=sig,lower_bound=lb,relative_slack=(norm0-lb)/norm0,scope='rank-four numerical W, G=diag(1,1/3,1/3,1/3) equal number weight; rank-two Eckart-Young lower bound, finite candidate paths not global optimization')
 np.savez_compressed(D/'CONTROLS.npz',controls=np.array(out),labels=np.array([r['label'] for r in rows]))
 (D/'R7.json').write_text(json.dumps(data,indent=2)+'\n');print(data,flush=True)
if __name__=='__main__':construct()
