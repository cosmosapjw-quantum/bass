"""Execute the native positive graph and independent dense/block action,
DOP853 oracle, harmonic comparison, and actual local two-way reservoirs."""
import argparse,pathlib,json,sys,os,hashlib,math,subprocess,time,concurrent.futures
import numpy as np
from scipy.integrate import lebedev_rule,solve_ivp
from scipy.constants import h,c,k as k_B
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--rec',type=P,required=True);p.add_argument('--graphs',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--only',default='')
args=p.parse_args();rec=args.rec.resolve();root=args.out.resolve();root.mkdir(exist_ok=False,parents=True);exe=args.binary.resolve()
sys.path.insert(0,str(rec/'src'))
from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid,apply_nonlinear_bose_operator
net=CollisionNetwork.from_npz(rec/'data/full_scalar_com_khw_v050.npz')
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return np.genfromtxt(p,names=True,delimiter='\t')
def numbers(a):return ' '.join(format(float(v),'.17g') for v in np.ravel(a))+'\n'
def graph(path):
 with path.open('rb') as f:
  assert f.read(8)==b'RECPOS01';n,a,b=np.fromfile(f,dtype='<u4',count=3)
  d=np.fromfile(f,dtype='<f8',count=4*a).reshape(a,4);mp=np.fromfile(f,dtype='<f8',count=3*n).reshape(n,3);blocks=[]
  for _ in range(b):
   i,j=np.fromfile(f,dtype='<u4',count=2)
   W=np.fromfile(f,dtype='<f8',count=a*a).reshape(a,a)
   blocks.append((i,j,W))
  assert not f.read(1)
 assert np.array_equal(mp[:,0],net.mode_measure) and np.array_equal(mp[:,1],net.equilibrium_weight) and np.array_equal(mp[:,2],net.momentum_scale)
 return d[:,:3],d[:,3],mp,blocks
def make(order,init,duration,steps,clock='material',drift=None,label=None):
 name=label or f'o{order}_{init}_t{steps}_{clock}'
 return dict(case=name,order=order,init=init,duration=duration,steps=steps,clock=clock,drift=drift)
cases=[]
# Native time convergence and high/low occupation; zero floor adversaries
# are no longer forced into strictly positive log variables.
for n in [1,2,4,8,16,32]:
 cases.append(make(7,'smooth',2.,n,label=f'time_{n}'))
for order in (7,11,17,29):
 cases.append(make(order,'smooth',0.,0,label=f'angular_{order}'))
 cases.append(make(order,'localized',0.,0,label=f'localized_action_{order}'))
 if order<29:
  cases.append(make(order,'localized',0.4,2,label=f'localized_step_{order}'))
for init in ('low','high','equilibrium','isotropic','zero'):
 cases.append(make(7,init,2.,4,label='stress_'+init))
cases.append(make(7,'smooth',1e4,1,label='stiff_1'))
cases.append(make(7,'smooth',2.,8,'normal',label='normal_clock'))
for n in (8,16,32):
 cases.append(make(7,'low',2.,n,drift=dict(ext=8,extent=80.,amplitude=1e-4),label=f'live_time_{n}'))
for ext in (2,4,16):
 cases.append(make(7,'low',2.,16,drift=dict(ext=ext,extent=80.,amplitude=1e-4),label=f'live_extent80_ext{ext}'))
cases.append(make(7,'low',2.,16,drift=dict(ext=8,extent=40.,amplitude=1e-4),label='live_narrow'))
cases.append(make(7,'low',2.,16,drift=dict(ext=8,extent=120.,amplitude=1e-4),label='live_wide'))
# One larger-angle live run demonstrates angular sign reversal without
# claiming accuracy of the outer reservoir closure.
cases.append(make(11,'low',2.,8,drift=dict(ext=8,extent=80.,amplitude=1e-4),label='live_ang50'))
def init_state(init,d):
 z=net.activity_weight;na=len(d);x=net.centers[:,None]
 amp={'smooth':.5,'low':1e-17,'high':5.,'equilibrium':.5,'isotropic':.5,'localized':.5,'zero':0.}[init]
 zz=amp/(1+amp)*z/z.max()
 eq=zz/(1-zz)
 f=np.repeat(eq[:,None],na,axis=1)
 if init in ('smooth','low','high'):
  f*=1+.13*np.sin(x/2)*d[None,:,2]+.08*(3*d[None,:,0]**2-1)+.05*np.cos(x/3)
 if init=='isotropic':f*=1+.1*np.sin(x/2)
 if init=='localized':
  f[:]=0.;f[10,0]=.5
 return f
def result(case):
 t0=time.monotonic();name=case['case'];gp=(args.graphs/f"graph_o{case['order']}.bin").resolve()
 d,w,mp,blocks=graph(gp);a=len(w);n=len(mp)
 f=init_state(case['init'],d)
 beta=np.array([.3,.1,0.]) if case['clock']=='normal' else np.zeros(3)
 D=1/(1/np.sqrt(1-beta@beta)*(1+d@beta))
 V=mp[:,0,None]*w[None,:]/D[None,:];z=mp[:,1]/mp[:,0]
 # independent block operator: raw forward/reverse formula, with
 # shared mean activity subtraction to reduce equilibrium cancellation.
 def rhs(ff):
  ff=ff.reshape(n,a);one=1+ff;ph=ff/z[:,None]/one;ref=np.sum(ph*w[None,:])/n;delta=one*(ph-ref)
  num=np.zeros_like(ff)
  for i,j,K in blocks:
   if i==j:
    num[i]+=one[i]*(K@delta[i]-(ph[i]-ref)*(K@one[i]))
   else:
    num[i]+=one[i]*(K@delta[j]-(ph[i]-ref)*(K@one[j]))
    num[j]+=one[j]*(K.T@delta[i]-(ph[j]-ref)*(K.T@one[i]))
  return (num/V).ravel()
 path=root/(name+'.txt')
 with path.open('w') as out:
  out.write(f'rec_positive_case_v1\n{case["duration"]:.17g} {case["steps"]}\n')
  out.write(numbers(D));out.write(numbers(f))
  if not case['drift']:out.write('0\n')
  else:
   de=case['drift'];ext=de['ext'];extent=de['extent'];amp=de['amplitude']
   out.write(f'1\n{PCC.nu_abs:.17g} {PCC.dnu:.17g} {ext} {extent:.17g}\n')
   out.write(numbers(net.state_intervals))
   # Angular-dependent sign and later reversal, with evolving exterior.
   shift=amp*(.2+.8*d[:,2]);out.write(numbers(shift));out.write(numbers(-shift))
   l=np.linspace(-extent,-21.25,ext+1);r=np.linspace(21.25,extent,ext+1);x=np.r_[(l[:-1]+l[1:])/2,(r[:-1]+r[1:])/2]
   zz=1e-17*np.exp(-h*PCC.dnu*x/(k_B*3000.))
   extf=zz[None,:]*(1+.1*d[:,2,None]+.2*np.sin(x[None,:]/13))
   out.write(numbers(extf))
 dest=root/name;cmd=[str(exe),str(gp),str(path),str(dest)]
 proc=subprocess.run(cmd,text=True,capture_output=True,timeout=180)
 r=dict(case,command=cmd,returncode=proc.returncode,stderr=proc.stderr[-2000:],graph_sha256=sha(gp),input_sha256=sha(path))
 if proc.returncode:r['status']='FAIL_EXECUTION';return r
 meta=dict(l.split('=',1) for l in (dest/'run.txt').read_text().splitlines() if '=' in l)
 for key,val in list(meta.items()):
  try:
   v=float(val)
   if math.isfinite(v):meta[key]=v
  except ValueError:pass
 raw=read(dest/'state.tsv');history=read(dest/'history.tsv');actual=raw['occupation_action'];final=raw['final_f'];ref=rhs(f)
 abs_scale=max(np.max(abs(ref)),np.max(abs(f))*1e-14,1e-300)
 metrics=dict(action_relative=float(np.max(abs(actual-ref))/abs_scale),action_abs=float(np.max(abs(actual-ref))),initial_number=float(np.sum(f*V)),minimum_action_at_zero=float(np.min(actual[f.ravel()==0])) if np.any(f==0) else None)
 if case['init']=='equilibrium':
  assert metrics['action_abs']<2e-14*np.max(f),(name,metrics)
 else:assert metrics['action_relative']<5e-8,(name,metrics)
 assert np.min(final)>=0.
 if case['init'] in ('localized','zero'):assert metrics['minimum_action_at_zero']>=-1e-20
 if case['init']=='localized':
  metrics['old_counterexample_target_action']=float(actual[7*a])
  assert actual[7*a]>=0
  assert np.max(actual[f.ravel()==0])>0
 # Reference smooth harmonic action on same positive quadrature (band that
 # is integrated exactly by this Lebedev rule); source graph is not forced
 # to match each high angular moment.
 if name.startswith('angular_'):
  L=min(12,(case['order']-1)//2)
  grid=HarmonicGrid.from_directions(d,w,ell_max=L)
  orig=apply_nonlinear_bose_operator(f,mode_measure=mp[:,0],equilibrium_weight=mp[:,1],pair_moments=net.pair_moments,same_cell_rates=net.same_cell_rates,grid=grid,photon_momentum_scale=mp[:,2])
  metrics['harmonic_relative_l1']=float(np.sum(abs(actual.reshape(n,a)-orig.occupation_action)*V)/np.sum(abs(orig.occupation_action)*V))
  metrics['harmonic_band']=L
  # Same action four-force difference measured against gross momentum
  # transfer, not tiny signed heating cancellation.
  q=np.array([meta[f'action_q_{i}'] for i in range(4)])
  scale=np.sum(abs(orig.number_action)*w[None,:]*mp[:,2,None])
  metrics['harmonic_force_scaled']=float(np.max(abs(q-orig.Q_gamma))/scale)
 if name.startswith('time_') or name=='normal_clock':
  # Independent full dense W matrix, exact same finite event graph.
  W=np.zeros((n*a,n*a))
  for i,j,B in blocks:
   W[i*a:(i+1)*a,j*a:(j+1)*a]=B
   W[j*a:(j+1)*a,i*a:(i+1)*a]=B.T
  zz=np.repeat(z,a);vv=V.ravel()
  def dense(t,x):
   q=x/zz;one=1+x
   return (one*(W@q)-q*(W@one))/vv
  oracle=solve_ivp(dense,(0,case['duration']),f.ravel(),method='DOP853',rtol=2e-12,atol=1e-14)
  assert oracle.success
  exact=oracle.y[:,-1];metrics['ode_relative_l1']=float(np.sum(abs(final-exact)*vv)/np.sum(f.ravel()*vv))
  metrics['ode_relative_signal_l1']=float(np.sum(abs(final-exact)*vv)/np.sum(abs(exact-f.ravel())*vv))
 if case['drift']:
  for k in ['red_in','red_out','blue_in','blue_out']:assert meta[k]>0,(name,k)
  assert meta['interface_atom_energy']==0
  assert max(meta['max_core_number_defect'],meta['max_exterior_number_defect'])<2e-12
  last=history[-1]
  metrics['total_projection_relative']=float(abs(last['projection'])/history[0]['energy_j_m3'])
  metrics['projection_to_collision']=float(abs(last['projection'])/max(abs(last['collision_energy']),1e-300))
  metrics['core_projection_to_collision']=abs(meta['projection_core'])/max(abs(last['collision_energy']),1e-300)
  metrics['exterior_projection_to_collision']=abs(meta['projection_exterior'])/max(abs(last['collision_energy']),1e-300)
  metrics['escape_fraction']=float(last['escape_mass']/history[0]['mass'])
  metrics['interface_red_in_fraction']=meta['red_in']/history[0]['mass']
  metrics['interface_blue_in_fraction']=meta['blue_in']/history[0]['mass']
  metrics['end_collision_energy_j_m3']=float(last['collision_energy'])
 for k in ('number_defect','energy_defect','max_collision_number_defect','max_drift_number_defect','max_drift_energy_defect','equilibrium_null_per_s'):
  assert meta[k]<2e-10,(name,k,meta[k])
 assert meta['action_number_defect']<1e-10 and meta['action_force_defect']<1e-10
 assert meta['max_collision_force_defect']<5e-8,(name,meta['max_collision_force_defect'])
 assert meta['max_free_increase']<=1e-10*max(np.sum(f*V),1e-300),(name,meta['max_free_increase'])
 r.update(status='PASS_SCOPED',metrics=metrics,run=meta,wall_s=time.monotonic()-t0,hashes={p.name:sha(p) for p in dest.iterdir() if p.is_file()})
 return r
selected=[q for q in cases if q['case'].startswith(args.only)];assert selected
results=[]
# large graph audits sequential; avoid concurrent 302-node allocations.
for ca in selected:
 try:r=result(ca)
 except Exception as e:r=dict(ca,status='FAIL_CHECK',error=repr(e))
 print(r['case'],r['status'],r.get('error',''),r.get('stderr',''),flush=True);results.append(r)
(root/'RESULTS.json').write_text(json.dumps(dict(schema='r118c2c.native/1',binary_sha256=sha(exe),source_sha256=sha(rec/'data/full_scalar_com_khw_v050.npz'),cases=results),indent=2,allow_nan=False)+'\n')
print('done',len(results),flush=True)
