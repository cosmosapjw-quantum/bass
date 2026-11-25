import pathlib,json,hashlib,gzip,re,math,sys
d=pathlib.Path(__file__).resolve().parent
read=lambda f:json.loads((d/f).read_text())
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
r=read('RESULTS.json');a=r['cases'];by={c['case']:c for c in a};o=read('ORACLE.json');source=read('SOURCE_RECEIPT.json')
assert len(a)==len(by)==88 and all(c['status']=='PASS_SCOPED' for c in a)
assert sum(c['steps'] for c in a)==8410 and source['binary_sha256']==r['binary_sha256']
keys=['number_defect','energy_balance_defect','max_step_number_defect','max_step_continuity_l1','max_step_energy_defect','max_nonlinear_scaled_residual','max_nonlinear_iterations','equilibrium_relative_l1']
mx={k:max(abs(c['metrics'][k]) for c in a if k in c['metrics']) for k in keys}
assert all(v<2e-10 for k,v in mx.items() if k!='max_nonlinear_iterations')
pm={k:max(c.get(k,0.) for c in o['profile']) for k in ('voigt_relative','dipole_relative','volume_relative','up_relative','down_relative')}
assert len(o['profile'])==88 and max(pm.values())<1e-9
assert len(o['linear'])==10 and max(c['dense_be_relative_l1'] for c in o['linear'])<2e-11
assert len(o['stiff'])==2 and max(c['high_precision_relative_l1'] for c in o['stiff'])<2e-12
assert len(o['bose'])==8 and max(c['nonlinear_root_be_relative_l1'] for c in o['bose'])<2e-11
for profile in ('voigt','dipole'):
 v=[c['continuous_time_relative_l1'] for c in o['linear'] if profile in c['case']]
 assert 1.8<v[-2]/v[-1]<2.2
for init in ('bose-pulse','bose-high'):
 v=[c['continuous_time_relative_l1'] for c in o['bose'] if c['case'].startswith(init)]
 assert 3.8<v[-2]/v[-1]<4.2
h=o['hummer']
assert h['rate_relative_gap']<1e-8 and h['cell_voigt_relative_gap']<1e-11
assert abs(h['dipole_FPA_cell_averaged_second_moment']/h['binned_second_moment']-1)<1e-3 and h['conditional_l2_factorization_l1']>0.1
assert h['source_sha256']==next(v for p,v in source['rec_source_sha256'].items() if p.endswith('full_hummer_reference.npz'))
m={c['case']:c for c in o['mesh']}
for model in ('voigt','dipole'):
 assert m[f'bench_{model}_stretched_wide128']['mean_abs_error']<m[f'bench_{model}_uniform_wide512']['mean_abs_error']
 assert m[f'bench_{model}_stretched_wide512']['mean_abs_error']<m[f'bench_{model}_stretched_wide256']['mean_abs_error']
assert by['he_branch_zero']['metrics']['peak_scattering_s']==0
assert by['he_branch_zero']['metrics']['redistribution_energy_j']==0
assert abs(by['he_branch_half']['metrics']['peak_scattering_s']*2/by['physical_He_2800_dipole']['metrics']['peak_scattering_s']-1)<1e-14
assert by['drift_only_outflow']['metrics']['final_mass']==0 and abs(by['drift_only_outflow']['metrics']['escaped_mass']/by['drift_only_outflow']['metrics']['initial_mass']-1)<2e-12
legacy=[v for c in read('REGRESSION.json').values() for v in c['byte_equal'].values()]
assert len(legacy)==44 and all(legacy)
def tests(name):
 t=gzip.decompress((d/'logs'/name).read_bytes()).decode()
 v=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',t)
 assert v and all(x=='ok' and f=='0' for x,_,f in v)
 return sum(int(n) for _,n,_ in v)
assert tests('all.log.gz')==258 and tests('examples.log.gz')==3
if '--raw' in sys.argv:
 for c in a:
  p=pathlib.Path(c['command'][1])
  for f,h in c['hashes'].items():assert sha(p/f)==h,(c['case'],f)
 for p,h in {**source['input_sha256'],**source['rec_source_sha256']}.items():assert sha(p)==h,p
 assert sha(a[0]['command'][0])==r['binary_sha256']
out=dict(schema='bass.r118c2.acceptance/1',research_id='R118-C2-SOURCE-CALIBRATED-RESONANCE-KERNEL-01',status='IMPLEMENTATION_VERIFIED_SCOPED',scope='Frozen local scalar source-normalized FP patch; pure scattering branching supplied; nonseparable physical REC full kernel not implemented in BASS; no feedback',source=source,cases=88,time_steps=8410,tests={'rust':258,'examples':3,'new':6},legacy_byte_equal=44,metrics_max=mx,profile_max=pm,dense_be_max=max(c['dense_be_relative_l1'] for c in o['linear']),stiff=o['stiff'],bose_root_max=max(c['nonlinear_root_be_relative_l1'] for c in o['bose']),bose_stiff=o['bose_stiff'],hummer=h,mesh=o['mesh'],physical_source_states=[dict(case=c['case'],metrics={k:c['metrics'][k] for k in ('T_m_k','n_ground_m3','H_s','doppler_fraction','voigt_a','peak_scattering_s','peak_scattering_per_eta','static_sobolev_tau_diagnostic')}) for c in a if c['case'].startswith('physical_') and c['profile']=='dipole'],turning_boundary_escape={c['case']:c['metrics']['escaped_mass']/c['metrics']['initial_mass'] for c in a if c['case'].startswith(('he_turn_dipole_','he_turn_refine_'))},remaining=['actual nonseparable REC scalar angular-frequency bridge with source-owned core/exterior measure','source-owned scattering branching/destruction and true emission, continuum and population feedback','physical global frequency boundary coupling and converged high-order transport','polarized kernel and coupled thermal/momentum exchange'],science_promotion=False,next_id='R118-C2B-REC-NATIVE-ANGULAR-REDISTRIBUTION-BRIDGE-01')
out['receipt_sha256']={str(p.relative_to(d)):sha(p) for p in sorted(d.glob('*.json')) if p.name!='ACCEPTANCE.json'}
out['receipt_sha256'].update({str(p.relative_to(d)):sha(p) for p in sorted((d/'logs').glob('*.gz'))})
out['receipt_sha256']['INITIAL_TRIAL.json.gz']=sha(d/'INITIAL_TRIAL.json.gz')
(d/'ACCEPTANCE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('status','cases','time_steps','tests','legacy_byte_equal','metrics_max','profile_max','dense_be_max','stiff','bose_root_max','hummer','next_id')},indent=2))
