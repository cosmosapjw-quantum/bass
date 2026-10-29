"""CE1-H: constructive pressure-Jacobian bound and sharp path propagation."""
from fractions import Fraction
import numpy as np
import pytest
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_interval import Interval, _iv_fraction
from bianchi.nonperturbative.einstein_tabulated_sharp import (
    initial_continuum_pressure_cap, certify_sharp_tabulated_path,
    run_sharp_tabulated_rk4,
)


def fixture(refinement=1):
    return TabulatedRadiation([0,.5,1],[0,.25,.75,1],
        [[.1,.25,.05],[.2,.15,.15]], refinement=refinement,backend='python_oracle')


def test_initial_pressure_exact_energy_sum_and_sharp_cap():
    s=fixture()
    cert=initial_continuum_pressure_cap(s)
    assert cert['method']=='MPFR192_EXACT_CELL_MEANS'
    assert len(cert['pressure_intervals'])==3
    assert cert['pressure_max_upper'] < .34
    assert cert['pressure_max_upper'] > .32
    assert cert['energy_continuum_upper'] > .89
    assert cert['pressure_max_upper'] < cert['energy_continuum_upper']
    assert cert['lipschitz_upper'] < 1.4
    assert cert['lipschitz_upper'] > 1.2
    assert cert['exact_continuum_sum_identity'] is True


def test_isotropic_full_sky_cell_pressure_one_third():
    s=TabulatedRadiation([0,1],[0,1],[[.9]],backend='python_oracle')
    cert=initial_continuum_pressure_cap(s)
    for lo,hi in cert['pressure_intervals']:
        assert lo <= float(s.continuum_energy)/3 <= hi
    assert cert['pressure_max_upper'] < .300000000000001


def test_refinement_does_not_change_physical_initial_pressure():
    caps=[initial_continuum_pressure_cap(fixture(r))['pressure_max_upper'] for r in (1,2,4)]
    assert max(caps)-min(caps) < 5e-15


def test_sharp_comparison_improves_original_ce1g_on_same_path():
    s=fixture()
    path=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    out=certify_sharp_tabulated_path(s,path,end=.08,subcells=1)
    assert out['status']=='SCOPED_CE1H_SHARP_PRESSURE_COMPARISON'
    assert out['sharp_total_ell_h_upper'][1] < out['ce1g_total_ell_h_upper'][1]
    assert out['sharp_total_ell_h_upper'][0] < out['ce1g_total_ell_h_upper'][0]
    assert out['sharp_source_ell_h_upper'][1] < out['ce1g_source_ell_h_upper'][1]
    assert out['pressure_lipschitz_upper'] < 4*out['Emax_upper']
    assert out['steps']==4 and len(out['rows'])==4
    assert out['production_ready'] is False


def test_knot_jump_retained_in_sharp_bound():
    s=fixture()
    p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    p.coefficients[0,3,3] += 1e-5
    out=certify_sharp_tabulated_path(s,p)
    assert out['max_knot_jump_h_upper'] > 5e-6
    assert out['sharp_time_and_jump_ell_h_upper'][1] >= out['max_knot_jump_h_upper']


def test_guard_wrong_source_and_backend():
    with pytest.raises(TypeError): initial_continuum_pressure_cap(object())
    s=fixture()
    with pytest.raises(ValueError,match='backend'):
        run_sharp_tabulated_rk4(s,steps=2)
    with pytest.raises(TypeError): certify_sharp_tabulated_path(s,object())


def test_sharp_certificate_preserves_original_target_and_physics():
    s=fixture(2)
    out=run_sharp_tabulated_rk4(s,steps=4,backend='python_oracle')
    assert out['refinement']==2 and out['rays']==24
    assert out['sharp_total_ell_h_upper'][1] <= out['ce1g_total_ell_h_upper'][1]
    assert out['source_semantics']=='CE1-F exact continuum positive angular cells vs exact stored binary ray/mass source'
    assert out['time_semantics']=='CE1-G exact stored binary Hermite full-panel residual and jumps'


def test_direct_initial_constraint_root_matches_ce1f_enclosure():
    from bianchi.nonperturbative.einstein_tabulated_sharp import _initial_constraint_mismatch
    from bianchi.nonperturbative.einstein_tabulated_source import certified_tabulated_geometry
    s=fixture(2)
    p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    direct=_initial_constraint_mismatch(s,p,(.2,-.13,-.07))
    original=certified_tabulated_geometry(s,end=.08,shear=(.2,-.13,-.07))['initial_h_error_upper']
    assert direct == original


def test_narrow_positive_cell_pressure_cap_never_exceeds_energy_comparison():
    s=TabulatedRadiation([0,.001,1],[0,.001,1],[[.9,0],[0,0]],backend='python_oracle')
    cert=initial_continuum_pressure_cap(s)
    assert cert['pressure_max_upper'] > .899
    p=rk4_path(s,s.initial_state(),.02,2,backend='python_oracle')
    out=certify_sharp_tabulated_path(s,p,end=.02)
    assert out['comparison_pressure_cap'] <= out['Emax_upper']
    assert out['sharp_total_ell_h_upper'][1] <= out['ce1g_total_ell_h_upper'][1]
