"""CE1F reconciliation record verifier: file identity, not physics re-execution."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parent
manifest=json.loads((R/'MANIFEST.json').read_text())
for rel,digest in manifest['sha256'].items():
    f=R/rel
    assert f.is_file(),rel
    assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,rel
w=json.loads((R/'evidence/WITNESS_S0.json').read_text())
assert w['excess_strictly_positive']
r=json.loads((R/'evidence/CI_40792700025/ce1f_comparison.json').read_text())
assert len(r['rows'])==4
assert all(v['same_exact_continuum_energy'] and v['repaired_exact_energy_cap_valid'] for v in r['rows'])
assert max(v['max_pressure_difference'] for v in r['rows']) < 2e-14
assert max(v['max_coupled_6state_difference'] for v in r['rows']) < 1e-11
assert all(v['independent_original_cell_quadrature_ratio_max']<1 for v in r['rows'])
D=json.loads((R/'DAG_UPDATED.json').read_text())
assert len(D['nodes'])==15 and D['progress']['count']==9 and D['progress']['total']==15
assert D['reconciliation_20261029']['status']=='COMPLETE_SCOPED'
print('PRESERVATION_AND_RECORDED_RESULT_PASS',len(manifest['sha256']),'files', 'upper_dag=9/15')
