"""Selected KM2C tests; no old scientific campaign is replayed."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.curved_tilt import FieldProfile, make_fixture, CurvedMemory, DirectHistory, VolterraHistory, balances
from bianchi.nonperturbative._core.tilted_collision import expected_fourforce, radiation_tensor, TiltedThomson

def setup(kind='main', beta=(0.3, -0.4, 0.2), nu0=1.3, n=6, T=0.12):
    geo, J = make_fixture(n, FieldProfile(kind, nu0), beta, T)
    return (geo, J, CurvedMemory(geo, J, beta, nu0))

def test_projection_and_gain_pullback_match_physical_generator():
    geo, J0, m = setup()
    X = m.X0
    for t in (0.0, 0.08, 0.12):
        z = m.at(t)
        J = m.carrier(t, X)
        M = m.project(t, X)
        assert np.max(abs(M - z['op'].source(J))) < 2e-11
        C = z['op'].rhs(J, m.nu0)
        E = z['screen']
        r = z['mu']
        pulled = np.einsum('nia,nij,njb->nab', E, C, E) / r[:, None, None] ** 4
        test = -z['d'][:, None, None] * X + np.einsum('nab,b->na', z['G'], M.ravel()).reshape(X.shape)
        assert np.max(abs(test - pulled)) < 2e-11

def test_optical_depth_is_time_dependent_and_ray_resolved():
    geo, J, m = setup(T=0.4)
    from numpy.polynomial.legendre import leggauss
    x, w = leggauss(24)
    ref = sum((ws * m.at(float(s))['d'] for s, ws in zip(0.2 * (x + 1), 0.2 * w)))
    assert np.max(abs(ref - m.tau(0.4))) < 2e-11
    assert np.max(abs(m.tau(0.4) - 0.4 * m.at(0)['d'])) > 0.0001

def test_volterra_no_rhs_callback(monkeypatch):
    geo, J, m = setup(T=0.1)

    def forbidden(*args, **kwargs):
        raise AssertionError('direct RHS called')
    monkeypatch.setattr(TiltedThomson, 'rhs', forbidden)
    v = VolterraHistory(m, 8)
    assert np.isfinite(v.carrier(0.1)).all()

def test_curved_direct_vs_unknown_source_solution():
    geo, J, m = setup(n=8, T=0.2)
    d = DirectHistory(m)
    v = VolterraHistory(m, 16)
    assert np.max(abs(d.moment(0.2) - v.moment(0.2))) < 3e-09
    assert np.max(abs(d.carrier(0.2) - v.carrier(0.2))) < 3e-09

def test_flat_limit_against_prior_fixed_beta_solver():
    from bianchi.nonperturbative._core.tilted_history import VolterraHistory as Flat
    geo, J, m = setup(kind='flat', T=0.2)
    v = VolterraHistory(m, 16)
    f = Flat(m.at(0)['op'], J, 1.3, 0.2, 16)
    assert np.max(abs(v.carrier(0.2) - f.carrier(0.2))) < 2e-10

def test_zero_beta_against_prior_rest_memory_solver():
    from bianchi.nonperturbative._core.source_memory import SourceMemory
    from bianchi.nonperturbative._core.volterra_solver import VolterraHistory as Rest
    geo, J, m = setup(beta=(0, 0, 0), T=0.15)
    v = VolterraHistory(m, 12)
    r = Rest(SourceMemory(geo, J), np.linspace(0, 0.15, 13))
    assert np.max(abs(v.carrier(0.15) - r.state(0.15))) < 2e-10

def test_vacuum_is_exact_full_initial_transport():
    geo, J, m = setup(nu0=0.0, T=0.2)
    v = VolterraHistory(m, 4)
    assert np.max(abs(v.carrier(0.2) - m.carrier(0.2, m.X0))) < 2e-13
    assert np.max(abs(m.tau(0.2))) == 0.0

def test_isotropic_expansion_factorizes_fixed_beta_collision():
    from bianchi.nonperturbative._core.tilted_history import DirectHistory as Flat
    geo, J, m = setup(kind='isotropic', T=0.2)
    d = DirectHistory(m)
    f = Flat(m.at(0)['op'], J, 1.3, 0.2)
    assert np.max(abs(d.carrier(0.2) - np.exp(-4 * 0.3 * 0.2) * f.carrier(0.2))) < 3e-10

def test_force_and_geometry_are_separated():
    geo, J, m = setup(n=12, T=0.15)
    d = DirectHistory(m)
    b = balances(m, 0.15, d.carrier(0.15))
    assert b['force_rel'] < 5e-09
    assert b['energy_balance_rel'] < 5e-09
    assert b['flux_balance_rel'] < 5e-09
    assert abs(b['geometric_invariant_rate']) > 0.01

def test_causal_prefix_and_global_reconstruction():
    geo, J, m = setup(T=0.2)
    v = VolterraHistory(m, 8)
    half = VolterraHistory(m, 4, end=0.1)
    assert np.max(abs(v.stages[:4] - half.stages)) < 2e-11
    assert np.max(abs(v.global_reconstruction(0.2) - v.moment(0.2))) < 2e-10

def test_initial_gain_null_carrier_not_discarded():
    geo, J = make_fixture(10, FieldProfile('main', 1.3), (0, 0, 0.6), 0.2, {('I', 3, 0): 0.1})
    m = CurvedMemory(geo, J, (0, 0, 0.6), 1.3)
    v = VolterraHistory(m, 16)
    assert np.linalg.norm(m.initial_source(0)) < 2e-12
    assert np.linalg.norm(v.moment(0.2)) > 0.0001

def test_contract_validation():
    geo, J, m = setup()
    with pytest.raises(ValueError):
        CurvedMemory(geo, J, [1, 0, 0], 1.0)
    with pytest.raises(ValueError):
        CurvedMemory(geo, J, [0, 0, 0], -1.0)
    with pytest.raises(ValueError):
        VolterraHistory(m, 0)
    with pytest.raises(ValueError):
        m.tau(-0.1)
    with pytest.raises(ValueError):
        VolterraHistory(m, 4).carrier(0.13)

def test_ambient_RK_extension_matches_checked_rhs_on_physical_states():
    from bianchi.nonperturbative._core.curved_tilt import linear_collision
    geo, J, m = setup(n=8, T=0.15)
    d = DirectHistory(m)
    for t in (0.0, 0.075, 0.15):
        Jt = d.carrier(t)
        op = m.at(t)['op']
        assert np.max(abs(linear_collision(op, Jt, 1.3) - op.rhs(Jt, 1.3))) < 2e-12
        assert np.max(abs(np.einsum('nij,nj->ni', Jt, op.n))) < 2e-10
