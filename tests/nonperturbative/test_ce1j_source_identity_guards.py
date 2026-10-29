"""PR243/244 independent correction witnesses applied narrowly to CE1-J child."""
import pytest
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_interval import stored_ray_energy_majorant
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_time import certify_tabulated_computed_path


def fixture():
    return TabulatedRadiation([0,.5,1],[0,.25,.75,1],
        [[.1,.25,.05],[.2,.15,.15]],backend='python_oracle')


def test_majorant_recomputes_after_current_positive_mass_changed():
    s=fixture();v=stored_ray_energy_majorant(s)
    s.mass=s.mass*64
    assert stored_ray_energy_majorant(s)>=64*v


def test_majorant_recomputes_after_current_ray_changed():
    s=fixture();v=stored_ray_energy_majorant(s)
    s.n=s.n*2
    assert stored_ray_energy_majorant(s)>=2*v


def test_direct_ce1g_path_rejects_stored_origin_mismatch():
    s=fixture();p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
    p.coefficients[0,0,3]+=.01
    with pytest.raises(ValueError,match='origin'):
        certify_tabulated_computed_path(s,p)
