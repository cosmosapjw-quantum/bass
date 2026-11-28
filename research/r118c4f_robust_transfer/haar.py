"""Reuse exact C4E 190 Commander MC scores; orientation/prior sensitivity and conditional injections."""
from pathlib import Path
import json,numpy as np,hashlib
D=Path(__file__).resolve().parent;P=D.parent;E=P/'r118c4e_precision_refit';C3=P/'r118c4c_conditioned_transfer';C4=P/'r118c4d_precision_jet'
old=(E/'haar_refine.py').read_text();ns={'__file__':str(E/'haar_refine.py'),'__name__':'inspect'}
exec(compile(old[:old.index("ns={'__file__'")],str(E/'haar_refine.py'),'exec'),ns)
src=ns['src'];src=src.replace("cached=np.load(D/'EXPANDED_SCORES.npz')","cached=np.load(C4E/'EXPANDED_SCORES.npz')").replace("(D/'NEW_INPUTS.json').read_text()","(C4E/'NEW_INPUTS.json').read_text()")
assert 'C4E' in src
src=src[:src.index(' t=qmc.Sobol')]+'''
 prior=np.load(C4E/'HAAR_LR_2048.npz');tau2=json.loads((C4E/'HAAR_COVARIANCE_2048.json').read_text())['tau2'];assert np.array_equal(C,prior['covariance']) and np.array_equal(mu,prior['mean'])
 yy=np.r_[cal,test]-mu;results=[];alllogs=[];rng=np.random.default_rng(11846)
 def orientation(seed):
  t=qmc.Sobol(3,scramble=True,seed=seed).random_base2(13);angles=np.c_[2*np.pi*t[:,0],np.arccos(2*t[:,1]-1),2*np.pi*t[:,2]]
  resp=np.array([compressed(tuple(a)) for a in angles]);F=np.einsum('rni,nm,rmj->rij',resp,Ci,resp);assert np.min(np.linalg.eigvalsh(F))>0
  return angles,resp,F
 # Generate injections at independently selected second-scramble orientations and directions.
 a2,R2,F2=orientation(11846);inj_idx=rng.choice(len(R2),20,replace=False);u=rng.normal(size=(20,6));raw=np.einsum('nki,ni->nk',R2[inj_idx],u);raw/=np.sqrt(np.einsum('ni,ij,nj->n',raw,Ci,raw))[:,None]
 data=np.r_[yy,*[test-mu+s*raw for s in [2.,4.,8.]]]
 for seed in [11845,11846]:
  angles,resp,Fs=orientation(seed) if seed==11845 else (a2,R2,F2)
  if seed==11845:assert np.array_equal(angles[:2048],prior['angles'])
  g=np.einsum('rni,nm,km->rki',resp,Ci,data)
  for factor in [.1,.3,1.,3.,10.]:
   vv=tau2*factor;inv=np.linalg.inv(Fs+np.eye(6)/vv);ll=-.5*np.linalg.slogdet(np.eye(6)+vv*Fs)[1][:,None]+.5*np.einsum('rki,rij,rkj->rk',g,inv,g)
   if seed==11845 and factor==1:assert np.max(abs(ll[:2048,:60]-prior['logLR']))<1e-11
   logs={n:logsumexp(ll[:n],axis=0)-np.log(n) for n in [2048,4096,8192]}
   a=logs[8192];th=float(np.quantile(a[:40],.95));testv=a[40:60]
   results.append(dict(seed=seed,prior_factor=factor,threshold=th,null_exceed=int(sum(testv>th)),null_mean=float(testv.mean()),detection_counts={str(s):int(sum(a[60+i*20:80+i*20]>th)) for i,s in enumerate([2.,4.,8.])},quadrature_max_abs={str(n):float(max(abs(logs[n]-a))) for n in [2048,4096]},quadrature_null_max_abs=float(max(abs(logs[4096][:60]-a[:60])))))
   alllogs.append(a);print(results[-1],flush=True)
 arr=np.array(alllogs);comparison={str(f):float(max(abs(arr[i]-arr[5+i]))) for i,f in enumerate([.1,.3,1.,3.,10.])}
 np.savez_compressed(D/'PRIOR_LOG_LR.npz',logLR=arr,injection_unit=raw,injection_orientation=a2[inj_idx],ids=ids0[ids0>=210],factors=np.array([.1,.3,1.,3.,10.]),seeds=np.array([11845,11846]))
 write('HAAR_PRIOR_SENSITIVITY.json',dict(rows=results,seed_difference_max_abs=comparison,tau2=tau2,prior_source_sha=sha(C4E/'HAAR_LR_2048.npz'),n_pairs=190,train=130,calibration=40,test=20,orientation_count=8192,scope='same C4E observed-simulation scores reused for sensitivity, not fresh test; synthetic injections on actual test draws normalized in training covariance; conditional amplitude prior, no observed sky or cosmological posterior'))
'''
g={'__file__':str(D/'haar.py'),'__name__':'c4f_haar','C4_OLD':C4,'C4E':E};exec(compile(src,str(C3/'orientation.py'),'exec'),g);g['run']()
