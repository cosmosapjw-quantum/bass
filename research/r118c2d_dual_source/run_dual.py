"""Native 70-state source graph, two-moment live reservoirs, BASS mixed
spectrum ingestion. BASS source is a frozen scalar trace of actual accepted
cold-Thomson replay, not a reconstructed blackbody or active chemistry."""
import argparse,pathlib,json,sys,os,hashlib,math,subprocess,time
import numpy as np
from scipy.constants import h,c,k
from scipy.optimize import brentq
from scipy.integrate import solve_ivp
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--lift',type=P,required=True);p.add_argument('--graphs',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--old',type=P,required=True);p.add_argument('--mixed',type=P,required=True);p.add_argument('--only',default='');args=p.parse_args()
root=args.out.resolve();root.mkdir(exist_ok=False,parents=True);exe=args.binary.resolve()
src=np.load(args.lift,allow_pickle=False);bounds=src['bounds'];nu0=float(src['nu0']);dnu=float(src['dnu']);X=bounds.ravel();g=src['g'].ravel();pi=src['pi'].ravel();z=pi/g
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return np.genfromtxt(p,names=True,delimiter='\t')
def line(a):return ' '.join(format(float(v),'.17g') for v in np.ravel(a))+'\n'
def graph(name):
 gp=args.graphs/f'graph_{name}.bin'
 with gp.open('rb') as f:
  assert f.read(8)==b'RECPOS01';n,a,b=np.fromfile(f,dtype='<u4',count=3)
  q=np.fromfile(f,dtype='<f8',count=4*a).reshape(a,4);mp=np.fromfile(f,dtype='<f8',count=3*n).reshape(n,3);blocks=[]
  for _ in range(b):
   i,j=np.fromfile(f,dtype='<u4',count=2)
   W=np.fromfile(f,dtype='<f8',count=a*a).reshape(a,a)
   blocks.append((i,j,W))
  assert not f.read(1)
 assert np.array_equal(mp[:,0],g) and np.array_equal(mp[:,1],pi)
 return gp,q[:,:3],q[:,3],blocks
def mean(k):
 return .5-k/12+k**3/720 if k<1e-3 else 1/k-(1/np.expm1(k) if k<700 else 0)
def split_portion(m0,m1,l,r,a,b,closure):
 N=m0+m1
 if N<=0:return 0.,0.
 s=max(0.,(a-l)/(r-l));t=min(1.,(b-l)/(r-l))
 if t<=s:return 0.,0.
 R=m1/N
 if closure=='compact':
  lo,hi=(0.,2*R) if R<=.5 else (2*R-1,1.)
  s=max(s,lo);t=min(t,hi)
  if t<=s:return 0.,0.
  m=N*(t-s)/(hi-lo);return m,m*(l+(r-l)*(s+t)/2)
 flip=R>.5;y=min(R,1-R)
 if y<=0:return (N,N*(r if R>0 else l)) if s<=R<=t else (0.,0.)
 K=brentq(lambda k:mean(k)-y,0,1/y,xtol=1e-14)
 if flip:s,t=1-t,1-s
 n=N*(t-s) if K<1e-14 else N*np.exp(-K*s)*(-np.expm1(-K*(t-s)))/(-np.expm1(-K))
 tm=s+(t-s)*mean(K*(t-s));tm=1-tm if flip else tm
 return n,n*(l+(r-l)*tm)
def mixed_input(case,closure,d,w):
 path=args.mixed/case
 r=read(path/'frequency_rays.tsv');node=read(path/'frequency_nodes.tsv');diag=read(path/'diagnostics.tsv')[-1]
 n=len(r);u=node['u'].reshape(n,-1);tr=sum(node['n_'+p] for p in ['xx','yy','zz']).reshape(n,-1)
 assert np.all(tr>=0) and n==len(w)
 x=np.exp(u[0]);dx=np.diff(x);a=x[:-1];b=x[1:]
 v0=dx*(3*a*a+2*a*b+b*b)/12;v1=dx*(a*a+2*a*b+3*b*b)/12
 vol=np.r_[v0,0.]+np.r_[0.,v1]
 L=tr[:,:-1]*(v0/vol[:-1]);R=tr[:,1:]*(v1/vol[1:])
 orig_n=tr.sum(axis=1);orig_e=tr@x
 nerr=float(np.max(abs((L+R).sum(axis=1)/orig_n-1)))
 eerr=float(np.max(abs((L*a+R*b).sum(axis=1)/orig_e-1)))
 beta=np.array([diag['host_beta_x'],diag['host_beta_y'],diag['host_beta_z']]);gam=1/np.sqrt(1-beta@beta);en=np.c_[r['e_x'],r['e_y'],r['e_z']];bn=en@beta
 D=gam*(1-bn);db=(en+(((gam-1)*bn/(beta@beta))-gam)[:,None]*beta)/D[:,None]
 wb=r['weight']/(4*np.pi*D**2);wb/=wb.sum()
 assert np.max(abs(d-db))<2e-12 and np.max(abs(w-wb))<2e-12
 # Absolute unit is the R118-C1 z_emit=2800 reference, not the REC
 # fixed 3000 K source bath. The resulting run is a cross-epoch stress.
 T=2.7255*2801.;nu_unit=k*T/h
 f=np.zeros((70,n));counts=[]
 for ray in range(n):
  nu_scale=nu_unit*np.exp(r['log_shift'][ray])*D[ray]
  phase=8*np.pi*nu_scale**3/c**3
  lo=(nu0+dnu*bounds[:,0])/nu_scale;hi=(nu0+dnu*bounds[:,1])/nu_scale
  counts.append(int(np.sum((x[:-1]<max(hi))&(x[1:]>min(lo)))))
  for i in range(35):
   n0=0.;m0=0.
   for j in np.flatnonzero((x[:-1]<hi[i])&(x[1:]>lo[i])):
    q,e=split_portion(L[ray,j],R[ray,j],x[j],x[j+1],lo[i],hi[i],closure)
    n0+=q;m0+=e
   if n0==0:continue
   # Use centered normalized broad-frequency integral: both N and E
   # exactly retained by endpoint projection, with roundoff tolerance.
   rr=(m0/n0-lo[i])/(hi[i]-lo[i])
   assert -2e-10<=rr<=1+2e-10,(rr,i,ray)
   rr=np.clip(rr,0,1)
   f[2*i,ray]=phase*n0*(1-rr)/g[2*i];f[2*i+1,ray]=phase*n0*rr/g[2*i+1]
 md=dict(source_case=case,closure=closure,source_bins=len(x)-1,T_emit_K=T,scalar_number_partition_defect=nerr,scalar_energy_partition_defect=eerr,coarse_cells_covering_line_min=min(counts),coarse_cells_covering_line_max=max(counts),source_files={str(path/n):sha(path/n) for n in ['frequency_rays.tsv','frequency_nodes.tsv','diagnostics.tsv']},max_occupation=float(f.max()),min_occupation=float(f.min()))
 return f,md
def old_input(name,na):
 tok=(args.old/(name+'.txt')).read_text().split()
 assert tok[0]=='rec_positive_case_v1'
 duration=float(tok[1]);steps=int(tok[2]);clock=np.array(tok[3:3+na],float);pos=3+na
 f=np.repeat(np.array(tok[pos:pos+35*na],float).reshape(35,na),2,axis=0);pos+=35*na
 flag=int(tok[pos]);pos+=1;extra=''
 if flag:
  nu_old,dd,ext,extent=map(float,tok[pos:pos+4]);pos+=4
  assert nu_old==nu0 and dd==dnu
  b0=np.array(tok[pos:pos+70],float).reshape(35,2);pos+=70;assert np.array_equal(b0,bounds)
  extra=f'1\n{int(ext)} {extent:.17g}\n'+' '.join(tok[pos:])+'\n'
 else:assert pos==len(tok);extra='0\n'
 return duration,steps,clock,f,extra
old=json.loads((args.old/'RESULTS.json').read_text());cases=[]
for a0 in old['cases']:
 name=a0['case']
 if name.startswith('live_') or name.startswith('time_') or name in ['normal_clock','stress_equilibrium','stress_zero','localized_step_7','localized_step_11','localized_step_17','stress_high','stiff_1']:
  cases.append(dict(case=name,graph='o'+str(a0['order']),old=name,drift=bool(a0['drift'])))
# Actual mixed replay cases and two different realizable cell reconstructions.
for bins in (512,1024,2048):
 for closure in ('exp','compact'):
  cases.append(dict(case=f'mixed_{bins}_{closure}',graph='mixed',mixed=f'early_cold_f{bins}',closure=closure,drift=False))
# Exact discrete detailed-balance null with new endpoint thermal weights.
cases.append(dict(case='lifted_equilibrium',graph='o7',special='eq',drift=False))
results=[]
for ca in cases:
 name=ca['case']
 if not name.startswith(args.only):continue
 try:
  gp,d,w,blocks=graph(ca['graph']);a=len(w);extra='0\n';md=None
  if 'old' in ca:dt,steps,clock,f,extra=old_input(name,a)
  elif 'mixed' in ca:
   f,md=mixed_input(ca['mixed'],ca['closure'],d,w);dt=0.5;steps=2;clock=np.ones(a)
  else:
   zz=.3*z/z.max();f=np.repeat((zz/(1-zz))[:,None],a,axis=1);dt=1e4;steps=2;clock=np.ones(a)
  # Positive graph operator reference, independently assembled from blocks.
  V=g[:,None]*w[None,:]/clock[None,:]
  def rhs(flat):
   f=flat.reshape(70,a);one=1+f;phi=f/(z[:,None]*one)
   ref=np.sum(phi*w[None,:])/70;delta=one*(phi-ref);num=np.zeros_like(f)
   for i,j,W in blocks:
    if i==j:num[i]+=one[i]*(W@delta[i]-(phi[i]-ref)*(W@one[i]))
    else:
     num[i]+=one[i]*(W@delta[j]-(phi[i]-ref)*(W@one[j]))
     num[j]+=one[j]*(W.T@delta[i]-(phi[j]-ref)*(W.T@one[i]))
   return num
  case=root/(name+'.txt');case.write_text(f'rec_dual_source_case_v1\n{dt:.17g} {steps}\n{nu0:.17g} {dnu:.17g}\n'+line(X)+line(clock)+line(f)+extra)
  dest=root/name;cmd=[str(exe),str(gp),str(case),str(dest)]
  proc=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
  if proc.returncode:raise RuntimeError(proc.stderr)
  m=dict(q.split('=',1) for q in (dest/'run.txt').read_text().splitlines())
  for key,val in list(m.items()):
   try:m[key]=float(val)
   except ValueError:pass
  s=read(dest/'state.tsv');hist=read(dest/'history.tsv');obs=s['mass_action'].reshape(70,a);ref=rhs(f.ravel())
  scale=max(float(np.sum(abs(ref))),float(np.sum(f*V))*1e-13,1e-300)
  err=float(np.sum(abs(obs-ref)))/scale
  metric=dict(action_relative=err,action_abs=float(np.max(abs(obs-ref))),initial_mass=float(np.sum(f*V)))
  # Use absolute gross rate scale for a true equilibrium, not division by zero.
  if name in ['lifted_equilibrium','stress_zero']:assert err<1e-3,(name,err)
  else:assert err<1e-8,(name,err)
  assert m['minimum_occupation']>=0 and m['number_defect']<2e-10 and m['centered_balance_defect']<2e-10
  assert max(m['max_drift_number_defect'],m['max_drift_centered_defect'],m['max_core_number_defect'],m['max_exterior_number_defect'],m['max_core_centered_defect'],m['max_exterior_centered_defect'])<2e-12
  if ca['drift']:
   assert min(m[k] for k in ['red_in','red_out','blue_in','blue_out'])>0
   assert m['interface_atom_energy']==0
   sig=abs(m['collision_x'])
   metric.update(core_projection_to_collision=abs(m['core_projection_x'])/max(sig,1e-300),exterior_projection_to_collision=abs(m['exterior_projection_x'])/max(sig,1e-300),absolute_balance_to_collision=m['centered_absolute_defect']/max(sig,1e-300),escape_fraction=float(hist['escape_mass'][-1]/hist['mass'][0]),collision_energy_j_m3=m['collision_energy_j_m3'])
  if name.startswith('time_') or name=='normal_clock':
   # Independent fixed-graph ODE, moderate time only.
   W=np.zeros((70*a,70*a))
   for i,j,K in blocks:
    W[i*a:(i+1)*a,j*a:(j+1)*a]=K;W[j*a:(j+1)*a,i*a:(i+1)*a]=K.T
   zz=np.repeat(z,a);vv=V.ravel()
   def ode(t,x):
    q=x/zz;one=1+x;return (one*(W@q)-q*(W@one))/vv
   r=solve_ivp(ode,(0,dt),f.ravel(),method='DOP853',rtol=2e-12,atol=1e-14)
   assert r.success
   ref_end=r.y[:,-1];metric['ode_signal_l1']=float(np.sum(abs(s['final_f']-ref_end)*vv)/np.sum(abs(ref_end-f.ravel())*vv))
  r=dict(ca,status='PASS_SCOPED',command=cmd,graph_sha256=sha(gp),case_sha256=sha(case),metrics=metric,run=m,mixed_receipt=md,hashes={p.name:sha(p) for p in dest.iterdir()})
 except Exception as e:r=dict(ca,status='FAIL_CHECK',error=repr(e))
 results.append(r);print(name,r['status'],r.get('error',''),flush=True)
(root/'RESULTS.json').write_text(json.dumps(dict(binary_sha256=sha(exe),lift_sha256=sha(args.lift),cases=results),indent=2,allow_nan=False)+'\n')
print('done',len(results),flush=True)
