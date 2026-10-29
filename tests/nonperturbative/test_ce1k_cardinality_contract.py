"""Regression for CE1-K: an unsafe mutated cell/ray topology must fail closed."""
import numpy as np
import pytest

from bianchi.nonperturbative.einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_pressure, certified_tabulated_energy,
)
from bianchi.nonperturbative.einstein_interval import stored_ray_energy_majorant


def test_appended_positive_ray_rejected_before_false_source_certificate():
    s = TabulatedRadiation([0, 1], [0, 1], [[.9]], backend='python_oracle')
    s.n = np.vstack([s.n, np.array([1., 0., 0.])])
    s.mass = np.append(s.mass, 1.0)
    with pytest.raises(ValueError, match='cardinality'):
        certified_tabulated_pressure(s, [.08, .08, .08])


def test_appended_ray_rejected_before_false_stored_energy_comparison():
    s = TabulatedRadiation([0, 1], [0, 1], [[.9]], backend='python_oracle')
    s.n = np.vstack([s.n, np.array([1., 0., 0.])])
    s.mass = np.append(s.mass, 1.0)
    with pytest.raises(ValueError, match='cardinality'):
        certified_tabulated_energy(s)


def test_same_cardinality_positive_mass_and_ray_mutations_still_allowed():
    s = TabulatedRadiation([0, 1], [0, 1], [[.9]], backend='python_oracle')
    s.mass = s.mass.copy() * 1.5
    s.n = s.n.copy() * 1.01
    bound = certified_tabulated_pressure(s, [.08, .08, .08])
    assert bound['bound_max'] > 0
    assert stored_ray_energy_majorant(s) > 1.0


def test_missing_ray_rejected_for_energy_and_pressure():
    s = TabulatedRadiation([0, .5, 1], [0, 1], [[.4], [.5]], backend='python_oracle')
    s.n = s.n[:1].copy()
    s.mass = s.mass[:1].copy()
    for certify in (lambda: certified_tabulated_pressure(s, [.08]*3),
                    lambda: certified_tabulated_energy(s)):
        with pytest.raises(ValueError, match='cardinality'):
            certify()


def test_incorrect_ray_rank_rejected():
    s = TabulatedRadiation([0, 1], [0, 1], [[.9]], backend='python_oracle')
    s.n = s.n.reshape(3)
    with pytest.raises(ValueError, match='shape'):
        certified_tabulated_pressure(s, [.08]*3)


def test_incorrect_mass_shape_rejected():
    s = TabulatedRadiation([0, 1], [0, 1], [[.9]], backend='python_oracle')
    s.mass = s.mass.reshape(1, 1)
    with pytest.raises(ValueError, match='shape'):
        certified_tabulated_pressure(s, [.08]*3)
