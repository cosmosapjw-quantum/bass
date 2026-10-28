"""DL2 scope-local acceptance tests; no BASS production campaign is invoked."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.polarized_dictionary import Grid, synthesize, analyze, source_matrix, collision_coefficients, stokes, hermitian
from bianchi.q import polarization as p8

@pytest.mark.parametrize('n', [8, 12, 20])
def test_all_m_roundtrip_and_source(n):
    g = Grid(n, 2 * n)
    for field, l in [('I', 0), ('I', 1), ('I', 2), ('E', 2), ('B', 2), ('V', 1), ('I', 4), ('E', 4), ('B', 4), ('V', 4)]:
        for m in range(-l, l + 1):
            c = {(field, l, m): 1.0}
            J = synthesize(g, c)
            out = analyze(g, J, 4)
            assert max((abs(v - c.get(k, 0.0)) for k, v in out.items())) < 2e-11
            M = np.einsum('n,nij->ij', g.w, J)
            assert np.max(np.abs(M - source_matrix(c))) < 2e-11

@pytest.mark.parametrize('chi', [1e-08, 0.1, 1.0, 8.0])
def test_same_physics_evolution(chi):
    g = Grid(12, 24)
    rng = np.random.default_rng(20261027)
    c = {(f, l, m): float(rng.normal() * 0.02) for f in ['I', 'E', 'B', 'V'] for l in range(5) if f not in ('E', 'B') or l >= 2 for m in range(-l, l + 1)}
    c['I', 0, 0] = 2 * np.sqrt(4 * np.pi)
    J = synthesize(g, c)
    screen = np.stack([g.bt, g.bp], axis=2)
    H2 = np.einsum('nia,nij,njb->nab', screen, hermitian(J), screen)
    assert np.linalg.eigvalsh(H2).min() > 0
    assert np.max(np.abs(np.einsum('nij,nj->ni', hermitian(J), g.n))) < 2e-11
    actual = p8.collide(g.n, g.w, J, chi)
    expected = synthesize(g, collision_coefficients(c, chi))
    assert np.max(np.abs(actual - expected)) < 2e-11
    H2 = np.einsum('nia,nij,njb->nab', screen, hermitian(actual), screen)
    assert np.linalg.eigvalsh(H2).min() > 0

def test_dark_quadrupole_is_not_recoverable_from_gain_moment():
    g = Grid(12, 24)
    c = {('I', 2, 1): np.sqrt(6), ('E', 2, 1): 1.0}
    J = synthesize(g, c)
    assert np.max(np.abs(np.einsum('n,nij->ij', g.w, J))) < 2e-11
    assert np.max(np.abs(p8.collide(g.n, g.w, J, 0.7) - np.exp(-0.7) * J)) < 2e-11
    assert np.linalg.norm(J) > 1

def test_legacy_screen_gauge_conversion():
    g = Grid(12, 24)
    J = synthesize(g, {('E', 2, -1): 0.3, ('B', 3, 2): 0.2, ('I', 0, 0): np.sqrt(4 * np.pi)})
    I, Q, U, V = p8.stokes_diagnostic(g.n, J)
    k = np.argmin(np.abs(g.n), axis=1)
    b = np.eye(3)[k]
    b -= np.einsum('ni,ni->n', b, g.n)[:, None] * g.n
    b /= np.linalg.norm(b, axis=1)[:, None]
    z = np.einsum('ni,ni->n', b, g.bt) + 1j * np.einsum('ni,ni->n', b, g.bp)
    own = stokes(g, J)
    assert np.max(np.abs(z ** 2 * (Q + 1j * U) - (own[1] + 1j * own[2]))) < 2e-11
    assert np.max(np.abs(Q + 1j * U - (own[1] + 1j * own[2]))) > 0.01

def test_negative_chi_and_invalid_modes_rejected():
    with pytest.raises(ValueError):
        collision_coefficients({}, -0.1)
    with pytest.raises(ValueError):
        synthesize(Grid(8, 16), {('E', 1, 0): 1.0})

def test_initial_gain_null_tail_can_source_after_shear_streaming():
    g = Grid(12, 24)
    J = synthesize(g, {('I', 4, 0): 1.0})
    S = np.diag([-0.2, -0.2, 0.4])
    H = 0.3
    Z = np.zeros((3, 3))
    z = np.zeros(3)
    s = np.einsum('ni,ij,nj->n', g.n, S, g.n)
    mdot = np.einsum('n,nij->ij', g.w, -(4 * H + s)[:, None, None] * J + p8.tensor_rate(J, g.n, H, S, z, Z, z))
    I = stokes(g, J)[0]
    pred = -0.5 * np.einsum('n,n,ni,nj,nk,nl,kl->ij', g.w, I, g.n, g.n, g.n, g.n, S)
    assert np.max(np.abs(np.einsum('n,nij->ij', g.w, J))) < 2e-11
    assert np.max(np.abs(mdot - pred)) < 2e-11
    assert np.linalg.norm(mdot) > 0.001
