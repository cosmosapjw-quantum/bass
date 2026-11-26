import json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent;G=np.array(json.loads((D.parent/'r118c3c_memory_kernel/WEDGE.json').read_text())['gram']);W=np.zeros(10);W[1]=1.;W[9]=.5
a=np.zeros((5,5));i,j=np.triu_indices(5,1);a[i,j]=W;a[j,i]=-W
s=np.linalg.svd(a,compute_uv=False);p=2*G@W
assert sum(s>1e-12)==4 and np.linalg.norm(p)<1e-12
(D/'RANK4.json').write_text(json.dumps(dict(wedge=W.tolist(),singular=s.tolist(),projected=float(np.linalg.norm(p)),scope='algebraic rank-four spin1 null, not physical dynamics'),indent=2)+'\n')
print(s,p)
