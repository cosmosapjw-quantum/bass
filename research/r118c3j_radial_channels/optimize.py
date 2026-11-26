"""Construct maximally bounded spin-one skew control and test mesh transfer."""
import numpy as np,json,sys
from pathlib import Path
from scipy.linalg import schur
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_reachability'))
from reachability import projector,skew,vector
from itertools import combinations
def construct(M):
 # axial STF normal is the second basis tensor in native STF convention.
 Q=np.eye(5)[:,[0,2,3,4]];P,pairs=projector();i,j=pairs.T
 B=np.array([Q[i,k]*Q[j,l]-Q[i,l]*Q[j,k] for k,l in combinations(range(4),2)]).T
 _,s,V=np.linalg.svd(P@B,full_matrices=False);assert s[-1]<1e-12
 target=skew(V[-1],4);T,V=schur(target,output='real')
 ids=sorted([0,2],key=lambda k:-abs(T[k,k+1]));V=V[:,[j for k in ids for j in (k,k+1)]];T=V.T@target@V
 t=np.array([T[0,1],T[2,3]])
 S,U=schur(M,output='real');blocks=[];k=0
 while k<len(M)-1:
  if S[k+1,k]!=0:
   blocks.append(k);k+=2
  else:k+=1
 blocks=sorted(blocks,key=lambda k:-abs(S[k,k+1]))[:2];assert len(blocks)==2
 U=U[:,[j for k in blocks for j in (k,k+1)]];m0=U.T@M@U;m=np.array([m0[0,1],m0[2,3]])
 scale=min(abs(m/t));z=np.sqrt(abs(scale*t/m))
 A=Q@V@np.diag(np.ravel(np.c_[z*np.sign(t/m),z]))@U.T
 assert np.linalg.norm(A,2)<=1+1e-12
 return A,scale
def evaluate(M,A):
 P,_=projector()
 W=np.array(A.astype(np.longdouble)@M.astype(np.longdouble)@A.astype(np.longdouble).T,float);v=vector(W)
 return dict(norm=float(np.linalg.norm(v)),projected=float(np.linalg.norm(P@v)/np.linalg.norm(v)))
def main():
 p=json.loads((D/'RADIAL.json').read_text())['cases'];rows=[]
 for a,b in zip(p[:3],p[3:]):
  M=np.array(a['M']);N=np.array(b['M']);A,scale=construct(M);r=evaluate(M,A);s=evaluate(N,A)
  rows.append(dict(nw=a['nw'],control_norm=float(np.linalg.norm(A,2)),attained_coarse=r,transfer_fine=s,bound=a['pure_spin1_wedge_bound_unit_control'],matrix_difference=float(np.linalg.norm(N-M,2)),A=A.tolist()))
 o=dict(rows=rows,scope='linear algebra on computed temporal matrices, tiny cancellation sensitive to discretization; not nonlinear native null')
 (D/'CONTROL.json').write_text(json.dumps(o,indent=2)+'\n');print([{k:v for k,v in x.items() if k!='A'} for x in rows])
if __name__=='__main__':main()
