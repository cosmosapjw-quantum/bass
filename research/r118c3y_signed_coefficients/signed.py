"""C3Y: signed vector extraction, actual native zero and additional fine pair; no fitted norm."""
from pathlib import Path
import numpy as np, json, subprocess, hashlib, concurrent.futures as cf, sys, time
D=Path(__file__).resolve().parent
X=D.parent/'r118c3x_native_coefficients';W=D.parent/'r118c3w_harmonic_collision';P=D.parent/'r118c3u_exact_wedge';L=D.parent/'r118c3l_reachable_sky'
BIN=Path.home()/'worktrees/bass-r109-native-20261124/_rustcore/target/release/examples/c3w_radial'
def native(job):
 tag,e,nt,nr,nm=job;name=f'{tag}_{e:g}_{nt}_{nr}_{nm}'
 C=np.load(P/f'{tag}_selected_4096.npz')['control']
 np.savetxt(D/(name+'.ctrl'),np.r_[[.001,.006,.05],(e*C.T).ravel()][None],fmt='%.17e')
 st=time.monotonic()
 with (D/(name+'.csv')).open('w') as f,(D/(name+'.geom')).open('w') as g:
  q=subprocess.run([str(BIN),str(L/'clock.csv'),str(D/(name+'.ctrl')),str(nt),str(nr),str(nm)],stdout=f,stderr=g,timeout=240)
 assert q.returncode==0 and 'max_gauss=' in (D/(name+'.geom')).read_text()
 return dict(case=name,seconds=time.monotonic()-st,returncode=q.returncode)
def read(tag,e,n,nr=192,nm=8,l=8):
 name=f'{tag}_{e:g}_{n}_{nr}_{nm}'+('' if l==8 else f'_l{l}')
 for p in [D,X,W]:
  f=p/(name+'.csv');g=p/(name+'.geom')
  if f.exists() and g.exists() and 'max_gauss=' in g.read_text():
   x=np.genfromtxt(f,names=True,delimiter=',');assert len(x)==2*(l+1)**2
   m=(x['epoch']==1)&np.isin(x['ell'],[3,5,7]);z=x['Bre'][m]+1j*x['Bim'][m]
   assert len(z)==33 and np.isfinite(z).all()
   return z
 raise FileNotFoundError(name)
def pair(e,n,nr=192,nm=8,l=8):
 p=read('best',e,n,nr,nm,l);m=read('best',-e,n,nr,nm,l);z=read('base',0,n,nr,nm,l)
 return (p+m-2*z)/(2*e*e),(p-m)/(2*e)
def fit(n,es):
 Y=np.array([pair(e,n) for e in es]);t=np.array(es)**2;scale=t.max();A=np.vander(t/scale,3,increasing=True);Q=np.vander(t/scale,4,increasing=True)
 even=np.linalg.lstsq(A,Y[:,0],rcond=None)[0]/scale**np.arange(3)[:,None]
 if len(es)<4:raise ValueError('four amplitudes required for B1/B7')
 odd=np.linalg.lstsq(Q,Y[:,1],rcond=None)[0]/scale**np.arange(4)[:,None]
 co=np.stack([even[0],odd[0],odd[1],even[1],odd[2],even[2],odd[3]]) # B2, B1, B3..B7
 constrained=np.linalg.lstsq(A,Y[:,1]/t[:,None],rcond=None)[0]/scale**np.arange(3)[:,None]
 pred=np.stack([A@(even*scale**np.arange(3)[:,None]),Q@(odd*scale**np.arange(4)[:,None])],axis=1)
 return co,dict(condition_even=float(np.linalg.cond(A)),condition_odd=float(np.linalg.cond(Q)),residual_relative=float(np.linalg.norm(Y-pred)/np.linalg.norm(Y)),constrained_odd_relative=float(np.linalg.norm(odd[1:]-constrained)/np.linalg.norm(constrained)),B1_norm=float(np.linalg.norm(odd[0])))
def stat(z):
 return {str(l):np.linalg.norm(z[...,i:j],axis=-1).tolist() for l,i,j in [(3,0,7),(5,7,18),(7,18,33)]}
def independent():
 # Native actual 3 distinct control histories, no synthetic noise. Inspect the physical template span and its conditioning.
 out={}
 for n in [4096,8192]:
  cols=[]
  for tag in ['whole','late','generic']:
   vals=[]
   for sign in [1,-1]:
    x=np.genfromtxt(L/f'{tag}_{n}_{sign}.csv',names=True,delimiter=',');m=(x['epoch']==1)&np.isin(x['ell'],[3,5,7]);vals.append(x['Bre'][m]+1j*x['Bim'][m])
   for v in [(vals[0]+vals[1])/(2*.0025**2),(vals[0]-vals[1])/(2*.0025**3)]:cols.append(v)
  X0=np.array(cols).T;assert np.isfinite(X0).all()
  colnorm=np.linalg.norm(X0,axis=0);assert min(colnorm)>0
  X0=X0/colnorm;blocks={}
  for label,i,j in [('l3',0,7),('l5',7,18),('l7',18,33),('joint',0,33)]:
   a=np.r_[X0[i:j].real,X0[i:j].imag];s=np.linalg.svd(a,compute_uv=False);blocks[label]=dict(singular=s.tolist(),rank_1e_8=int(sum(s>1e-8*s[0])),smallest_over_largest=float(s[-1]/s[0]))
  out[str(n)]=dict(blocks=blocks,column_norms=colnorm.tolist())
 return out
def main():
 ident=json.loads((W/'ops/BUILD_ID.json').read_text());sha=hashlib.sha256(BIN.read_bytes()).hexdigest();assert sha==ident['binary']['sha256']
 jobs=[('base',0.,8192,192,8),('best',-.03,8192,192,8),('best',.03,8192,192,8),('base',0.,4096,256,8),('base',0.,4096,192,12)]
 # Extra fine time axis at one amplitude, actual zero; separate from polynomial coefficient inference.
 jobs += [('base',0.,16384,192,8),('best',-.04,16384,192,8),('best',.04,16384,192,8)]
 out=dict(binary_sha=sha,jobs=[],failures=[])
 # Store quick independent result first.
 (D/'REACHABILITY.json').write_text(json.dumps(independent(),indent=2)+'\n')
 with cf.ThreadPoolExecutor(max_workers=2) as ex:
  fs={ex.submit(native,j):j for j in jobs}
  for f in cf.as_completed(fs):
   try:r=f.result();out['jobs'].append(r);print(r,flush=True)
   except Exception as e:out['failures'].append(dict(job=fs[f],error=repr(e)));print(out['failures'][-1],flush=True)
   (D/'NATIVE_RUNS.json').write_text(json.dumps(out,indent=2)+'\n')
 rows={};co={}
 for n in [4096,8192]:
  try:
   c,v=fit(n,[.02,.03,.04,.06]);co[n]=c;rows[str(n)]=dict(metrics=v,norms=stat(c),zero=stat(read('base',0,n)))
  except (FileNotFoundError,ValueError) as e:rows[str(n)]=dict(blocked=repr(e))
 if 4096 in co:
  try:
   c,v=fit(4096,[.01,.02,.03,.04,.06]);rows['4096_window']=dict(metrics=v,relative_change=(np.linalg.norm(c-co[4096],axis=1)/np.maximum(np.linalg.norm(co[4096],axis=1),1e-300)).tolist(),norms=stat(c))
  except FileNotFoundError as e:rows['4096_window']=dict(blocked=repr(e))
 if len(co)==2:
  c=(4*co[8192]-co[4096])/3;rows['Richardson']=dict(norms=stat(c),coefficient_order=[2,1,3,4,5,6,7],time_difference_norm=stat(co[8192]-co[4096]))
  np.savez_compressed(D/'SIGNED_COEFFICIENTS.npz',n4096=co[4096],n8192=co[8192],rich=c)
 axes={}
 for nr,nm in [(256,8),(192,12)]:
  try:
   a=np.array(pair(.04,4096,nr,nm));b=np.array(pair(.04,4096));axes[f'{nr}_{nm}']=dict(abs_difference=stat(a-b),norms=stat(a),zero=stat(read('base',0,4096,nr,nm)))
  except FileNotFoundError as e:axes[f'{nr}_{nm}']=dict(blocked=repr(e))
 timeaxis={}
 try:
  a,b,c=[np.array(pair(.04,n)) for n in [4096,8192,16384]]
  timeaxis=dict(diff_4096_8192=stat(a-b),diff_8192_16384=stat(b-c),ratio=np.divide(np.linalg.norm(a-b,axis=1),np.maximum(np.linalg.norm(b-c,axis=1),1e-300)).tolist(),zero=stat(read('base',0,16384)))
 except FileNotFoundError as e:timeaxis=dict(blocked=repr(e))
 result=dict(fits=rows,independent_axes=axes,time_axis=timeaxis,scope='actual native vectors; signed amplitude extrapolation only; B2 exact null unresolved; no observed covariance')
 (D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()

