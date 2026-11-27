"""Official mask+beam, 33-dimensional B subspace, train-only shrinkage and fixed orientation family."""
from pathlib import Path
import numpy as np,json,hashlib,sys
from astropy.io import fits
import healpy as hp
from scipy.special import sph_harm_y
D=Path(__file__).resolve().parent;P=D.parent;A=P/'r118c4b_temporal_mask';Z=P/'r118c3z_spin_projector_mc';L=P/'r118c3l_reachable_sky';H=Path.home()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def spin(theta,phi,lmax):
 sn=np.sin(theta);mu=np.cos(theta);ct=mu/sn;cols=[]
 for l in range(2,lmax+1):
  norm=np.sqrt((l-1)*l*(l+1)*(l+2))
  for m in range(-l,l+1):
   f,g=sph_harm_y(l,m,theta,phi,diff_n=1);ft=g[:,0];ftt=-ct*ft+(m*m/sn**2-l*(l+1))*f
   cols.append((ftt-(2*m/sn+ct)*ft+(m*m/sn**2+2*m*mu/sn**2)*f)/norm)
 return np.stack(cols,axis=1)
def realbasis(Y,lmax,factor):
 c=[]
 for l in range(2,lmax+1):
  i=l*l-4+l;c.append(factor*Y[:,i])
  for m in range(1,l+1):
   c.append(factor*(Y[:,i+m]+(-1)**m*Y[:,i-m])/np.sqrt(2));c.append(factor*1j*(Y[:,i+m]-(-1)**m*Y[:,i-m])/np.sqrt(2))
 return np.stack(c,axis=1)
def real(X):return np.r_[X.real,X.imag]
def run():
 acq=json.loads((A/'ACQUISITION.json').read_text());mask=H/'Downloads/htt_r105_commander/official_pr3/COM_Mask_CMB-common-Mask-Pol_2048_R3.00.fits';assert sha(mask)==acq['mask']['sha256']
 saved=np.load(A/'MASK_SAMPLE.npz');idx=saved['selected'];raw=saved['all_ring_pixels'];nest=hp.ring2nest(2048,raw)
 with fits.open(mask,memmap=True) as h:assert np.array_equal(h[1].data['PMASK'][nest],saved['mask_values'])
 beam=saved['beam'];theta,phi=hp.pix2ang(2048,idx);Y=spin(theta,phi,10);E=real(realbasis(Y,10,-1));Qe,_=np.linalg.qr(E,mode='reduced')
 # 33 B harmonic real columns in l3,5,7, beam fixed by ell (basis not beam weighted, template is).
 js=np.concatenate([np.arange(l*l-4,(l+1)**2-4) for l in [3,5,7]]);X=real(realbasis(Y,10,-1j))[:,js];Xp=X-Qe@(Qe.T@X);Q,R=np.linalg.qr(Xp,mode='reduced');assert np.linalg.matrix_rank(R)==33 and np.linalg.norm(Q.T@Qe)<1e-10
 coeff=[]
 for tag in ['whole','late','generic']:
  rows=[np.genfromtxt(L/f'{tag}_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]];r=[]
  for row in rows:
   a=np.zeros(60,complex)
   for l in [3,5,7]:
    m=(row['epoch']==1)&(row['ell']==l);a[l*l-4:(l+1)**2-4]=row['Bre'][m]+1j*row['Bim'][m]
   r.append(a)
  coeff.extend([(r[0]+r[1])/(2*.0025**2),(r[0]-r[1])/(2*.0025**3)])
 coeff=np.array(coeff);coeff/=np.linalg.norm(coeff,axis=1)[:,None]
 def rotate(a,angles):
  alm=np.zeros(hp.Alm.getsize(7),complex)
  for l in [3,5,7]:
   for m in range(l+1):alm[hp.Alm.getidx(7,l,m)]=a[l*l-4+l+m]
  before=alm.copy();hp.rotate_alm(alm,psi=angles[0],theta=angles[1],phi=angles[2],lmax=7)
  o=np.zeros(60,complex)
  for l in [3,5,7]:
   for m in range(l+1):
    v=alm[hp.Alm.getidx(7,l,m)];o[l*l-4+l+m]=v;o[l*l-4+l-m]=(-1)**m*v.conjugate()
  assert abs(np.linalg.norm(o)-1)<1e-9
  return o
 def response(angles):
  C=np.stack([rotate(a,angles) if angles!=(0.,0.,0.) else a for a in coeff])
  for l in [3,5,7]:C[:,l*l-4:(l+1)**2-4]*=beam[l]
  Xr=real(-1j*Y[:,:60]@C.T);return Q.T@Xr,np.linalg.norm(Xr-Qe@(Qe.T@Xr),axis=0)
 root=H/'Downloads/htt_r105_commander';records=[];ss=[];nn=[];ids=list(range(45))+list(range(210,230))
 for i in ids:
  meta=(root/'rereduce_0_29' if i<3 else root/'reductions')/f'commander_{i:05d}.json';prior=json.loads(meta.read_text())['input_sha256_and_bytes'];rec={'id':i};vals=[]
  for tag in ['cmb','noise']:
   p=root/'raw_pairs'/f'dx12_v3_commander_{tag}_mc_{i:05d}_raw.fits';q=prior[f'{tag}_{i:05d}'];assert p.stat().st_size==q['bytes']
   with fits.open(p,memmap=True) as h:
    t=h[1];hdr=t.header;assert hdr['NSIDE']==2048 and hdr['ORDERING'].strip()=='RING' and hdr['TUNIT2'].strip()=='K_CMB' and hdr.get('POLCCONV','COSMO').strip().upper()=='COSMO'
    v=[]
    for j in [1,2]:
     a=t.data.field(j);k=a.shape[-1] if a.ndim==2 else 1;v.append(np.array(a[idx//k,idx%k] if a.ndim==2 else a[idx],float))
    y=np.concatenate(v)*1e6;assert np.isfinite(y).all() and max(abs(y))<1e7
   rec[tag]={'bytes':p.stat().st_size,'prior':q,'sample_sha256':hashlib.sha256(y.tobytes()).hexdigest()};vals.append(Q.T@y)
  ss.append(vals[0]);nn.append(vals[1]);records.append(rec)
  if len(ss)%10==0:print('sample',len(ss),flush=True)
 S,N=np.array(ss),np.array(nn);train=(S+N)[:45];test=(S+N)[45:]
 def cov(T,a):
  C=np.cov(T,rowvar=False);return (1-a)*C+a*np.trace(C)/len(C)*np.eye(len(C))
 def score(X,C,mu):
  v=X-mu;return np.linalg.slogdet(C)[1]+np.einsum('ni,ij,nj->n',v,np.linalg.inv(C),v)
 alphas=np.linspace(0,1,21);cv=[float(np.mean([score(train[i:i+1],cov(np.delete(train,i,axis=0),a),np.delete(train,i,axis=0).mean(0))[0] for i in range(len(train))])) for a in alphas];alpha=float(alphas[np.argmin(cv)])
 C=cov(train,alpha);C0=cov(train,0.);out=[]
 angles=[(0.,0.,0.)]+[(a,b,0.) for a in [0.,np.pi/2,np.pi,3*np.pi/2] for b in [np.pi/6,np.pi/2,5*np.pi/6]]
 for ang in angles:
  Xr,ret=response(ang);F=Xr.T@np.linalg.solve(C,Xr);ev=np.linalg.eigvalsh(F);assert ev[0]>0
  out.append(dict(angles_rad=list(ang),fisher_eigen=ev.tolist(),condition=float(ev[-1]/ev[0]),trace=float(np.trace(F)),template_mask_retention=ret.tolist()))
 np.savez_compressed(D/'ORIENTATION_SCORES.npz',sample_pixel=idx,response_basis=R,signal=S,noise=N,ids=ids,coeff=coeff,covariance=C)
 write('ORIENTATION_INPUTS.json',records)
 obj=dict(mask_sha=acq['mask']['sha256'],beam_sha=acq['beam']['tail_sha256'],train=45,heldout=20,dimension=33,alpha=alpha,loo_scores=cv,train_score_unshrunk=float(score(test,C0,train.mean(0)).mean()),train_score_shrunk=float(score(test,C,train.mean(0)).mean()),orientations=out,scope='fixed finite 13 orientations, official mask/beam, actual 45 training + 20 previously unused heldout Commander MC, finite B subspace and l<=10 E projection, full-sky unit template coefficients, not observed fit or look-elsewhere calibration')
 write('ORIENTATION.json',obj);print(obj,flush=True)
if __name__=='__main__':run()
