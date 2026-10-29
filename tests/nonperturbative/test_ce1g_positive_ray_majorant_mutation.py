"""CE1-G audit: the fourth-derivative cap must follow the CURRENT positive source."""
from fractions import Fraction

import numpy as np
import pytest

from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_interval import (
    stored_ray_energy_majorant, residual_taylor_mpfr,
)


def model():
    return TabulatedRadiation([0, .5, 1], [0, .25, .75, 1],
                              [[.1, .25, .05], [.2, .15, .15]],
                              backend='python_oracle')


def test_positive_mass_replacement_invalidates_majorant():
    s = model()
    a = stored_ray_energy_majorant(s)
    assert a > 0
    s.mass = s.mass.copy() * 100
    b = stored_ray_energy_majorant(s)
    assert b >= a * 99.999, 'Old unkeyed cache makes majorant underestimate current mass'
    actual_sum = sum((Fraction.from_float(float(w)) for w in s.mass), Fraction())
    max_norm2 = max(sum((Fraction.from_float(float(z))**2 for z in ray), Fraction()) for ray in s.n)
    assert Fraction.from_float(float(b))**2 >= actual_sum**2 * max_norm2


def test_positive_ray_replacement_invalidates_majorant():
    s = model()
    a = stored_ray_energy_majorant(s)
    s.n = s.n.copy() * 2
    b = stored_ray_energy_majorant(s)
    assert b >= a*1.999, 'Old unkeyed cache makes majorant underestimate current ray norm'


def test_time_fourth_derivative_cap_tracks_current_source():
    s = model()
    p = rk4_path(s, s.initial_state(), .08, 4, backend='python_oracle')
    initial = residual_taylor_mpfr(s,p,0,subcells=1)
    s.mass = s.mass.copy() * 100
    changed = residual_taylor_mpfr(s,p,0,subcells=1)
    assert changed['fourth_derivative_bound'] > initial['fourth_derivative_bound'] * 30
    assert changed['h_defect'] >= 0


def test_unmodified_source_majorant_is_idempotent():
    s = model()
    one = stored_ray_energy_majorant(s)
    two = stored_ray_energy_majorant(s)
    assert one == two
