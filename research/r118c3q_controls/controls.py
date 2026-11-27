"""Stable output-space skew-plane stabilizer; actual finite-domain controls."""
import json,sys,numpy as np
from pathlib import Path
from scipy.linalg import schur,expm
D=Path(__file__).resolve().parent;P=D.parent/'r118c3p_analytic_s4';N=D.parent/'r118c3n_analytic_s2'
M=np.array(json.loads((N/'JOINT.json').read_text())['M']);C0=np.load(P/'opt_verified_2048.npz')['control'];W0=C0@M@C0.T
T,U=schur(W0,output='real')
# Each two-dimensional skew plane has SL(2) stabilizer; actual physical
# SO(3) acts on all STF components jointly, not these independent squeezes.
B=[np.array([[1.,0.],[0.,-1.]]),np.array([[0.,1.],[1.,0.]]),np.array([[0.,-1.],[1.,0.]])]
assert abs(T[0,1])>1e-14 and abs(T[2,3])>1e-14,T
def control(t):
 L=np.eye(5)
 for i in range(2):L[2*i:2*i+2,2*i:2*i+2]=expm(sum(t[3*i+j]*B[j] for j in range(3)))
 A=U@L@U.T@C0
 return A/np.linalg.norm(A)
def check(C):
 W=C@M@C.T
 return dict(norm=float(np.linalg.norm(C)),wedge_ratio=float(np.linalg.norm(W)/np.linalg.norm(W0)),wedge_direction_error=float(np.linalg.norm(W/np.linalg.norm(W)-W0/np.linalg.norm(W0))))
def test():
 rows=[]
 for i in range(6):
  for t in [-.15,.15]:
   z=np.zeros(6);z[i]=t;C=control(z);q=check(C)
   assert q['wedge_ratio']>.8 and q['wedge_direction_error']<1e-5,(i,q)
   rows.append(dict(axis=i,t=t,**q))
 o=dict(skew_plane=T.tolist(),rows=rows,scope='finite numerical M and W; two independent SL(2) blocks preserve W before normalization. Not exact rank theorem.')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':test()
