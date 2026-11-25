import pathlib,hashlib,gzip,json,re,sys,math,numpy as np
d=pathlib.Path(__file__).resolve().parent
read=lambda name:json.loads((d/name).read_text())
gz=lambda name:json.loads(gzip.decompress((d/name).read_bytes()))
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
s=read('SOURCE_RESULTS.json');r=read('RESULTS.json');g=read('GRAPH_RESULTS.json');o=read('ORACLE.json');rev=read('SOURCE_REVERSE.json');p=read('SOURCE_RECEIPT.json')
assert len(s['pairs'])==459 and len({(x['i'],x['j']) for x in s['pairs']})==459
off=[x for x in s['pairs'] if x['i']!=x['j']];same=[x for x in s['pairs'] if x['i']==x['j']]
assert len(off)==442 and len(same)==17
assert max(x['source_moment_error'] for x in off)<2e-12
assert sha(d/'SOURCE_MEASURE.npz')==s['measure_sha256']
m=np.load(d/'SOURCE_MEASURE.npz',allow_pickle=False)
assert np.all(np.isfinite(m['density'])) and np.min(m['density'])>=0 and np.min(m['weight'])>0
same_errors=[]
for lane,name in [('production',None),('reference','same_reference'),('refined','same_refined')]:
 q=s if name is None else gz(name+'.json.gz')
 x=[x for x in q['pairs'] if x['i']==x['j']]
 assert len(x)==17
 if name is not None:assert sha(d/(name+'.npz'))==q['measure_sha256']
 same_errors.append(dict(lane=lane,max_relative_to_release=max(z['source_moment_error'] for z in x)))
assert all(a['max_relative_to_release']>b['max_relative_to_release'] for a,b in zip(same_errors,same_errors[1:]))
assert len(rev)==4 and max(x['reverse_moment_gap'] for x in rev)<2e-12
assert [x['angles'] for x in g]==[26,50,110,302,974]
assert all(x['max_row_defect']<5e-13 for x in g)
assert all(a['weighted_pair_l1_l4']>b['weighted_pair_l1_l4'] for a,b in zip(g,g[1:]))
assert all(a['weighted_same_l1_l4']>b['weighted_same_l1_l4'] for a,b in zip(g,g[1:]))
for a in g:
 q=gz(f"GRAPH_o{a['order']}.json.gz");assert len(q['details'])==459 and all(q[k]==v for k,v in a.items())
cs=r['cases'];b={x['case']:x for x in cs}
assert len(b)==len(cs)==33 and all(x['status']=='PASS_SCOPED' and x['returncode']==0 for x in cs)
assert sum(x['steps'] for x in cs)==242
assert r['binary_sha256']==p['binary_sha256']
keys=('number_defect','energy_defect','max_collision_number_defect','max_collision_force_defect','max_drift_number_defect','max_drift_energy_defect','action_number_defect','action_force_defect','equilibrium_null_per_s','max_core_number_defect','max_exterior_number_defect')
mx={k:max(abs(x['run'][k]) for x in cs) for k in keys}
assert max(mx.values())<2e-10
assert all(x['run']['minimum_occupation']>=0 and x['run']['max_free_increase']==0 for x in cs)
assert all(x['metrics']['action_relative']<2e-12 for x in cs if x['init']!='equilibrium')
assert b['stress_equilibrium']['metrics']['action_abs']<2e-15
loc=[x for x in cs if x['init']=='localized']
assert len(loc)==7 and all(x['metrics']['old_counterexample_target_action']==0 and x['metrics']['minimum_action_at_zero']>=0 for x in loc)
seq=[b[f'time_{n}']['metrics']['ode_relative_signal_l1'] for n in (1,2,4,8,16,32)]
ratios=[x/y for x,y in zip(seq,seq[1:])];assert all(3.9<x<4.1 for x in ratios)
live=[x for x in cs if x['drift']]
assert len(live)==9 and all(x['run']['interface_atom_energy']==0 and min(x['run'][k] for k in ('red_in','red_out','blue_in','blue_out'))>0 for x in live)
assert len(o['pair'])==8 and max(x['relative_l1'] for x in o['pair'])<2e-12
assert o['drift']['relative_l1']<5e-11 and o['normal_force_relative_gap']<2e-12
def tests(name):
 t=gzip.decompress((d/'logs'/name).read_bytes()).decode();a=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',t)
 assert a and all(x=='ok' and int(z)==0 for x,y,z in a);return sum(int(y) for x,y,z in a)
assert tests('all_final.log.gz')==266 and tests('examples_final.log.gz')==3
if '--raw' in sys.argv:
 for path,digest in p['source_sha256'].items():assert sha(path)==digest,path
 for x in cs:
  exe,gp,case,out=x['command'];assert sha(exe)==r['binary_sha256'] and sha(gp)==x['graph_sha256'] and sha(case)==x['input_sha256']
  for name,digest in x['hashes'].items():assert sha(pathlib.Path(out)/name)==digest
 for x in o['pair']+[o['drift']]:
  for name,digest in x['hashes'].items():assert sha(pathlib.Path(x['command'][3])/name)==digest
 receipt=pathlib.Path(p['raw_root'])
 for lane in ('source_production','source_reference','same_reference','same_refined','source_trial'):
  src=receipt/('bass_r118c2c_'+lane);q=json.loads((src/'SOURCE_RESULTS.json').read_text());assert sha(src/'SOURCE_MEASURE.npz')==q['measure_sha256']
out=dict(research_id='R118-C2C-POSITIVE-SOURCE-EVENT-MEASURE-AND-BOUNDARY-COUPLING-01',status='IMPLEMENTATION_VERIFIED_SCOPED',positivity_status='POSITIVE_RECIPROCAL_FINITE_GRAPH',feedback_status='BLOCKED_PROJECTION_ENERGY_EXCEEDS_COLLISION_SIGNAL',science_promotion=False,source_pairs=442,same_cells=17,source_moment_max=max(x['source_moment_error'] for x in off),same_cell_refinement=same_errors,source_reverse_max=max(x['reverse_moment_gap'] for x in rev),angular=g,cases=33,steps=242,rust_tests=266,example_tests=3,metrics_max=mx,action_max_relative=max(x['metrics']['action_relative'] for x in cs if x['init']!='equilibrium'),equilibrium_absolute_action_error=b['stress_equilibrium']['metrics']['action_abs'],time_signal_relative_errors=seq,time_ratios=ratios,pair_oracle_max=max(x['relative_l1'] for x in o['pair']),drift_oracle=o['drift'],normal_force_oracle=o['normal_force_relative_gap'],live=[dict(case=x['case'],metrics=x['metrics'],projection_core=x['run']['projection_core'],projection_exterior=x['run']['projection_exterior']) for x in live],provenance=p,next_id='R118-C2D-DUAL-MOMENT-SOURCE-ENERGY-AND-MIXED-SPECTRUM-COUPLING-01')
out['receipt_sha256']={str(f.relative_to(d)):sha(f) for f in sorted(d.rglob('*')) if f.is_file() and f.name!='ACCEPTANCE.json' and '__pycache__' not in str(f)}
(d/'ACCEPTANCE.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('VERIFIED',out['status'],out['cases'],'native cases',out['rust_tests']+out['example_tests'],'tests',out['feedback_status'])
