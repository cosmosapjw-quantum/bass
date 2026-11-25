import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((D/'RESULTS.json').read_text())
assert all(int((D/f).read_text())==0 for f in ('green.exit','run.exit','native.exit'))
assert len(j['results'])==10 and len(j['source_hashes'])==18
for p,h in j['source_hashes'].items():assert sha(p)==h
a=[v['modes'][m] for v in j['results'].values() for m in ('photon','all')]
assert max(x['lyapunov_relative_balance'] for x in a)<2e-8
assert max(x['lyapunov_max_increment'] for x in a)<2e-11
assert all(x['lyapunov_final']<=x['lyapunov_initial'] for x in a)
assert all(max(abs(np.asarray(v['orders'])-2))<.05 for v in j['midpoint'].values())
assert '27 native mixture feedback cases' in (D/'native.log').read_text()
assert '24 native scattering cases' in (D/'native.log').read_text()
q=j['results']['q256'];b=j['results']['bass_cross']
res=dict(status='PASS_SCOPED_LINEAR_EINSTEIN_THOMSON',parent='6ff2cc03550cc246ad7731c5f89b3a0823d1494a',histories=len(j['results']),raw_source_files=len(j['source_hashes']),ode_runs=30,lyapunov_runs=len(a),native_feedback_cases=27,native_collision_cases=24,max_lyapunov_balance=max(x['lyapunov_relative_balance'] for x in a),max_lyapunov_increment=max(x['lyapunov_max_increment'] for x in a),q256=q['modes'],feedback_relative=q['feedback_rel'],q256_bass_B_relative=q['modes']['all']['end'][2]/b['modes']['all']['end'][2]-1,midpoint_max_fine_error=max(x['errors'][-1] for x in j['midpoint'].values()),scope='linear homogeneous LRS I; prescribed FLRW monopole and actual z20->4 ne; massless neutrino diagnostic',production_admission='RESEARCH_ONLY',native_subagent='NOT_RUN',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ('files','q256')})
