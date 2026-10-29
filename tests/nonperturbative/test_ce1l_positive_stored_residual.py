"""CE1-L hostile review: direct MPFR fourth majorant requires nonnegative stored mass."""
import numpy as np
import pytest
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_interval import (
    stored_ray_energy_majorant, _p4_interval, Interval, residual_taylor_mpfr,
)
from bianchi.nonperturbative.einstein_error_budget import HermitePath


def bad_source():
    s=TabulatedRadiation([0,.5,1],[0,1],[[.4],[.5]],backend='python_oracle')
    s.mass=np.array([100.,-99.])
    return s


def test_signed_cancellation_must_not_enter_fourth_derivative_certificate():
    s=bad_source()
    actual_fourth=16*float(max(abs(s.moments([0,0,0])[1])))
    # Independent analytic isotropic ell_i(u)=u/2 gives 16*|P_i(0)|.
    # Frozen RED cap was 187.00000000000006, violating this premise.
    assert actual_fourth>3*187.00000000000006
    with pytest.raises(ValueError,match='Nonnegative|positive|mass|signed'):
        _p4_interval(s,[Interval(.5),Interval(0),Interval(0)],
                     [Interval(0),Interval(0),Interval(0)])
    with pytest.raises(ValueError,match='Nonnegative|positive|mass|signed'):
        stored_ray_energy_majorant(s)


def test_signed_mass_rejected_by_low_level_mpfr_residual():
    s=bad_source()
    a=np.array([0.,0.,0.,.5,.5,.5])
    b=np.array([.01,.01,.01,.5,.5,.5])
    path=HermitePath(np.array([0.,.02]),np.array([a,b]),np.array([
        [.5,.5,.5,0.,0.,0.],[.5,.5,.5,0.,0.,0.]
    ]))
    with pytest.raises(ValueError,match='Nonnegative|positive|mass|signed'):
        residual_taylor_mpfr(s,path,0,subcells=1)


def test_original_positive_source_remains_valid():
    s=TabulatedRadiation([0,.5,1],[0,1],[[.4],[.5]],backend='python_oracle')
    assert stored_ray_energy_majorant(s)>0
