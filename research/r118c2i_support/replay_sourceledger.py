"""Rerun historical PR173 source-only native probe and original oracle gate."""
import argparse,ast,hashlib,json,math,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False);exe=a.binary.resolve()
d=Path(__file__).resolve().parent/'legacy_sourceledger'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
owner='b33b7f1c5945b9ccf3c59b0168305a7063ad4490'
probe=sha(d/'original_probe.rs')
# Reuse the historical gate verbatim rather than alter its tolerances.
tree=ast.parse((d/'native_runner.py').read_text())
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('strict_json','validate_native')]
ns={'json':json,'math':math,'COMPLETE':'bass.sourceledger.complete.v1','SCHEMA':'bass.sourceledger.native.v1'}
old=[json.loads(l) for l in (d/'NATIVE.jsonl').read_text().splitlines() if l.strip()]
ns['SOURCE_ID']=old[0]['source_id']
exec(compile(ast.Module(body=functions,type_ignores=[]),str(d/'native_runner.py'),'exec'),ns)
logs={}
for name in ['INPUT','EMPTY','MISSING_END','NEGATIVE_DT','NEGATIVE_SUPPORT','REVERSE_TIME']:
 out=root/(name+'.jsonl')
 r=subprocess.run([str(exe),str(d/(name+'.tsv')),str(out)],capture_output=True,text=True,timeout=120)
 logs[name]=dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,output_exists=out.exists())
 if name=='INPUT':assert r.returncode==0 and out.exists(),logs[name]
 else:assert r.returncode!=0 and not out.exists(),logs[name]
v=ns['validate_native']((root/'INPUT.jsonl').read_text(),json.loads((d/'EXPECTED.json').read_text()),owner,probe)
new=[json.loads(l) for l in (root/'INPUT.jsonl').read_text().splitlines() if l.strip()]
def removeid(row):return {k:v for k,v in row.items() if k not in ('owner_sha','probe_sha')}
equal=sum(removeid(x)==removeid(y) for x,y in zip(old,new))
assert len(old)==len(new)==59
receipt=dict(status='PASS_SCOPED_SOURCE_ONLY',owner=owner,original_probe_sha256=probe,restored_probe_sha256=sha(d.parent.parent.parent/'_rustcore/examples/sourceledger_recovered.rs'),binary_sha256=sha(exe),historical_rows=58,semantic_equal_rows=equal-1 if removeid(old[-1])==removeid(new[-1]) else equal,validation=v,negatives=logs,fixtures={f.name:sha(f) for f in sorted(d.iterdir()) if f.is_file()},native_output_sha256=sha(root/'INPUT.jsonl'))
(root/'RESULTS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('sourceledger rows',v['rows'],'equal incl completion',equal,'max parity',max(x for q in v['defects'] for x in q['normalized_differences'].values()),'negative rejection',[(n,x['returncode']) for n,x in logs.items() if n!='INPUT'])
