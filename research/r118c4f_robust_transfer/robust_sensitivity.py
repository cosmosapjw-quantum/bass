"""Local tangent-space audit: can the two empirical wedge constraints be solved independently?"""
from pathlib import Path
import sys,json,numpy as np
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from bass import W,J,ma,mb,mm,dm,P3,Q,norm,budget,budget_rel,stat,feasible
b=np.load(D/'TRAIN_CONTROLS.npz')
x=b['coordinates'][list(b['labels']).index(str(b['selected']))].ravel().copy()
scale=np.linalg.norm(x)
# Scale Jacobians by relative parameter displacement, not absolute units.
A=np.vstack([np.array(J(x,mm)/norm,float),2*(x.reshape(5,7)@Q.T@Q).ravel()/budget])*scale
u,s,v=np.linalg.svd(A,full_matrices=True)
rank=int(np.sum(s>s[0]*1e-13));N=v[rank:].T
assert N.shape==(35,35-rank)
B=np.array(P3@J(x,dm)/norm,float)*scale
K=B@N
f=np.array(P3@W(x,dm)/norm,float)
uu,ss,vv=np.linalg.svd(K,full_matrices=False)
rows=[]
for cutoff in [1e-5,1e-8,1e-11,1e-14]:
 keep=ss>ss[0]*cutoff
 z=-(vv[keep].T@((uu[:,keep].T@f)/ss[keep]))
 dx=N@z
 rr=float(np.linalg.norm(f+K@z))
 tests=[]
 for frac in [1.,.1,.01,.001]:
  y=x+frac*dx*scale
  tests.append(dict(fraction=frac,relative_step=float(frac*np.linalg.norm(dx)),mean_first_order_residual=float(np.linalg.norm(A@(frac*dx))),actual_difference_spin3=float(np.linalg.norm(P3@W(y,dm))/norm),max_training_spin3=max(stat(y,m)['spin3'] for m in [ma,mb]),budget_relative=abs(budget_rel(y)),feasible=bool(feasible(y))))
 rows.append(dict(cutoff=cutoff,rank=int(sum(keep)),minimum_norm_relative_step=float(np.linalg.norm(dx)),linear_residual=rr,actual=tests))
out=dict(selected=str(b['selected']),initial_difference_spin3=float(np.linalg.norm(f)),mean_constraint_rank=rank,mean_singular_values=s.tolist(),projected_difference_singular_values=ss.tolist(),mean_null_residual=float(np.linalg.norm(A@N)/np.linalg.norm(A)),rows=rows,scope='local linearized mean-preserving tangent; finite step audits only, not global infeasibility or a newly selected control')
(D/'ROBUST_SENSITIVITY.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(rank=rank,mean_null=N.shape[1],projected_singular_values=ss.tolist(),initial=out['initial_difference_spin3'],rows=[{k:v for k,v in r.items() if k!='actual'} for r in rows]),indent=2))
