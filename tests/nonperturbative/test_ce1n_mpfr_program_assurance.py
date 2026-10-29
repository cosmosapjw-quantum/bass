"""CE1-N: directed-MPFR certification must honor current binary inputs and panel coverage.

These are scientific contract regressions, not formal implementation verification.
"""
from fractions import Fraction
import random
import numpy as np
import pytest
from mpmath import mp

from bianchi.nonperturbative.einstein_error_budget import PolynomialRadiation, rk4_path
from bianchi.nonperturbative.einstein_interval import (
    Interval, _ideal_moment, _source_stored_binary,
    residual_taylor_mpfr, source_full_rounding_bound,
)


def _exact_pressure_lower_difference(source):
    stored = _source_stored_binary(source, [Interval(0)] * 3)
    result=[]
    for i in range(3):
        cont = _ideal_moment(source,i,0,0,0)
        lo=Fraction.from_float(stored[i].lower)
        hi=Fraction.from_float(stored[i].upper)
        result.append(max(Fraction(0),lo-cont,cont-hi))
    return result


def _assert_current_source_enclosed(source, certificate):
    gap=_exact_pressure_lower_difference(source)
    assert max(gap)>Fraction(1,1000000)
    for i,bound in enumerate(certificate['bounds']):
        assert Fraction.from_float(bound)>=gap[i], (
            f'axis={i}: exact-pressure gap lower={float(gap[i])}, '
            f'outward certificate upper={bound}'
        )


def test_positive_mass_rebinding_cannot_reuse_old_mismatch_coefficients():
    s=PolynomialRadiation(ntheta=8,backend='python_oracle')
    box=[0.,0.,0.]
    original=source_full_rounding_bound(s,box,box,max_K=3)
    assert max(original['bounds'])<1e-9
    s.mass=s.mass.copy()*2.0
    after=source_full_rounding_bound(s,box,box,max_K=3)
    _assert_current_source_enclosed(s,after)


def test_positive_ray_rebinding_cannot_reuse_old_mismatch_coefficients():
    s=PolynomialRadiation(ntheta=8,backend='python_oracle')
    box=[0.,0.,0.]
    source_full_rounding_bound(s,box,box,max_K=3)
    s.n=s.n.copy()*1.001
    after=source_full_rounding_bound(s,box,box,max_K=3)
    _assert_current_source_enclosed(s,after)


@pytest.fixture(scope='module')
def frozen_path():
    source=PolynomialRadiation(ntheta=4,backend='python_oracle')
    path=rk4_path(source,source.initial_state(),.08,2,backend='python_oracle')
    return source,path


@pytest.mark.parametrize('bad_subcells', [-4,-1,0,1.2,True,257])
def test_direct_taylor_certifier_fails_closed_on_invalid_subcell_count(bad_subcells,frozen_path):
    source,path=frozen_path
    with pytest.raises(ValueError,match='subcells'):
        residual_taylor_mpfr(source,path,0,subcells=bad_subcells)


def test_frozen_reference_current_source_is_still_enclosed():
    s=PolynomialRadiation(ntheta=8,backend='python_oracle')
    bound=source_full_rounding_bound(s,[0.,0.,0.],[0.,0.,0.],max_K=3)
    observed=_exact_pressure_lower_difference(s)
    assert all(Fraction.from_float(bound['bounds'][i])>=observed[i] for i in range(3))


def test_mpfr_outward_arithmetic_against_exact_rational_oracle():
    rng=random.Random(25029)
    for _ in range(200):
        a=Fraction(rng.randint(-200,200),2**rng.randint(1,35))
        b=Fraction(rng.choice((-1,1))*rng.randint(1,200),2**rng.randint(1,35))
        x=Interval(float(a));y=Interval(float(b))
        for observed,exact in ((x+y,a+b),(x-y,a-b),(x*y,a*b),(x/y,a/b)):
            assert Fraction.from_float(observed.lower)<=exact<=Fraction.from_float(observed.upper)


def test_mpfr_transcendentals_independent_high_precision_oracle():
    rng=random.Random(251029)
    with mp.workdps(100):
        for _ in range(60):
            x=rng.uniform(0.01,4.)
            v=Interval(x)
            for obs,exact in ((v.sqrt(),mp.sqrt(mp.mpf(x))),
                              (v.exp(),mp.exp(mp.mpf(x))),
                              (v.sinh(),mp.sinh(mp.mpf(x))),
                              (v.cosh(),mp.cosh(mp.mpf(x))),
                              (v.tanh(),mp.tanh(mp.mpf(x)))):
                assert mp.mpf(obs.lower)<=exact<=mp.mpf(obs.upper)
