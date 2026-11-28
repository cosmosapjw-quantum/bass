"""Expand actual 33d official-mask Commander scores without rereading earlier samples."""
from pathlib import Path
import numpy as np,sys,json,hashlib
D=Path(__file__).resolve().parent;P=D.parent;C3=P/'r118c4c_conditioned_transfer';A=P/'r118c4b_temporal_mask';H=Path.home()
src=(C3/'orientation.py').read_text()
old="ids=list(range(45))+list(range(210,230))";assert src.count(old)==1;src=src.replace(old,"ids=list(range(45,90))+list(range(230,250))")
token=" S,N=np.array(ss),np.array(nn);train=(S+N)[:45];test=(S+N)[45:]";assert src.count(token)==1
src=src[:src.index(token)]+'''
 S,N=np.array(ss),np.array(nn);old=np.load(C3_OLD/'ORIENTATION_SCORES.npz')
 assert np.array_equal(idx,old['sample_pixel']) and np.array_equal(R,old['response_basis']) and np.array_equal(coeff,old['coeff'])
 ids0=np.r_[old['ids'],ids];assert len(np.unique(ids0))==130
 o=np.argsort(ids0);ids0=ids0[o];S=np.r_[old['signal'],S][o];N=np.r_[old['noise'],N][o];X=S+N
 np.savez_compressed(D/'EXPANDED_SCORES.npz',sample_pixel=idx,response_basis=R,coeff=coeff,ids=ids0,signal=S,noise=N)
 write('NEW_INPUTS.json',records)
 def cov(X,a,target):
  s=np.cov(X,rowvar=False);T=np.eye(len(s))*np.trace(s)/len(s) if target=='isotropic' else np.diag(np.diag(s))
  return (1-a)*s+a*T
 def score(X,C,mu):
  v=X-mu;return np.linalg.slogdet(C)[1]+np.einsum('ni,ij,nj->n',v,np.linalg.inv(C),v)
 alphas=np.linspace(0,1,21);results=[]
 for n in [45,90]:
  train=X[ids0<n];assert len(train)==n
  oldtest=X[(ids0>=210)&(ids0<230)];newtest=X[(ids0>=230)&(ids0<250)]
  assert len(oldtest)==len(newtest)==20
  folds=[np.delete(train,i,axis=0) for i in range(n)];fit_results=[]
  for target in ['isotropic','diagonal']:
   cv=[float(np.mean([score(train[i:i+1],cov(f,a,target),f.mean(0))[0] for i,f in enumerate(folds)])) for a in alphas]
   j=int(np.argmin(cv));fit_results.append(dict(target=target,alpha=float(alphas[j]),cv=cv,cv_min=cv[j]))
  best=min(fit_results,key=lambda a:a['cv_min']);S0=cov(train,0.,'isotropic');C=cov(train,best['alpha'],best['target'])
  metrics={}
  for k,te in [('prior',oldtest),('new',newtest),('combined',np.r_[oldtest,newtest])]:
   v=te-train.mean(0);w=np.linalg.solve(np.linalg.cholesky(C),v.T).T
   metrics[k]=dict(n=len(te),unshrunk=float(score(te,S0,train.mean(0)).mean()),shrunk=float(score(te,C,train.mean(0)).mean()),mean_mahalanobis=float(np.mean(np.sum(w*w,axis=1))),cov_condition=float(np.linalg.cond(C)))
  angles=[(0.,0.,0.)]+[(a,b,0.) for a in [0.,np.pi/2,np.pi,3*np.pi/2] for b in [np.pi/6,np.pi/2,5*np.pi/6]]
  orientation=[]
  for ang in angles:
   Xr,ret=response(ang);F=Xr.T@np.linalg.solve(C,Xr);ev=np.linalg.eigvalsh(F);assert ev[0]>0
   orientation.append(dict(angles=list(ang),eigen=ev.tolist(),condition=float(ev[-1]/ev[0])))
  results.append(dict(train=n,selected=best,fits=fit_results,heldout=metrics,orientations=orientation))
 out=dict(n_pairs=130,old_pairs=65,new_pairs=65,dimension=33,mask_sha=acq['mask']['sha256'],beam_sha=acq['beam']['tail_sha256'],prior_scores_sha256=sha(C3_OLD/'ORIENTATION_SCORES.npz'),results=results,scope='actual official mask/beam projected B33 scores. Same 65 old+65 new; 90 train and 40 test including new separate 20. Selection only training LOO. Not observed-sky fit or official likelihood.')
 write('EXPANDED_COVARIANCE.json',out);print(out,flush=True)
'''
ns={'__file__':str(D/'covariance.py'),'__name__':'c4d_cov','C3_OLD':C3};exec(compile(src,str(C3/'orientation.py'),'exec'),ns);ns['run']()
