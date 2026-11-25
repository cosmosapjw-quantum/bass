import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((D/'RESULTS.json').read_text())
assert all(int((D/f).read_text())==0 for f in ('green.exit','run.exit'))
assert len(j['results'])==2 and len(j['source_hashes'])==18
for p,h in j['source_hashes'].items():assert sha(p)==h
rows=[x for v in j['results'].values() for x in v]
assert len(rows)==12 and len(j['angular_checks'])==54 and len(j['independent'])==6
modes=[x['modes'][m] for x in rows for m in ('all','photon')]
assert max(x['balance'] for x in modes)<3e-8
assert max(x['max_inc'] for x in modes)<1e-11
assert all(x['Lf']<=x['L0'] for x in modes)
assert max(x['max_abs'] for x in j['independent'].values())<2e-8
assert max(x['relative'] for x in j['angular_checks'] if x['h']==1e-5)<3e-10
for name,v in j['results'].items():
    assert all(a['chi_rel_massless'][1]>=b['chi_rel_massless'][1] for a,b in zip(v,v[1:]))
res=dict(status='PASS_SCOPED_MASSIVE_EINSTEIN_VLASOV_THOMSON',parent='083bf910046ca552ee3fcc48616ab8664df80dc8',histories=2,raw_sources_verified=18,ODE_runs=36,independent_ODE_runs=6,angular_checks=54,max_balance=max(x['balance'] for x in modes),max_angular_relative_h1e5=max(x['relative'] for x in j['angular_checks'] if x['h']==1e-5),max_independent_ODE_gap=max(x['max_abs'] for x in j['independent'].values()),scope=j['scope'],production_admission='RESEARCH_ONLY',native_subagent='NOT_RUN',files={f.name:sha(f) for f in D.iterdir() if f.is_file() and f.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k!='files'})
