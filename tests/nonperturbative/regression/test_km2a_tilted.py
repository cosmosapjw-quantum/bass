"""Instantaneous collision-only contract; no historical IVP campaigns."""
import numpy as np
import pytest
from bianchi.q import polarization as P8
from bianchi.nonperturbative._core import polarized_dictionary as PD
from bianchi.nonperturbative._core.tilted_collision import TiltedThomson, boost_map, radiation_tensor, expected_fourforce

def mapped(beta, n=12):
    g = PD.Grid(n, 2 * n)
    S, nlab, invD = boost_map(g.n, -np.asarray(beta))
    return (g, nlab, g.w / invD ** 2, S, invD)

def mixed(g):
    return PD.synthesize(g, {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 1, 1): 0.12, ('I', 2, -1): 0.08, ('I', 4, 2): 0.04, ('E', 2, 0): 0.09, ('B', 3, 1): 0.06, ('V', 1, -1): 0.07})

def to_lab(J, S, D):
    return D[:, None, None] ** 4 * np.einsum('nik,nkl,njl->nij', S, J, S)

@pytest.mark.parametrize('beta', [[0, 0, 0], [0.6, 0, 0], [0.3, -0.4, 0.2]])
def test_screen_and_carrier_roundtrip(beta):
    g, n, w, Se, De = mapped(beta)
    S, ne, D = boost_map(n, beta)
    J = mixed(g)
    lab = to_lab(J, Se, De)
    back = to_lab(lab, S, D)
    assert np.max(abs(ne - g.n)) < 2e-12
    assert np.max(abs(D * De - 1)) < 2e-12
    assert np.max(abs(back - J)) < 2e-11
    assert np.max(abs(np.einsum('nki,nkj->nij', S, S) - P8.screen_proj(n))) < 2e-11

def test_zero_beta_and_vacuum():
    g = PD.Grid(12, 24)
    J = mixed(g)
    op = TiltedThomson(g.n, g.w, [0, 0, 0])
    M = np.einsum('n,nij->ij', g.w, J)
    expected = 1.7 * (3 / (8 * np.pi) * np.einsum('nik,kl,nlj->nij', g.P, M, g.P) - J)
    assert np.max(abs(op.rhs(J, 1.7) - expected)) < 2e-11
    assert np.array_equal(TiltedThomson(g.n, g.w, [0.6, 0, 0]).rhs(J, 0.0), np.zeros_like(J))

@pytest.mark.parametrize('beta', [[0.6, 0, 0], [0.3, -0.4, 0.2]])
def test_local_force_and_correct_invariant(beta):
    g, n, w, S, D = mapped(beta)
    J = to_lab(mixed(g), S, D)
    op = TiltedThomson(n, w, beta)
    rhs = op.rhs(J, 1.3)
    Q = np.einsum('n,n,na->a', w, np.trace(rhs, axis1=1, axis2=2), np.c_[np.ones(len(w)), n])
    expected = expected_fourforce(radiation_tensor(n, w, J), beta, 1.3)
    assert np.max(abs(Q - expected)) < 2e-10
    assert abs(Q[0] - np.dot(beta, Q[1:])) < 2e-10

def test_boosted_isotropy_is_equilibrium():
    beta = [0.6, 0, 0]
    g, n, w, S, D = mapped(beta)
    J = to_lab(P8.unpolarized(g.n, np.ones(len(w))), S, D)
    assert np.max(abs(TiltedThomson(n, w, beta).rhs(J, 1.1))) < 2e-11

def test_correct_D_rates_and_input_rejection():
    n = np.array([[1.0, 0, 0], [-1.0, 0, 0], [0, 1.0, 0]])
    _, _, D = boost_map(n, [0.6, 0, 0])
    assert np.allclose(D, [0.5, 2, 1.25], atol=2e-15, rtol=0)
    for beta in ([1, 0, 0], [np.nan, 0, 0]):
        with pytest.raises(ValueError):
            boost_map(n, beta)
    with pytest.raises(ValueError):
        TiltedThomson(n, np.ones(3), [0, 0, 0]).rhs(np.zeros((3, 3, 3)), -1)
    with pytest.raises(ValueError):
        boost_map(2 * n, [0, 0, 0])

def test_old_single_optical_depth_sandwich_lacks_rate():
    g, n, w, S, D = mapped([0.6, 0, 0])
    Je = mixed(g)
    J = to_lab(Je, S, D)
    op = TiltedThomson(n, w, [0.6, 0, 0])
    Me = np.einsum('n,nij->ij', g.w, Je)
    Ce = 3 / (8 * np.pi) * np.einsum('nik,kl,nlj->nij', g.P, Me, g.P) - Je
    wrong = to_lab(Ce, S, D)
    right = op.rhs(J, 1.0)
    assert np.max(abs(right - op.D[:, None, None] * wrong)) < 2e-11
    assert np.max(abs(right - wrong)) > 0.001

def test_pairwise_oracle_matches_and_no_scalar_projection():
    from bianchi.nonperturbative._core.covariant_oracle import pairwise_rhs
    g, n, w, S, D = mapped([0.3, -0.4, 0.2], 8)
    J = to_lab(mixed(g), S, D)
    a = TiltedThomson(n, w, [0.3, -0.4, 0.2]).rhs(J, 1.2)
    b = pairwise_rhs(n, w, J, [0.3, -0.4, 0.2], 1.2)
    assert np.max(abs(a - b)) / np.max(abs(J)) < 2e-11

def test_gain_rank_and_noncommutation():
    g, n, w, S, D = mapped([0.6, 0, 0], 8)
    op = TiltedThomson(n, w, [0.6, 0, 0])
    J = to_lab(mixed(g), S, D)
    cols = np.stack([op.gain_from_source(np.eye(9)[i].reshape(3, 3)).ravel() for i in range(9)], axis=1)
    assert np.linalg.matrix_rank(cols, tol=1e-11) == 9
    comm = op.D[:, None, None] * op.gain(J) - op.gain(op.D[:, None, None] * J)
    assert np.max(abs(comm)) > 0.001

def test_scalar_spectral_reference():
    from bianchi.nonperturbative._core.spectral_check import compare
    r = compare([0.6, 0, 0], nrad=10)
    assert r['relative_error'] < 2e-10

def test_legacy_boost_domain_and_small_beta():
    from bianchi.q.polstate import _boost_screen_map
    g = PD.Grid(8, 16)
    for beta in ([0, 0, 0], [1e-10, 0, 0], [0.3, -0.4, 0.2]):
        S, _, _ = boost_map(g.n, beta)
        old, _, _ = _boost_screen_map(beta, g.n)
        assert np.max(abs(S - np.einsum('nik,nkj->nij', old, g.P))) < 2e-11
