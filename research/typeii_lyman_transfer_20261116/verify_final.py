#!/usr/bin/env python3
"""One bounded same-author verification/hostile pass, with scoped identities."""
import ast,json,hashlib,os,subprocess,sys
from pathlib import Path
import numpy as np
from line_transfer import *
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 tests=[]
 for opt in (False,True):
  cmd=[sys.executable]+(['-O'] if opt else [])+[str(HERE/'test_line.py')]
  cp=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
  (HERE/('UNIT_OPTIMIZED.log' if opt else 'UNIT_NORMAL.log')).write_text(cp.stdout+cp.stderr)
  check(cp.returncode==0,'unit contracts');tests.append({'optimized':opt,'exit':cp.returncode,'cases':14})
 g=line_grid(3000.,cells=24)
 invalid=[('negative_depth',lambda:sobolev(-1.)),('nonfinite_depth',lambda:sobolev(np.inf)),
 ('nonunit_direction',lambda:drift(np.zeros(5),np.zeros(5),np.array([[2.,0,0]]))),
 ('superluminal_tilt',lambda:drift(np.array([0.,0,0,0,1.]),np.zeros(5),np.array([[1.,0,0]]))),
 ('negative_temperature',lambda:line_grid(-2.)),('wide_band',lambda:line_grid(3000.,halfwidth=1e5)),
 ('bad_profile_edges',lambda:profile_masses(np.array([0.,1.,.5]),.01)),
 ('negative_damping',lambda:profile_masses(np.array([0.,1.]),-.01)),
 ('negative_occupation',lambda:collision(g,1e8,1e-5,-np.ones(24),3000.)),
 ('negative_density',lambda:collision(g,-1.,1.,np.zeros(24),3000.)),
 ('zero_monotonic_drift',lambda:frozen_steady(g,1e8,1e-5,3000.,0.)),
 ('inverted_medium',lambda:frozen_steady(g,0.,1.,3000.,1e-13)),
 ('excess_emitted_probability',lambda:singleflight(np.array([1.,1.]),np.ones(2))),
 ('nonconservative_fate',lambda:resonance_fates(np.eye(7)))]
 rejected=[]
 for name,fn in invalid:
  try:fn()
  except ValueError:rejected.append(name)
  else:raise RuntimeError('invalid input accepted '+name)
 files=['KERNEL_VERIFICATION.json','CLOSED_ATOM_PHOTON_TRACE.csv','SOURCE_LINE_RESULTS.json','DIRECTIONAL_LINE_DIAGNOSTICS.csv','FINITE_LINE_BAND_FLUXES.csv','RESONANCE_FATE_RESULTS.json','RESONANCE_FATES.csv']
 before={f:sha(HERE/f) for f in files}
 replay=[]
 for name in ('verify_kernels.py','run_line_sources.py','source_resonance_fates.py'):
  cp=subprocess.run([sys.executable,'-O',str(HERE/name)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
  (HERE/(name+'_OPTIMIZED.log')).write_text(cp.stdout+cp.stderr);check(cp.returncode==0,'science replay '+name)
  check(all(sha(HERE/f)==v for f,v in before.items()),'deterministic physics output changed '+name)
  replay.append({'program':name,'exit':cp.returncode})
 # Oldest source roots and all immediate source identities are verified separately
 # from the numeric equivalence of freshly integrated characteristic curves.
 lock=json.loads((ROOT/'research/typeii_host_preflight_20261101/SOURCE_LOCK.json').read_text())['original_git_blobs_sha1']
 for rel,want in lock.items():
  got=subprocess.check_output(['git','hash-object',str(ROOT/rel)],text=True).strip();check(got==want,'original BASS source drift')
 for name in ('line_transfer.py','verify_kernels.py','run_line_sources.py','source_resonance_fates.py'):
  check(not any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse((HERE/name).read_text()))),'removable scientific gate')
 r=json.loads((HERE/'SOURCE_LINE_RESULTS.json').read_text());geom=np.genfromtxt(HERE/'DIRECTIONAL_LINE_DIAGNOSTICS.csv',delimiter=',',names=True)
 trace=np.genfromtxt(ROOT/'research/typeii_cascade_effective_20261116/SOURCE_TRACE_STATIONARY.csv',delimiter=',',names=True)
 # Wrong local clock: H*kappa*Gamma instead of H*kappa/D. The erroneous
 # inference uses the homogeneous atomic reaction clock on a photon path.
 beta=np.repeat(trace['beta'],26);gamma=1/np.sqrt(1-beta*beta)
 wrong_clock=gamma*geom['D']-1
 # Wrong isotropic expansion substitutes Hn for Hray.
 wrong_iso=geom['D']/geom['kappa']-1
 check(np.max(abs(wrong_clock))>.04 and np.max(abs(wrong_iso))>.1,'wrong clock/drift controls missing')
 z1100=next(x for x in r['source_probes'] if abs(x['z_mean']-1100)<1e-6)
 # Discarding true surviving photons is distinct from discarding only the
 # tiny profile probability. Record optical support, not underflowed exp(-tau).
 support={'finite_band_profile_mass':z1100['finite_band'][1]['profile_mass'],
 'formal_unrepresented_symmetric_red_wing_depth':z1100['missing_symmetric_red_wing_tau_20_range'],
 'log_single_flight_survival_beyond_band_if_symmetric_frozen_assumed':[-x for x in z1100['missing_symmetric_red_wing_tau_20_range']],
 'warning':'formal symmetric-tail falsifier; thermodynamic asymmetry, scattering and time evolution change a real escape calculation'}
 # Actual-source spatial/frequency resolution comparison, fixed width and inputs.
 a=geom[np.argmin(abs(geom['z_mean']-1100))];i=int(a['source_index']);T=float(trace['Tm_K'][i]);Tn=float(trace['Tn_K'][i]);D=float(a['D']);hr=float(a['H_atom_path_s'])
 vals=[]
 for n in (160,320,640,1280):
  gg=line_grid(T,halfwidth=20.,cells=n);fb=float(planck(H*gg['nu_edges'][-1]/(KB*Tn*D)))
  v=frozen_steady(gg,z1100['n_lower_trace_m3'],z1100['n_upper_trace_m3'],T,hr,fb)
  vals.append({'cells':n,'red_flux':v['red_out'],'collision_net':v['net_line_emission']})
 ds=[abs(vals[k]['red_flux']-vals[-1]['red_flux']) for k in range(3)]
 check(ds[2]<ds[0],'actual source grid refinement not improving')
 # Deliberately omit heat from the finite-bin exchange energy ledger.
 gt=line_grid(3000.,halfwidth=30.,cells=100);fp=planck(H*gt['nu']/(KB*3000.))
 nu=3e8*np.exp(-E0/(KB*3000.));right=collision(gt,1e8,nu,fp,3000.,True);wrong=collision(gt,1e8,nu,fp,3000.,False)
 anis=np.exp(-((gt['x']-10.)/3.)**2)*1e-10;ener=collision(gt,1e8,1e-6,anis,3000.)
 heat_missing=abs(ener['photon_energy']+ener['bound_energy'])/ener['gross_energy']
 check(wrong['balance_relative']>1e-4 and heat_missing>1e-6,'thermal/energy falsifiers')
 fate=json.loads((HERE/'RESONANCE_FATE_RESULTS.json').read_text())['source_probes'][0]
 out={'unit_cases_each_mode':14,'unit_executions':28,'unit_receipts':tests,'invalid_cases_rejected':rejected,
 'optimized_source_replays':replay,'science_output_hashes':before,'source_files_original_BASS':len(lock),
 'wrong_photon_path_clock_max_relative_drift_error':float(np.max(abs(wrong_clock))),
 'wrong_isotropic_H_max_relative_drift_error':float(np.max(abs(wrong_iso))),
 'thermal_correct_balance_max':right['balance_relative'],'wrong_identical_profiles_max_thermal_imbalance':wrong['balance_relative'],
 'omit_detuning_heat_relative_energy_defect':float(heat_missing),'finite_band_false_escape_control':support,
 'actual_source_band_grid_refinement':vals,'source_tagged_fate_total_over_true_ionization':1/fate['ionization_probability'],
 'self_hostile_review':'PERFORMED_SAME_AUTHOR_NOT_BLIND','native_subagent':'NOT_RUN','distinct_author_referee':'NOT_RUN',
 'preservation':'GitHub+host stage archives; external copies L2 onward blocked by observed ENOSPC, not claimed complete',
 'claim_gate':'finite local line interface and source-characteristic diagnostics, not global Lyman escape, redistribution, cosmic xe/tau or production readiness'}
 (HERE/'VERIFICATION_AND_HOSTILE.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k not in ('science_output_hashes','unit_receipts')},indent=2))
if __name__=='__main__':main()
