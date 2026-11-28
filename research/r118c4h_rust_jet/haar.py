"""Defensive mixture of angular central Gaussian proposals on unit quaternions."""
from pathlib import Path
import json,numpy as np,hashlib
D=Path(__file__).resolve().parent;P=D.parent;G=P/'r118c4g_discrete_quadratic';F=P/'r118c4f_robust_transfer';E=P/'r118c4e_precision_refit';C3=P/'r118c4c_conditioned_transfer';C4=P/'r118c4d_precision_jet'
old=(G/'haar.py').read_text();ns={'__file__':str(G/'haar.py'),'__name__':'inspect'}
exec(compile(old[:old.index("g={'__file__'")],str(G/'haar.py'),'exec'),ns)
src=ns['src'];src=src[:src.index(' # Uniform 8192 pilots')]+'''
 from scipy.spatial.transform import Rotation
 from scipy.special import ndtri
 # Reuse the C4G fixed actual data, same wide amplitude prior and pilot seed.
 pilot=qmc.Sobol(3,scramble=True,seed=118470).random_base2(13);L0=ll(pilot,data)
 ang=np.c_[2*np.pi*pilot[:,0],np.arccos(2*pilot[:,1]-1),2*np.pi*pilot[:,2]]
 q0=Rotation.from_euler('ZYZ',ang).as_quat()
 old=np.load(C4G/'ADAPTIVE_LOG_WEIGHTS.npz');assert np.array_equal(old['pilot_cube'],pilot) and np.max(abs(old['pilot_logLR']-L0))<1e-10
 def logq(q,covs,probs):
  inv=np.linalg.inv(covs);v=np.einsum('ni,kij,nj->nk',q,inv,q)
  return logsumexp(np.log(probs)[None,:]-.5*np.linalg.slogdet(covs)[1][None,:]-2*np.log(v),axis=1)
 assert max(abs(logq(q0,np.eye(4)[None],np.ones(1))))<1e-14
 def loglike(q,Y):
  aa=Rotation.from_quat(q).as_euler('ZYZ');aa[:,0]%=2*np.pi;aa[:,2]%=2*np.pi
  x=np.c_[aa[:,0]/(2*np.pi),(1+np.cos(aa[:,1]))/2,aa[:,2]/(2*np.pi)]
  return ll(x,Y)
 assert np.max(abs(loglike(q0[:16],data)-L0[:16]))<1e-10
 rows=[];lw0=[]
 for j,label in enumerate(labels):
  v=L0[:,j];w=np.exp(v-v.max());w/=w.sum();cent=[]
  for k in np.argsort(-v,kind='stable'):
   if not cent or np.max(abs(q0[k]@q0[cent].T))<.93:cent.append(k)
   if len(cent)==8:break
  assigned=np.argmax(abs(q0@q0[cent].T),axis=1);cov=[np.eye(4)];mass=[]
  for k in range(len(cent)):
   mask=assigned==k;ww=w[mask];wt=float(ww.sum())
   if wt<1e-5:continue
   M=np.einsum('i,ij,ik->jk',ww,q0[mask],q0[mask])/wt
   # mild inflation and eigenvalue floor prevent collapse at sparse pilot peaks.
   val,V=np.linalg.eigh(M);val=np.maximum(val,0.002);val[:-1]*=1.7;cov.append((V*val)@V.T);mass.append(wt)
  cov=np.array(cov);prob=np.r_[.25,.75*np.array(mass)/sum(mass)];chol=np.linalg.cholesky(cov)
  # check proposal normalization via uniform expectation on independent Haar samples; peaked q makes this noisy.
  mu=np.exp(logq(q0,cov,prob)).mean()
  for seed in [118481,118482]:
   U=qmc.Sobol(5,scramble=True,seed=seed).random_base2(13);k=np.minimum(np.searchsorted(np.cumsum(prob),U[:,0],side='right'),len(prob)-1)
   z=ndtri(np.clip(U[:,1:],1e-15,1-1e-15));q=np.einsum('nij,nj->ni',chol[k],z);q/=np.linalg.norm(q,axis=1)[:,None]
   density=logq(q,cov,prob);assert min(density)>=np.log(.25)-1e-12
   logval=loglike(q,data[j:j+1])[:,0];lw=logval-density;a={str(n):float(logsumexp(lw[:n])-np.log(n)) for n in [2048,4096,8192]};ess=float(np.exp(2*logsumexp(lw)-logsumexp(2*lw)))
   rows.append(dict(label=label,seed=seed,logLR=a,ess=ess,components=len(prob),pilot_density_mean=float(mu),prob=prob.tolist(),eigenvalues=np.linalg.eigvalsh(cov).tolist()));lw0.append(lw);print(rows[-1],flush=True)
 prev=json.loads((C4G/'ADAPTIVE_HAAR.json').read_text())['summary'];summary=[]
 for j,label in enumerate(labels):
  a,b=rows[2*j:2*j+2];summary.append(dict(label=label,quaternion_scramble_difference=abs(a['logLR']['8192']-b['logLR']['8192']),prior_cell_difference=prev[j]['adaptive_scramble_difference'],uniform_difference=prev[j]['uniform_prior_scramble_difference'],logLR=[a['logLR']['8192'],b['logLR']['8192']],ess=[a['ess'],b['ess']]))
 np.savez_compressed(D/'QUATERNION_WEIGHTS.npz',log_weights=np.array(lw0),labels=np.array(labels))
 write('QUATERNION_HAAR.json',dict(rows=rows,summary=summary,pilot_n=8192,evaluation_n=8192,defensive_fraction=.25,prior_factor=10.,scope='ACG mixture on S3 antipodal quaternions, density relative Haar; fixed C4G four targets and data, two independent eval scrambles, numerical quadrature not observed posterior'))
'''
g={'__file__':str(D/'haar.py'),'__name__':'c4h_haar','C4_OLD':C4,'C4E':E,'C4F':F,'C4G':G};exec(compile(src,str(C3/'orientation.py'),'exec'),g);g['run']()
