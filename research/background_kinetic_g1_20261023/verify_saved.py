"""Verify preserved identities and finite acceptance without solving any IVP."""
from pathlib import Path
import hashlib, json, sys
import numpy as np

ROOT = Path(__file__).resolve().parent

def main():
    checks = {}
    for path, lock in json.loads((ROOT/'evidence/SOURCE_LOCK.json').read_text()).items():
        b = (ROOT/path).read_bytes()
        assert hashlib.sha256(b).hexdigest() == lock['sha256'], path
        assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == lock['git_blob'], path
    result = json.loads((ROOT/'evidence/controls_001/RESULTS.json').read_text())
    rows = result['cases']+[result['wrong_weight_control']]
    assert len(rows) == 18 and len({r['name'] for r in rows}) == 18
    for row in rows:
        p = ROOT/'evidence/controls_001'/(row['name']+'.npz')
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['raw_sha256'], p
        with np.load(p, allow_pickle=False) as d:
            assert d['state'].shape == (72, 101)
            assert np.all(np.isfinite(d['state']))
            for field, raw in [('max_core_constraint','core_constraint'),
                               ('max_kinetic_constraint','kinetic_constraint'),
                               ('max_moment_mismatch','ledger')]:
                assert float(np.max(d[raw])) == row[field], (p,field)
        if not row['wrong_weight']:
            assert max(row[k] for k in result['maxima']) < 2e-8
            assert row['min_weight'] > 0
    assert result['wrong_weight_control']['max_moment_mismatch'] > 1e-4
    assert result['turnaround']['final_h'] < 0
    assert result['rotating_full_state_error'] < 2e-8
    assert max(x['max_scaled_state_difference'] for x in result['convergence']) < 2e-8
    if (ROOT/'figures/MANIFEST.json').exists():
        for path, lock in json.loads((ROOT/'figures/MANIFEST.json').read_text()).items():
            b=(ROOT/'figures'/path).read_bytes()
            assert len(b)==lock['bytes'] and hashlib.sha256(b).hexdigest()==lock['sha256'],path
    if (ROOT/'PAYLOAD_MANIFEST.json').exists():
        for path, lock in json.loads((ROOT/'PAYLOAD_MANIFEST.json').read_text()).items():
            b=(ROOT/path).read_bytes()
            assert len(b)==lock['bytes'] and hashlib.sha256(b).hexdigest()==lock['sha256'],path
    checks.update(status='PASS_SAVED', histories=18, valid_physical_histories=17,
                  intentional_negative_controls=1, new_ivps=0, rerenders=0,
                  full_old_suites_replayed=0)
    print(json.dumps(checks,indent=2))
    return 0
if __name__=='__main__': sys.exit(main())
