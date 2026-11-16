#!/usr/bin/env python3
"""One bounded same-author hostile/replay pass for actual finite cascades.
No independent-author or genuinely blind-referee claim is made.
"""
from pathlib import Path
import ast,hashlib,json,os,subprocess,sys
import numpy as np
import cascade as m
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 receipts=[]
 for optimized in (False,True):
  cmd=[sys.executable]+(['-O'] if optimized else [])+[str(P/'test_cascade.py')]
  run=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT,env=env,timeout=60)
  label='UNIT_OPTIMIZED' if optimized else 'UNIT_NORMAL'
  (P/(label+'.log')).write_text(run.stdout+run.stderr);m.check(run.returncode==0,'unit contracts failed')
  receipts.append({'test':label,'exit':run.returncode,'cases':16})
 # Numerical/source outputs are replayed with removable asserts disabled.
 files=['KERNEL_VERIFICATION.json','SOURCE_CASCADE_RESULTS.json','EFFECTIVE_BOUND_FREE.csv','SOURCE_TRACE_STATIONARY.csv','TRACE_DYNAMIC_MEMORY.csv','FULL_GENERATORS.npy','REDUCED_GENERATORS.npy','FAST_LIFTS.npy']
 before={name:sha(P/name) for name in files}
 for script in ('verify_kernels.py','run_cascade_sources.py'):
  run=subprocess.run([sys.executable,'-O',str(P/script)],capture_output=True,text=True,cwd=ROOT,env=env,timeout=90)
  (P/(script+'_OPTIMIZED.log')).write_text(run.stdout+run.stderr);m.check(run.returncode==0,'optimized source replay '+script)
  receipts.append({'test':script+'_OPTIMIZED','exit':run.returncode})
 m.check(all(sha(P/name)==h for name,h in before.items()),'scientific output byte replay drift')
 # Catch physically invalid or structurally inconsistent inputs before a solve.
 n=m.network(3000,3000,.05,1e8)
 wrong=n['Q'].copy();wrong[0,0]*=2
 neg=n['Q'].copy();neg[1,0]=-1
 cases={
  'temperature_negative':lambda:m.network(-1,3000,0,1e8),
  'electron_density_negative':lambda:m.network(3000,3000,0,-1),
  'tilt_superluminal':lambda:m.network(3000,3000,1.1,1e8),
  'temperature_nan':lambda:m.two_photon(float('nan'),0),
  'forbidden_E1':lambda:m.einstein_A((2,0),(1,0)),
  'negative_photon_pair_energy':lambda:m.pair_average(-1.,1.,3000,0),
  'unknown_spectral_table':lambda:m.two_photon_table('invented'),
  'nonconservative_generator':lambda:m.eliminate(wrong),
  'negative_generator_rate':lambda:m.eliminate(neg),
  'duplicate_retained_state':lambda:m.eliminate(n['Q'],[0,0,1]),
  'negative_population':lambda:m.energy(n,np.r_[-1.,np.ones(6)]),
  'singular_stationary_scale':lambda:m.stationary(n['Q'],np.zeros(7)),
 }
 rejected=[]
 for name,fn in cases.items():
  try:fn()
  except (ValueError,RuntimeError,np.linalg.LinAlgError):rejected.append(name)
  else:raise RuntimeError('bad input was accepted: '+name)
 # Wrong statistical and normalization choices at fixed microscopic source.
 T=3000.;b=.05;tp=m.two_photon(T,b);therm=m.two_photon(T,0)
 doubled_vacuum=2*m.two_photon(T,0,vacuum=True)['down']
 m.check(abs(doubled_vacuum/8.2206-1)>0.99,'factor-two double counting not detected')
 omitted_stimulated=therm['up']/8.2206/np.exp(-therm['gap_J']/(m.KB*T))-1
 no_quad=m.two_photon(8000,.2);angular_error=no_quad['wrong_independent_angles_up']/no_quad['up']-1
 # An effective rate already contains cascades. Adding direct capture again
 # double counts that specific microscopic channel.
 e=m.eliminate(n['Q']);a_eff=e['S'][:3,3]/n['ne'];a_dir=np.array([r['alpha_m3_s'] for r in n['boundfree'][:3]])
 double_capture_relative=a_dir/a_eff
 m.check(min(double_capture_relative)>.1,'double-capture counterexample lost')
 # Atom number/energy in the eliminated lift cannot be discarded.
 hi=m.network(8000,8000,.05,1e8);eh=m.eliminate(hi['Q']);pr=np.array([.25]*4);lift=m.lift(eh,pr)
 omitted_fast=float(sum(lift[eh['f']]))
 m.check(omitted_fast>1e-5,'fast population storage counterexample too small')
 # There is no requirement that a zero-frequency approximation fit finite
 # residence-time dynamics, but passing it off as exact is explicitly refuted.
 results=json.loads((P/'SOURCE_CASCADE_RESULTS.json').read_text())
 dynamic=results['dynamic_memory_test'];m.check(dynamic['instant_exit_routing_max_retained_L1_error']>.9,'instantaneous routing false equivalence not detected')
 # Test propagation of nonzero photon chemical potential around an allowed cycle.
 eta=.3;aff=m.cycle_affinity(T,0,eta)
 m.check(abs(aff-2*eta)<1e-11 and abs(aff)>.5,'BE cycle incorrectly declared detailed balanced')
 source_lock=json.loads((P/'sources/PROVENANCE.json').read_text())['HYREC_source_files']
 for name,h in source_lock.items():m.check(sha(P/'sources'/name)==h,'original atomic source changed')
 bass=json.loads((ROOT/'research/typeii_host_preflight_20261101/SOURCE_LOCK.json').read_text())['original_git_blobs_sha1']
 for path,want in bass.items():
  got=subprocess.check_output(['git','hash-object',path],cwd=ROOT,text=True).strip();m.check(got==want,'original BASS source changed')
 for filename in ('cascade.py','run_cascade_sources.py','verify_kernels.py','verify_final.py'):
  tree=ast.parse((P/filename).read_text());m.check(not any(isinstance(x,ast.Assert) for x in ast.walk(tree)),'bypassable science validation assert')
 out={'analytic_contracts':16,'normal_optimized_unit_cases':32,'execution_receipts':receipts,
  'optimized_science_outputs_byte_exact':before,'invalid_cases_rejected':rejected,'original_HYREC_source_files':len(source_lock),'original_BASS_blobs':len(bass),
  'double_count_half_spectrum_vacuum_rate_s':doubled_vacuum,
  'omit_stimulated_down_thermal_ratio_relative_error':float(omitted_stimulated),
  'independent_angle_approximation_two_gamma_up_error_T8000_beta02':float(angular_error),
  'add_direct_capture_on_effective_relative_errors':double_capture_relative.tolist(),
  'drop_fast_population_mass_at_T8000':omitted_fast,
  'BE_eta03_cycle_log_affinity':aff,
  'instant_initial_fast_routing_max_L1_error':dynamic['instant_exit_routing_max_retained_L1_error'],
  'same_author_hostile_review':'PERFORMED_NOT_BLIND','distinct_author_referee':'NOT_RUN','native_subagent':'NOT_RUN',
  'limits':['fixed proper electron reservoir, not closed electron feedback','six bound states only','finite-support parent bound-free data','optically thin prescribed radiation, no line escape/trapping','unaligned leading nonrelativistic atom and E1E1 angular kernel','stationary Schur not exact chronological generator','no native HYREC replacement or new cosmological xe/optical depth']}
 (P/'VERIFICATION_AND_HOSTILE.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
