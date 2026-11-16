#!/usr/bin/env python3
"""One bounded same-author verification pass, actual source replays and hostile controls."""
import ast,json,os,subprocess,sys,hashlib
import numpy as np
from redistribution import *
from source_geometry import source,Angles

def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 tests=[]
 for opt in (False,True):
  cmd=[sys.executable]+(['-O'] if opt else [])+[str(HERE/'test_transport.py')]
  p=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,timeout=45)
  (HERE/('UNIT_OPTIMIZED.log' if opt else 'UNIT_NORMAL.log')).write_text(p.stdout+p.stderr)
  check(p.returncode==0 and 'Ran 16 tests' in p.stderr,'unit contracts not passed')
  tests.append({'optimized':opt,'exit':p.returncode,'cases':16})
 e=np.linspace(NU0*.999,NU0*1.001,17);rates=np.ones(16);faces=np.ones(17);m=frequency_model(e,3000.,rates,faces,0.)
 n,w=sphere_rule(3,4);na,D=atom_directions(n,.05);Q,pi=angular_generator(na,w/D**2,D)
 invalid=[
 ('nonunit_direction',lambda:atom_directions(n*2,.05)),
 ('superluminal_tilt',lambda:atom_directions(n,1.)),
 ('nan_direction',lambda:atom_directions(n*np.nan,.05)),
 ('negative_temperature',lambda:frequency_model(e,-1.,rates,faces,0.)),
 ('negative_rate',lambda:frequency_model(e,3000.,-rates,faces,0.)),
 ('bad_face_shape',lambda:frequency_model(e,3000.,rates,faces[:-1],0.)),
 ('death_probability_above_one',lambda:frequency_model(e,3000.,rates,faces,1.1)),
 ('nonpositive_clock',lambda:frequency_model(e,3000.,rates,faces,0.,clock=0.)),
 ('negative_frequency_population',lambda:frequency_step(m,-rates,.1)),
 ('negative_step',lambda:frequency_step(m,rates,-.1)),
 ('reversed_edges',lambda:mode_capacity(e[::-1])),
 ('negative_geometric_volume',lambda:capacities(e,w,D,-1.)),
 ('negative_Bose_occupation',lambda:pair_flux(-1.,.2,.1)),
 ('negative_angle_step',lambda:angular_evolve(Q,pi,np.ones((12,1)),np.array([-1.]))),
 ('nonpositive_remap_factor',lambda:redshift_remap(np.ones((1,16)),e,np.array([0.]))),
 ('outside_source_time',lambda:source().matter(-1.)),
 ]
 rejects=[]
 for name,fn in invalid:
  try:fn()
  except (ValueError,RuntimeError) as ex:rejects.append({'name':name,'type':type(ex).__name__})
  else:raise RuntimeError('invalid input admitted: '+name)
 files=['PHASE_AND_KERNEL_VERIFICATION.json','COUPLED_SPLIT_VERIFICATION.json','TRANSIENT_RESULTS.json']
 for label in ('time80','source1700_640'):
  files += ['outputs/'+label+s for s in ('.json','.csv','_final_N.npy')]
 digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 before={f:digest(HERE/f) for f in files};replays=[]
 commands=[('phase',['-O',str(HERE/'verify_phase_and_kernels.py')]),('coupled',['-O',str(HERE/'verify_coupled_split.py')]),('actual_tagged',['-O','-c',"from transient_transport import simulate;simulate('time80',cells=80,nmu=4,nphi=8,steps=80);simulate('source1700_640',z0=1700.,cells=80,nmu=4,nphi=8,steps=640)"]),('campaign_analysis',['-O',str(HERE/'analyze_campaign.py')])]
 for name,cmd in commands:
  p=subprocess.run([sys.executable]+cmd,cwd=HERE,env=env,text=True,capture_output=True,timeout=150)
  (HERE/(name+'_OPTIMIZED.log')).write_text(p.stdout+p.stderr)
  check(p.returncode==0,'optimized source replay failed '+name+': '+p.stderr[-1000:]);replays.append({'program':name,'exit':p.returncode})
 check(all(digest(HERE/f)==h for f,h in before.items()),'science output byte identity failed')
 locked=json.loads((ROOT/'research/typeii_host_preflight_20261101/SOURCE_LOCK.json').read_text())['original_git_blobs_sha1']
 for name,want in locked.items():
  got=subprocess.check_output(['git','hash-object',name],cwd=ROOT,text=True).strip();check(got==want,'original source changed '+name)
 ph=json.loads((HERE/'PHASE_AND_KERNEL_VERIFICATION.json').read_text());cp=json.loads((HERE/'COUPLED_SPLIT_VERIFICATION.json').read_text());tr=json.loads((HERE/'TRANSIENT_RESULTS.json').read_text())
 st,hn=source().state(float(np.log(1701/1101)));v=st[4];G=1/np.sqrt(1-v*v)
 _,D=atom_directions(n,v)
 wrongclock=float(max(abs((1/G)/D-1)))
 diag={'missing_angular_J_full_interval_photon_number_error':ph['wrong_frozen_sky_weight_photon_defect'][-1],'wrong_atom_rest_measure_stationary_L1_residual':cp['wrong_rest_slice_equilibrium_L1_residual'],'wrong_atom_reaction_clock_vs_photon_path_max_relative':wrongclock,'missing_recoil_Wien_stationarity_defect':cp['missing_recoil_Wien_L1_residual_s_inverse'],'total_resonance_as_true_ionization_rate_overcount_z1100':1/source().matter(float(np.log(1701/1101)))['pd'],'zero_time_readout_defect':'actual regression failed missing death_energy_J key, repaired by zero-valued field; positive-time physics unchanged','low_sky_resolution_defect':'512 directions failed long-interval sky-area target;4608 directions pass same threshold; source formulas unchanged'}
 for name in ('redistribution.py','source_geometry.py','transient_transport.py','verify_phase_and_kernels.py','verify_coupled_split.py','analyze_campaign.py','verify_final.py'):
  tree=ast.parse((HERE/name).read_text());check(not any(isinstance(x,ast.Assert) for x in ast.walk(tree)),'bypassable science check '+name)
 result={'unit_runs':tests,'unit_executions':32,'invalid_cases_rejected':rejects,'optimized_replays':replays,'actual_tagged_reexecutions':2,'science_outputs_byte_exact':before,'original_BASS_blobs':len(locked),'source_cases':tr['actual_source_cases'],'hostile_controls':diag,'self_hostile_review':'PERFORMED_SAME_AUTHOR_NOT_BLIND','native_subagent':'NOT_RUN','distinct_author_referee':'NOT_RUN','external_copy':'NOT_ATTEMPTED_KNOWN_PARENT_ENOSPC','precision_scope':'conservation and convergence verified for the declared finite-band factorized closure; no exact correlated RII or global escape claim'}
 (HERE/'VERIFICATION_AND_HOSTILE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='science_outputs_byte_exact'},indent=2))
if __name__=='__main__':main()
