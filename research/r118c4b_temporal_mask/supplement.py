"""Fill three official-mask MC pairs omitted by old reduction directory."""
from pathlib import Path
import json,numpy as np,hashlib,sys
from astropy.io import fits
from scipy.stats import f
D=Path(__file__).resolve().parent;P=D.parent;Z=P/'r118c3z_spin_projector_mc';H=Path.home()
old=json.loads((D/'OFFICIAL_MASK_MC.json').read_text());a=json.loads((D/'ACQUISITION.json').read_text());mask=H/'r118c4b_mask_cache/COM_Mask_CMB-common-Mask-Pol_2048_R3.00.fits'
assert old['ids']==list(range(3,30))+list(range(180,210)),old['ids']
with fits.open(D/'BEAM_EXTENSION.fits') as h:beam=np.array(h[1].data['POL_BEAM'],float)
s=(Z/'bass.py').read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
rep("t,p=hp.pix2ang(16,np.arange(hp.nside2npix(16)));keep=abs(np.pi/2-t)>=np.deg2rad(20);idx=hp.ang2pix(2048,t[keep],p[keep]);assert len(np.unique(idx))==len(idx)","t,p0=hp.pix2ang(16,np.arange(hp.nside2npix(16)));raw_idx=hp.ang2pix(2048,t,p0);nest=hp.ring2nest(2048,raw_idx);assert np.array_equal(hp.nest2ring(2048,nest),raw_idx)\n with fits.open(mask_path,memmap=True) as hh:\n  m=hh[1].data['PMASK'][nest];assert np.isfinite(m).all();keep=m>0.5\n idx=raw_idx[keep];assert len(np.unique(idx))==len(idx)")
rep("a[l*l-4:(l+1)**2-4]=row['Bre'][m]+1j*row['Bim'][m]","a[l*l-4:(l+1)**2-4]=beam_value[l]*(row['Bre'][m]+1j*row['Bim'][m])")
rep("for i in range(30):","for i in range(3):")
token=" A,N=np.array(A),np.array(N);assert len(A)>=16,(len(A),records)"
assert s.count(token)==1
s=s[:s.index(token)]+'''
 A,N=np.array(A),np.array(N);assert ids==[0,1,2],records
 np.savez_compressed(D/'OFFICIAL_MASK_SUPPLEMENT.npz',sample_pixel=idx,signal=A,noise=N,response=R)
 (D/'OFFICIAL_MASK_SUPPLEMENT_INPUTS.json').write_text(json.dumps(records,indent=2)+'\\n')
'''
ns={'__file__':str(D/'supplement.py'),'__name__':'supplement','mask_path':str(mask),'beam_value':beam};exec(compile(s,str(Z/'bass.py'),'exec'),ns);ns['mc']()
x=np.load(D/'OFFICIAL_MASK_SUPPLEMENT.npz');y=np.load(D/'OFFICIAL_MASK_SCORES.npz')
assert np.array_equal(x['sample_pixel'],y['sample_pixel']) and np.array_equal(x['response'],y['response'])
A=np.r_[x['signal'],y['signal']];N=np.r_[x['noise'],y['noise']];R=y['response'];ids=[0,1,2]+old['ids'];assert ids==list(range(30))+list(range(180,210))
T=A[:30]+N[:30];V=A[30:]+N[30:];S=np.cov(T,rowvar=False);q=np.linalg.solve(np.linalg.cholesky(S),(V-T.mean(0)).T).T;d2=np.sum(q*q,axis=1);n,p=T.shape;crit=(1+1/n)*(n-1)*p/(n-p)*f.ppf(.95,p,n-p)
def fisher(X):
 C=np.cov(X,rowvar=False);F=R.T@np.linalg.solve(C,R);ev=np.linalg.eigvalsh(F);return dict(cov_eigen_uK2=np.linalg.eigvalsh(C).tolist(),fisher_eigen_per_unit_template_uK2=ev.tolist(),condition=float(ev[-1]/ev[0]))
out=dict(n_pairs=60,ids=ids,train_n=30,heldout_n=30,n_sample_pixels=len(y['sample_pixel']),holdout_score_mean=float(d2.mean()),finite_gaussian_95=float(crit),holdout_exceed=int(np.sum(d2>crit)),heldout_whitened_cov_eigen=np.linalg.eigvalsh(np.cov(q,rowvar=False)).tolist(),train_fisher=fisher(T),heldout_fisher=fisher(V),scope='official common mask+beam, same C4B sampling and template basis; supplement 0..2 from prior exact re-reduction; no observed sky fit or official likelihood')
(D/'OFFICIAL_MASK_FULL60.json').write_text(json.dumps(out,indent=2)+'\n');np.savez_compressed(D/'OFFICIAL_MASK_FULL60_SCORES.npz',sample_pixel=y['sample_pixel'],response=R,signal=A,noise=N)
print(json.dumps(out),flush=True)
