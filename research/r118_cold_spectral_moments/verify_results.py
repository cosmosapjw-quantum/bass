"""Verify the explicitly bounded R118 result receipts and report limits."""
import collections,hashlib,json,pathlib,re,subprocess,sys,gzip
d=pathlib.Path(__file__).resolve().parent
r=json.loads((d/'RESULTS.json').read_text());oracle=json.loads((d/'FREQUENCY_ORACLE.json').read_text())
by={c['case']:c for c in r['cases']};a=[c for c in r['cases'] if c['status']=='PASS_SCOPED']
w=[c for c in r['cases'] if c['status']=='REALIZABILITY_WARNING']
assert len(by)==len(r['cases'])==47 and len(a)==41 and len(w)==6
assert set(c['case'] for c in w)=={'thermal_i_32','thermal_i_64','thermal_i_128','thermal_viih_64','thermal_stronger','thermal_viih_64_L8'}
assert all(all(c.get('legacy_byte_equal',{}).values()) for c in r['cases'])
assert sum(len(c.get('legacy_byte_equal',{})) for c in r['cases'])==318
assert sum(c['metrics']['events'] for c in a)==8464
assert all(by['he_'+x]['status']=='PASS_SCOPED' for x in ('I','II','III','IV','V','VI0','VIh_-0.25','VIstar','VII0','VIIh_0.25','VIII','IX'))
assert all(by[x]['status']=='PASS_SCOPED' for x in ('thermal_i_32_L8','thermal_i_64_L8','thermal_i_128_L8','thermal_viih_64_L12','thermal_viih_64_L16','thermal_stronger_L6','thermal_stronger_L16','thermal_stronger_ray_oracle','thermal_viih_64_ray_oracle'))
assert len(oracle)==2 and all(max(q['errors'].values())<5e-10 for q in oracle)
keys=['number_collision_defect','rest_energy_collision_defect','number_continuity_defect','class_a_number_drift','bolometric_integral_gap','bolometric_screen_gap','observer_invariance','max_m0_defect','signed_reality','low_spin_defect']
metrics={k:max(abs(c['metrics'][k]) for c in a if c['metrics'][k] is not None) for k in keys}
assert metrics['number_collision_defect']<2e-11 and metrics['rest_energy_collision_defect']<2e-11
assert metrics['bolometric_integral_gap']<5e-9
assert metrics['class_a_number_drift']<2e-7 and metrics['observer_invariance']<1e-12
def ratio(seq):
 return {k:(by[seq[0]]['last'][k]-by[seq[1]]['last'][k])/(by[seq[1]]['last'][k]-by[seq[2]]['last'][k]) for k in ('mean_variance','mean_y_m','energy_comoving')}
ratios={'thermal_I_L8':ratio(['thermal_i_32_L8','thermal_i_64_L8','thermal_i_128_L8']),'cold_beta_0.2':ratio(['cold_beta_0.2_4','cold_beta_0.2_8','cold_beta_0.2_16'])}
assert all(3.8<q<4.2 for v in ratios.values() for q in v.values())
comparisons={}
for x,y in [('thermal_stronger_L16','thermal_stronger_ray_oracle'),('thermal_viih_64_L16','thermal_viih_64_ray_oracle'),('thermal_stronger_L12','thermal_stronger_L16'),('thermal_viih_64_L12','thermal_viih_64_L16')]:
 comparisons[x+'__'+y]={k:abs(by[x]['last'][k]-by[y]['last'][k]) for k in ('mean_variance','mean_y_m','energy_comoving','number_comoving')}
assert all(q['mean_variance']<2e-12 and q['mean_y_m']<2e-12 for q in comparisons.values())
logs={}
for name in ('all_final','examples_final'):
 raw=gzip.decompress((d/(name+'.log.gz')).read_bytes())
 assert b'FAILED' not in raw
 logs[name]={'passed':sum(map(int,re.findall(rb'test result: ok\. (\d+) passed',raw))),'sha256':hashlib.sha256(raw).hexdigest()}
assert logs['all_final']['passed']==237 and logs['examples_final']['passed']==3
data=dict(schema='bass.r118.acceptance/1',baseline='5622db58771dbb2dff1e89ccdf1b547fa1d3e27a',rec_pin='f67be237187372f4d89fe8c021819a38261b14eb',binary_sha256=r['binary_sha256'],scope='fixed accepted history cold spectral moments; not new feedback or grid-free spectral collision',native_subagent='NOT_RUN',tests=logs,accepted_cases=41,realizability_warnings=6,legacy_byte_equal_files=318,accepted_events=8464,metrics_max=metrics,ratios=ratios,comparisons=comparisons,oracle=oracle,warnings=[dict(case=c['case'],metrics=c['metrics']) for c in w],science_DAG_promotions=0)
(d/'ACCEPTANCE.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({k:v for k,v in data.items() if k not in ('warnings','oracle')},indent=2))
