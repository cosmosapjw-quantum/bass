"""Scope-local finite-time tests; no previous research campaign is rerun."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.frozen_bianchi_v import FrozenV, Geometry, Direct, Harmonic, exact_free, coordinate_reference, free_dipole_moments
from bianchi.nonperturbative._core.polarized_dictionary import Grid, synthesize, hermitian, collision_coefficients
from bianchi.nonperturbative._core.source_memory import SourceMemory
from bianchi.nonperturbative._core.volterra_solver import VolterraHistory
from bianchi.q import polarization as P8

def initial():
    return {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 1, 0): 0.13, ('I', 4, 1): 0.04, ('E', 2, 2): 0.09, ('B', 2, 2): 0.05, ('V', 1, -1): 0.03}

@pytest.mark.parametrize('A', [(0.0, 0.0, 0.7), (0.2, -0.3, 0.4)])
def test_geometry_rhs_and_screen(A):
    g = Grid(8, 16)
    p = FrozenV(A, 0.0)
    geo = Geometry(g, p, 0.5)
    t = 0.31
    z = geo.at(t)
    dp = P8.direction_rate(z['e'], 0.0, np.zeros((3, 3)), np.zeros(3), np.zeros((3, 3)), np.array(A))
    v = (z['e'] @ np.array(A))[:, None] * z['e'] - np.array(A)
    assert np.max(abs(dp - v)) < 2e-11
    for k in range(2):
        rhs = P8.screen_vector_rate(z['screen'][:, :, k], z['e'], 0.0, np.zeros((3, 3)), np.zeros(3), np.zeros((3, 3)), np.array(A))
        assert np.max(abs(rhs - geo.screen_rate(t)[:, :, k])) < 2e-11
    assert np.max(abs(z['mu'] - 1)) == 0
    assert np.max(abs(np.einsum('nia,nib->nab', z['screen'], z['screen']) - np.eye(2))) < 2e-11
    assert np.max(abs(np.einsum('ni,nia->na', z['e'], z['screen']))) < 2e-11

def test_coordinate_reference_and_no_redshift():
    g = Grid(5, 10)
    p = FrozenV((0, 0, 0.7), 0)
    geo = Geometry(g, p, 0.5)
    n, r = coordinate_reference(g.n, 0.7, 0.5)
    assert np.max(abs(n - geo.at(0.5)['e'])) < 5e-10
    assert np.max(abs(r - 1)) < 5e-10

def test_direct_matches_exact_free():
    g = Grid(10, 20)
    p = FrozenV((0, 0, 0.7), 0)
    geo = Geometry(g, p, 0.3)
    c = initial()
    d = Direct(geo, synthesize(g, c))
    assert np.max(abs(d.state(0.3) - exact_free(geo, 0.3, c))) < 5e-10

def test_static_scattering_limit():
    g = Grid(8, 16)
    p = FrozenV((0, 0, 0), 1.3)
    geo = Geometry(g, p, 0.3)
    c = initial()
    d = Direct(geo, synthesize(g, c))
    assert np.max(abs(d.state(0.3) - synthesize(g, collision_coefficients(c, 0.39)))) < 5e-10

def test_volterra_does_not_call_direct(monkeypatch):
    g = Grid(8, 16)
    p = FrozenV((0, 0, 0.6), 1.2)
    geo = Geometry(g, p, 0.15)
    J = synthesize(g, initial())
    d = Direct(geo, J)
    want = d.moment(0.15)

    def forbidden(*args, **kwargs):
        raise AssertionError('Direct callback forbidden')
    monkeypatch.setattr(Direct, '__init__', forbidden)
    v = VolterraHistory(SourceMemory(geo, J), np.linspace(0, 0.15, 17))
    assert np.max(abs(v.moment(0.15) - want)) < 3e-09

def test_free_dipole_energy_is_not_conserved_locally():
    g = Grid(24, 48)
    p = FrozenV((0, 0, 0.7), 0)
    geo = Geometry(g, p, 0.6)
    z = geo.at(0.6)
    I = 2 + 0.3 * g.n[:, 2]
    rho = float(z['w'] @ I)
    qz = float(z['w'] @ (I * z['e'][:, 2]))
    rho_ex, q_ex = free_dipole_moments(0.7, 0.6, 2, 0.3)
    assert abs(rho - rho_ex) < 2e-10 and abs(qz - q_ex) < 2e-10
    assert abs(rho - 8 * np.pi) > 0.1

def test_full_initial_gain_null_state_is_kept():
    g = Grid(12, 24)
    p = FrozenV((0, 0, 0.7), 1.3)
    geo = Geometry(g, p, 0.25)
    J = synthesize(g, {('B', 2, 2): 0.1})
    assert np.max(abs(geo.moment(0, J))) < 2e-11
    v = VolterraHistory(SourceMemory(geo, J), np.linspace(0, 0.25, 33))
    assert np.linalg.norm(v.moment(0.25)) > 0.001

def test_harmonic_initial_cutoff_and_wrong_rate_rejected():
    with pytest.raises(ValueError):
        FrozenV((0, 0, 0.7), -1)
    with pytest.raises(ValueError):
        Harmonic(FrozenV(), {('I', 6, 0): 0.1}, 4, 0.2)
    with pytest.raises(ValueError):
        Geometry(Grid(8, 16), FrozenV(), -1)

def test_semigroup_direction_and_jacobian():
    g = Grid(8, 16)
    p = FrozenV((0.1, 0.2, 0.5), 0)
    geo = Geometry(g, p, 0.6)
    n1, j1, E1 = geo.flow(g.n, geo.screen0, 0.2)
    n2, j2, E2 = geo.flow(n1, E1, 0.4)
    n, j, E = geo.flow(g.n, geo.screen0, 0.6)
    assert np.max(abs(n2 - n)) < 2e-11 and np.max(abs(j1 * j2 - j)) < 2e-11
    assert np.max(abs(E2 - E)) < 2e-11

def test_isotropic_exact_solution_and_screen_positivity():
    g = Grid(16, 32)
    p = FrozenV((0, 0, 0.7), 1.3)
    geo = Geometry(g, p, 0.3)
    J = synthesize(g, {('I', 0, 0): 2 * np.sqrt(4 * np.pi)})
    v = VolterraHistory(SourceMemory(geo, J), np.linspace(0, 0.3, 33))
    out = v.state(0.3)
    z = geo.at(0.3)
    expected = np.eye(3) - np.einsum('ni,nj->nij', z['e'], z['e'])
    assert np.max(abs(out - expected)) < 3e-09
    h = np.einsum('nia,nij,njb->nab', z['screen'], hermitian(out), z['screen'])
    assert np.linalg.eigvalsh(h).min() > 0.9
