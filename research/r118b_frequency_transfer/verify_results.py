"""Audit persisted R118-B receipts. Does not rerun the solver or promote science."""
import collections, gzip, hashlib, json, math, pathlib, re
root=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads((root/p).read_text())
sha=lambda p:hashlib.sha256((root/p).read_bytes()).hexdigest()
sources=['CORE_RESULTS.json','DENSE_RESULTS.json','PROJECTED_REFINEMENT.json']
records=[read(p) for p in sources]
for key in ('binary_sha256','reference_sha256','ionization_sha256','velocity_sha256'):
 assert all(r[key]==records[0][key] for r in records),key
assert sha('early_table_xe.tsv')==records[0]['ionization_sha256']
assert all(sha(p)==h for p,h in records[0]['velocity_sha256'].items())
all_cases=[x for r in records for x in r['cases']]
good=[x for x in all_cases if x['status']=='PASS_SCOPED']
bad=[x for x in all_cases if x['status']!='PASS_SCOPED']
by={x['case']:x for x in good}
assert len(good)==len(by)==65
assert len(bad)==4 and all(x['status']=='FAIL_EXECUTION' and x['case'] in by and 'n_mu >= 4' in x['stderr'] for x in bad)
assert collections.Counter(x['method'] for x in good)=={'union':53,'projected':12}
bounds={'number_collision_defect':2e-11,'material_energy_preprojection_defect':2e-11,'line_number_defect':2e-11,'normal_energy_balance_defect':2e-10,'number_continuity_trapezoid_defect':2e-8,'observer_trace_error':2e-10,'max_fv_stage_residual':2e-13}
keys=list(bounds)+['material_energy_projection_defect','max_fv_stage_iterations']
maxima={k:max(abs(x['metrics'][k]) for x in good) for k in keys}
assert all(math.isfinite(v) for v in maxima.values())
assert all(maxima[k]<v for k,v in bounds.items()),maxima
assert min(x['metrics']['min_screen_relative'] for x in good)>=-1e-10
dense=read('DENSE_ORACLE.json')
assert len(dense)==4 and all(x['case'] in by and x['max_component_relative_global_scale']<2e-11 for x in dense)
line=read('LINE_ORACLE.json');lo={x['case']:x for x in line['cases']}
assert len(lo)==13 and all(k in by for k in lo)
assert all(lo[k]['relative_line_signal_l1']<1e-4 for k in ('monotone_f1024','turn_f1024'))
assert lo['narrow_line']['relative_line_signal_l1']<1e-3
assert all(x['relative_error']<1e-12 for x in line['tangency'])
def ratio(v):return [abs((a-b)/(b-c)) for a,b,c in zip(v,v[1:],v[2:])]
pe=[by[f'projected_t{n}']['last']['energy_centered'] for n in (2,4,8,16)]
pr=ratio(pe);assert all(3.7<r<4.4 for r in pr)
ue=[by[f'cold_t{n}']['last']['energy_centered'] for n in (2,4,8,16)]
ce=[by[f'cold_f{n}']['metrics']['moment_B4_gap'] for n in (128,256,512,1024)]
assert all(a>b for a,b in zip(ce,ce[1:])) and ce[-1]<3e-4
te=[lo[f'turn_t{n}']['relative_fv_line_signal_l1'] for n in (8,16,32,64)]
assert 3.5<te[-2]/te[-1]<4.5
early=[by[n] for n in ('early_host_line','early_host_line_f512','early_host_line_f1024','early_host_line_f2048')]
assert all(x['metrics']['min_drift']<0<x['metrics']['max_drift'] and x['metrics']['turning_rays']==16 for x in early)
en=[abs(x['last']['line_number_centered']) for x in early];assert all(a>b for a,b in zip(en,en[1:]))
assert by['early_host_line_ang72']['metrics']['turning_rays']==36
for k in ('projected_early_refine_512','projected_early_refine_1024'):assert by[k]['metrics']['turning_rays']==16
legacy=[v for x in good for v in x.get('legacy_byte_equal',{}).values()]
reg=read('REGRESSION.json')
legacy.extend(v for k,x in reg.items() if k!='default_projected' for v in x['byte_equal'].values())
assert len(legacy)==160 and all(legacy)
assert len(reg['default_projected']['byte_equal'])==3 and all(reg['default_projected']['byte_equal'].values())
def tests(p):
 s=gzip.decompress((root/'logs'/p).read_bytes()).decode()
 results=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',s)
 assert results and all(k=='ok' and f=='0' for k,n,f in results)
 return sum(int(n) for k,n,f in results)
assert tests('all_final.log.gz')==245 and tests('examples_final.log.gz')==3
out=dict(schema='bass.r118b.acceptance/1',research_id='R118-B-NONMONOTONE-FREQUENCY-TRANSFER-01',status='IMPLEMENTATION_VERIFIED_SCOPED',parent='9eeedf1a3cfbe1d80a68de77af4339db828ff72f',binary_sha256=records[0]['binary_sha256'],reference_sha256=records[0]['reference_sha256'],ionization_sha256=records[0]['ionization_sha256'],verified_cases=65,methods={'union':53,'projected':12},superseded_configuration_failures=[dict(case=x['case'],stderr=x['stderr']) for x in bad],tests={'rust':245,'examples':3},events={k:int(sum(x['metrics'][k] for x in good)) for k in ('collision_events','collision_subcells','line_cells')},max_abs_metrics=maxima,legacy_byte_equal=160,default_explicit_parity=3,dense_max_absolute=max(x['max_component_absolute_error'] for x in dense),dense_max_relative=max(x['max_component_relative_global_scale'] for x in dense),line_oracle=lo,tangency=line['tangency'],projected_time_energy_ratios=pr,union_time_energy_ratios=ratio(ue),cold_B4_absolute_gaps=ce,turn_fv_time_l1_errors=te,early_line_number=[x['last']['line_number_centered'] for x in early],early_line_material_energy=[x['last']['line_material_energy_centered'] for x in early],early_thomson_projection_energy=[x['last']['thomson_projection_energy_centered'] for x in early],early_drift_range=[early[-1]['metrics']['min_drift'],early[-1]['metrics']['max_drift']],projected_early_line_number={k:by[k]['last']['line_number_centered'] for k in ('projected_early_host_line','projected_early_refine_512','projected_early_refine_1024')},scope='Fixed accepted geometry/cold recoil replay; prescribed finite line, no population or energy feedback; number-weighted piecewise constant reconstruction; projection energy error not physical heat.',science_promotion=False,remaining=['Dual number-energy conservative spectral reconstruction','True resonance redistribution and calibrated atomic profiles','Self-consistent REC populations and thermal/recoil feedback','Frequency and angular convergence over long histories'],next_id='R118-C-CONSERVATIVE-RESONANCE-REDISTRIBUTION-01')
out['receipt_sha256']={p:sha(p) for p in sources+['DENSE_ORACLE.json','LINE_ORACLE.json','REGRESSION.json','INITIAL_TRIAL.json.gz','early_table_xe.tsv','rest_velocity.tsv','turn_velocity.tsv']+[str(p.relative_to(root)) for p in sorted((root/'logs').glob('*.gz'))]}
(root/'ACCEPTANCE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('status','verified_cases','methods','tests','events','max_abs_metrics','legacy_byte_equal','dense_max_absolute','projected_time_energy_ratios','union_time_energy_ratios','early_drift_range','projected_early_line_number')},indent=2))
