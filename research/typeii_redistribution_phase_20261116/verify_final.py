#!/usr/bin/env python3
"""One bounded same-author hostile and implementation verification pass."""
import ast,hashlib,json,os,subprocess,sys
import numpy as np
from redistribution import *

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 unit=[]
 for optimized in (False,True):
  cmd=[sys.executable]+(['-O'] if optimized else [])+[str(HERE/'test_redistribution.py')]
  r=subprocess.run(cmd,cwd=HERE,env=env,capture_output=True,text=True,timeout=60)
  (HERE/('UNIT_OPTIMIZED.log' if optimized else 'UNIT_NORMAL.log')).write_text(r.stdout+r.stderr)
  check(r.returncode==0,'unit contracts failed');unit.append({'optimized':optimized,'exit':r.returncode,'cases':14})
 n,w=sphere(4,8);N=np.ones((2,5));z=np.zeros_like(N)
 calls={
 'nonfinite_B':lambda:bernoulli(np.nan),
 'negative_occupation':lambda:thermal_flux(np.array([1.,-1.]),np.array([.1])),
 'occupation_edge_shape':lambda:thermal_flux(np.ones(4),np.ones(2)),
 'superluminal':lambda:to_atom(n,1.01),
 'nonunit':lambda:to_normal(2*n,.1),
 'bad_sphere':lambda:sphere(1,3),
 'negative_angular_weight':lambda:angular_generator(n,-w,np.ones(len(w))),
 'negative_Doppler':lambda:angular_generator(n,w,-np.ones(len(w))),
 'negative_temperature':lambda:medium_rates(np.array([NU0]),-1,1,0),
 'negative_density':lambda:medium_rates(np.array([NU0]),3000,-1,0),
 'invalid_fate_probability':lambda:medium_rates(np.array([NU0]),3000,1,1.1),
 'fractional_grid':lambda:fixed_grid(3000.,20.,160.5),
 'negative_photon_count':lambda:backward_birth_death(-1e-14*N,z,z,z,1.),
 'negative_destruction_rate':lambda:backward_birth_death(N,z,z,-N,1.),
 'negative_step':lambda:backward_birth_death(N,z,z,z,-1.),
 }
 rejected=[]
 for name,call in calls.items():
  try:call()
  except ValueError:rejected.append(name)
  else:raise RuntimeError('invalid admitted: '+name)
 files=['KERNEL_AND_GEOMETRY_VERIFICATION.json']+['PACKET_'+name+suffix for name in ('base','fine_evolving') for suffix in ('_RESULT.json','_TRACE.csv','_FINAL_COUNTS.npy')]
 hashes={name:sha(HERE/name) for name in files}
 commands=[('kernel',[str(HERE/'verify_kernels.py')]),('base',[str(HERE/'packet_campaign.py'),'--base-only']),('fine',['-c',"from packet_campaign import evolve; evolve(cells=640,steps=768,save='PACKET_fine_evolving')"])]
 receipts=[]
 for name,args in commands:
  r=subprocess.run([sys.executable,'-O',*args],cwd=HERE,env=env,capture_output=True,text=True,timeout=120)
  (HERE/('REPLAY_'+name+'.log')).write_text(r.stdout+r.stderr);check(r.returncode==0,'source replay '+name+' failed '+r.stderr[-700:]);receipts.append({'program':name,'exit':r.returncode})
 check(all(sha(HERE/f)==h for f,h in hashes.items()),'source science byte identity changed')
 original=json.loads((ROOT/'research/typeii_host_preflight_20261101/SOURCE_LOCK.json').read_text())['original_git_blobs_sha1']
 for p,h in original.items():check(subprocess.check_output(['git','hash-object',p],cwd=ROOT,text=True).strip()==h,'original BASS drift '+p)
 for name in ('redistribution.py','packet_campaign.py','verify_kernels.py','verify_time_dependence.py','verify_final.py'):
  tree=ast.parse((HERE/name).read_text());check(not any(isinstance(a,ast.Assert) for a in ast.walk(tree)),'removable scientific assertion')
 # Specific wrong physical-model controls, not generic agreement checking.
 xx=np.linspace(.2,8,64);f=1/np.expm1(xx+.2);delta=np.diff(xx)
 fw=bernoulli(delta)*f[:-1]*(1+f[1:]);rv=bernoulli(-delta)*f[1:]*(1+f[:-1]);correct=float(max(abs(fw-rv)/np.maximum(fw+rv,1e-300)))
 wrong=thermal_flux(f,delta,False);wrong_scale=bernoulli(delta)*f[:-1]+bernoulli(-delta)*f[1:]
 no_stim=float(max(abs(wrong)/wrong_scale));check(no_stim>1e-3 and correct<1e-14,'induced-scattering falsifier')
 na,wa=sphere(6,12);nn,D=to_normal(na,.05);Q,pi=angular_generator(na,wa,D)
 wrongQ,_=angular_generator(na,wa,np.ones(len(wa)));wrong_clock=float(max(abs(wrongQ@pi)));check(wrong_clock>1e-4,'wrong photon path-clock angular control')
 kernel=json.loads((HERE/'KERNEL_AND_GEOMETRY_VERIFICATION.json').read_text())
 source=json.loads((HERE/'SOURCE_PACKET_RESULTS.json').read_text());extras=json.loads((HERE/'EXTRA_SOURCE_PACKET_RESULTS.json').read_text());runs=source['cases']+extras['cases']
 check(len(runs)==15,'actual source case count')
 checks=json.loads((HERE/'TIME_DEPENDENCE_AND_CONVERGENCE.json').read_text())
 for r in runs:
  check(abs(r['survival']+r['red_band_exit']+r['blue_band_exit']+r['tagged_ionized']-1)<3e-9,'physical fate sum')
 no_dest=next(r for r in runs if r['case']=='no_destruction');check(no_dest['tagged_ionized']==0,'no-destruction control')
 b20=next(r for r in runs if r['case']=='fine_evolving');b80=next(r for r in runs if r['case']=='band80')
 # Show why the band answer is not a global escape factor.
 boundary_effect=(b80['red_band_exit']+b80['blue_band_exit'])-(b20['red_band_exit']+b20['blue_band_exit'])
 check(abs(boundary_effect)>.4,'boundary support counterexample disappeared')
 # Occupancy estimate of the prescribed parent radiation in widest tested band.
 ge=Geometry(np.log(1701/1101),np.log(1701/1101)+.01,6,12);ss=ge.at(ge.t0);g=fixed_grid(ss['Tm'],80,160)
 Tn=2.7255*(1+ss['z']);fbg=lt.planck(H*g['nu_edges'][0]/(KB*Tn*max(ss['D'])))
 check(fbg<1e-12,'dilute background assumption not valid in source band')
 result={'unit_executions':28,'unit_receipts':unit,'invalid_cases_rejected':rejected,'optimized_replays':receipts,'science_sha256':hashes,'original_BASS_blobs':len(original),'source_cases':len(runs),
 'max_source_count_ledger_defect':max(r['max_count_ledger_defect'] for r in runs),'max_source_normal_energy_ledger_defect':max(r['max_normal_energy_ledger_defect_in_initial_line_energy'] for r in runs),
 'max_source_fourforce_frame_defect':max(r['max_collision_fourforce_defect'] for r in runs),
 'thermal_correct_BE_pair_relative_residual':correct,'wrong_omit_induced_BE_pair_relative_residual':no_stim,'wrong_omit_D_angular_equilibrium_generator_residual':wrong_clock,
 'wrong_omit_angular_J_comoving_photon_factor':kernel['long_source_wrong_omit_J_number'],'max_prescribed_background_occupation_blue_boosted_red_band_edge':float(fbg),
 'band80_minus_band20_total_exit_probability':boundary_effect,
 'refined_time_dependence_change':checks['max_change_of_time_dependence_effect_under_joint_refinement'],
 'independent_unsplit_source_ODE':checks['independent_reference'],
 'self_hostile_review':'PERFORMED_SAME_AUTHOR_NOT_BLIND','native_subagent':'NOT_RUN','distinct_author_referee':'NOT_RUN',
 'claim_gate':'exact geometric measure and conservative discrete identities; conditional factorized leading FP/Rayleigh packet model, not exact joint R_II or global escape',
 'storage':'GitHub plus host stage archives; external NOT_ATTEMPTED_KNOWN_ENOSPC'}
 (HERE/'VERIFICATION_AND_HOSTILE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='science_sha256'},indent=2))
if __name__=='__main__':main()
