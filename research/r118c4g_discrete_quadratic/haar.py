"""Defensive importance stratification on Haar cube, fixed empirical Commander likelihood."""
from pathlib import Path
import json,numpy as np,hashlib
D=Path(__file__).resolve().parent;P=D.parent;E=P/'r118c4e_precision_refit';F=P/'r118c4f_robust_transfer';C3=P/'r118c4c_conditioned_transfer';C4=P/'r118c4d_precision_jet'
old=(E/'haar_refine.py').read_text();ns={'__file__':str(E/'haar_refine.py'),'__name__':'inspect'}
exec(compile(old[:old.index("ns={'__file__'")],str(E/'haar_refine.py'),'exec'),ns)
src=ns['src'];src=src.replace("cached=np.load(D/'EXPANDED_SCORES.npz')","cached=np.load(C4E/'EXPANDED_SCORES.npz')").replace("(D/'NEW_INPUTS.json').read_text()","(C4E/'NEW_INPUTS.json').read_text()")
src=src[:src.index(' t=qmc.Sobol')]+'''
 prior=np.load(C4E/'HAAR_LR_2048.npz');tau2=json.loads((C4E/'HAAR_COVARIANCE_2048.json').read_text())['tau2'];assert np.array_equal(C,prior['covariance']) and np.array_equal(mu,prior['mean'])
 f=np.load(C4F/'PRIOR_LOG_LR.npz');raw=f['injection_unit'];assert np.array_equal(f['ids'],ids0[ids0>=210]);Y=np.r_[cal,test]-mu
 # Prespecified subset: one null and three injection cases; strong-signal quadrature diagnostic only.
 labels=['null0','snr4_0','snr8_0','snr8_1'];data=np.stack([Y[40],Y[40]+4*raw[0],Y[40]+8*raw[0],Y[41]+8*raw[1]])
 factor=10.;vv=tau2*factor;bins=8;nc=bins**3;alpha=.25
 def response_cube(x):
  aa=np.c_[2*np.pi*x[:,0],np.arccos(2*x[:,1]-1),2*np.pi*x[:,2]]
  return np.array([compressed(tuple(a)) for a in aa])
 def ll(x,Y):
  resp=response_cube(x);F=np.einsum('rni,nm,rmj->rij',resp,Ci,resp);g=np.einsum('rni,nm,km->rki',resp,Ci,Y)
  inv=np.linalg.inv(F+np.eye(6)/vv)
  return -.5*np.linalg.slogdet(np.eye(6)+vv*F)[1][:,None]+.5*np.einsum('rki,rij,rkj->rk',g,inv,g)
 # Uniform 8192 pilots populate all 512 cells equally; independent evaluation.
 pilot=qmc.Sobol(3,scramble=True,seed=118470).random_base2(13);L0=ll(pilot,data)
 ix=np.ravel_multi_index(np.minimum((pilot*bins).astype(int),bins-1).T,(bins,)*3);counts=np.bincount(ix,minlength=nc);assert np.all(counts==16)
 logs=[];rows=[]
 for j,label in enumerate(labels):
  v=L0[:,j];vmax=v.max();w=np.bincount(ix,weights=np.exp(v-vmax),minlength=nc)/counts
  prob=alpha/nc+(1-alpha)*w/w.sum();assert abs(prob.sum()-1)<1e-14 and min(prob)>=alpha/nc
  for seed in [118471,118472]:
   U=qmc.Sobol(4,scramble=True,seed=seed).random_base2(13);k=np.searchsorted(np.cumsum(prob),U[:,0],side='right');k=np.minimum(k,nc-1);cell=np.array(np.unravel_index(k,(bins,)*3)).T;x=(cell+U[:,1:])/bins
   l=ll(x,data[j:j+1])[:,0];lw=l-np.log(nc*prob[k]);a={str(n):float(logsumexp(lw[:n])-np.log(n)) for n in [2048,4096,8192]};ess=float(np.exp(2*logsumexp(lw)-logsumexp(2*lw)))
   rows.append(dict(label=label,seed=seed,prior_factor=factor,logLR=a,ess=ess,uniform_pilot=float(logsumexp(v)-np.log(len(v))),max_density=float(nc*max(prob)),min_density=float(nc*min(prob)),pilot_peak=float(vmax)));print(rows[-1],flush=True);logs.append(lw)
 arr=np.array(logs);prior_log=f['logLR'];idx=[40,80,100,101];prev=prior_log[[4,9]][:,idx]
 summary=[]
 for j,label in enumerate(labels):
  a,b=rows[2*j:2*j+2];summary.append(dict(label=label,adaptive_scramble_difference=abs(a['logLR']['8192']-b['logLR']['8192']),uniform_prior_scramble_difference=float(abs(prev[0,j]-prev[1,j])),adaptive_8192=[a['logLR']['8192'],b['logLR']['8192']],uniform_8192=prev[:,j].tolist()))
 np.savez_compressed(D/'ADAPTIVE_LOG_WEIGHTS.npz',labels=np.array(labels),log_weights=arr,pilot_logLR=L0,pilot_cube=pilot)
 write('ADAPTIVE_HAAR.json',dict(rows=rows,summary=summary,prior_factor=factor,defensive_fraction=alpha,cells=nc,pilot_n=8192,evaluation_n=8192,scope='conditional numerical quadrature on fixed C4F data/injection subset; pilot and two evaluation scrambles independent; no new null calibration, no cosmological inference'))
'''
g={'__file__':str(D/'haar.py'),'__name__':'c4g_haar','C4_OLD':C4,'C4E':E,'C4F':F};exec(compile(src,str(C3/'orientation.py'),'exec'),g);g['run']()
