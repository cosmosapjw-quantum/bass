"""CE1-U original six-cell GL exact rational / MPFR source+time safety contract."""
import numpy as np
import pytest
from fractions import Fraction
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from research.ce1u_20261030.certified_gl_source import (
    exact_gl_brackets, _poly_coeffs, _eval_horner, sample_gl_source,
    certify_gl_source, SOURCE_SHA,
)
from research.ce1u_20261030.certify_gl_coupled import certify_gl_coupled

@pytest.mark.parametrize('order', [4,6,8])
def test_gl_roots_isolated_with_exact_rational_sign_change(order):
    poly=_poly_coeffs(order)
    roots=exact_gl_brackets(order)
    assert len(roots)==order
    for ((lo,hi),(wlo,whi)) in roots:
        assert _eval_horner(poly,lo)*_eval_horner(poly,hi)<0
        assert Fraction(-1)<lo<hi<Fraction(1)
        assert 0<wlo<=whi

@pytest.mark.parametrize('order', [4,6,8])
def test_source_original_physical_cells_and_safe_positive_roundoff(order):
    s=sample_gl_source(order)
    a=certify_gl_source(order,s)
    assert a['rays']==6*order*order
    assert a['physical_table_sha256']==SOURCE_SHA
    assert 0<a['qmu_upper']<1 and 0<a['qphi_upper']<1
    assert a['binary_input_pressure_error_upper']<1e-11
    assert a['total_pressure_error_upper']>a['ideal_gl_pressure_error_upper']
    assert np.min(s.mass)>0
    assert a['mpfr_precision_bits']==192

@pytest.mark.parametrize('order', [6,8])
def test_locked_gl_source_rejects_mass_and_angle_mutations(order):
    s=sample_gl_source(order)
    s.mass=s.mass.copy();s.mass[0]*=1.01
    with pytest.raises(ValueError,match='binary identity'):
        certify_gl_source(order,s)
    s=sample_gl_source(order);s.n=s.n.copy();s.n[0,0]*=.99
    with pytest.raises(ValueError,match='binary identity'):
        certify_gl_source(order,s)

@pytest.mark.parametrize('order', [6,8])
def test_reject_another_valid_but_different_physical_continuum(order):
    table=np.array([[.1,.25,.05],[.2,.15,.15]])
    table[0,0]+=.01
    s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],table,refinement=order,backend='python_oracle')
    reference=sample_gl_source(order)
    s.n=reference.n.copy();s.mass=reference.mass.copy();s.energy0=reference.energy0
    with pytest.raises(ValueError,match='physical input'):
        certify_gl_source(order,s)

@pytest.mark.parametrize('order', [4,6,8])
def test_actual_four_panel_certified_h_bound(order):
    x=certify_gl_coupled(order)
    assert x['rays']==6*order*order
    assert len(x['rows'])==4
    assert x['fixed_target_h']==1e-5 and x['target_met']
    assert 0<x['source_h_upper']<1e-5
    assert 0<x['time_jump_h_upper']<1e-5
    assert x['final_h_upper'] < 1e-5
    assert x['production_ready'] is False

def test_gl6_gl8_strictly_reduce_source_enclosure():
    assert certify_gl_source(8)['total_pressure_error_upper'] < certify_gl_source(6)['total_pressure_error_upper']

def test_unsupported_or_boolean_gl_order_fails():
    for n in (0,2,True,9):
        with pytest.raises(ValueError):certify_gl_source(n)
