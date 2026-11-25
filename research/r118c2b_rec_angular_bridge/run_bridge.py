"""Source-locked v050 native bridge benchmark. The v049 fields are inputs,
NOT reference actions for the v050 conductances. Recompute the original
Python operator and its JVP at each tested input.
"""
import argparse,csv,hashlib,json,math,os,pathlib,subprocess,sys,time
import numpy as np
from scipy.constants import h,c
from scipy.special import eval_legendre
from numpy.polynomial.legendre import leggauss
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--rec',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--out',type=P,required=True)
p.add_argument('--only',default='');args=p.parse_args()
root=args.out.resolve();root.mkdir(exist_ok=False,parents=True);exe=args.binary.resolve();rec=args.rec.resolve()
sys.path.insert(0,str(rec/'src'))
from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork,implicit_bose_step,boost_four_hydrogen_to_normal
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid,apply_nonlinear_bose_operator,apply_nonlinear_bose_jvp
paths=dict(network=rec/'data/full_scalar_com_khw_v050.npz',states=rec/'data/pr02_nonlinear_bose_runtime_v049.npz',geometry=rec/'data/pr01c_background_snapshots_v048.npz',interface=rec/'data/pr04c_coupled_interface_v056.npz',packets=rec/'archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55/THREE_SNAPSHOT_INTERFACE_PACKETS.csv')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
net=CollisionNetwork.from_npz(paths['network']);owner=np.load(paths['network'],allow_pickle=False);s=np.load(paths['states'],allow_pickle=False);geo=np.load(paths['geometry'],allow_pickle=False);interface=np.load(paths['interface'],allow_pickle=False)
assert np.array_equal(net.state_labels,s['state_labels']) and np.array_equal(net.mode_measure,s['mode_measure']) and np.array_equal(net.equilibrium_weight,s['equilibrium_weight'])
def line(arr):return ' '.join(format(float(v),'.17g') for v in np.asarray(arr).ravel())+'\n'
netfile=root/'network.txt'
with netfile.open('w') as f:
 f.write('rec_angular_network_v1\n35 24\n')
 for i,label in enumerate(net.state_labels):f.write(label+' '+line([*net.state_intervals[i],net.mode_measure[i],net.equilibrium_weight[i],net.momentum_scale[i]]))
 f.write(line(net.pair_moments));f.write(line(net.same_cell_rates))
# Readback verifies all exported bytes semantically, exact float round trip.
tokens=netfile.read_text().split();assert tokens[:3]==['rec_angular_network_v1','35','24']
for i in range(35):
 a=tokens[3+6*i:3+6*(i+1)];assert a[0]==net.state_labels[i]
 assert np.array_equal(np.array(a[1:],float),np.r_[net.state_intervals[i],net.mode_measure[i],net.equilibrium_weight[i],net.momentum_scale[i]])
off=3+6*35;nn=25*35*35
assert np.array_equal(np.array(tokens[off:off+nn],float).reshape(25,35,35),net.pair_moments)
assert np.array_equal(np.array(tokens[off+nn:],float).reshape(25,35),net.same_cell_rates)
cases=[]
def add(name,d,w,L,f,geom,clock='material',dt=None,packets=(),expected=None,ref_name=None,bass=None,adversarial=None):
 cases.append(dict(name=name,d=np.asarray(d),w=np.asarray(w)/np.sum(w),L=L,f=np.asarray(f),geom=geom,clock=clock,dt=dt,packets=packets,expected=expected,ref_name=ref_name,bass=bass,adversarial=adversarial))
def snapshot(model,index):
 def get(key):return geo[f'{model}_{key}'][index]
 H=float(get('H_s_inv'))
 return dict(H=H,beta=get('beta_H'),bp=get('D0_beta_H_s_inv')/H,shear=get('sigma_s_inv')/H,N=get('N_s_inv')/H,A=get('A_s_inv')/H,R=get('frame_rotation_s_inv')/H)
for name,model,i,L in [('finite_or_mixed_tilt','Bianchi_VI_h_tilted_large_shear',100,12),('nonlinear_even_shear','Bianchi_II_large_shear',70,20),('directional_crossing','Bianchi_II_large_shear',0,24)]:
 d=s[name+'_directions_hydrogen'];w=s[name+'_weights'];f=s[name+'_occupation'];g=snapshot(model,i)
 add(name,d,w,L,f,g,ref_name=name)
 if name=='finite_or_mixed_tilt':add(name+'_normal_clock',d,w,L,f,g,'normal',ref_name=name)
 if L>12:add(name+'_L12',d,w,12,f,g,ref_name=name)
 if L>20:add(name+'_L20',d,w,20,f,g,ref_name=name)
g=dict(H=1e-13,beta=np.zeros(3),bp=np.zeros(3),shear=np.zeros((3,3)),N=np.zeros((3,3)),A=np.zeros(3),R=np.zeros(3))
d=s['finite_or_mixed_tilt_directions_hydrogen'];w=s['finite_or_mixed_tilt_weights'];z=net.activity_weight
# Manufactured physically tiny / high-occupation spectral-angular
# perturbations, same fixed source kernel. No calibration to new T.
for amplitude in (1e-12,0.5,5.):
 activity=amplitude/(1+amplitude)/z.max();eq=activity*z/(1-activity*z)
 f=eq[:,None]*(1+.12*np.sin(net.centers[:,None]/2)*d[None,:,2]+.08*(3*d[None,:,0]**2-1))
 add('stress_'+str(amplitude),d,w,12,f,g,dt=0.5)
# Full original v056 paired packet receipts. Use integrated packet number
# and true face energy; original v056 ell=0 (not ell=3).
rows=list(csv.DictReader(paths['packets'].open()))
for k,target in enumerate(interface['target_z']):
 selected=[q for q in rows if float(q['target_z'])==target]
 assert len(selected)==2
 packets=[dict(side=q['side'],direction='into' if q['direction']=='native_to_com' else 'out',nu=float(q['interface_frequency_Hz']),number=1e5*float(q['total_number_flux_per_H_s']),energy=1e5*float(q['total_photon_energy_flux_W_per_H']),nh=float(q['nH_cm3'])*1e6,source_packet_sha=q['packet_sha256']) for q in selected]
 H=float(selected[0]['H_s_inv'])
 add('interface_z'+str(int(target)),interface['directions'],interface['angular_weights'],0,interface['old_occupation'],dict(g,H=H),dt=1e5,packets=packets,expected=interface['updated_occupation'][k])
# Actual accepted collisionless BASS geometry; source-fixed atomic kernel.
# The input f below is a placeholder replaced inside Rust by the cell-
# averaged characteristic Planck solution. No Thomson mixed-spectrum fit.
d=s['finite_or_mixed_tilt_directions_hydrogen'];w=s['finite_or_mixed_tilt_weights']
for family in ('FLRW','I','II','III','IV','V','VI0','VIh:-0.25','VIstar','VII0','VIIh:0.25','VIII','IX'):
 for nt in ((16,32) if family in ('I','VIIh:0.25') else (16,)):
  duration=.025;shear=0. if family=='FLRW' else .03
  name='bass_'+family.replace(':','_')+'_t'+str(nt)
  add(name,d,w,12,np.repeat(z[:,None],len(w),axis=1),dict(g,H=5e-14,beta=np.array([.1,.03,0.])),clock='normal',dt=.5,bass=[family,shear,duration,nt,3000*np.exp(duration),PCC.nu_abs,PCC.dnu])
# Concrete inward-pointing-cone test at the actual released L24 kernel.
# The largest negative *absolute* pair coefficient at mu=1 occurs at I07/I10.
# No implicit step attempted for these adversarial occupation fields (dt=0).
d=s['directional_crossing_directions_hydrogen'];w=s['directional_crossing_weights']
i,j=7,10;angle=0
for floor in (1e-8,1e-12,1e-16,1e-20):
 f=np.full((35,len(w)),floor);f[j,angle]=.5
 add('adversarial_'+str(floor),d,w,24,f,g,dt=0.,adversarial=dict(target=i,source=j,angle=angle,floor=floor))
def norm(a):return float(np.max(np.abs(a)))
def rel(a,b):return norm(a-b)/norm(b) if norm(b)>0. else None
def read(p):return np.genfromtxt(p,names=True,delimiter='\t')
def run(ca):
 name=ca['name'];start=time.monotonic();d,w,L,f,geom=map(ca.get,('d','w','L','f','geom'));grid=HarmonicGrid.from_directions(d,w,ell_max=L);w=grid.weights
 kw=dict(mode_measure=net.mode_measure,equilibrium_weight=net.equilibrium_weight,pair_moments=net.pair_moments,same_cell_rates=net.same_cell_rates,grid=grid)
 kwb=dict(kw,pair_moments=net.boundary_pair_moments(),same_cell_rates=np.zeros_like(net.same_cell_rates))
 orig=apply_nonlinear_bose_operator(f,photon_momentum_scale=net.momentum_scale,**kw)
 bound=apply_nonlinear_bose_operator(f,photon_momentum_scale=net.momentum_scale,**kwb)
 v=f*.03*np.sin(net.centers[:,None]/3.1+.017*np.arange(len(w))[None,:])
 j=apply_nonlinear_bose_jvp(f,v,**kw).occupation_action_jvp
 jb=apply_nonlinear_bose_jvp(f,v,**kwb).occupation_action_jvp
 beta=geom['beta'];gamma=1/np.sqrt(1-beta@beta)
 dop=1/(gamma*(1+d@beta))
 clk=dop if ca['clock']=='normal' else np.ones_like(w)
 action=orig.occupation_action
 crit=np.min(-f[(action*clk[None,:])<0]/(action*clk[None,:])[(action*clk[None,:])<0]) if np.any(action<0) else np.inf
 dt=ca['dt'] if ca['dt'] is not None else 1.02*float(crit)
 packets=ca['packets'];nh=packets[0]['nh'] if packets else 1.
 case=root/(name+'.txt')
 with case.open('w') as out:
  out.write(f'rec_angular_case_v1\n{len(w)} {L}\n');out.write(line([geom['H'],*beta,*geom['bp']]))
  for key in ('shear','N','A','R'):out.write(line(geom[key]))
  out.write(f'{dt:.17g} {ca["clock"]}\n');out.write(line(np.c_[d,w]));out.write(line(f));out.write(line(v));out.write(f'{len(packets)} {nh:.17g}\n')
  for q in packets:out.write(q['side']+' '+q['direction']+' '+line([q['nu'],q['number'],q['energy']]))
 dest=root/name;cmd=[str(exe),str(netfile),str(case),str(dest)]+([] if ca["bass"] is None else list(map(str,ca["bass"])))
 proc=subprocess.run(cmd,text=True,capture_output=True,timeout=180)
 result=dict(case=name,command=cmd,L=L,angles=len(w),dt_s=dt,clock=ca['clock'],returncode=proc.returncode,stderr=proc.stderr[-1500:],packets=packets,bass=ca["bass"],adversarial=ca["adversarial"],case_sha256=sha(case))
 if proc.returncode:result['status']='FAIL_EXECUTION';return result
 m=dict(q.split('=',1) for q in (dest/'run.txt').read_text().splitlines() if '=' in q)
 for key in m:
  try:m[key]=float(m[key])
  except ValueError:pass
 raw=read(dest/'action.tsv');shape=f.shape
 col=lambda name:raw[name].reshape(shape)
 act=col('full_action');bact=col('boundary_action');updated=col('updated');inc=col('increment')
 frame=read(dest/'frame.tsv')
 if ca['bass']:
  f=col('occupation')
  v=f*.03*np.sin(net.centers[:,None]/3.1+.017*np.arange(len(w))[None,:])
  orig=apply_nonlinear_bose_operator(f,photon_momentum_scale=net.momentum_scale,**kw)
  bound=apply_nonlinear_bose_operator(f,photon_momentum_scale=net.momentum_scale,**kwb)
  j=apply_nonlinear_bose_jvp(f,v,**kw).occupation_action_jvp
  jb=apply_nonlinear_bose_jvp(f,v,**kwb).occupation_action_jvp
  action=orig.occupation_action
  geom=dict(geom,H=m['bass_H_s'])
 # Both direct geometry and Lorentz clock agreement.
 qn=np.array([m[f'q_normal_eta_{k}'] for k in range(4)])
 qh=np.array([m[f'q_gamma_{k}'] for k in range(4)])
 q_scale=max(float(np.sum(abs(orig.number_action)*w[None,:]*net.momentum_scale[:,None])),orig.gross_action_scale*float(net.momentum_scale.max())*1e-15)
 expected_qn=boost_four_hydrogen_to_normal(orig.Q_gamma,beta)/geom['H']
 metrics=dict(action_rel=rel(act,action),boundary_rel=rel(bact,bound.occupation_action),jvp_rel=rel(col('jvp'),j),boundary_jvp_rel=rel(col('boundary_jvp'),jb),q_h_scaled=norm(qh-orig.Q_gamma)/max(q_scale,1e-300),q_n_scaled=norm(qn-expected_qn)/max(q_scale/geom['H'],1e-300),clock_rel=rel(col('normal_eta_action'),action*dop[None,:]/geom['H']),doppler_rel=rel(frame['D'],dop))
 # Very small net actions (exact equilibrium/interface initial state) are
 # compared to gross action scale, not to a cancellation-sized signal.
 gross=max(orig.gross_action_scale,1e-300)
 metrics['number_scaled']=abs(m['number_residual'])/gross
 metrics['action_gross_scaled']=float(np.sum(abs(act-action)*net.mode_measure[:,None]*w[None,:]))/gross
 bgross=max(bound.gross_action_scale,1e-300)
 metrics['boundary_gross_scaled']=float(np.sum(abs(bact-bound.occupation_action)*net.mode_measure[:,None]*w[None,:]))/bgross
 if ca['ref_name']:
  key=ca['ref_name'];directions=np.c_[frame['nx'],frame['ny'],frame['nz']]
  metrics['direction_abs']=norm(directions-s[key+'_directions_normal'])
  metrics['drift_abs_over_H']=norm(frame['dlognu_deta']-s[key+'_R_hydrogen_s_inv']/geom['H'])
  metrics['drift_positive']=int(np.sum(frame['dlognu_deta']>0))
  metrics['drift_negative']=int(np.sum(frame['dlognu_deta']<0))
 if ca['bass']:
  T=read(dest/'temperature.tsv')['T_h_K'];x,wx=leggauss(32)
  lo=net.state_intervals[:,0];hi=net.state_intervals[:,1]
  nu=PCC.nu_abs+PCC.dnu*((lo+hi)[:,None]/2+(hi-lo)[:,None]*x/2)
  ww=wx[None,:]*nu**2
  exact=(ww[:,:,None]/np.expm1(h*nu[:,:,None]/(PCC.k*T[None,None,:]))).sum(axis=1)/ww.sum(axis=1)[:,None]
  metrics.update(bass_occupation_integral_rel=rel(f,exact),bass_temperature_min=float(T.min()),bass_temperature_max=float(T.max()))
  assert metrics['bass_occupation_integral_rel']<1e-12
  assert m['bass_source_measure_defect']<1e-10 and m['bass_source_momentum_defect']<1e-10
  assert m['bass_temperature_gap']<1e-7 and m['bass_landing_error']<1e-7
 if ca['adversarial']:
  ad=ca['adversarial'];val=float(act[ad['target'],ad['angle']]);metrics['negative_gain_target']=val
  assert val< -1e-9
 if packets:
  ledger=read(dest/'packets.tsv')
  assert np.all(ledger['native_number_per_h']+ledger['com_number_per_h']==0)
  assert np.all(ledger['native_energy_j_per_h']+ledger['com_energy_j_per_h']==0)
  assert np.all(ledger['atom_energy_j_per_h']==0)
  expected_inc=np.zeros_like(f)
  for q in packets:
   i=np.where(net.state_labels==('FR00' if q['side']=='red' else 'FB02'))[0][0]
   expected_inc[i]=nh*q['number']/net.mode_measure[i]*(1 if q['direction']=='into' else -1)
  metrics['packet_increment_rel']=rel(inc,expected_inc)
  metrics['packet_unresolved_energy_j_per_h']=ledger['unresolved_j_per_h'].tolist()
  metrics['source_updated_rel']=rel(updated,ca['expected'])
 if m['implicit_status']=='PASS':
  final=apply_nonlinear_bose_operator(updated,photon_momentum_scale=net.momentum_scale,**kw)
  residual=updated-f-inc-dt*clk[None,:]*final.occupation_action
  metrics['independent_implicit_residual']=norm(residual)/max(norm(f),norm(inc),1e-300)
  # For ordinary material clocks independently solve owner Python BE.
  # The original v056 packet result is an additional immutable reference.
  if dt>0 and not packets and ca['clock']=='material' and not name.endswith('_L12') and not name.endswith('_L20'):
   try:
    py=implicit_bose_step(f,dt_s=dt,network=net,grid=grid)
    metrics['source_be_relative']=rel(updated,py.occupation)
    metrics['source_be_iterations']=int(py.newton_iterations)
   except Exception as e:metrics['source_be_error']=str(e)
  result['status']='COUNTEREXAMPLE_VERIFIED' if ca['adversarial'] else 'PASS_SCOPED'
 else:result['status']='ACTION_VERIFIED_IMPLICIT_REJECTED'
 # Equilibrium action absolute residual is a poor relative metric for
 # tiny fields. Compare against gross scale and direct JVP for all.
 for k in ('action_gross_scaled','boundary_gross_scaled','jvp_rel','boundary_jvp_rel','number_scaled','doppler_rel'):
  assert metrics[k]<2e-9,(name,k,metrics[k])
 # Force denominator is source gross absolute four-momentum rate. For
 # near equilibrium use original collision gross number scale instead.
 if not packets:
  assert max(metrics['q_h_scaled'],metrics['q_n_scaled'],metrics['clock_rel'] or 0.)<2e-9,(name,metrics)
 if ca['ref_name']:
  assert metrics['direction_abs']<2e-12 and metrics['drift_abs_over_H']<2e-10,(name,metrics)
 if m['implicit_status']=='PASS':
  assert metrics['independent_implicit_residual']<2e-9 and m['implicit_number_defect']<2e-10
 if packets:assert metrics['packet_increment_rel']<2e-12
 result.update(metrics=metrics,run=m,hashes={p.name:sha(p) for p in dest.iterdir() if p.is_file()},wall_s=time.monotonic()-start)
 return result
results=[]
for ca in cases:
 if args.only and not ca['name'].startswith(args.only):continue
 try:r=run(ca)
 except Exception as e:r=dict(case=ca['name'],status='FAIL_CHECK',error=repr(e))
 results.append(r);print(r['case'],r['status'],r.get('error',''),r.get('stderr',''),r.get('run',{}).get('implicit_error',''),flush=True)
# Audit positivity of pointwise Legendre polynomial reconstruction.
# Signed truncation is not a positive event measure; do not clip.
mu=np.linspace(-1,1,2001);pair=net.pair_moments
poly=[]
for L in (12,20,24):
 K=np.einsum('lm,lij->mij',np.array([(2*l+1)*eval_legendre(l,mu) for l in range(L+1)]),pair[:L+1])
 mask=(pair[0]>0)&~np.eye(35,dtype=bool)
 rr=K[:,mask]/pair[0,mask];neg=rr<0
 poly.append(dict(L=L,pairs=int(mask.sum()/2),sample_points=len(mu),negative_samples=int(neg.sum()),minimum_relative_to_pair_monopole=float(rr.min()),worst_integrated_negative_part=float(np.max(np.trapezoid(np.maximum(-rr,0),mu,axis=0)/2))))
out=dict(schema='bass.r118c2b.rec_angular/1',binary_sha256=sha(exe),source_sha256={str(p):sha(p) for p in paths.values()},network_export_sha256=sha(netfile),cases=results,kernel_sign_audit=poly)
(root/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('done',len(results),'kernel sign',poly,flush=True)
