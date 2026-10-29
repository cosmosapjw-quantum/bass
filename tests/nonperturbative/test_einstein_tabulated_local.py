"""CE1-I frozen-path and adversarial gates."""
from fractions import Fraction
import pytest
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_local import (
    certify_common_linear_growth, certify_pathlocal_tabulated_path,
    run_pathlocal_tabulated_rk4)


def fixture(refinement=1):
    return TabulatedRadiation([0,.5,1],[0,.25,.75,1],
       [[.1,.25,.05],[.2,.15,.15]],refinement=refinement,backend='python_oracle')


def test_common_growth_has_exact_rational_slack():
    s=fixture();p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    g=certify_common_linear_growth(s,p)
    assert g['exact_flow_slope_lower']>.37
    assert (g['slope_numerator'],g['slope_denominator'])==(3,8)
    assert min(x for row in g['path_min_bernstein_slack_per_panel'] for x in row)>=0


def test_ce1i_actual_scoped_bound_tighter_without_target_drift():
    s=fixture();o=run_pathlocal_tabulated_rk4(s,steps=4,backend='python_oracle')
    assert o['status']=='SCOPED_CE1I_PATH_LOCAL_COMPARISON'
    assert o['decaying_ce1i']['total'][1] < o['constant_ce1h']['total'][1]
    assert o['constant_ce1h']['total'][1] < o['ce1g_total_ell_h_upper'][1]
    assert o['per_panel_pressure_cap_upper'][1] < o['per_panel_pressure_cap_upper'][0]
    assert o['source_pressure_upper_unchanged'] > 0
    assert o['Emax_upper_unchanged'] >= .9
    assert o['production_ready'] is False


def test_exact_rational_bernstein_rejects_excessive_slope():
    s=fixture();p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    with pytest.raises(ValueError):certify_common_linear_growth(s,p,slope=Fraction(1,2))


def test_adversarial_negative_ell_hermite_detected():
    s=fixture();p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    p.coefficients[1,0,1] -= .1
    with pytest.raises(ValueError,match='Hermite growth'):
        certify_common_linear_growth(s,p)


def test_optin_backend_and_step_count():
    with pytest.raises(ValueError,match='backend'):
        run_pathlocal_tabulated_rk4(fixture(),steps=4)
    with pytest.raises(ValueError,match='steps'):
        run_pathlocal_tabulated_rk4(fixture(),steps=True,backend='python_oracle')
