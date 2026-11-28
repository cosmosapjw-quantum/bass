"""Matched-evaluation arithmetic mixture of independently evaluated importance estimates."""
from pathlib import Path
import numpy as np,json
from scipy.special import logsumexp
D=Path(__file__).resolve().parent;G=D.parent/'r118c4g_discrete_quadratic'
a=np.load(G/'ADAPTIVE_LOG_WEIGHTS.npz');b=np.load(D/'QUATERNION_WEIGHTS.npz');assert np.array_equal(a['labels'],b['labels'])
x=a['log_weights'];y=b['log_weights'];assert x.shape==y.shape==(8,8192)
# Fixed equal allocation, not selected on heldout output. Independent proposals share a pilot.
def lr(z,n):return logsumexp(z[:,:n],axis=1)-np.log(n)
z=np.logaddexp(lr(x,4096),lr(y,4096))-np.log(2.)
rows=[]
for j,k in enumerate(a['labels']):
 i=2*j;rows.append(dict(label=str(k),equal_allocation_8192=z[i:i+2].tolist(),scramble_difference=float(abs(z[i]-z[i+1])),cell_8192_difference=float(abs(lr(x,8192)[i]-lr(x,8192)[i+1])),quaternion_8192_difference=float(abs(lr(y,8192)[i]-lr(y,8192)[i+1]))))
(D/'MIXED_PROPOSAL_REPLAY.json').write_text(json.dumps(dict(rows=rows,scope='arithmetic mean of two independent importance integrals, 4096+4096 evaluation draws per estimate; fixed prior and shared pilot; no new likelihood evaluations or evidence of true error'),indent=2)+'\n')
print(json.dumps(rows,indent=2))
