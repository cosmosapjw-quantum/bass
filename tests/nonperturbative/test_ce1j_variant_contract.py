"""CE1-J: source/path variant reconciliation acceptance, fixed collisionless scope."""
from fractions import Fraction
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_interval import stored_ray_energy_majorant
from bianchi.nonperturbative.einstein_tabulated_time import run_scoped_tabulated_rk4
from bianchi.nonperturbative.einstein_tabulated_sharp import run_sharp_tabulated_rk4
from bianchi.nonperturbative.einstein_tabulated_local import run_local_tabulated_rk4


def fixture():
    return TabulatedRadiation([0,.5,1],[0,.25,.75,1],
                              [[.1,.25,.05],[.2,.15,.15]],
                              refinement=1,backend='python_oracle')


def test_current_ray_norm_majorant_recomputed_not_reused():
    source=fixture()
    initial=stored_ray_energy_majorant(source)
    source.n=source.n.copy()*2.0
    new=stored_ray_energy_majorant(source)
    assert new>=1.999*initial
    actual_mass=sum((Fraction.from_float(float(w)) for w in source.mass),Fraction())
    norm2=max(sum((Fraction.from_float(float(x))**2 for x in ray),Fraction())
              for ray in source.n)
    assert Fraction.from_float(float(new))**2>=actual_mass**2*norm2


def test_majorant_repeat_is_idempotent_for_unchanged_stored_data():
    source=fixture()
    a=stored_ray_energy_majorant(source)
    b=stored_ray_energy_majorant(source)
    assert a==b
    assert not hasattr(source,'_ce1c_stored_mass_cap')


def test_three_comparison_lanes_same_binary_physical_fixture():
    # Intentional independent public interfaces: no tolerance relaxation.
    a=run_scoped_tabulated_rk4(fixture(),steps=2,end=.04,subcells=1,backend='python_oracle')
    b=run_sharp_tabulated_rk4(fixture(),steps=2,end=.04,subcells=1,backend='python_oracle')
    c=run_local_tabulated_rk4(fixture(),steps=2,end=.04,subcells=1,backend='python_oracle')
    assert a['rays']==b['rays']==c['rays']==6
    assert a['source_pressure_upper']==c['source_pressure_upper']
    assert c['ce1g_total_ell_h_upper']==a['total_ell_h_upper']
    assert b['ce1g_total_ell_h_upper']==a['total_ell_h_upper']
    assert c['local_total_ell_h_upper'][1] <= b['sharp_total_ell_h_upper'][1]
    assert c['ce1h_total_ell_h_upper'][1] <= b['sharp_total_ell_h_upper'][1]
    assert c['fixed_target_h']==1e-5
    assert not c['production_ready']
