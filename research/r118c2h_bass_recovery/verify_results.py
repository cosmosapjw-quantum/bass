"""Verify C2H compact receipt and, optionally, original raw inputs/outputs."""
import argparse,csv,gzip,hashlib,json,pathlib,re
D=pathlib.Path(__file__).resolve().parent
R=D.parents[1]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(s):return json.loads((D/s).read_text())
def check(raw=False):
    rr=load('ROOT_RECEIPT.json'); lr=load('RESULTS.json')
    assert rr['byte_exact'] and rr['root_count']==16 and rr['packets']==70656
    assert rr['max_q']<1e-12 and rr['negative_control']=='NEGATIVE_OR_ZERO_PHOTON_SOURCE'
    assert sha(D/'ROOT_ALL_CURRENT.csv')==sha(D/'legacy/ROOT_ALL.csv')==rr['root_csv_sha256']
    assert sha(R/'_rustcore/examples/f08_recovered_root.rs')==rr['source_sha256']
    rows=list(csv.DictReader((D/'ROOT_ALL_CURRENT.csv').open()))
    assert len(rows)==16 and all(x['root_status']=='PASS' and x['root_contains_conservative']=='true' and x['photons_contain_conservative']=='true' for x in rows)
    cases=lr['cases']
    assert len(cases)==12 and all(x['status']=='PASS_SCOPED' and x['returncode']==0 for x in cases)
    assert {x['q_ref'] for x in cases}=={-.01,0.,.01}
    assert {x['end'] for x in cases}=={19.98,19.9}
    for x in cases:
        assert x['characteristic_error']<2e-7 and x['direction_error']<2e-7
        assert x['tau_relative']<2e-8 and x['max_number_defect']<1e-8 and x['max_energy_defect']<1e-8
    counts={}
    for k in ('test','examples'):
        s=gzip.decompress((D/'logs'/f'r118c2h_bass_{k}_final.log.gz').read_bytes()).decode()
        matches=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored',s)
        assert matches and 'test result: FAILED' not in s
        counts[k]=sum(int(x[0]) for x in matches)
        assert all(x[1:]==('0','0') for x in matches)
    assert counts=={'test':276,'examples':3}
    if raw:
        root=pathlib.Path(rr['raw_input_dir'])
        for name,v in rr['root_inputs'].items():assert sha(root/name)==v
        assert sha(R/'_rustcore/target/release/examples/f08_recovered_root')==rr['root_binary_sha256']
        assert sha(R/'_rustcore/target/release/examples/rei_live_characteristics')==lr['binary_sha256']
        assert sha(pathlib.Path.home()/'Downloads/rec_r118c2g_boundary/normal.json')==lr['donor_sha256']
        for x in cases:
            out=pathlib.Path(x['command'][1])
            for name,v in x['hashes'].items():assert sha(out/name)==v
    result={'root_count':len(rows),'packet_records':rr['packets'],'live_cases':len(cases),'tests':counts,'maxima':{k:max(x[k] for x in cases) for k in ['tau_relative','characteristic_error','direction_error','max_number_defect','max_energy_defect','max_root_residual']}}
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--raw',action='store_true');args=ap.parse_args()
    print(json.dumps(check(args.raw),indent=2))
