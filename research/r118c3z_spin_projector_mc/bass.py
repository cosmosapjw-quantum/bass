"""C3Z: exact commutator projector, native bandlimit, actual Commander MC compressed scores."""
from pathlib import Path
import numpy as np,json,hashlib,subprocess,concurrent.futures as cf,sys,time
from itertools import combinations
D=Path(__file__).resolve().parent;P=D.parent;Y=P/'r118c3y_signed_coefficients';X=P/'r118c3x_native_coefficients';W=P/'r118c3w_harmonic_collision';U=P/'r118c3u_exact_wedge';L=P/'r118c3l_reachable_sky';BROOT=D.parents[1]
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def projector():
 from scipy.linalg import null_space
 B=np.zeros((5,3,3));B[0]=np.diag([1,-1,0])/np.sqrt(2);B[1]=np.diag([-1,-1,2])/np.sqrt(6)
 for k,(i,j) in enumerate([(0,1),(0,2),(1,2)],2):B[k,i,j]=B[k,j,i]=1/np.sqrt(2)
 pairs=np.array(list(combinations(range(5),2)));ii,jj=pairs.T
 C=np.stack([(B[i]@B[j]-B[j]@B[i])[[0,0,1],[1,2,2]] for i,j in pairs],axis=1)
 P3=np.eye(10)-C.T@np.linalg.solve(C@C.T,C);prior=json.loads((P/'r118c3c_memory_kernel/WEDGE.json').read_text())
 assert np.array_equal(pairs,prior['pairs'])
 delta=np.linalg.norm(P3-2*np.array(prior['gram']));assert delta<1e-12
 z=np.load(U/'best_selected_4096.npz');A=z['A'];c=z['control'];R=json.loads((P/'r118c3s_radial_envelope/RADIAL_FINE.json').read_text());M=np.array(R['M']);H=np.array(R['H'])
 assert np.linalg.norm(A@H-c)/np.linalg.norm(c)<1e-10
 vec=lambda w:w[ii,jj]
 # Extended precision for near-cancelled wedge.
 av=A.astype(np.longdouble);mv=M.astype(np.longdouble);ww=av@mv@av.T;v=vec(ww);w3=P3.astype(np.longdouble)@v
 J=np.column_stack([P3@vec(E@M@A.T+A@M@E.T) for E in np.eye(A.size).reshape(A.size,*A.shape)])
 s=np.linalg.svd(J,compute_uv=False);rng=np.random.default_rng(27);E=rng.normal(size=A.shape);E/=np.linalg.norm(E)
 fd=[]
 for eps in [1e-3,1e-5,1e-7]:
  ee=E.astype(np.longdouble);p=vec((av+eps*ee)@mv@(av+eps*ee).T);m=vec((av-eps*ee)@mv@(av-eps*ee).T)
  e=np.linalg.norm(P3.astype(np.longdouble)@(p-m)/(2*eps)-J@E.ravel())/np.linalg.norm(J@E.ravel());fd.append(float(e))
 out=dict(rank=int(np.linalg.matrix_rank(P3,tol=1e-12)),commutator_gram=(C@C.T).tolist(),previous_projector_difference=float(delta),wedge_norm=float(np.linalg.norm(v)),spin3_norm=float(np.linalg.norm(w3)),spin3_fraction=float(np.linalg.norm(w3)/np.linalg.norm(v)),jacobian_sv=s.tolist(),sensitivity_relative=float(s[0]*np.linalg.norm(A)/np.linalg.norm(v)),FD_relative=fd,scope='exact spin decomposition; numerical selected control, not exact native null')
 write('PROJECTOR.json',out);print(out,flush=True)
def native():
 bin=BROOT/'_rustcore/target/release/examples/c3x_radial';ident=json.loads((X/'ops/BUILD_ID.json').read_text())
 assert sha(bin)==ident['binary']['sha256']
 ctrl=np.load(U/'best_selected_4096.npz')['control']
 def job(j):
  e,nt=j;tag='base' if e==0 else 'best';nm=f'{tag}_{e:g}_{nt}_192_8_l10';c=np.r_[[.001,.006,.05],(e*ctrl.T).ravel()]
  np.savetxt(D/(nm+'.ctrl'),c[None],fmt='%.17e');t=time.monotonic()
  try:
   with (D/(nm+'.csv')).open('w') as f,(D/(nm+'.geom')).open('w') as g:q=subprocess.run([str(bin),str(L/'clock.csv'),str(D/(nm+'.ctrl')),str(nt),'192','8','10'],stdout=f,stderr=g,timeout=240)
   return dict(case=nm,exit=q.returncode,complete='max_gauss=' in (D/(nm+'.geom')).read_text(),seconds=time.monotonic()-t)
  except Exception as e:return dict(case=nm,error=repr(e))
 jobs=[(0.,4096),(0.,8192),(-.04,8192),(.04,8192)]
 with cf.ThreadPoolExecutor(max_workers=2) as ex:
  rows=[]
  for r in ex.map(job,jobs):rows.append(r);print(r,flush=True);write('NATIVE_RUNS.json',dict(binary_sha=sha(bin),rows=rows))
 def read(e,nt,l):
  tag='base' if e==0 else 'best';nm=f'{tag}_{e:g}_{nt}_192_8'+('_l10' if l==10 else '')
  for p in [D,Y,X,W]:
   q=p/(nm+'.csv');g=p/(nm+'.geom')
   if q.exists() and g.exists() and 'max_gauss=' in g.read_text():
    x=np.genfromtxt(q,names=True,delimiter=',');assert len(x)==2*(l+1)**2
    m=(x['epoch']==1)&np.isin(x['ell'],[3,5,7]);return x['Bre'][m]+1j*x['Bim'][m]
  raise FileNotFoundError(nm)
 vals={};norm=lambda v:{str(l):float(np.linalg.norm(v[i:j])) for l,i,j in [(3,0,7),(5,7,18),(7,18,33)]}
 arrays={}
 for nt in [4096,8192]:
  try:
   for l in [8,10]:
    z=read(0,nt,l);p=read(.04,nt,l);m=read(-.04,nt,l)
    # Normalize odd by eps and even by eps^2; no assumption B1 exactly zero.
    a=(p+m-2*z)/(2*.04**2);b=(p-m)/(2*.04);arrays[nt,l]=(a,b)
    vals[f'{nt}_l{l}']=dict(zero=norm(z),even=norm(a),odd=norm(b))
   a,b=arrays[nt,8];c,d=arrays[nt,10]
   vals[f'{nt}_bandlimit']=dict(even_abs=norm(c-a),odd_abs=norm(d-b),even_rel=float(np.linalg.norm(c-a)/np.linalg.norm(c)),odd_rel=float(np.linalg.norm(d-b)/np.linalg.norm(d)))
  except (FileNotFoundError,AssertionError) as e:vals[str(nt)+'_blocked']=repr(e)
 if all((n,l) in arrays for n in [4096,8192] for l in [8,10]):
  for l in [8,10]:
   a,b=arrays[4096,l];c,d=arrays[8192,l];vals[f'time_l{l}']=dict(even_abs=norm(c-a),odd_abs=norm(d-b))
 write('BANDLIMIT.json',dict(results=vals,scope='same amplitude/control at two time grids, zero measured, fixed radial/angular; not full seven-order fit'))
 print(vals,flush=True)
def mc():
 import healpy as hp
 from astropy.io import fits
 from scipy.special import sph_harm_y
 from scipy.linalg import qr
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
 # Convention check vs healpy alm2map_spin at exact test pixel centers.
 t,p=hp.pix2ang(8,np.arange(hp.nside2npix(8)));Z=spin(t,p,4)
 rng=np.random.default_rng(20261127);c=np.zeros(21,complex);alm=np.zeros(hp.Alm.getsize(4),complex)
 for l in range(2,5):
  for m in range(0,l+1):
   v=rng.normal()+1j*(rng.normal() if m else 0.);alm[hp.Alm.getidx(4,l,m)]=v;c[l*l-4+l+m]=v;c[l*l-4+l-m]=(-1)**m*v.conjugate()
 q,u=hp.alm2map_spin([np.zeros_like(alm),alm],8,2,lmax=4);ref=q+1j*u;ours=-1j*Z@c
 conv_err=float(np.linalg.norm(ref-ours)/np.linalg.norm(ref));assert conv_err<1e-10,conv_err
 # Actual raw RING pixel centres, deterministic sparse sample, analytic high-latitude cut.
 t,p=hp.pix2ang(16,np.arange(hp.nside2npix(16)));keep=abs(np.pi/2-t)>=np.deg2rad(20);idx=hp.ang2pix(2048,t[keep],p[keep]);assert len(np.unique(idx))==len(idx)
 idx=np.sort(idx);theta,phi=hp.pix2ang(2048,idx);Z=spin(theta,phi,10);E=real(realbasis(Z,10,-1));Qe,_=np.linalg.qr(E,mode='reduced')
 # B native normalized brightness template directions, fixed Galactic orientation, unit beam.
 cols=[]
 for tag in ['whole','late','generic']:
  r=[np.genfromtxt(L/f'{tag}_8192_{s}.csv',names=True,delimiter=',') for s in [1,-1]]
  z=[]
  for row in r:
   a=np.zeros(Z.shape[1],complex)
   for l in [3,5,7]:
    m=(row['epoch']==1)&(row['ell']==l);a[l*l-4:(l+1)**2-4]=row['Bre'][m]+1j*row['Bim'][m]
   z.append(a)
  cols.extend([(z[0]+z[1])/(2*.0025**2),(z[0]-z[1])/(2*.0025**3)])
 X=real(-1j*Z@np.array(cols).T);X/=np.linalg.norm(X,axis=0);Xp=X-Qe@(Qe.T@X)
 Q,R=np.linalg.qr(Xp,mode='reduced');assert np.linalg.matrix_rank(R)==6;assert np.linalg.norm(Q.T@Qe)<1e-10
 root=Path.home()/'Downloads/htt_r105_commander';raw=root/'raw_pairs';met=root/'rereduce_0_29'
 def sample(path):
  with fits.open(path,memmap=True) as hh:
   t=hh[1];h=t.header
   assert h['NSIDE']==2048 and h['ORDERING'].strip()=='RING' and h['TUNIT2'].strip()=='K_CMB'
   assert h.get('POLCCONV','COSMO').strip().upper()=='COSMO'
   values=[]
   for j in [1,2]:
    a=t.data.field(j);k=a.shape[-1] if a.ndim==2 else 1
    z=a[idx//k,idx%k] if a.ndim==2 else a[idx];values.append(np.array(z,dtype=float))
   vals=np.concatenate(values)*1e6;assert np.isfinite(vals).all() and max(abs(vals))<1e7
   return vals,dict(bytes=path.stat().st_size,header={k:h.get(k) for k in ['NSIDE','ORDERING','COORDSYS','POLCCONV','TUNIT2']},sample_sha=hashlib.sha256(vals.tobytes()).hexdigest())
 A=[];N=[];ids=[];records=[]
 for i in range(30):
  try:
   v=[];rec=dict(id=i)
   prior=json.loads((met/f'commander_{i:05d}.json').read_text())
   for tag in ['cmb','noise']:
    p=raw/f'dx12_v3_commander_{tag}_mc_{i:05d}_raw.fits';y,meta=sample(p);meta['prior_reduction_identity']=prior['input_sha256_and_bytes'].get(f'{tag}_{i:05d}');assert meta['bytes']==meta['prior_reduction_identity']['bytes'];rec[tag]=meta;v.append(Q.T@y)
   A.append(v[0]);N.append(v[1]);ids.append(i);records.append(rec)
  except (FileNotFoundError,AssertionError,KeyError,ValueError) as e:records.append(dict(id=i,error=repr(e)))
  if i%5==4:print('MC sample',i,len(ids),flush=True)
 A,N=np.array(A),np.array(N);assert len(A)>=16,(len(A),records)
 def cov(a):return np.cov(a,rowvar=False,ddof=1)
 def fisher(a):
  C=cov(a);ev=np.linalg.eigvalsh(C);assert ev[0]>0;F=R.T@np.linalg.solve(C,R);v=np.linalg.eigvalsh(F);return dict(cov_eigen_uK2=ev.tolist(),fisher_eigen_per_unit_template_uK2=v.tolist(),condition=float(v[-1]/v[0]))
 out=dict(n_pairs=len(A),ids=ids,n_sample_pixels=len(idx),healpy_spin_convention_error=conv_err,projected_norms=np.linalg.norm(Xp,axis=0).tolist(),E_nuisance_rank=int(np.linalg.matrix_rank(E)),noise=fisher(N),signal=fisher(A),paired=fisher(A+N),first_half=fisher((A+N)[:len(A)//2]),last_half=fisher((A+N)[len(A)//2:]),scope='actual Commander FFP10 sample covariance, sparse nearest-centre Galactic |b|>=20deg analytic mask (not official common mask), unit beam, fixed orientation, low-l E nuisance projected; normalized template amplitude only, no observed-sky fit or official likelihood. Raw full file hash inherited from earlier reduction, sample bytes freshly hashed.')
 write('COMMANDER_MC.json',out);write('COMMANDER_INPUTS.json',records);np.savez_compressed(D/'COMMANDER_SCORES.npz',sample_pixel=idx,signal=A,noise=N,response=R)
 print(out,flush=True)
if __name__=='__main__':{'projector':projector,'native':native,'mc':mc}[sys.argv[1]]()

