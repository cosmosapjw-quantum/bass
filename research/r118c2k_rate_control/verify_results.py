"""Verify final-pin actual outputs, ledger ownership and matched comparisons."""
import argparse,json,hashlib,gzip,re,shutil
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);a=p.parse_args()
D=Path(__file__).resolve().parent;repo=D.parents[1];R=a.raw
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((R/'RESULTS.json').read_text());cs=j['cases']
assert len(cs)==15 and sum(c['steps'] for c in cs)==76032
assert all(c['status']=='PASS_SCOPED' and c['returncode']==0 for c in cs)
assert sum(c['end']==4 for c in cs)==6
assert sha(repo/'_rustcore/target/release/examples/rei_live_characteristics')==j['binary_sha256']
assert sha(Path.home()/'Downloads/rec_r118c2g_boundary/normal.json')==j['donor_sha256']
o=json.loads((D/'OWNERSHIP.json').read_text());t=json.loads((D/'TERMINAL_RATES.json').read_text())
assert len(o['cases'])==len(t['cases'])==15
for c,own,rate in zip(cs,o['cases'],t['cases']):
 assert c['case']==own['case']==rate['case']
 q=R/c['case']
 for f,v in c['hashes'].items():assert sha(q/f)==v
 assert sha(q/'uv_exchange.tsv')==own['input_hash']
 assert sha(q/'packets.tsv')==rate['packets_sha256']
 assert c['number_defect']<1e-8 and c['energy_defect']<1e-8 and c['characteristic_error']<5e-10
 assert c['uv_ledger']['energy']<1e-9 and c['uv_ledger']['axial_momentum']<1e-9 and c['uv_ledger']['binding_heat']<1e-9
 if c['tolerance'] is not None:
  assert float(c['rate_guard']['max_group_relative'])<=c['tolerance']/2
  assert float(c['rate_guard']['max_final_relative'])<=c['tolerance']
 assert max(own['future_causal_excess'].values())<1e-13
 for v in rate['gamma_s']+rate['heat_eV_per_absorber_s']:assert v>=0
 if c['end']==4:assert c['compression']['isotropic_uv_reduced']=='true'
# Short guard does not alter the admitted previous same-width path.
for c in cs:
 if c['end']!=4 and c['tolerance'] is not None:
  b=next(x for x in cs if x['end']==c['end'] and x['shear']==c['shear'] and x['width']==c['width'] and x['tolerance'] is None)
  assert c['terminal']==b['terminal']
assert sha(Path.home()/'Downloads/rei_r118c2k_segments/fresh64/history.csv')==t['rei64_history_sha256']
r=json.loads((D/'REI_TERMINAL_ORACLE.json').read_text())
home=Path.home()/'Downloads'
paths={'q16':home/'rei_r118c2k_segments/extend16','q32':home/'rei_r118c2k_segments/resume32','q64':home/'rei_r118c2k_segments/fresh64','prior_native_check':home/'rei_r118c2j_reduced/long32'}
assert len(r['cases'])==4
for c in r['cases']:
 assert sha(paths[c['case']]/'checkpoint.txt')==c['checkpoint_sha256'] and c['quadrature_gap']<1e-9
 if c['case']=='prior_native_check':assert c['native_relative']<1e-8
(D/'terminal_oracle.log.gz').write_bytes(gzip.compress(Path('/tmp/r118c2k_terminal_oracle.log').read_bytes(),mtime=0))
shutil.copyfile(R/'RESULTS.json',D/'RESULTS.json')
for f in Path('/tmp').glob('r118c2k_bass*.log'):
 (D/(f.name+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
def tests(n):
 txt=Path('/tmp/r118c2k_bass_'+n+'.log').read_text();assert 'test result: FAILED' not in txt
 z=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored',txt)
 assert z and all(int(v[1])==0 for v in z)
 return sum(int(v[0]) for v in z)
b=next(c for c in cs if c['steps']==32768)
a=dict(status='PASS_SCOPED',parent='4c050431f8053d77c3c76ee2045f7db4f1bc49c9',rec_pin='91df4b2a3ddcd86a9319823061ab3d580866c62d',rei_pin='e93661d3b83beb4cb2c381339dde6e860c28e7c1',cases=len(cs),steps=sum(c['steps'] for c in cs),rust_tests=tests('full'),example_tests=tests('examples'),max_uv_energy=max(c['uv_ledger']['energy'] for c in cs),max_uv_axial=max(c['uv_ledger']['axial_momentum'] for c in cs),max_event_gap=max(c['uv_ledger']['max_event_gap'] for c in cs),max_group_rate=max(float(c['rate_guard']['max_group_relative']) for c in cs),max_final_rate=max(float(c['rate_guard']['max_final_relative']) for c in cs),max_owner_step_energy=max(c['energy_step_relative'] for c in o['cases']),finest=b,rei64_comparison=t['rei64_vs_guarded_bass'],binary_sha256=j['binary_sha256'],raw=str(R),limitations=['local frozen-stage rate control, not history-wide bound','same-ray threshold-aware compression; actual support retained but altered weights','normal-frame LRS-I/FLRW diagnostic only, no active material/emitter or boundary-sector dynamics','REI continuous birth controller is separate; BASS still BE','HeIII global convergence unresolved'],files={f.name:sha(f) for f in D.iterdir() if f.is_file() and f.name!='ACCEPTANCE.json'})
(D/'ACCEPTANCE.json').write_text(json.dumps(a,indent=2)+'\n')
print(json.dumps({k:v for k,v in a.items() if k not in ('files','finest')},indent=2))
