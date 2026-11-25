"""Verify scoped C2I results; --raw also hashes external raw evidence."""
import argparse,hashlib,json,math,gzip,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
d=Path(__file__).resolve().parent;repo=d.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((d/'RESULTS.json').read_text());s=json.loads((d/'SOURCELEDGER_RESULTS.json').read_text())
cs=r['cases'];assert len(cs)==18 and all(x['status']=='PASS_SCOPED' and x['returncode']==0 for x in cs)
assert sum(x['end']==4 for x in cs)==9
assert sum(x['steps'] for x in cs)==121088
assert max(x['number_defect'] for x in cs)<1e-8
assert max(x['energy_defect'] for x in cs)<1e-8
assert max(x['characteristic_error'] for x in cs)<5e-10
assert max(float(x['compression']['max_U_relative']) for x in cs)<3e-14
assert max(abs(x['stress']['Pi_over_rho']) for x in cs if x['compression']['isotropic_uv_reduced']=='true')<2e-12
assert all(x['compression']['isotropic_uv_reduced']=='true' for x in cs if x['end']==4)
assert s['status']=='PASS_SCOPED_SOURCE_ONLY' and s['historical_rows']==s['semantic_equal_rows']==58
assert s['validation']['rows']==58
assert max(x for q in s['validation']['defects'] for x in q['normalized_differences'].values())<=5e-11
assert len(s['negatives'])==6 and all(v['returncode']!=0 and not v['output_exists'] for k,v in s['negatives'].items() if k!='INPUT')
assert sha(repo/'_rustcore/examples/sourceledger_recovered.rs')==s['restored_probe_sha256']
for k,v in s['fixtures'].items():assert sha(d/'legacy_sourceledger'/k)==v
if a.raw:
 assert sha(Path.home()/'Downloads/rec_r118c2g_boundary/normal.json')==r['donor_sha256']
 assert sha(repo/'_rustcore/target/release/examples/rei_live_characteristics')==r['binary_sha256']
 assert sha(repo/'_rustcore/target/release/examples/sourceledger_recovered')==s['binary_sha256']
 for x in cs:
  root=Path(x['command'][1])
  for k,v in x['hashes'].items():assert sha(root/k)==v
 assert sha(Path.home()/'Downloads/bass_r118c2i_sourceledger/INPUT.jsonl')==s['native_output_sha256']
 old=json.loads((d/'FLRW_ANGULAR_TRIAL.json').read_text())
 for x in old['cases']:
  for k,v in x['hashes'].items():assert sha(Path(x['command'][1])/k)==v
 probe=json.loads((d/'FLRW_FAST_PATH_PROBE.json').read_text())
 for k,v in probe['files'].items():assert sha(Path(probe['raw'])/k)==v
print('PASS_SCOPED 18 cases / 121088 steps, 58 native source-only rows, 5 invalid fixtures, final isotropic stress and raw hashes')
