"""Additional time refinement of the direct discrete coefficient; compare vector Richardson not norm fitting."""
from pathlib import Path
import json,time,sys,numpy as np
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from bass import solve,sha
prior=np.load(D/'DISCRETE_B2.npz');labels=['old','new'];vals=list(prior['B2'][:,:2]);nlist=list(map(int,prior['n']));rows=[]
for n in [65536,131072]:
 t=time.monotonic();b,*_=solve(n,192,labels);rows.append(dict(n=n,seconds=time.monotonic()-t,norm=np.linalg.norm(b,axis=1).astype(float).tolist()));vals.append(b);nlist.append(n);print(rows[-1],flush=True)
arr=np.array(vals);rich=(4*arr[1:]-arr[:-1])/3;diff=np.linalg.norm(np.diff(arr,axis=0),axis=2)
# The clock is piecewise linear, so extrapolation need not have a smooth h^4 remainder.
out=dict(n=nlist,labels=labels,new_rows=rows,vector_differences=diff.astype(float).tolist(),difference_ratios=(diff[:-1]/diff[1:]).astype(float).tolist(),richardson_norm=np.linalg.norm(rich,axis=2).astype(float).tolist(),richardson_successive_difference=np.linalg.norm(np.diff(rich,axis=0),axis=2).astype(float).tolist(),raw_source_sha=sha(D/'DISCRETE_B2.npz'),scope='same discrete recurrence and native clock; direct coefficient at 2 additional time grids, vector Richardson is empirical diagnostic, not continuum error certificate')
np.savez_compressed(D/'TIME_REFINEMENT.npz',n=nlist,labels=labels,B2=arr,richardson=rich)
(D/'TIME_REFINEMENT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2),flush=True)

