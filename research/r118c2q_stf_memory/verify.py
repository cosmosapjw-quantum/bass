import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((D/'RESULTS.json').read_text())
assert all(int((D/f).read_text())==0 for f in ('native.exit','native_run.exit','run.exit','stf_native.exit','lib_tests.exit'))
assert '48 general STF Thomson cases' in (D/'stf_native.log').read_text()
assert '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
assert len(j['source_hashes'])==18
for p,h in j['source_hashes'].items():assert sha(p)==h
assert j['native_rows']==774 and len(j['angular_checks'])==18 and j['max_native_relative']<1e-9 and j['rotation_gap']<2e-8 and j['independent_ode_gap']<2e-8
rows=[x for r in j['results'].values() for x in r];assert len(rows)==12 and max(x['balance'] for x in rows)<2e-8
assert all(r[0]['stf_angle_deg']<1e-5 for r in j['results'].values())
assert np.linalg.norm(j['zero_initial_shear']['end'][0])>1e-6
res=dict(status='PASS_SCOPED_NATIVE_STF_MEMORY',parent='d393ebe839a68090126b756309b721afe896fe8d',native_radial_cases=774,native_thomson_cases=48,lib_tests=189,angular_cases=18,full_ODE_runs=13,independent_ODE_runs=1,max_lyapunov_balance=max(x['balance'] for x in rows+[j['zero_initial_shear']]),max_radial_relative=j['max_native_relative'],max_angular_relative=max(x['relative'] for x in j['angular_checks']),rotation_gap=j['rotation_gap'],independent_ode_gap=j['independent_ode_gap'],zero_shear_end_norm=float(np.linalg.norm(j['zero_initial_shear']['end'][0])),scope=j['scope'],production_admission='RESEARCH_ONLY_NATIVE_PROVIDER_NOT_GEOMETRY_OWNER',native_subagent='NOT_RUN',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k!='files'})
