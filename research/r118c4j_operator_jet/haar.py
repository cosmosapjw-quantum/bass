"""Fresh equal-count IID and independently scrambled Sobol on fixed C4I mixture allocation."""
from pathlib import Path
import json,numpy as np
D=Path(__file__).resolve().parent;P=D.parent;I=P/'r118c4i_native_jet';H=P/'r118c4h_rust_jet';G=P/'r118c4g_discrete_quadratic';F=P/'r118c4f_robust_transfer';E=P/'r118c4e_precision_refit';C3=P/'r118c4c_conditioned_transfer';C4=P/'r118c4d_precision_jet'
old=(I/'haar.py').read_text();ns={'__file__':str(I/'haar.py'),'__name__':'inspect'}
exec(compile(old[:old.rindex("\ng={'__file__'")],str(I/'haar.py'),'exec'),ns)
src=ns['src'];a=src.index('  def sample(k,n,seed):');b=src.index('  # Separate independent random pilot',a)
src=src[:a]+'''
  def sample(k,n,seed,method):
   dim=[3,4,5][k]
   if method=='iid':U=np.random.default_rng(seed).random((n,dim))
   else:
    U=qmc.Sobol(dim,scramble=True,seed=seed).random_base2(int(np.ceil(np.log2(n))))[:n]
   if k==0:q=qfromcube(U)
   elif k==1:
    ids=np.minimum(np.searchsorted(np.cumsum(pc),U[:,0],side='right'),nc-1)
    cell=np.array(np.unravel_index(ids,(bins,)*3)).T;q=qfromcube((cell+U[:,1:])/bins)
   else:
    ids=np.minimum(np.searchsorted(np.cumsum(prob),U[:,0],side='right'),len(prob)-1)
    z=ndtri(np.clip(U[:,1:],1e-15,1-1e-15));q=np.einsum('nij,nj->ni',chol[ids],z);q/=np.linalg.norm(q,axis=1)[:,None]
   aa=Rotation.from_quat(q).as_euler('ZYZ');aa[:,0]%=2*np.pi;aa[:,2]%=2*np.pi;cube=np.c_[aa[:,0]/(2*np.pi),(1+np.cos(aa[:,1]))/2,aa[:,2]/(2*np.pi)]
   ix=np.ravel_multi_index(np.minimum((cube*bins).astype(int),bins-1).T,(bins,)*3)
   dens=np.stack([np.ones(n),nc*pc[ix],np.exp(logq(q,cov,prob))],axis=1)
   return ll(cube,data[j:j+1])[:,0],dens
'''+src[b:]
a=src.index('  # Separate independent random pilot');src=src[:a]+'''
  prev=json.loads((C4I/'MIS.json').read_text())['rows'][j]
  assert prev['label']==label
  # Half the C4I budget, fixed previous allocation; no selection on fresh evaluations.
  N=4096;counts=np.floor(np.array(prev['selected_counts'])*N/8192).astype(int);counts[-1]+=N-sum(counts);alpha=counts/N
  methods={}
  for method in ['iid','rqmc']:
   ev=[]
   for rep in range(4):
    parts=[sample(k,int(counts[k]),1185000+10000*j+100*rep+k+(500 if method=='rqmc' else 0),method) for k in range(3)]
    lw=np.concatenate([l-np.log(d@alpha) for l,d in parts]);assert len(lw)==N
    val=float(logsumexp(lw)-np.log(N));ess=float(np.exp(2*logsumexp(lw)-logsumexp(2*lw)))
    ev.append(dict(rep=rep,logLR=val,ess=ess));lw0.append(lw)
   methods[method]=dict(evaluations=ev,logLR_sd=float(np.std([x['logLR'] for x in ev],ddof=1)),mean=float(np.mean([x['logLR'] for x in ev])))
  rows.append(dict(label=label,counts=counts.tolist(),methods=methods,prior_C4I_mean=float(np.mean([x['logLR'] for x in prev['evaluations']]))));print(rows[-1],flush=True)
 np.savez_compressed(D/'RQMC_WEIGHTS.npz',log_weights=np.array(lw0),labels=np.array(labels))
 write('RQMC.json',dict(rows=rows,evaluation_total=4096,replicates=4,scope='fresh equal-cost IID and scrambled Sobol, same frozen mixture and C4I pilot allocation; non-power-of-two prefixes per proposal; empirical replicate spread not proof or absolute integration error'))
'''
g={'__file__':str(D/'haar.py'),'__name__':'c4j_haar','C4_OLD':C4,'C4E':E,'C4F':F,'C4G':G,'C4I':I};exec(compile(src,str(C3/'orientation.py'),'exec'),g);g['run']()
