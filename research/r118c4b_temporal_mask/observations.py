"""Official PR3 mask/beam acquisition and actual MC diagnostic; independent shrinkage fallback."""
from pathlib import Path
import json,numpy as np,hashlib,sys,requests,re,io
from urllib.parse import urljoin
from scipy.stats import f
D=Path(__file__).resolve().parent;P=D.parent;Z=P/'r118c3z_spin_projector_mc';A=P/'r118c4a_robust_wedge';H=Path.home()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def shrink():
 train=np.load(Z/'mc_extension/COMMANDER_SCORES_120.npz');test=np.load(A/'HOLDOUT_SCORES.npz')
 assert np.array_equal(train['sample_pixel'],test['sample_pixel']) and np.array_equal(train['response'],test['response'])
 T=train['signal']+train['noise'];V=test['signal']+test['noise'];R=train['response'];alphas=np.linspace(0,1,21)
 def est(t,a):
  s=np.cov(t,rowvar=False);return (1-a)*s+a*np.trace(s)/len(s)*np.eye(len(s))
 def score(t,C,mu):
  q=t-mu;return np.linalg.slogdet(C)[1]+np.einsum('ni,ij,nj->n',q,np.linalg.inv(C),q)
 cv=[]
 for a in alphas:
  cv.append(float(np.mean([score(T[i:i+1],est(np.delete(T,i,axis=0),a),np.delete(T,i,axis=0).mean(0))[0] for i in range(len(T))])))
 chosen=float(alphas[np.argmin(cv)]);results={}
 for a in [0.,chosen,1.]:
  s=est(T,a);x=V-T.mean(0);q=np.sum(np.linalg.solve(np.linalg.cholesky(s),x.T)**2,axis=0);F=R.T@np.linalg.solve(s,R)
  results[str(a)]=dict(test_gaussian_score=float(score(V,s,T.mean(0)).mean()),mean_mahalanobis=float(q.mean()),whitened_cov_eigen=np.linalg.eigvalsh(np.cov(np.linalg.solve(np.linalg.cholesky(s),x.T))).tolist(),fisher_condition=float(np.linalg.cond(F)))
 write('SHRINKAGE.json',dict(train=120,test=60,alphas=alphas.tolist(),LOO_scores=cv,selected=chosen,results=results,scope='actual analytic-cut compressed scores; train-only LOO shrinkage to isotropic covariance; heldout from prior C4A not independent of research selection, no new likelihood'))
 print('shrink',chosen,results,flush=True)
def official():
 from astropy.io import fits
 import healpy as hp
 root=H/'r118c4b_mask_cache';root.mkdir(exist_ok=False)
 prior=json.loads((H/'Downloads/htt_r105_commander/reductions/commander_00180.json').read_text())['input_sha256_and_bytes']
 mask=prior['polarization_mask'];observ=prior['observed'];acq={}
 previews={'mask':'https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/previews/COM_Mask_CMB-common-Mask-Pol_2048_R3.00/index.html','beam':'https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/previews/COM_CMB_IQU-commander_2048_R3.00_full/index.html'}
 def url(kind,filename):
  r=requests.get(previews[kind],timeout=15);r.raise_for_status()
  links=re.findall(r'href\s*=\s*["\']([^"\']+)["\']',r.text,re.I)
  return urljoin(r.url,next(x for x in links if x.endswith(filename)))
 def get_mask():
  u=url('mask',mask['filename']);p=root/mask['filename'];hs=hashlib.sha256();n=0
  with requests.get(u,stream=True,timeout=(15,30)) as r:
   r.raise_for_status()
   with p.open('wb') as f:
    for x in r.iter_content(1024*1024):
     n+=len(x);assert n<=mask['bytes'];hs.update(x);f.write(x)
   assert n==mask['bytes'] and hs.hexdigest()==mask['sha256'],(n,hs.hexdigest(),mask)
  with fits.open(p,memmap=True) as h:
   a=h[1];assert a.header['NSIDE']==2048 and a.header['ORDERING'].strip()=='NESTED' and 'PMASK' in a.columns.names
  return p,dict(url=u,bytes=n,sha256=hs.hexdigest(),exact_prior_hash=True)
 def get_beam():
  u=url('beam',observ['filename']);total=observ['bytes'];size=2880+((4097*8+2879)//2880)*2880;lo=total-size
  with requests.get(u,headers={'Range':f'bytes={lo}-{total-1}'},stream=True,timeout=(15,30)) as r:
   assert r.status_code==206,(r.status_code,'range unsupported')
   assert r.headers.get('Content-Range','').startswith(f'bytes {lo}-{total-1}/'),r.headers
   data=r.raw.read(size+1);assert len(data)==size and data[:8]==b'XTENSION'
  primary=io.BytesIO();fits.PrimaryHDU().writeto(primary);p=D/'BEAM_EXTENSION.fits';p.write_bytes(primary.getvalue()+data)
  with fits.open(p) as h:
   a=h[1];assert a.header['LMIN']==0 and a.header['LMAX_P']==4096 and a.header['METHOD'].strip()=='COMMANDER';beam=np.array(a.data['POL_BEAM'],float);assert beam.shape==(4097,) and np.isfinite(beam[:11]).all() and np.all(beam[2:11]>0)
  return beam,dict(url=u,range=[lo,total-1],response_content_range=r.headers.get('Content-Range'),tail_sha256=hashlib.sha256(data).hexdigest(),pol_beam_l0_l10=beam[:11].tolist(),scope='provider range HDU identity; not full-map SHA verification')
 try:p,acq['mask']=get_mask()
 except Exception as e:
  acq['mask_error']=repr(e);write('ACQUISITION.json',acq);print('mask blocked',repr(e),flush=True);return
 beam=np.ones(4097)
 try:beam,acq['beam']=get_beam()
 except Exception as e:acq['beam_error']=repr(e)
 write('ACQUISITION.json',acq)
 # Source reuse exact spin convention and template map, fresh official sample.
 s=(Z/'bass.py').read_text()
 def rep(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
 rep("t,p=hp.pix2ang(16,np.arange(hp.nside2npix(16)));keep=abs(np.pi/2-t)>=np.deg2rad(20);idx=hp.ang2pix(2048,t[keep],p[keep]);assert len(np.unique(idx))==len(idx)","t,p0=hp.pix2ang(16,np.arange(hp.nside2npix(16)));raw_idx=hp.ang2pix(2048,t,p0);nest=hp.ring2nest(2048,raw_idx);assert np.array_equal(hp.nest2ring(2048,nest),raw_idx)\n with fits.open(mask_path,memmap=True) as hh:\n  m=hh[1].data['PMASK'][nest];assert np.isfinite(m).all();keep=m>0.5\n idx=raw_idx[keep];assert len(np.unique(idx))==len(idx)\n np.savez_compressed(D/'MASK_SAMPLE.npz',all_ring_pixels=raw_idx,mask_values=m,selected=idx,beam=beam_value[:11])")
 rep("a[l*l-4:(l+1)**2-4]=row['Bre'][m]+1j*row['Bim'][m]","a[l*l-4:(l+1)**2-4]=beam_value[l]*(row['Bre'][m]+1j*row['Bim'][m])")
 rep("met=root/'rereduce_0_29'","met=root/'reductions'")
 rep("for i in range(30):","for i in list(range(30))+list(range(180,210)):")
 rep("assert len(A)>=16,(len(A),records)","assert len(A)>=40,(len(A),records)")
 rep("out=dict(n_pairs=len(A),ids=ids,","i0=np.array(ids)<30;i1=np.array(ids)>=180;assert i0.sum()>=20 and i1.sum()>=20\n T=A[i0]+N[i0];V=A[i1]+N[i1];S=np.cov(T,rowvar=False);q=np.linalg.solve(np.linalg.cholesky(S),(V-T.mean(0)).T).T;d2=np.sum(q*q,axis=1)\n from scipy.stats import f\n n,p=T.shape;crit=(1+1/n)*(n-1)*p/(n-p)*f.ppf(.95,p,n-p)\n out=dict(train_n=int(i0.sum()),heldout_n=int(i1.sum()),holdout_score_mean=float(d2.mean()),holdout_exceed=int(np.sum(d2>crit)),finite_gaussian_95=float(crit),heldout_whitened_cov_eigen=np.linalg.eigvalsh(np.cov(q,rowvar=False)).tolist(),n_pairs=len(A),ids=ids,")
 rep("actual Commander FFP10 sample covariance, sparse nearest-centre Galactic |b|>=20deg analytic mask (not official common mask), unit beam, fixed orientation, low-l E nuisance projected; normalized template amplitude only, no observed-sky fit or official likelihood.","actual Commander FFP10 sample covariance, official PR3 common PMASK threshold .5 on deterministic sparse RING pixels; provider beam applied to B templates if acquired (see ACQUISITION.json); fixed orientation and E nuisance projection, no observed-sky fit or official likelihood.")
 rep("write('COMMANDER_MC.json',out);write('COMMANDER_INPUTS.json',records);np.savez_compressed(D/'COMMANDER_SCORES.npz'","write('OFFICIAL_MASK_MC.json',out);write('OFFICIAL_MASK_INPUTS.json',records);np.savez_compressed(D/'OFFICIAL_MASK_SCORES.npz'")
 ns={'__file__':str(D/'observations.py'),'__name__':'c4b_official','mask_path':str(p),'beam_value':beam}
 exec(compile(s,str(Z/'bass.py'),'exec'),ns);ns['mc']()
if __name__=='__main__':{'shrink':shrink,'official':official}[sys.argv[1]]()

