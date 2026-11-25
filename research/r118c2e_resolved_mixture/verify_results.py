"""Bounded C2E numerical evidence and raw source/output identity check."""
import pathlib,json,gzip,hashlib,re,sys,math,numpy as np
d=pathlib.Path(__file__).resolve().parent
read=lambda f:json.loads((d/f).read_text())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
s=read('SOURCE_RESULTS.json');par=read('SOURCE_PARITY.json');c=read('CLOSURE_RESULTS.json');r=read('REPLAY_RESULTS.json');l=read('REPLAY_LOCAL.json');p=read('SOURCE_RECEIPT.json')
assert s['pairs']==459 and s['samples']==73304 and s['levels']==[1,2,4,8]
assert s['max_marginal']<2e-12 and s['max_same_sym']<2e-12 and par['normalized_density_gap']<2e-12
assert sha(d/'INTEGRATED_SOURCE.npz')==par['integrated_sha256']
with np.load(d/'INTEGRATED_SOURCE.npz') as q:
 for n in [1,2,4,8]:
  v=q[f'Q{n}'];assert v.shape==(459,n+1,n+1) and np.all(np.isfinite(v)) and v.min()>=0
assert [q['subcells'] for q in c]==[1,2,4,8]
for q in c:
 assert q['thermal_activity_deviation']<2e-14
 assert q['cases'][0]['aware_per_photon_s']<2e-18 and q['cases'][0]['old_per_photon_s']>1e-15
for i in [1,2,3,4,5]:
 assert all(a['cases'][i]['aware_error']>b['cases'][i]['aware_error'] for a,b in zip(c,c[1:]))
 assert c[-1]['cases'][i]['aware_error']<1e-3
assert r['binary_sha256']==l['binary_sha256']==p['binary_sha256']
cs=r['cases']+l['cases'];assert len(r['cases'])==13 and len(l['cases'])==5
assert len({x['case'] for x in cs})==18 and all(x['status']=='PASS_SCOPED' for x in cs)
mk=('b3_gap','b4_gap','m0_gap')
replay_metrics={k:max(x['metrics'][k] for x in cs) for k in mk}
assert replay_metrics['b3_gap']<2e-12 and replay_metrics['b4_gap']<2e-12
assert all(x['metrics']['min_weight']>=0 for x in cs)
rk=('temperature_escape_number','temperature_escape_energy','temperature_tail_number_bound','temperature_tail_energy_bound','temperature_tail_count','temperature_number_defect','temperature_material_energy_defect','temperature_projection_energy_defect','temperature_stage_residual')
replay_run={k:max(x['run'][k] for x in cs) for k in rk}
assert max(replay_run[k] for k in rk if k!='temperature_tail_count')<2e-12
assert replay_run['temperature_tail_number_bound']<1e-270 and replay_run['temperature_tail_energy_bound']<1e-270
a=read('MIXED_RESULTS.json')+read('MIXED_LOCAL.json');ratio=read('RATIO_RESULTS.json')
assert len(a)==20 and len(ratio)==2 and sum(len(x['refinements']) for x in a)==24
by={x['case']:x for x in a+ratio};assert len(by)==22
max_poly={k:max(x[k] for x in a+ratio) for k in ('poly_activity_relative_error','poly_A_absolute_error','poly_f_relative_error','max_parent_row_defect')}
assert max(max_poly.values())<2e-12
v=lambda n:by[n]['continuum_energy_j_m3_s']
assert all(v(n)<0 for n in by if n.startswith(('early_','near_t','near_local','near_wide','near_ang')))
assert v('flrw_hot_0p1pct')<0<v('flrw_cold_0p1pct')
assert abs(v('near_flrw'))<1e-36 and v('ratio_hot')<0<v('ratio_cold')
for x in a:
 if x['refinements'] and x['case']!='near_flrw':
  assert x['refinements'][-1]['relative_error']<.0021
def rel(x,y):return abs(x-y)/abs(y)
convergence=dict(early_1024_to_2048=rel(v('early_t1024'),v('early_t2048')),near_local_512_to_1024=rel(v('near_local_512'),v('near_local_1024')),near_local_32_to_72=rel(v('near_local_512'),v('near_local_ang72')),bath_ratio_hot_to_matched=abs(v('ratio_hot')/v('near_local_1024')),bath_ratio_cold_to_matched=abs(v('ratio_cold')/v('near_local_1024')))
assert convergence['early_1024_to_2048']<.001 and convergence['near_local_512_to_1024']<.01 and convergence['near_local_32_to_72']<.03
def tests(name):
 q=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',gzip.decompress((d/'logs'/name).read_bytes()).decode())
 assert q and all(x=='ok' and int(z)==0 for x,y,z in q)
 return sum(int(y) for x,y,z in q)
assert tests('all.log.gz')==274 and tests('examples.log.gz')==3
if '--raw' in sys.argv:
 for path,digest in p['source_hashes'].items():assert sha(path)==digest,path
 for x in cs:
  cmd=x['command'];exe=cmd[0];out=pathlib.Path(cmd[cmd.index('--out')+1])
  assert sha(exe)==p['binary_sha256']
  for f,digest in x['hashes'].items():assert sha(out/f)==digest,(out,f)
 raw=pathlib.Path(p['raw_root'])/'bass_r118c2e_source'
 with np.load(d/'INTEGRATED_SOURCE.npz') as out:
  for n in (1,2,4,8):
   with np.load(raw/f'REFINE_{n}.npz') as z:
    q=z['density'];w=z['weight'];off=z['offset']
    ref=np.array([np.einsum('m,mij->ij',w[l:r],q[l:r]) for l,r in zip(off[:-1],off[1:])])
    assert np.array_equal(ref,out[f'Q{n}'])
result=dict(research_id='R118-C2E-LOCALLY-RESOLVED-MIXED-SPECTRAL-REPLAY-AND-SOURCE-CLOSURE-01',status='IMPLEMENTATION_VERIFIED_SCOPED',line_sampling_status='COLD_MIXTURE_UNDERRESOLUTION_CLOSED_SCOPED',source_closure_status='FREQUENCY_REFINED_ACTION_NUMERICALLY_CHECKED',feedback_status='BLOCKED_SOURCE_BATH_CALIBRATION_AND_LIVE_LINE_EVOLUTION',science_promotion=False,source=s,source_parity=par,closure=c,replay_cases=18,replay_metrics=replay_metrics,replay_run=replay_run,mixed_actions=22,refined_mixed_actions=24,mixed=a,ratio=ratio,convergence=convergence,poly_max=max_poly,rust_tests=274,example_tests=3,provenance=p,next_id='R118-C2F-SOURCE-STATE-CALIBRATED-LIVE-RESONANCE-EVOLUTION-01')
result['receipt_sha256']={str(f.relative_to(d)):sha(f) for f in sorted(d.rglob('*')) if f.is_file() and f.name!='ACCEPTANCE.json' and '__pycache__' not in str(f)}
(d/'ACCEPTANCE.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('VERIFIED',result['status'],len(cs),'replays',len(a+ratio),'actions',result['rust_tests']+result['example_tests'],'tests',convergence)
