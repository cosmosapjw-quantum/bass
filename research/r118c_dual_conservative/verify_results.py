"""Verify bounded R118-C source, execution, and oracle receipts; no science promotion."""
import collections,gzip,hashlib,json,math,pathlib,re,sys
d=pathlib.Path(__file__).resolve().parent
read=lambda n:json.loads((d/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read('RESULTS.json');source=read('SOURCE_RECEIPT.json')
a=r['cases'];by={x['case']:x for x in a}
assert len(a)==len(by)==72 and all(x['status']=='PASS_SCOPED' for x in a)
assert source['binary_sha256']==r['binary_sha256']
assert len([x for x in a if x['case'].startswith('r117_he_') and x['case'] not in ('r117_he_i_rays','r117_he_i_continuum')])==12
keys=('number_collision_defect','material_energy_preprojection_defect','material_energy_projection_defect','line_number_defect','normal_energy_balance_defect','number_continuity_trapezoid_defect','max_fv_stage_residual','max_fv_stage_iterations','redistribution_number_defect','redistribution_energy_defect','pair_balance_defect','observer_trace_error')
mx={k:max(abs(x['metrics'][k]) for x in a) for k in keys}
for k,v in mx.items():
 if k=='max_fv_stage_iterations':continue
 assert v<(2e-8 if k=='number_continuity_trapezoid_defect' else 2e-11),(k,v)
assert all(x['metrics']['min_screen_relative']>=-1e-10 and x['metrics']['numerical_second_energy_moment']>=-1e-14 for x in a)
events={k:int(sum(x['metrics'][k] for x in a)) for k in ('collision_events','collision_subcells','line_cells','redistribution_cells')}
assert events==dict(collision_events=4364,collision_subcells=4368,line_cells=6640,redistribution_cells=504)
legacy=[v for x in a for v in x.get('legacy_byte_equal',{}).values()]
reg=read('REGRESSION.json');old=[v for x in reg.values() for v in x.values()]
assert len(legacy)==302 and all(legacy) and len(old)==34 and all(old)
dense=read('DENSE_ORACLE.json')
assert len(dense)==2 and all(x['dense_unknowns']==2754 and x['max_relative']<2e-11 for x in dense)
oracle=read('LINE_REDIST_ORACLE.json');line={x['case']:x for x in oracle['line']};red={x['case']:x for x in oracle['redistribution']}
assert len(line)==18 and len(red)==4
assert max(line[k]['relative_continuum_hat_L1'] for k in ('monotone_f1024','turn_f1024'))<3e-4
assert line['narrow_f1024']['relative_continuum_hat_L1']<5e-3
assert red['redist_t128']['relative_l1_signal']<2e-5
def ratios(x):return [abs((a-b)/(b-c)) for a,b,c in zip(x,x[1:],x[2:])]
cold=[by[f'cold_t{n}']['last']['energy_centered'] for n in (2,4,8,16)]
pr=ratios(cold);assert all(3.7<v<4.4 for v in pr)
rr=[red[f'redist_t{n}']['relative_l1_signal'] for n in (16,32,64,128)]
red_ratios=[x/y for x,y in zip(rr,rr[1:])];assert all(3.7<v<4.4 for v in red_ratios)
turn=[line[f'turn_t{n}']['relative_nodal_L1'] for n in (8,16,32,64,128)]
assert 3.7<turn[-2]/turn[-1]<4.4
cold_mesh=[by[f'cold_f{n}']['metrics'] for n in (64,128,256,512,1024)]
assert all(x['moment_B4_gap']<2e-10 for x in cold_mesh)
spread=[x['numerical_second_energy_moment'] for x in cold_mesh]
assert all(x>y for x,y in zip(spread,spread[1:]))
early=[by[f'early_line_f{n}'] for n in (128,256,512,1024,2048)]
assert all(x['metrics']['min_drift']<0<x['metrics']['max_drift'] and x['metrics']['turning_rays']==16 for x in early)
assert by['early_line_ang72']['metrics']['turning_rays']==36
q=early[-1]['last']
projection_to_line=abs(q['thomson_projection_energy_centered']/q['line_material_energy_centered'])
assert projection_to_line<1e-6
assert abs(q['line_projection_energy_centered'])<1e-12
assert all(by[f'early_cold_f{n}']['metrics']['moment_B4_gap']<2e-10 for n in (128,256,512,1024,2048))
assert by['cold_beta_0.85_wide']['metrics']['moment_B4_gap']<2e-10
assert by['cold_beta_0.85']['last']['escaped_number_centered']>1e-8
assert by['cold_beta_0.85_wide']['last']['escaped_number_centered']<1e-12
assert by['cold_thick']['metrics']['collision_subcells']>by['cold_thick']['metrics']['collision_events']
def tests(n):
 text=gzip.decompress((d/'logs'/n).read_bytes()).decode()
 rows=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',text)
 assert rows and all(s=='ok' and f=='0' for s,_,f in rows)
 return sum(int(n) for _,n,_ in rows)
assert tests('all_final.log.gz')==252 and tests('examples_final.log.gz')==3
eq=gzip.decompress((d/'logs/equilibrium.log.gz').read_bytes()).decode()
m=re.search(r'Wien equilibrium relative L1 ([\de+.-]+), energy ledger ([\de+.-]+)',eq)
assert m and abs(float(m[1]))<1e-13 and abs(float(m[2]))<1e-15
if '--raw' in sys.argv:
 for x in a:
  p=pathlib.Path(x['command'][x['command'].index('--out')+1])
  for f,h in x['hashes'].items():assert sha(p/f)==h,(x['case'],f)
 for p,h in source['input_sha256'].items():assert sha(pathlib.Path(p))==h,p
 assert sha(pathlib.Path(a[0]['command'][0]))==r['binary_sha256']
prev=json.loads(gzip.decompress((d/'INITIAL_TRIAL.json.gz').read_bytes()))
assert len(prev['cases'])==68 and all(x['status']=='PASS_SCOPED' for x in prev['cases'])
out=dict(schema='bass.r118c.acceptance/1',research_id='R118-C-CONSERVATIVE-RESONANCE-REDISTRIBUTION-01',status='IMPLEMENTATION_VERIFIED_SCOPED',source=source,cases=72,tests={'rust':252,'examples':3,'new':7},events=events,legacy_byte_equal=336,metrics_max=mx,dense_oracle=dense,line_oracle=line,redistribution_oracle=red,cold_time_ratios=pr,redistribution_time_oracle_ratios=red_ratios,turn_time_nodal_oracle_errors=turn,cold_spread=spread,cold_B4_absolute_gaps=[x['moment_B4_gap'] for x in cold_mesh],early_line_number=[x['last']['line_number_centered'] for x in early],early_line_material_energy=[x['last']['line_material_energy_centered'] for x in early],early_thomson_projection_energy=[x['last']['thomson_projection_energy_centered'] for x in early],early_projection_to_line_abs_ratio=projection_to_line,early_spread=[x['metrics']['numerical_second_energy_moment'] for x in early],early_drift_range=[early[-1]['metrics']['min_drift'],early[-1]['metrics']['max_drift']],equilibrium={'relative_L1':float(m[1]),'energy_ledger':float(m[2])},scope='positive two-moment nodal measure; prescribed true absorption/emission and dilute reversible angle-coherent diffusion on fixed accepted history; not calibrated atomic transfer',science_promotion=False,remaining=['calibrated line diffusion/redistribution coefficients and Voigt wing physics','frequency-local high-order or adaptive reconstruction to reduce nodal diffusion','angular redistribution and stimulated scattering','source-owned atomic populations and energy/momentum feedback'],next_id='R118-C2-SOURCE-CALIBRATED-RESONANCE-KERNEL-01')
out['receipt_sha256']={str(p.relative_to(d)):sha(p) for p in sorted(d.glob('*.json')) if p.name!='ACCEPTANCE.json'}
out['receipt_sha256'].update({str(p.relative_to(d)):sha(p) for p in sorted((d/'logs').glob('*.gz'))})
out['receipt_sha256']['INITIAL_TRIAL.json.gz']=sha(d/'INITIAL_TRIAL.json.gz')
(d/'ACCEPTANCE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('status','cases','tests','events','legacy_byte_equal','metrics_max','cold_time_ratios','redistribution_time_oracle_ratios','early_projection_to_line_abs_ratio','early_drift_range','equilibrium','next_id')},indent=2))
