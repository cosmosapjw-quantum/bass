import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import typeii_conservation_quad as v

def result(): return v.run(ROOT/'typeII_v_schedule.json')

def test_paired_grids_preserve_boosted_equilibrium_null():
    r=result();vals=[x['null'] for x in r['quadrature'] if x['mode']=='paired-rest-normal']
    assert max(vals)<2e-14

def test_paired_grids_preserve_collision_left_invariant():
    r=result();vals=[x['left'] for x in r['quadrature'] if x['mode']=='paired-rest-normal']
    assert max(vals)<2e-14

def test_deep_collision_semigroup_preserves_left_invariant_on_paired_grid():
    r=result();vals=[max(x['semigroup_drift']) for x in r['quadrature'] if x['mode']=='paired-rest-normal']
    assert max(vals)<5e-12

def test_fixed_low_order_grid_exposes_expected_finite_boost_quadrature_defect():
    r=result();by={(x['grid'],x['v'],x['mode']):x for x in r['quadrature']}
    assert by[('Lebedev26',.1,'fixed-normal')]['null']>1e-8
    assert by[('GL8x16',.1,'fixed-normal')]['null']<1e-10
    assert by[('Lebedev26',.1,'paired-rest-normal')]['null']<2e-14

def test_kato_parallel_transport_hits_endpoint_manifold_at_second_order():
    r=result();assert r['kato_endpoint']['order']>1.95
    assert r['kato_endpoint']['endpoint_manifold_defect'][-1]<5e-10
