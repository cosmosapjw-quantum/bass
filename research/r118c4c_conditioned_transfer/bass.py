"""C4C: independently integrate in Schur and physical-control coordinates, exact early clock splits."""
from pathlib import Path
import sys,json,hashlib,numpy as np,time,subprocess,concurrent.futures as cf
from scipy.integrate import solve_ivp
from scipy.linalg import schur
from numpy.polynomial.legendre import leggauss
from itertools import combinations
D=Path(__file__).resolve().parent;P=D.parent;R=D.parents[1];S=P/'r118c3s_radial_envelope';B=P/'r118c4b_temporal_mask';A4=P/'r118c4a_robust_wedge';X=P/'r118c3x_native_coefficients';L=P/'r118c3l_reachable_sky'
sys.path.insert(0,str(S));from envelope import windows,coeff,OG,ON,OM,OL,T0,K0,CLOCK,EARLY
ns={'__file__':str(A4/'bass.py'),'__name__':'prior'};exec(compile((A4/'bass.py').read_text(),ns['__file__'],'exec'),ns)
P1=ns['P1'].astype(np.longdouble);P3=ns['P3'].astype(np.longdouble);vec=ns['vec'];wedge=ns['wedge']
def write(n,v):(D/n).write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
Z=np.load(B/'REFINED_CONTROLS.npz');H=Z['H'];A=Z['A'][list(Z['labels']).index('refit_intermediate')];control=A@H
old=json.loads((B/'M_256_3072.json').read_text());Q=H@np.linalg.inv(np.array(old['H']));M0=Q@np.array(old['M'])@Q.T;M0=(M0-M0.T)/2;_,U=schur(M0,output='real')
def integrate(mode,nr,stride):
 t0=time.monotonic();e=np.genfromtxt(EARLY,names=True,delimiter=',');l=np.genfromtxt(CLOCK,names=True,delimiter=',');a0=e['a'][0];cut=np.log(1/(21*a0));end=np.log(.2/a0);y,w=leggauss(nr);y=30*(1+y);w=30*w;f=1/(1+np.exp(y));V=windows(y,2);masses=[.001,.006,.05];fac=ON/(w@(y**3*f))/3;cold=OM+ON-fac*sum(coeff(y,w,m,1.)[0] for m in masses)
 T={'original':np.eye(7),'schur':U,'physical':A.T}[mode];HH=H@T;n=T.shape[1];i,j=np.array(list(combinations(range(n),2))).T
 ic=np.zeros(4*n+len(i));ic[:n]=HH[0]
 # Exact clock interpolation; analytic radial quadrature evaluated at each RHS.
 def rhs(t,z,early):
  a=a0*np.exp(t);rr=np.array([coeff(y,w,m,a) for m in masses]);rho,pt,J,G0=rr.T
  Am=np.array([V@(2/15*w*y**5*f*(1-f)/np.hypot(y,a*m/T0)) for m in masses])
  h2=(cold*a+OG+fac*rho.sum())/a**4+OL;q=(cold*a+2*OG+fac*(rho+pt).sum())/(2*h2*a**4)-OL/h2
  ne=np.interp(t,e['u'],e['ne_m3']) if early else np.interp(t-cut,l['u'],l['ne_m3']);k=K0*ne/np.sqrt(h2)
  s,b,I,P=z[:4*n].reshape(4,n);stress=(fac*(np.r_[0.,Am.ravel()]@HH-G0.sum()*b)+(2/15)*OG*I)/a**4
  return np.r_[(q-2)*s+3*stress/h2,s,-4*s-k*(.9*I+.4*P),-k*(.15*I+.4*P),s[i]*P[j]-s[j]*P[i]-k*z[4*n:]]
 segments=[np.unique(np.r_[0,e['u'][(e['u']>0)&(e['u']<cut)],cut]),np.unique(np.r_[cut,cut+l['u'][::stride][(l['u'][::stride]>0)&(l['u'][::stride]<end-cut)],end])]
 z=ic;count=0;nf=0
 for k,ts in enumerate(segments):
  for a,b in zip(ts[:-1],ts[1:]):
   o=solve_ivp(lambda t,z:rhs(t,z,k==0),(a,b),z,method='DOP853',rtol=3e-14,atol=np.r_[np.full(4*n,1e-17),np.full(len(i),1e-27)])
   assert o.success;z=o.y[:,-1];count+=1;nf+=o.nfev
 M=np.zeros((n,n));M[i,j]=z[4*n:];M[j,i]=-z[4*n:]
 tag=f'{mode}_{nr}_{stride}';np.savez_compressed(D/(tag+'.npz'),M=M,T=T,z=z)
 row=dict(mode=mode,nr=nr,stride=stride,segments=count,nfev=nf,seconds=time.monotonic()-t0,sv=np.linalg.svd(M,compute_uv=False).tolist(),rtol=3e-14,atol_wedge=1e-27,early_exact_knots=True,late_grouped_knots=True)
 write(tag+'.json',row);print(row,flush=True)
def analyze():
 base=np.load(D/'original_192_64.npz')['M'];s=np.load(D/'schur_192_64.npz');direct=np.load(D/'physical_192_64.npz')['M'];fine=np.load(D/'physical_256_32.npz')['M'];target=P1@wedge(Z['A'][list(Z['labels']).index('baseline')],np.array(json.loads((S/'RADIAL_FINE.json').read_text())['M']));norm=float(np.linalg.norm(target))
 Msch=U.astype(np.longdouble)@s['M'].astype(np.longdouble)@U.T.astype(np.longdouble)
 vals={'prior_post':wedge(A,M0),'segmented_original_post':wedge(A,base),'segmented_schur_post':wedge(A,Msch),'segmented_physical_direct':vec(direct).astype(np.longdouble),'segmented_physical_fine':vec(fine).astype(np.longdouble)}
 out=dict(target_norm=norm,schur_matrix_rel=float(np.linalg.norm(Msch-base)/np.linalg.norm(base)),direct_vs_original_relative_to_target=float(np.linalg.norm(vals['segmented_physical_direct']-vals['segmented_original_post'])/norm),direct_vs_schur_relative_to_target=float(np.linalg.norm(vals['segmented_physical_direct']-vals['segmented_schur_post'])/norm),direct_refinement_relative_to_target=float(np.linalg.norm(vals['segmented_physical_direct']-vals['segmented_physical_fine'])/norm),controls_sha256=sha(B/'REFINED_CONTROLS.npz'),clock_sha256=[sha(EARLY),sha(CLOCK)],results={k:dict(spin3_relative=float(np.linalg.norm(P3@w)/norm),spin1_relative=float(np.linalg.norm(P1@w-target)/norm),wedge=np.asarray(w,float).tolist()) for k,w in vals.items()},scope='binary64 DOP853 with componentwise tight tolerance and coordinate-transform test, extended precision postcontraction; not arbitrary precision nor exact continuum')
 write('TRANSFER.json',out);print(out,flush=True)
def native():
 binary=R/'_rustcore/target/release/examples/c3x_radial';want=json.loads((X/'ops/BUILD_ID.json').read_text())['binary']['sha256'];assert sha(binary)==want
 def job(e):
  tag=f'native_{e:g}';np.savetxt(D/(tag+'.ctrl'),np.r_[[.001,.006,.05],(e*control.T).ravel()][None],fmt='%.17e')
  t=time.monotonic()
  with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.geom')).open('w') as g:r=subprocess.run([str(binary),str(L/'clock.csv'),str(D/(tag+'.ctrl')),'4096','192','8','8'],stdout=f,stderr=g,timeout=200)
  assert r.returncode==0 and 'max_gauss=' in (D/(tag+'.geom')).read_text();return dict(e=e,exit=r.returncode,seconds=time.monotonic()-t)
 with cf.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(job,[-.01,.01,-.02,.02,-.04,.04]))
 def read(p):
  a=np.genfromtxt(p,names=True,delimiter=',');m=(a['epoch']==1)&(a['ell']==3);return a['Bre'][m]+1j*a['Bim'][m]
 zp=P/'r118c3y_signed_coefficients/base_0_4096_192_8.csv'
 if not zp.exists():zp=P/'r118c3w_harmonic_collision/base_0_4096_192_8.csv'
 z=read(zp);results={};eps=np.array([.01,.02,.04]);r=eps**2;V=np.vander(r,3,increasing=True);W=np.linalg.inv(V)[0]
 for k in ['candidate','baseline']:
  pairs=[]
  for e in eps:
   def path(v):
    if k=='candidate':return D/f'native_{v:g}.csv'
    for p in [X,P/'r118c3w_harmonic_collision',P/'r118c3y_signed_coefficients']:
     a=p/f'best_{v:g}_4096_192_8.csv'
     if a.exists():return a
    raise FileNotFoundError(str(v))
   p,m=read(path(e)),read(path(-e));pairs.append((p+m-2*z)/(2*e**2))
  Y=np.array(pairs);fit=np.linalg.solve(V,Y);two=(4*Y[0]-Y[1])/3
  results[k]=dict(even_norm=np.linalg.norm(Y,axis=1).tolist(),B2_three_amp=float(np.linalg.norm(fit[0])),B2_two_small_amp=float(np.linalg.norm(two)),B4=float(np.linalg.norm(fit[1])),B6=float(np.linalg.norm(fit[2])),two_vs_three=float(np.linalg.norm(fit[0]-two)),B2_re=fit[0].real.tolist(),B2_im=fit[0].imag.tolist())
 write('NATIVE.json',dict(rows=rows,weights=W.tolist(),binary_sha=want,results=results,scope='three-amplitude even coefficient extrapolation with B8+ remainder; shared finite native grid and zero'))
 print(results,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='integrate':integrate(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]))
 elif sys.argv[1]=='analyze':analyze()
 else:native()
