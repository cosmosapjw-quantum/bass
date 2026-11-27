"""Construct a nonmaximal-W radial family via rank-one temporal-null updates."""
import json,numpy as np
from pathlib import Path
from scipy.linalg import null_space
D=Path(__file__).resolve().parent;P=D.parent/'r118c3s_radial_envelope'
r=json.loads((P/'RADIAL_FINE.json').read_text());M=np.array(r['M']);G=np.array(r['G']);H=np.array(r['H']);B=r['budget']
c=np.load(P/'embedded_2048.npz')['control'];A=c@np.linalg.inv(H);A*=np.sqrt(B)/np.linalg.norm(A)
W=A@M@A.T
# SVD of A M has two strong and two weak singular values. Use known rank
# four (observed in this finite matrix), not default rcond based on strong pair.
_,sv,V=np.linalg.svd(A@M,full_matrices=True);K=V[4:].T
assert K.shape==(7,3) and sv[3]>1e-15*sv[0]
dirs=[];rows=[]
# choose two stable, orthogonal output vectors for each temporal direction,
# avoiding nearly zero projected Av. No claim globally optimal basis.
for j,v in enumerate(K.T):
 av=A@v;Q=null_space(av[None,:])
 for i in [0,1]:
  u=Q[:,i];E=np.outer(u,v);assert abs(np.sum(A*E))<1e-14
  dirs.append(E)
  for t in [-.12,.12]:
   X=A+t*E;X*=np.sqrt(B)/np.linalg.norm(X)
   Y=X@M@X.T;target=W*B/(B+t*t)
   err=float(np.linalg.norm(Y-target)/np.linalg.norm(W))
   assert err<1e-5
   rows.append(dict(direction=len(dirs)-1,t=t,wedge_ratio=float(np.linalg.norm(Y)/np.linalg.norm(W)),wedge_error=err,budget=float(np.linalg.norm(X)**2)))
out=dict(rows=rows,sv=sv.tolist(),W_norm=float(np.linalg.norm(W)),null_res=float(np.linalg.norm(A@M@K)),budget=B,scope='finite numerical null rank four of AM, rank-one updates, fixed weighted budget, W direction preserved within numerical tolerance')
np.savez_compressed(D/'FAMILY.npz',A=A,M=M,G=G,H=H,dirs=np.array(dirs),W=W)
(D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
