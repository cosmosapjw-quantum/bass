"""Scoped C2D result and source provenance verification."""
import pathlib,json,gzip,hashlib,re,sys,numpy as np
d=pathlib.Path(__file__).resolve().parent
read=lambda f:json.loads((d/f).read_text())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
s=read('LIFT_RESULTS.json');g=read('GRAPH_RESULTS.json');r=read('RESULTS.json');o=read('ORACLE.json');c=read('CONTINUUM_NATIVE.json');p=read('SOURCE_RECEIPT.json')
assert len(s['pairs'])==459
off=[x for x in s['pairs'] if x['i']!=x['j']];same=[x for x in s['pairs'] if x['i']==x['j']]
assert len(off)==442 and len(same)==17 and max(x['release_error'] for x in off)<2e-12
assert max(x['raw_symmetry'] for x in same)<2e-12
assert max(x['marginal_error'] for x in s['pairs'])<2e-12
assert max(s['node_errors'].values())<2e-12
assert s['lift_sha256']==r['lift_sha256']==sha(d/'LIFT.npz')
z=np.load(d/'LIFT.npz',allow_pickle=False)
assert z['density'].shape==(73304,4) and np.all(z['density']>=0) and np.all(np.isfinite(z['density'])) and np.min(z['weight'])>0
# Independently reconstruct the two frequency marginals from the committed
# quadrature arrays. Same-cell cross blocks were symmetrized after audit.
marginal=0.
for k,(i,j) in enumerate(z['pairs']):
 sl=slice(z['offset'][k],z['offset'][k+1]);q=z['density'][sl];raw=z['raw'][sl];u=z['bounds'][i];v=z['bounds'][j]
 xt=np.repeat(u,2);xs=np.tile(v,2)
 projected=np.stack([q.sum(axis=1),q@xt,q@xs,q@(xt-xs)],axis=1)
 marginal=max(marginal,float(np.max(abs(projected-raw)/np.maximum(raw[:,0,None],1e-300))))
assert marginal<2e-12
assert [x['angles'] for x in g]==[26,50,110,32]
assert all(x['blocks']==1819 and x['fallback_blocks']==0 and x['row_error']<5e-13 for x in g)
assert all(x['maximum_pair_detuning_error']<2e-12 and x['detuning_scaled_error']<2e-10 for x in g)
assert all(a['force_scaled_error']>b['force_scaled_error'] for a,b in zip(g[:2],g[1:3]))
cs=r['cases'];by={x['case']:x for x in cs}
assert len(cs)==len(by)==30 and all(x['status']=='PASS_SCOPED' for x in cs)
assert sum(int(x['run']['steps']) for x in cs)==248
assert r['binary_sha256']==p['binary_sha256']==c['binary_sha256']
keys=['number_defect','centered_balance_defect','max_collision_number_defect','max_drift_number_defect','max_drift_centered_defect','max_core_number_defect','max_exterior_number_defect','max_core_centered_defect','max_exterior_centered_defect','action_number_defect','action_force_defect','max_free_increase']
maxima={k:max(abs(x['run'][k]) for x in cs) for k in keys}
assert max(maxima.values())<2e-10
assert all(x['run']['minimum_occupation']>=0 for x in cs)
non=[x for x in cs if x['case']!='lifted_equilibrium']
assert max(x['metrics']['action_relative'] for x in non)<2e-10
assert max(x['run']['max_collision_centered_defect'] for x in non)<2e-8
assert max(x['run']['max_force_defect'] for x in non)<2e-9
eq=by['lifted_equilibrium']
eq_scaled=abs(eq['run']['collision_x'])/eq['metrics']['initial_mass']
assert eq_scaled<2e-14
live=[x for x in cs if x['drift']];assert len(live)==9
assert all(min(x['run'][k] for k in ('red_in','red_out','blue_in','blue_out'))>0 and x['run']['interface_atom_energy']==0 for x in live)
proj={k:max(x['metrics'][k] for x in live) for k in ('core_projection_to_collision','exterior_projection_to_collision','absolute_balance_to_collision')}
assert proj['core_projection_to_collision']<1e-8 and proj['exterior_projection_to_collision']<1e-8 and proj['absolute_balance_to_collision']<1e-6
seq=[by[f'time_{n}']['metrics']['ode_signal_l1'] for n in (1,2,4,8,16,32)]
ratios=[x/y for x,y in zip(seq,seq[1:])];assert all(3.9<x<4.1 for x in ratios)
mixed=[x for x in cs if x.get('mixed_receipt')];assert len(mixed)==6
for bins in (512,1024,2048):
 a=by[f'mixed_{bins}_exp'];b=by[f'mixed_{bins}_compact']
 assert a['run']['collision_energy_j_m3']>0>b['run']['collision_energy_j_m3']
 for q in (a,b):
  m=q['mixed_receipt'];assert m['coarse_cells_covering_line_max']<=2
  assert max(m['scalar_number_partition_defect'],m['scalar_energy_partition_defect'])<2e-12
assert len(c['cases'])==5 and max(x['native_vs_graph_per_photon_s'] for x in c['cases'])<2e-13
assert o['relative_endpoint_l1']<2e-10 and max(o[k] for k in ('escape_error','escape_x_error','work_x_error'))<2e-10
def count(name):
 t=gzip.decompress((d/'logs'/name).read_bytes()).decode();q=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',t)
 assert q and all(a=='ok' and int(c)==0 for a,b,c in q);return sum(int(b) for a,b,c in q)
assert count('all.log.gz')==271 and count('examples.log.gz')==3
if '--raw' in sys.argv:
 for path,digest in (p['source_hashes']|p['previous_case_hashes']|p['mixed_input_hashes']).items():assert sha(path)==digest,path
 for x in cs:
  exe,gp,case,out=x['command']
  assert sha(exe)==r['binary_sha256'] and sha(gp)==x['graph_sha256'] and sha(case)==x['case_sha256']
  for file,digest in x['hashes'].items():assert sha(pathlib.Path(out)/file)==digest,(out,file)
 for x in c['cases']:
  exe,gp,case,out=x['native_command']
  assert sha(exe)==c['binary_sha256'] and sha(gp)==c['graph_sha256'] and sha(case)==x['input_sha256']
  for file,digest in x['hashes'].items():assert sha(pathlib.Path(out)/file)==digest
 assert sha(o['command'][2])==o['input_sha256']
 assert sha(o['command'][0])==r['binary_sha256']
 for f,digest in o['hashes'].items():assert sha(pathlib.Path(o['command'][3])/f)==digest
out=dict(research_id='R118-C2D-DUAL-MOMENT-SOURCE-ENERGY-AND-MIXED-SPECTRUM-COUPLING-01',status='IMPLEMENTATION_VERIFIED_SCOPED',projection_status='LOCAL_CENTROID_PROJECTION_BLOCKER_CLOSED',feedback_status='BLOCKED_UNRESOLVED_MIXED_LINE_AND_SOURCE_CLOSURE',science_promotion=False,source_pairs=459,lifted_frequency_nodes=70,source_marginal_max=marginal,source_release_offdiagonal_max=max(x['release_error'] for x in off),source_samecell_release_max=max(x['release_error'] for x in same),angular=g,cases=30,steps=248,continuum_action_cases=5,rust_tests=271,example_tests=3,metrics_max=maxima,non_null_collision_centered_max=max(x['run']['max_collision_centered_defect'] for x in non),non_null_force_max=max(x['run']['max_force_defect'] for x in non),equilibrium_roundoff_per_photon=eq_scaled,equilibrium_relative_centered_defect=eq['run']['max_collision_centered_defect'],equilibrium_relative_force_defect=eq['run']['max_force_defect'],time_signal_errors=seq,time_ratios=ratios,live_projection_max=proj,live=[dict(case=x['case'],metrics=x['metrics']) for x in live],mixed=[dict(case=x['case'],collision_energy_j_m3=x['run']['collision_energy_j_m3'],receipt=x['mixed_receipt']) for x in mixed],continuum=c['cases'],remap_oracle=o,provenance=p,next_id='R118-C2E-LOCALLY-RESOLVED-MIXED-SPECTRAL-REPLAY-AND-SOURCE-CLOSURE-01')
out['receipt_sha256']={str(f.relative_to(d)):sha(f) for f in sorted(d.rglob('*')) if f.is_file() and f.name!='ACCEPTANCE.json' and '__pycache__' not in str(f)}
(d/'ACCEPTANCE.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('VERIFIED',out['status'],out['cases'],out['rust_tests']+out['example_tests'],out['projection_status'],out['feedback_status'])
print('max projection',proj,'marginal',marginal)
