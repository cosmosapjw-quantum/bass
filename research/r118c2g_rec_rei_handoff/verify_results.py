"""Verify BASS one-way consumer and exact REC/REI pins."""
import argparse,gzip,hashlib,json,re
from pathlib import Path
D=Path(__file__).resolve().parent;repo=D.parents[1];home=Path.home()/'Downloads'
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
r=json.loads((D/'RESULTS.json').read_text())
assert len(r['cases'])==6 and r['status']=='PASS_SCOPED'
assert max(x['tau_relative'] for x in r['cases'])<5e-6
assert min(x['tau_relative'] for x in r['cases'])<5e-7
assert max(x['hubble_relative'] for x in r['cases'])<5e-7
for name,n in [('tests',274),('examples',3)]:
    text=gzip.decompress((D/f'logs/r118c2g_bass_{name}.log.gz').read_bytes()).decode()
    counts=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',text)
    assert counts and sum(int(x[1]) for x in counts)==n and sum(int(x[2]) for x in counts)==0
for pin in ('789522e6b7ad95948d3715f4c085e6d381c061aa','5998afd4a58bc7e02ea07088a5bfe14bba2c48df'):
    assert all(pin in (repo/'_rustcore'/x).read_text() for x in ['Cargo.toml','Cargo.lock'])
if a.raw:
    assert sha(home/'rei_r118c2g_owned_long/run/history.csv')==r['source_history_sha256']
    assert sha(home/'rec_r118c2g_boundary/normal.json')==r['donor_sha256']
    assert sha(Path(r['cases'][0]['command'][0]))==r['binary_sha256']
    root=home/'bass_r118c2g_rec_rei_handoff_final'
    for c in r['cases']:
        assert sha(root/f"xe_{c['n_intervals']}.tsv")==c['table_sha256']
        for f,h in c['hashes'].items():assert sha(root/c['case']/f)==h
print('PASS_SCOPED 6 one-way FLRW consumer cases; 277 tests')
