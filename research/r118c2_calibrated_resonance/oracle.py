"""Independent Faddeeva, Hummer source, semidiscrete FP and Bose validation.
Read actual Rust artifacts. Compare the same finite-volume model separately
from the physical approximation to the original REC scattering kernel."""
import pathlib,sys,json,hashlib,math
import numpy as np
import scipy.linalg as la
from scipy.special import wofz
from scipy.integrate import quad,solve_ivp
from scipy.optimize import root,brentq
import mpmath as mp
from numpy.polynomial.legendre import leggauss
r=pathlib.Path(sys.argv[1]);rec=pathlib.Path(sys.argv[2]);data=json.loads((r/'RESULTS.json').read_text());by={q['case']:q for q in data['cases']}
assert all(x['status']=='PASS_SCOPED' for x in by.values())
def load(n,f):return np.genfromtxt(r/n/f,names=True,delimiter='\t')
def phi(a,x):
 return np.real(wofz(np.asarray(x)+1j*a))
def dip(a,x):
 z=np.asarray(x)+1j*a
 w=wofz(z)
 ans=np.real(w+.35*((4*z*z-2)*w-4j*z/np.sqrt(np.pi)))
 # At very large detuning avoid cancellation in the Faddeeva derivative.
 # Independent adaptive integration of the exact positive moment.
 for i in np.ndindex(z.shape):
  t=float(z[i].real)
  if abs(t)>25:
   ans[i]=quad(lambda y:np.exp(-y*y)*a*(.3+1.4*y*y)/(np.pi*((t-y)**2+a*a)),-12,12,epsabs=1e-18,epsrel=2e-12)[0]
 return ans
def rates(c,g):
 m=c['metrics'];x=g['x'];b=m['doppler_fraction'];v=np.zeros(len(x))
 nodes,weights=leggauss(4)
 for i,(l,h) in enumerate(zip(x,x[1:])):
  t=(1+nodes)/2;vf=(1+b*(l+(h-l)*t))**2;ww=weights*(h-l)/2
  v[i]+=ww@(vf*(1-t));v[i+1]+=ww@(vf*t)
 dx=np.diff(x);mid=(x[1:]+x[:-1])/2
 f=dip(m['voigt_a'],mid) if c['profile']=='dipole' else phi(m['voigt_a'],mid)
 K=m['rate_scale_s']*f/(2*np.sqrt(np.pi))
 C=K*(1+b*mid)**2/dx;d=m['epsilon_doppler']*dx
 a=C*(d/np.expm1(d))/v[:-1];b=C*(-d/np.expm1(-d))/v[1:]
 return v,a,b
profiles=[]
for n,c in by.items():
 m=c['metrics'];g=load(n,'grid.tsv');pr=load(n,'profile.tsv')
 f=phi(m['voigt_a'],pr['x']);di=dip(m['voigt_a'],pr['x'])
 v,a,b=rates(c,g)
 metrics=dict(case=n,voigt_relative=float(np.max(abs(pr['voigt_H']/f-1))),dipole_relative=float(np.max(abs(pr['dipole_H']/di-1))),volume_relative=float(np.max(abs(g['phase_volume']/v-1))))
 if c['p']!=0:
  metrics.update(up_relative=float(np.max(abs(g['up_s'][:-1]/a-1))),down_relative=float(np.max(abs(g['down_s'][:-1]/b-1))))
 profiles.append(metrics)
# Mild full-chain matrix reference, exact exponential for BE convergence.
lin=[]
for model in ('voigt','dipole'):
 for n in (8,16,32,64,128):
  name=f'bench_{model}_t{n}';c=by[name];g=load(name,'grid.tsv');v,a,b=rates(c,g);N=len(v)
  L=np.diag(-np.r_[a,0.]-np.r_[0.,b])+np.diag(a,-1)+np.diag(b,1)
  m0=g['initial_mass'];actual=g['final_mass'];dt=c['metrics']['duration_s']/n
  factor=la.lu_factor(np.eye(N)-dt*L);y=m0.copy()
  for _ in range(n):y=la.lu_solve(factor,y)
  exact=la.expm(L*c['metrics']['duration_s'])@m0
  lin.append(dict(case=name,dense_be_relative_l1=float(np.sum(abs(y-actual))/m0.sum()),continuous_time_relative_l1=float(np.sum(abs(exact-actual))/m0.sum())))
# Very stiff BE matrix: independent 70-digit conventional Thomas
# elimination (including diagonal subtraction in arbitrary precision).
mp.mp.dps=70
stiff=[]
for model in ('voigt','dipole'):
 name=f'bench_{model}_stiff';c=by[name];g=load(name,'grid.tsv');N=len(g)
 # Use exported Rust coefficient bits for this SOLVER check, independent
 # coefficient check was above.
 a=[mp.mpf(float(x))*mp.mpf(c['metrics']['duration_s']) for x in g['up_s'][:-1]]
 b=[mp.mpf(float(x))*mp.mpf(c['metrics']['duration_s']) for x in g['down_s'][:-1]]
 d=[mp.mpf(1)+(a[i] if i<N-1 else 0)+(b[i-1] if i else 0) for i in range(N)]
 rhs=[mp.mpf(float(x)) for x in g['initial_mass']]
 for i in range(1,N):
  m=-a[i-1]/d[i-1];d[i]-=m*(-b[i-1]);rhs[i]-=m*rhs[i-1]
 y=[mp.mpf(0)]*N;y[-1]=rhs[-1]/d[-1]
 for i in range(N-2,-1,-1):y[i]=(rhs[i]+b[i]*y[i+1])/d[i]
 y=np.array([float(x) for x in y]);act=g['final_mass']
 stiff.append(dict(case=name,high_precision_relative_l1=float(np.sum(abs(y-act))),max_dimensionless_rate=float(max(a+b)),mp_decimal_digits=70))
# Bose-stimulated nonlinear independent root and ODE.
bose=[]
for init in ('bose-pulse','bose-high'):
 for n in (1,8,32,128):
  name=f'{init}_{n}';c=by[name];g=load(name,'grid.tsv');v,a,b=rates(c,g);m0=g['initial_mass'];act=g['final_mass'];dt=c['metrics']['duration_s']/n
  def rhs(y):
   f=a*y[:-1]*(1+y[1:]/v[1:])-b*y[1:]*(1+y[:-1]/v[:-1])
   return np.r_[-f,0.]+np.r_[0.,f]
  def jac(y):
   l=a*(1+y[1:]/v[1:])-b*y[1:]/v[:-1]
   r=a*y[:-1]/v[1:]-b*(1+y[:-1]/v[:-1])
   J=np.diag(-np.r_[l,0.]+np.r_[0.,r])+np.diag(l,-1)-np.diag(r,1)
   return J
  y=m0.copy()
  for step in range(n):
   # Newton with analytic Jacobian; the initial finite-difference root
   # failed on the sharply localized, nearly zero occupations.
   z=la.solve(np.eye(len(y))-dt*jac(y),dt*rhs(y))
   sol=root(lambda x:x-y-dt*rhs(x),y+z,jac=lambda x:np.eye(len(y))-dt*jac(x),tol=1e-11)
   assert np.linalg.norm(sol.fun,1)<1e-11*m0.sum(),(name,step,sol.message,np.linalg.norm(sol.fun,1)/m0.sum())
   y=sol.x
  exact=solve_ivp(lambda t,y:rhs(y),(0,c['metrics']['duration_s']),m0,rtol=1e-12,atol=1e-15*m0.sum(),method='DOP853')
  assert exact.success
  bose.append(dict(case=name,nonlinear_root_be_relative_l1=float(np.sum(abs(y-act))/m0.sum()),continuous_time_relative_l1=float(np.sum(abs(exact.y[:,-1]-act))/m0.sum())))
# Physical high-occupation stiff case compare to its fixed-number BE equilibrium,
# not just equilibrium at an arbitrarily assigned chemical potential.
name='bose_high_stiff';c=by[name];g=load(name,'grid.tsv');v=g['phase_volume'];x=g['x'];eps=c['metrics']['epsilon_doppler']*x
n0=g['initial_mass'].sum();mu=brentq(lambda mu:np.sum(v/np.expm1(eps-mu))-n0,eps.min()-100,eps.min()-1e-12)
eq=v/np.expm1(eps-mu)
bose_eq=dict(case=name,relative_l1_to_fixed_number_equilibrium=float(np.sum(abs(eq-g['final_mass']))/n0))
# Existing REC Hummer no-recoil, scalar angular kernel; actual owner data.
# Compare raw source normalization, bin-averaged profile, finite binned
# second jump moment and conditional angular-frequency moments.
f=rec/'data/full_hummer_reference.npz'
z=np.load(f,allow_pickle=False);e=z['x_edges'];x=z['x_centers'];G=z['physical_gain_sInv'];loss=z['within_core_loss_sInv'];scale=float(z['rate_scale_sInv'])
m=by['bench_dipole_t32']['metrics'];a=m['voigt_a']
cell=np.array([quad(lambda x:float(phi(a,x))/np.sqrt(np.pi),l,u,epsabs=1e-13,epsrel=1e-11)[0]/(u-l) for l,u in zip(e,e[1:])])
corr=np.array([quad(lambda x:float(dip(a,x))/np.sqrt(np.pi),l,u,epsabs=1e-13,epsrel=1e-11)[0]/(u-l) for l,u in zip(e,e[1:])])
j=int(np.argmin(abs(x)));g0=G[0,:,j]
central=dict(source_rate_scale_s=scale,new_rate_scale_s=m['rate_scale_s'],rate_relative_gap=abs(m['rate_scale_s']/scale-1),cell_voigt_relative_gap=float(np.max(abs(cell/z['cell_averaged_Voigt_profile']-1))),central_cell=[float(e[j]),float(e[j+1])],retained_fraction=float(g0.sum()/(scale*cell[j])),binned_second_moment=float(g0@((x-x[j])**2)/g0.sum()),voigt_FPA_second_moment=1.,dipole_FPA_cell_averaged_second_moment=float(corr[j]/cell[j]),central_angular_moments=(G[:5,:,j].sum(axis=1)/g0.sum()).tolist(),conditional_l2_factorization_l1=float(np.sum(abs(G[2,:,j]-.1*g0))/g0.sum()),conditional_l1_nonzero_l1=float(np.sum(abs(G[1,:,j]))/g0.sum()),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest())
# Uniform vs localized grid reference at same outer boundary, same BE time.
mesh=[]
for model in ('voigt','dipole'):
 name=f'bench_{model}_stretched_wide2048';ref=load(name,'grid.tsv');mr=ref['final_mass'];xr=ref['x'];ref_mean=float(mr@xr);ref_var=float(mr@(xr-ref_mean)**2)
 for mode in ('uniform','stretched'):
  for n in (128,256,512):
   name=f'bench_{model}_{mode}_wide{n}';g=load(name,'grid.tsv');y=g['final_mass'];x=g['x'];mean=float(y@x);var=float(y@(x-mean)**2)
   mesh.append(dict(case=name,mean=mean,variance=var,mean_abs_error=abs(mean-ref_mean),variance_abs_error=abs(var-ref_var),central_dx=float(x[n//2+1]-x[n//2])))
out=dict(profile=profiles,linear=lin,stiff=stiff,bose=bose,bose_stiff=bose_eq,hummer=central,mesh=mesh)
(r/'ORACLE.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('max profile', {k:max(x.get(k,0) for x in profiles) for k in ('voigt_relative','dipole_relative','volume_relative','up_relative','down_relative')})
print('linear',lin)
print('stiff',stiff)
print('bose',bose,'stiff',bose_eq)
print('Hummer',central)
print('mesh',mesh)
