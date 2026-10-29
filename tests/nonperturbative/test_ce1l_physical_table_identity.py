"""CE1-L hostile review: physical continuum is immutable; rays/masses may be rebound."""
from fractions import Fraction
import numpy as np
import pytest
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_source import (
    TabulatedRadiation, certified_tabulated_energy, certified_tabulated_pressure,
)
from bianchi.nonperturbative.einstein_tabulated_time import certify_tabulated_computed_path


def fixture(energy=.9):
    return TabulatedRadiation([0,1],[0,1],[[energy]],backend='python_oracle')


def test_cell_rebinding_rejected_before_false_geometry_certificate():
    source=fixture()
    path=rk4_path(source,source.initial_state((0.,0.,0.)),.08,4,backend='python_oracle')
    source.cells=fixture(1.).cells
    with pytest.raises(ValueError,match='physical|cell|immutable'):
        certify_tabulated_computed_path(source,path,shear=(0.,0.,0.))


def test_continuum_energy_rebinding_fails_before_certification():
    source=fixture()
    source.continuum_energy=Fraction(1,1)
    with pytest.raises(ValueError,match='physical|energy|immutable'):
        certified_tabulated_energy(source)


def test_replaced_original_cell_energy_rejected():
    source=fixture()
    source.cell_energy=np.array([[1.]])
    with pytest.raises(ValueError,match='physical|table|immutable'):
        certified_tabulated_pressure(source,[.08]*3)


def test_original_cell_energy_mutated_in_place_rejected():
    source=fixture()
    source.cell_energy.setflags(write=True)
    source.cell_energy[0,0]=1.0
    with pytest.raises(ValueError,match='physical|table|immutable'):
        certified_tabulated_energy(source)


def test_rebound_physical_edges_rejected():
    source=fixture()
    source.phi_fraction_edges=np.array([0.,.4,1.])
    with pytest.raises(ValueError,match='physical|edge|immutable'):
        certified_tabulated_pressure(source,[.08]*3)


def test_valid_positive_stored_mass_rebinding_retained():
    source=fixture()
    source.mass=source.mass.copy()*1.1
    assert certified_tabulated_pressure(source,[.08]*3)['bound_max']>0


def test_original_physical_table_remains_certifiable():
    source=fixture()
    path=rk4_path(source,source.initial_state((0.,0.,0.)),.08,4,backend='python_oracle')
    assert certify_tabulated_computed_path(
        source,path,shear=(0.,0.,0.)
    )['production_ready'] is False


def test_direct_initial_pressure_cap_cannot_bypass_physical_table_lock():
    from bianchi.nonperturbative.einstein_tabulated_sharp import initial_continuum_pressure_cap
    source=fixture()
    source.mu_edges=np.array([0.,.6,1.])
    with pytest.raises(ValueError,match='physical|table|immutable'):
        initial_continuum_pressure_cap(source)
