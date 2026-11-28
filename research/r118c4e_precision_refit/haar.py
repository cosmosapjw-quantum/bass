"""Actual new Commander MC, train-only shrinkage, Haar marginalization (proper Gaussian amplitude prior)."""
from pathlib import Path
import numpy as np,sys,json,hashlib
D=Path(__file__).resolve().parent;P=D.parent;C3=P/'r118c4c_conditioned_transfer';C4=P/'r118c4d_precision_jet';H=Path.home()
src=(C3/'orientation.py').read_text()
old="ids=list(range(45))+list(range(210,230))";assert src.count(old)==1;src=src.replace(old,"ids=list(range(90,130))+list(range(250,270))")
token=" S,N=np.array(ss),np.array(nn);train=(S+N)[:45];test=(S+N)[45:]";assert src.count(token)==1
src=src[:src.index(token)]+'''
 from scipy.stats import qmc
 from scipy.special import logsumexp
 S,N=np.array(ss),np.array(nn);old=np.load(C4_OLD/'EXPANDED_SCORES.npz')
 assert np.array_equal(idx,old['sample_pixel']) and np.array_equal(R,old['response_basis']) and np.array_equal(coeff,old['coeff'])
 ids0=np.r_[old['ids'],ids];assert len(np.unique(ids0))==190
 o=np.argsort(ids0);ids0=ids0[o];S=np.r_[old['signal'],S][o];N=np.r_[old['noise'],N][o];X=S+N
 np.savez_compressed(D/'EXPANDED_SCORES.npz',sample_pixel=idx,response_basis=R,coeff=coeff,ids=ids0,signal=S,noise=N)
 write('NEW_INPUTS.json',records)
 train=X[ids0<130];assert len(train)==130
 cal=X[(ids0>=210)&(ids0<250)];test=X[(ids0>=250)&(ids0<270)];assert len(cal)==40 and len(test)==20
 def cov(X,a,target):
  s=np.cov(X,rowvar=False);T=np.eye(len(s))*np.trace(s)/len(s) if target=='isotropic' else np.diag(np.diag(s))
  return (1-a)*s+a*T
 def score(X,C,mu):
  v=X-mu;return np.linalg.slogdet(C)[1]+np.einsum('ni,ij,nj->n',v,np.linalg.inv(C),v)
 alphas=np.linspace(0,1,21);folds=[np.delete(train,i,axis=0) for i in range(len(train))];fit_results=[]
 for target in ['isotropic','diagonal']:
  cv=[float(np.mean([score(train[i:i+1],cov(f,a,target),f.mean(0))[0] for i,f in enumerate(folds)])) for a in alphas]
  j=int(np.argmin(cv));fit_results.append(dict(target=target,alpha=float(alphas[j]),cv=cv,cv_min=cv[j]))
 best=min(fit_results,key=lambda a:a['cv_min']);C=cov(train,best['alpha'],best['target']);C0=cov(train,0.,'isotropic');Ci=np.linalg.inv(C);mu=train.mean(0)
 def coef_real(a):
  v=[]
  for l in [3,5,7]:
   i=l*l-4+l;v.append(a[i].real*beam[l])
   for m in range(1,l+1):v.extend([np.sqrt(2)*a[i+m].real*beam[l],np.sqrt(2)*a[i+m].imag*beam[l]])
  return np.array(v)
 def compressed(angles):
  cc=np.stack([coef_real(rotate(a,angles) if angles!=(0.,0.,0.) else a) for a in coeff]);return R@cc.T
 # Direct pixel and algebraic response compare on two orientations.
 replay=[]
 for ang in [(0.,0.,0.),(.3,1.1,.7)]:
  a=compressed(ang);b,_=response(ang);err=np.linalg.norm(a-b)/np.linalg.norm(b);assert err<1e-10;replay.append(float(err))
 t=qmc.Sobol(3,scramble=True,seed=11845).random_base2(9);angles=np.c_[2*np.pi*t[:,0],np.arccos(2*t[:,1]-1),2*np.pi*t[:,2]]
 resp=np.array([compressed(tuple(a)) for a in angles]);Fs=np.einsum('rni,nm,rmj->rij',resp,Ci,resp);eigen=np.linalg.eigvalsh(Fs);assert np.min(eigen)>0
 # Fixed proper coefficient prior, scale selected using training covariance and the orientation geometry only.
 tau2=6/float(np.mean(np.trace(Fs[:256],axis1=1,axis2=2)));Y=np.r_[cal,test]-mu;g=np.einsum('rni,nm,km->rki',resp,Ci,Y)
 inv=np.linalg.inv(Fs+np.eye(6)/tau2);ll=-.5*np.linalg.slogdet(np.eye(6)+tau2*Fs)[1][:,None]+.5*np.einsum('rki,rij,rkj->rk',g,inv,g)
 # Independent 33d dense covariance identity on actual first orientation and one heldout datum.
 x=Y[-1];v=resp[0];d=C+tau2*v@v.T;direct=.5*(np.linalg.slogdet(C)[1]-np.linalg.slogdet(d)[1]+x@Ci@x-x@np.linalg.solve(d,x));assert abs(direct-ll[0,-1])<1e-10
 logs={n:logsumexp(ll[:n],axis=0)-np.log(n) for n in [64,256,512]};cal95=float(np.quantile(logs[512][:40],.95));nt=logs[512][40:];new_score=float(score(test,C,mu).mean());new_raw=float(score(test,C0,mu).mean())
 out=dict(n_pairs=190,train=130,old_calibration=40,new_test=20,selected=best,fit_results=fit_results,heldout_score_unshrunk=new_raw,heldout_score_shrunk=new_score,mask_sha=acq['mask']['sha256'],beam_sha=acq['beam']['tail_sha256'],prior_sha=sha(C4_OLD/'EXPANDED_SCORES.npz'),tau2=tau2,orientation_count=512,orientation_replay_relative=replay,dense_LR_error=float(abs(direct-ll[0,-1])),fisher_condition_range=[float(np.min(eigen[:,-1]/eigen[:,0])),float(np.max(eigen[:,-1]/eigen[:,0]))],quadrature_max_abs={str(n):float(np.max(abs(logs[n]-logs[512]))) for n in [64,256]},calibration95_logLR=cal95,new_exceed=int(sum(nt>cal95)),new_logLR_mean=float(np.mean(nt)),new_logLR_range=[float(min(nt)),float(max(nt))],scope='conditional proper Gaussian template amplitude prior with empirical training covariance; Haar Sobol integral averaged likelihood ratio, empirical prior-heldout calibration and new heldout test; no observed sky, no official cosmological posterior')
 np.savez_compressed(D/'HAAR_LR.npz',ids=ids0[ids0>=210],angles=angles,logLR=ll,logLR64=logs[64],logLR256=logs[256],logLR512=logs[512],F=Fs,covariance=C,mean=mu)
 write('HAAR_COVARIANCE.json',out);print(out,flush=True)
'''
ns={'__file__':str(D/'haar.py'),'__name__':'c4e_haar','C4_OLD':C4};exec(compile(src,str(C3/'orientation.py'),'exec'),ns);ns['run']()
