"""CE1-AC proof implementation verification, model identity, nontrivial counterchecks."""
from __future__ import annotations
import json,math,sys
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from exact_jet_certificate import I,PI,RT2,Poly,phi_average,mu_average,moment,moment_symbol,certificate
from jet_numeric import numeric_jet
from cellwise_gl_rust import make_cell_rays, frozen_source_identity
SRC='022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035'

def test_original_model_sha():
    assert frozen_source_identity()==SRC
    assert (ROOT/'original_source/cellwise_gl_rust.py').is_file() or (ROOT/'dependencies/ce1ab_20261030/ce1aa_input/source/cellwise_gl_rust.py').is_file() or (ROOT.parent/'ce1aa_20261030/source/cellwise_gl_rust.py').is_file()

def test_pi_sqrt2_strict_exact_rational_enclosure():
    assert PI.lo>F(314,100) and PI.hi<F(315,100)
    assert RT2.lo>F(141,100) and RT2.hi<F(142,100)
    assert PI.lo<PI.hi and RT2.lo<RT2.hi
    assert RT2.lo**2<2<RT2.hi**2
    assert PI.width()<F(1,10**100)

def test_interval_matrix_basic_arithmetic_fail_closed():
    a=I(F(1,3),F(2,3));b=I(F(-3,2),F(1,2))
    c=a*b
    assert c.lo<=-1 and c.hi>=F(1,3)
    assert (I(2).sqrt()).lo**2<=2<=(I(2).sqrt()).hi**2
    with pytest.raises(ZeroDivisionError):_ = a/b
    with pytest.raises(ValueError):_ = I(2,1)

def test_all_35_original_exact_cell_moments_and_trace():
    from exact_jet_certificate import CELL_E
    E=sum((F.from_float(float(x)) for x in CELL_E.flatten()),F(0))
    assert moment(0,0,0).lo<=E<=moment(0,0,0).hi
    p=moment(1,0,0)+moment(0,1,0)+moment(0,0,1)
    assert p.lo<=E<=p.hi
    assert len(json.loads((ROOT/'data/EXACT_MOMENT_SYMBOLIC_35.json').read_text())['moments'])==35

@pytest.mark.parametrize('a,b,c',[(1,0,0),(0,1,0),(0,0,1),(2,1,0),(2,0,2),(0,0,4),(1,2,1)])
def test_exact_continuum_moments_against_independent_64ray_quadrature(a,b,c):
    ray,w=make_cell_rays(64)
    numeric=float(np.dot(w,(ray[:,0]**(2*a))*(ray[:,1]**(2*b))*(ray[:,2]**(2*c))))
    v=moment(a,b,c)
    midpoint=float((v.lo+v.hi)/2)
    assert abs(numeric-midpoint)<3e-13

@pytest.mark.parametrize('n',[6,8,16,64])
def test_separately_implemented_positive_GL_initial_jet(n):
    jet=numeric_jet(n)
    assert jet['source_sha256']==SRC and jet['det_scaled']>3e-5
    cert=json.loads((ROOT/'data/EXACT_CONTINUUM_INITIAL_JET_CERTIFICATE.json').read_text())
    midpoint=(float(cert['scaled_initial_jet_det_interval'][0])+float(cert['scaled_initial_jet_det_interval'][1]))/2
    assert abs(jet['det_scaled']-midpoint)<5e-10

def test_exact_initial_jet_positive_simple_rational_lower():
    cert=certificate()
    lo,hi=cert['scaled_initial_jet_det_interval']
    assert F(lo)>F(3,100000)
    assert F(hi)<F(31,10**6)
    assert cert['exact_initial_jet_det_strictly_positive']
    assert cert['max_moment_total_degree']==4
    assert cert['DAG_upper_completed']==9

def test_41_time_history_is_actual_original_model():
    data=json.loads((ROOT/'data/PHYSICAL_41_EPOCH_GL6_GL8_GL16_GL64.json').read_text())
    assert set(data['results'])=={'6','8','16','64'}
    for order,channel in data['results'].items():
        assert len(channel['states'])==41 and channel['source_sha256']==SRC
        assert channel['svd_squared_eigenvalues'][2]>5e-11
        assert max(abs(row['Hamiltonian_C']) for row in channel['states'])<1e-10
        assert channel['three_epoch_0_020_040_det_X_numeric']>1e-9
    for order in ('16','64'):
        assert data['results'][order]['fresh_solver_rhs_evals']>0
    assert not data['assertions']['41_epoch_rank3_exact_continuum_certified']
