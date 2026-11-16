#!/usr/bin/env python3
"""Original TypeII source-state finite cascades and stationary/dynamic reduction.
No cosmological population prediction: proper electron density is prescribed.
The full and reduced generators refer to trace nuclei in the same local bath.
"""
import csv,json,subprocess
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import expm
from scipy.integrate import solve_ivp
import cascade as m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PARENT='d29a08cb6e368339015dadb2b791044ba6af9848'

def source():
 fs=ROOT/'research/typeii_spectral_collisions_20261116/SPECTRAL_COMPTON_FIELDS.csv'
 hs=ROOT/'research/typeii_clock_interface_20261115/outputs/FULL_r2_both.dat'
 br=ROOT/'research/typeii_boundfree_balance_20261116/LEVEL_BOUND_FREE_SOURCE.csv'
 identity={}
 for p in (fs,hs,br):
  rel=str(p.relative_to(ROOT));expect=subprocess.check_output(['git','rev-parse',PARENT+':'+rel],cwd=ROOT,text=True).strip()
  got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip();m.check(got==expect,'immutable input drift: '+rel);identity[rel]=got
 f=np.genfromtxt(fs,delimiter=',',names=True);h=np.loadtxt(hs)
 x=PchipInterpolator(np.log1p(h[::-1,0]),h[::-1,1])(np.log1p(f['z_mean']))
 tm=PchipInterpolator(np.log1p(h[::-1,0]),h[::-1,2])(np.log1p(f['z_mean']))
 rr=np.genfromtxt(br,delimiter=',',names=True).reshape(len(f),6)
 m.check(len(f)==358 and np.all(rr['n']==np.array([k[0] for k in m.STATES])) and np.all(rr['l']==np.array([k[1] for k in m.STATES])),'parent nl rate ordering')
 records=[]
 for k in range(len(f)):
  row=[]
  for j,key in enumerate(m.STATES):
   a=rr[k,j];m.check(abs(a['z_mean']-f[k]['z_mean'])<1e-10,'source rate time mismatch')
   row.append({'photo_s':float(a['photo_rate_s']),'alpha_m3_s':float(a['capture_alpha_m3_s']),
    'chi_J':m.bf.level(key)['chi'],'photo_excess_J':float(a['mean_photo_excess_eV']*m.EV),'capture_kinetic_J':float(a['mean_captured_kinetic_eV']*m.EV)})
  records.append(row)
 nh0=11.223846333047e-6*.0224*(1-.245)*1e6
 nh=nh0*(1+f['z_mean'])**3*f['Gamma'][0]/f['Gamma']
 ne=nh*x;m.check(np.min(ne)>0 and np.isfinite(ne).all(),'proper electron input')
 return f,tm,ne,records,identity

def dynamics(net):
 """Finite-time and frequency-response exact versus stationary-only reduction."""
 Q=net['Q'];e=m.eliminate(Q);r,f=e['r'],e['f'];rr,rf,fr,ff=[e[k] for k in ('rr','rf','fr','ff')]
 scale=float(min(-np.diag(ff)));freq=[]
 # Proper second is the time unit; s is Laplace frequency in s^-1.
 initial=np.zeros(7);initial[3]=1.
 for rel in (1e-6,1e-4,.01,.1,1.,10.):
  s=(.1+1j)*scale*rel;D=np.linalg.inv(s*np.eye(3)-ff)
  exact=np.linalg.inv(s*np.eye(7)-Q)[np.ix_(r,r)]
  effective=np.linalg.inv(s*np.eye(4)-rr-rf@D@fr)
  gap=float(np.linalg.norm(exact-effective)/np.linalg.norm(exact));m.check(gap<1e-10,'exact resolvent block identity')
  fullstate=np.linalg.solve(s*np.eye(7)-Q,initial)[r]
  memory=np.linalg.solve(s*np.eye(4)-rr-rf@D@fr,initial[r]+rf@D@initial[f])
  igap=float(np.linalg.norm(fullstate-memory)/np.linalg.norm(fullstate));m.check(igap<1e-10,'initial fast population memory')
  static=np.linalg.inv(s*np.eye(4)-e['S']);stored=np.linalg.inv(s*e['storage']-e['S'])
  freq.append({'s_over_internal_rate':rel,'exact_block_relative_gap':gap,'initial_fast_relative_gap':igap,
     'bare_Schur_relative_error':float(np.linalg.norm(static-exact)/np.linalg.norm(exact)),
     'first_storage_relative_error':float(np.linalg.norm(stored-exact)/np.linalg.norm(exact))})
 # Exact finite-time evolution compared with an independent stiff ODE.
 u=np.unique(np.r_[0,np.geomspace(1e-5,30,181)]);Qdim=Q/scale
 exact=np.array([expm(Qdim*t)@initial for t in u])
 ode=solve_ivp(lambda t,p:Qdim@p,(0.,float(u[-1])),initial,method='Radau',jac=Qdim,t_eval=u,rtol=2e-11,atol=2e-14,max_step=.2)
 m.check(ode.success,'trace Radau evolution');err=float(np.max(abs(ode.y.T-exact)))
 m.check(err<2e-9 and min(exact.flat)>-2e-12 and max(abs(exact.sum(axis=1)-1))<2e-11,'trace time validation')
 # Instantaneously routing fast initial population to retained exits is not
 # exact during its residence time, even if it preserves total probability.
 routed=e['P']@initial[f]
 approximation=np.array([expm(e['S']/scale*t)@routed for t in u])
 early=float(np.max(np.sum(abs(approximation-exact[:,r]),axis=1)))
 storage_lhs=np.ones(4)@e['storage'];storage_rhs=np.ones(4)+np.ones(3)@e['L']
 storage_gap=float(max(abs(storage_lhs-storage_rhs)));m.check(storage_gap<1e-11,'first memory storage conservation')
 return {'internal_rate_s_inv':scale,'time_end_s':float(u[-1]/scale),'frequency_checks':freq,
  'expm_Radau_max_absolute_gap':err,'finite_time_nucleus_residual':float(max(abs(exact.sum(axis=1)-1))),
  'instant_exit_routing_max_retained_L1_error':early,
  'initial_fast_if_omitted_lost_mass':1.,'storage_conservation_identity_max_abs':storage_gap,
  'qualification':'linear tracer at fixed ne/bath; exact memory verified, stationary Schur is not an exact chronological generator'},np.column_stack((u,u/scale,exact,approximation))

def main():
 fields,Tm,ne,bfr,identity=source();rates=[];state_rows=[];probes=[];Qlist=[];Slist=[];Llist=[]
 reconstruction=[];energyerr=[];energyred=[];prob=[];storage=[];tablegap=[];equationerr=[]
 qprobes=(1700.,1500.,1392.,1100.,1000.,800.,300.);reference_net=None
 for k,f in enumerate(fields):
  T=float(f['Tn_K']);b=float(f['beta']);net=m.network(T,float(Tm[k]),b,float(ne[k]),bf_records=bfr[k]);e=m.eliminate(net['Q'])
  full=m.stationary(net['Q'],net['reference_weights'])
  red=m.stationary(e['S'],net['reference_weights'][m.RETAINED]);reconstructed=m.lift(e,red);reconstructed/=sum(reconstructed)
  rec=float(max(abs(reconstructed/full-1)));reconstruction.append(rec);m.check(rec<1e-9,'source stationary reconstruction')
  P=e['P'];prob.append(float(max(abs(P.sum(axis=0)-1))));m.check(min(P.flat)>=0,'negative exit probability')
  storage.append(float(max(abs(np.ones(4)@e['storage']-np.ones(4)-np.ones(3)@e['L']))))
  fluxin=net['Q']@full;scale=float(np.max(abs(net['Q'])*full[None,:]));equationerr.append(float(max(abs(fluxin))/scale))
  # A non-stationary retained population is used for a nontrivial energy ledger.
  raw=np.array([.4,.2,.3,.1]);lift=m.lift(e,raw);lift/=sum(lift);read=m.energy(net,lift)
  energyerr.append(read['relative_residual'])
  # The microscopic lift carries bound energy of fast states but their rate
  # vanishes in the zero-frequency reconstruction. This is a steady manifold identity.
  bound_red=float(m.ENERGY[m.RETAINED]@(e['S']@lift[m.RETAINED]))
  egap=abs(bound_red+read['photon_energy_J_s']+read['electron_kinetic_J_s'])/read['gross_energy_J_s'];energyred.append(float(egap))
  m.check(max(read['relative_residual'],egap)<2e-12,'microscopic/reduced energy ledger')
  tp=net['channels'][-1];lo=m.two_photon(T,b,table='standard')
  tablegap.append(abs(lo['down']/tp['down']-1))
  for i,key in enumerate(m.STATES[:3]):
   a=float(e['S'][i,3]/ne[k]);B=float(e['S'][3,i]);direct=bfr[k][i]
   row={'tau_H':float(f['tau_H']),'z_mean':float(f['z_mean']),'n':key[0],'l':key[1],
    'ne_prescribed_m3':float(ne[k]),'alpha_direct_m3_s':direct['alpha_m3_s'],'alpha_effective_m3_s':a,
    'alpha_effective_over_direct':a/direct['alpha_m3_s'],'photo_direct_s':direct['photo_s'],
    'photo_effective_s':B,'photo_effective_over_direct':B/direct['photo_s']}
   rates.append(row)
  affinity=m.cycle_affinity(T,b)
  state_rows.append([f['tau_H'],f['z_mean'],b,T,Tm[k],ne[k],*full,rec,tp['down'],tp['up'],affinity])
  Qlist.append(net['Q']);Slist.append(e['S']);Llist.append(e['L'])
  if min(abs(float(f['z_mean'])-z) for z in qprobes)<1e-7:
   pr={'z_mean':float(f['z_mean']),'Tn_K':T,'Tm_parent_K':float(Tm[k]),'beta':b,'ne_fixed_m3':float(ne[k]),
    'two_photon_down_s':tp['down'],'two_photon_up_s':tp['up'],'two_photon_stimulated_fractional_enhancement':tp['stimulated_enhancement'],
    'two_photon_table_relative_down_gap':float(lo['down']/tp['down']-1),
    'effective_bound_free':rates[-3:],'exit_probabilities_retained_by_n3':P.tolist(),
    'stationary_trace_fractions':full.tolist(),'eliminated_stationary_probability':float(sum(full[m.FAST])),
    'cycle_log_affinity':affinity,'energy_lift_relative_residual':egap}
   probes.append(pr)
   if abs(float(f['z_mean'])-1100)<1e-7:reference_net=net
 m.check(reference_net is not None,'reference z1100 absent')
 dynamic,traj=dynamics(reference_net)
 for name,data,header in [('SOURCE_TRACE_STATIONARY.csv',state_rows,'tau_H,z_mean,beta,Tn_K,Tm_K,ne_m3,p1s,p2s,p2p,p3s,p3p,p3d,pion,reconstruction_rel,two_gamma_down,two_gamma_up,cycle_log_affinity'),
   ('TRACE_DYNAMIC_MEMORY.csv',traj,'time_internal_units,proper_time_s,p1s,p2s,p2p,p3s,p3p,p3d,pion,instant_routed_1s,instant_routed_2s,instant_routed_2p,instant_routed_ion')]:
  np.savetxt(HERE/name,np.array(data),delimiter=',',header=header,comments='',fmt='%.17g')
 with (HERE/'EFFECTIVE_BOUND_FREE.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rates[0]),lineterminator='\n');w.writeheader();w.writerows(rates)
 # Deterministic NPY matrices allow exact source record reuse without ZIP timestamps.
 for name,value in [('FULL_GENERATORS.npy',Qlist),('REDUCED_GENERATORS.npy',Slist),('FAST_LIFTS.npy',Llist)]:np.save(HERE/name,np.array(value))
 out={'parent_head':PARENT,'input_Git_blobs':identity,'source_states':len(fields),'effective_bound_free_records':len(rates),
  'levels':[list(k) for k in m.STATES],'retained_indices':m.RETAINED.tolist(),'eliminated_indices':m.FAST.tolist(),
  'maximum_stationary_reconstruction_relative_gap':max(reconstruction),'maximum_stationary_equation_relative_gap':max(equationerr),
  'maximum_exit_probability_defect':max(prob),'maximum_storage_identity_gap':max(storage),
  'maximum_microscopic_energy_relative_residual':max(energyerr),'maximum_reduced_lift_energy_relative_residual':max(energyred),
  'max_standard_hires_two_photon_relative_down_difference':max(tablegap),
  'source_probes':probes,'dynamic_memory_test':dynamic,
  'scope':'fixed-ne local tracer network with optically thin imposed bath; no new cosmological xe, no native effective coefficient replacement'}
 (HERE/'SOURCE_CASCADE_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
 print('SOURCE_COUNTS',len(fields),len(rates),flush=True)
 print('MAXIMA',json.dumps({k:v for k,v in out.items() if k.startswith('max')}),flush=True)
 print('Z1100',json.dumps(next(p for p in probes if abs(p['z_mean']-1100)<1e-7)),flush=True)
 print('DYNAMICS',json.dumps(dynamic),flush=True)
if __name__=='__main__':main()
