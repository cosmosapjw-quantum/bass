"""Pilot-only allocation of deterministic mixture balance-heuristic importance sampling."""
from pathlib import Path
import json,numpy as np
D=Path(__file__).resolve().parent;P=D.parent;H=P/'r118c4h_rust_jet';G=P/'r118c4g_discrete_quadratic';F=P/'r118c4f_robust_transfer';E=P/'r118c4e_precision_refit';C3=P/'r118c4c_conditioned_transfer';C4=P/'r118c4d_precision_jet'
old=(H/'haar.py').read_text();ns={'__file__':str(H/'haar.py'),'__name__':'inspect'}
exec(compile(old[:old.rindex("\ng={'__file__'")],str(H/'haar.py'),'exec'),ns)
src=ns['src'];start=src.index('  # check proposal normalization');src=src[:start]+'''
  # same 512 cell proposal as C4G and same ACG construction as C4H
  bins=8;nc=bins**3;ix=np.ravel_multi_index(np.minimum((pilot*bins).astype(int),bins-1).T,(bins,)*3);cnt=np.bincount(ix,minlength=nc);assert np.all(cnt==16)
  a=np.bincount(ix,weights=np.exp(v-v.max()),minlength=nc)/cnt;pc=.25/nc+.75*a/a.sum()
  def qfromcube(x):
   return Rotation.from_euler('ZYZ',np.c_[2*np.pi*x[:,0],np.arccos(2*x[:,1]-1),2*np.pi*x[:,2]]).as_quat()
  def sample(k,n,seed):
   rng=np.random.default_rng(seed)
   if k==0:
    q=rng.normal(size=(n,4));q/=np.linalg.norm(q,axis=1)[:,None]
   elif k==1:
    ids=rng.choice(nc,size=n,p=pc);cell=np.array(np.unravel_index(ids,(bins,)*3)).T;q=qfromcube((cell+rng.random((n,3)))/bins)
   else:
    ids=rng.choice(len(prob),size=n,p=prob);q=np.einsum('nij,nj->ni',chol[ids],rng.normal(size=(n,4)));q/=np.linalg.norm(q,axis=1)[:,None]
   aa=Rotation.from_quat(q).as_euler('ZYZ');aa[:,0]%=2*np.pi;aa[:,2]%=2*np.pi;cube=np.c_[aa[:,0]/(2*np.pi),(1+np.cos(aa[:,1]))/2,aa[:,2]/(2*np.pi)]
   ix=np.ravel_multi_index(np.minimum((cube*bins).astype(int),bins-1).T,(bins,)*3);dens=np.stack([np.ones(n),nc*pc[ix],np.exp(logq(q,cov,prob))],axis=1)
   l=ll(cube,data[j:j+1])[:,0];assert np.min(dens)>=.25-1e-12
   return l,dens
  # Separate independent random pilot batches, no heldout-informed allocation.
  pil=[sample(k,1024,118490+100*j+k) for k in range(3)]
  lmax=max(np.max(x[0]) for x in pil)
  alloc=[(2,2,2),(4,1,1),(1,4,1),(1,1,4),(3,2,1),(3,1,2),(2,3,1),(1,3,2),(2,1,3),(1,2,3)]
  costs=[]
  for a in alloc:
   alpha=np.array(a)/6;cost=sum(alpha[k]*np.var(np.exp(x[0]-lmax)/(x[1]@alpha),ddof=1) for k,x in enumerate(pil));costs.append(float(cost))
  selected=int(np.argmin(costs));alpha=np.array(alloc[selected])/6
  counts=np.floor(alpha*8192).astype(int);counts[-1]+=8192-sum(counts);alpha=counts/8192
  evals=[]
  for seed in [118491,118492,118493,118494]:
   data0=[sample(k,int(counts[k]),seed+100*j+10000*k) for k in range(3)]
   lw=np.concatenate([l-np.log(d@alpha) for l,d in data0]);val=float(logsumexp(lw)-np.log(len(lw)));ess=float(np.exp(2*logsumexp(lw)-logsumexp(2*lw)))
   evals.append(dict(seed=seed,logLR=val,ess=ess))
   lw0.append(lw)
  # Compare to single proposal same budget using independent new random samples; evaluate each only once per target.
  control=[]
  for k in range(3):
   l,d=sample(k,8192,118495+100*j+10000*k);w=l-np.log(d[:,k]);control.append(dict(proposal=['uniform','cell','ACG'][k],logLR=float(logsumexp(w)-np.log(len(w))),ess=float(np.exp(2*logsumexp(w)-logsumexp(2*w)))))
  rows.append(dict(label=label,pilot_counts=[1024]*3,candidate_allocations=alloc,pilot_variance_proxy=costs,selected_counts=counts.tolist(),evaluations=evals,logLR_sd=float(np.std([x['logLR'] for x in evals],ddof=1)),range=float(np.ptp([x['logLR'] for x in evals])),single_proposal_controls=control));print(rows[-1],flush=True)
 np.savez_compressed(D/'MIS_WEIGHTS.npz',log_weights=np.array(lw0),labels=np.array(labels))
 write('MIS.json',dict(rows=rows,construction_pilot=8192,allocation_pilot_per_proposal=1024,evaluation_total=8192,scope='deterministic mixture balance denominator q_mix, pilot-only variance proxy on independent IID samples, 4 fresh eval replicates per target; prior data reused, no new observation; no QMC optimality claim'))
'''
# Important: newly inserted code is within original run() and j-loop indentation.
g={'__file__':str(D/'haar.py'),'__name__':'c4i_haar','C4_OLD':C4,'C4E':E,'C4F':F,'C4G':G};exec(compile(src,str(C3/'orientation.py'),'exec'),g);g['run']()
