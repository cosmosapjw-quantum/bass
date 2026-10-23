"""Read-only scientific-evidence verification. No RHS, quadrature or IVP calls."""
from pathlib import Path
import hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def error(a,b):return float(np.max(np.abs(a-b)/(1+np.maximum(np.abs(a),np.abs(b)))))
def load(p):return json.loads(Path(p).read_text())

def main():
    manifest=load(ROOT/'SCIENCE_MANIFEST.json')
    for name,r in manifest.items():
        p=ROOT/name
        assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],name
    summary=load(ROOT/'RESULTS.json');history=ROOT/'evidence/curved_002'
    receipts=[];arrays={}
    for p in sorted(history.glob('*_r*_a*.json')):
        r=load(p);raw=p.with_suffix('.npz')
        assert r['status']=='PASS_SCOPED' and sha(raw)==r['raw_sha256'],p.name
        for name,s in r['source'].items():assert sha(ROOT/name)==s,name
        with np.load(raw) as z:
            assert z['tau'].shape==(33,) and z['observable'].shape==(33,52)
            assert np.all(np.isfinite(z['observable'])) and np.min(z['minimum_weight'])>0
            for key in ('core_constraint','kinetic_constraint','mismatch'):
                assert float(z[key].max())==r['maxima'][key] and r['maxima'][key]<2e-8
            arrays[r['case']]=z['observable'].copy()
        receipts.append(r)
    assert len(receipts)==16
    base=load(history/'RESULTS.json')
    for c in base['comparisons']:
        def name(spec):
            r,a,t=spec
            return f"{c['family']}_r{r}_a{a}"+('_tight' if t else '')
        e=error(arrays[name(c['left'])],arrays[name(c['right'])])
        assert e==c['error'],c
        if c['required']:assert e<2e-8
    half=load(ROOT/'evidence/time_step_001/RESULTS.json')
    assert half['status']=='PASS_SCOPED' and len(half['cases'])==2
    for r in half['cases']:
        raw=ROOT/'evidence/time_step_001'/(r['family']+'_half_step.npz')
        assert sha(raw)==r['raw_sha256']
        for name,s in r['source'].items():assert sha(ROOT/name)==s,name
        with np.load(raw) as z, np.load(history/(r['family']+'_r8_a14.npz')) as ref:
            assert error(z['observable'],ref['observable'])==r['observable_error']
            assert error(z['state'],ref['state'])==r['full_state_error']
    assert summary['new_successful_IVPs']==18 and summary['old_campaign_IVPs_replayed']==0
    assert (ROOT/'evidence/curved_001/V_r4_a6.failure.json').is_file()
    assert (ROOT/'figures/fixed_angular_refinement.csv').read_bytes()==(ROOT/'figures/initial_render/fixed_angular_refinement.csv').read_bytes()
    print(json.dumps({'status':'PASS_SAVED_EVIDENCE','payload_hashes':len(manifest),'successful_histories':18,
        'history_comparisons_recomputed':len(base['comparisons'])+4,'new_IVPs':0,'new_moment_evaluations':0,
        'parent_campaign_replays':0,'source_lock_matches':True,'first_failure_retained':True},indent=2))
if __name__=='__main__':main()
