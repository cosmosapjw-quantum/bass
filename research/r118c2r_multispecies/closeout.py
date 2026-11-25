import hashlib,json,gzip,re
from pathlib import Path
D=Path(__file__).resolve().parent
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((D/'RESULTS.json').read_text());a=json.loads((D/'NATIVE_ARCHIVE.json').read_text())
assert all(int((D/f).read_text())==0 for f in ('green.exit','build.exit','native_run.exit','verify_mixture.exit','lib_tests.exit','regression.exit'))
assert '189 passed; 0 failed' in (D/'lib_tests.log').read_text()
assert len(a)==18 and len(j['cases'])==6
for p,h in j['sources'].items():assert sha(p)==h
for name,v in a.items():
 q=D/v['compressed'];assert sha(q)==v['compressed_sha256']
 with gzip.open(q,'rb') as z:assert hashlib.file_digest(z,'sha256').hexdigest()==v['raw_sha256']==j['native_csv_sha256'][name]
for line in (D/'BINARY.sha256').read_text().splitlines():
 h,p=line.split(maxsplit=1);assert sha(p)==h
rows=list(j['cases'].values())
assert all(r['balance']<1e-8 and r['native'][-1]['endpoint_error']<2e-8 and min(r['orders'])>1.8 for r in rows)
assert all(r['max_C']<1e-32 for r in rows if r['case']!='misaligned')
assert all(r['max_C']>1e-20 and r['onset'][-1]['relative']<1e-3 for r in rows if r['case']=='misaligned')
res=dict(status=j['status'],parent='84799a2827d8eb9fd6ffb168bd3c74f3c69f9993',native_runs=18,reference_runs=6,lib_tests=189,targeted_tests=5,raw_sources=3,max_fine_endpoint_error=max(r['native'][-1]['endpoint_error'] for r in rows),max_reference_balance=max(r['balance'] for r in rows),cases=j['cases'],production_admission='HOLD_FULL_NONLINEAR_OWNER',native_subagent='NOT_RUN',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','closeout.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n')
print({k:v for k,v in res.items() if k not in ('files','cases')})
