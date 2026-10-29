"""CE1-J source-local scale covariance and protected original fixture."""
import numpy as np
import pytest
from fractions import Fraction
from bianchi.nonperturbative.einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_pressure)
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_source_local import (
    certify_local_source_envelope, run_local_source_rk4)


def fixture(refinement=1):
    return TabulatedRadiation([0,.5,1],[0,.25,.75,1],
       [[.1,.25,.05],[.2,.15,.15]],refinement=refinement,backend='python_oracle')


def test_pressure_source_homogeneity_same_frozen_cells():
    s=fixture()
    ell=np.array([.1,.2,.03])
    s_shift=.04
    e,p=s.moments(ell)
    e2,p2=s.moments(ell+s_shift)
    assert np.allclose(p2,np.exp(-4*s_shift)*p,rtol=2e-15,atol=0)
    assert abs(e2/e-np.exp(-4*s_shift))<2e-15


def test_expanding_source_contraction_same_geometry_and_target():
    out=run_local_source_rk4(fixture(),backend='python_oracle')
    assert out['status']=='CE1J_SCOPED_SOURCE_LOCAL'
    assert out['per_panel_source_upper'][0]<=out['constant_source_upper']
    assert any(x<out['constant_source_upper'] for x in out['per_panel_source_upper'][1:])
    assert out['ce1j']['total'][1]<out['ce1i']['total'][1]<out['ce1h_total'][1]
    assert out['geometry_Emax_unchanged']>=.9
    assert not out['target_met'] and out['frozen_target']==1e-5  # refinement1 still NOT_MET
    assert out['production_ready'] is False


def test_mutated_panel_origin_is_rejected():
    s=fixture();path=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    path.coefficients[0,0,3] += .01
    with pytest.raises(ValueError, match='origin'):
        certify_local_source_envelope(s,path)


def test_bad_slope_is_not_transferred():
    s=fixture();path=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    with pytest.raises(ValueError, match='lower bound'):
        certify_local_source_envelope(s,path,slope=Fraction(1,2))


def test_oracle_required():
    with pytest.raises(ValueError,match='python_oracle'):
        run_local_source_rk4(fixture())
