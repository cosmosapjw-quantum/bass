"""CE1-M adversarial transport: CE1-K local source bound against CE1-L input lock."""
import numpy as np
import pytest
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation, certified_tabulated_pressure
from bianchi.nonperturbative.einstein_interval import stored_ray_energy_majorant
from bianchi.nonperturbative.einstein_tabulated_source_canonical import run_canonical_panel_source


def fixture(refinement=1):
    return TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=refinement,backend='python_oracle')


def test_physical_cell_rebinding_rejected_on_ce1m_oracle():
    s=fixture();t=fixture()
    s.cells=t.cells
    with pytest.raises(ValueError,match='physical'):
        run_canonical_panel_source(s,backend='python_oracle')


def test_binary_cell_energy_mutation_rejected():
    s=fixture();s.cell_energy=s.cell_energy.copy();s.cell_energy[0,0]=0.35
    with pytest.raises(ValueError,match='physical'):
        run_canonical_panel_source(s,backend='python_oracle')


def test_stored_ray_append_fails_closed():
    s=fixture();s.n=np.vstack([s.n,s.n[0]]);s.mass=np.append(s.mass,s.mass[0])
    with pytest.raises(ValueError,match='cardinality'):
        certified_tabulated_pressure(s,[.08]*3)
    with pytest.raises(ValueError):
        run_canonical_panel_source(s,backend='python_oracle')


def test_signed_cancelled_mass_rejected_in_analytic_remainder():
    s=fixture();s.mass=np.array([100.]+[-99.]+[0.]*(len(s.mass)-2))
    with pytest.raises(ValueError,match='Nonnegative'):
        stored_ray_energy_majorant(s)


def test_original_frozen_refinement_one_is_still_target_not_met():
    result=run_canonical_panel_source(fixture(),backend='python_oracle')
    assert result['total_h_upper']>1.e-5
    assert result['total_h_upper']<result['ce1i_total_h_upper']
    assert result['upper_dag']=='9/15'
    assert result['production_ready'] is False
