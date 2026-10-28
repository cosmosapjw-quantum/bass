"""KM2B fixed-beta, normal-time, bounded tests. No earlier campaigns."""
import numpy as np
import pytest
from scipy.integrate import quad
from bianchi.nonperturbative._core import polarized_dictionary as PD
from bianchi.q import polarization as P8
from bianchi.nonperturbative._core.tilted_collision import TiltedThomson, boost_map
from bianchi.nonperturbative._core.tilted_history import DirectHistory, VolterraHistory, exponential_weights, invariant, weighted_norm
from bianchi.nonperturbative._core.km2b_fixtures import electron_fixture, mixed_coefficients

def test_exponential_weights_exact_polynomials():
    poly = [lambda x: 2 * x * x - 3 * x + 1, lambda x: 4 * x - 4 * x * x, lambda x: 2 * x * x - x]
    for r in (0.0, 0.31, 0.5, 1.0):
        z = np.array([0.0, 1e-12, 0.02, 0.9, 1.1, 10.0, 100.0])
        a = exponential_weights(z, r)
        for j in range(3):
            b = np.array([quad(lambda v: q * np.exp(-q * (r - v)) * poly[j](v), 0, r, epsabs=2e-13)[0] for q in z])
            assert np.max(abs(a[:, j] - b)) < 2e-12
        assert np.max(abs(a.sum(axis=1) + np.expm1(-z * r))) < 2e-12

def test_rest_exact_semigroup():
    g, op, J = electron_fixture([0, 0, 0], 8)
    v = VolterraHistory(op, J, 1.3, 0.7, 64)
    expected = P8.collide(g.n, g.w, J, 1.3 * 0.7)
    assert np.max(abs(v.carrier(0.7) - expected)) < 3e-09

def test_vacuum_exact_and_invalid_inputs():
    _, op, J = electron_fixture([0.3, -0.4, 0.2], 8)
    v = VolterraHistory(op, J, 0.0, 0.7, 4)
    assert np.array_equal(v.carrier(0.7), J)
    assert np.array_equal(v.carrier(0.31), J)
    for nu, t, n in [(-1.0, 0.7, 4), (1.0, 0.0, 4), (1.0, 0.7, 0), (np.nan, 0.7, 4)]:
        with pytest.raises(ValueError):
            VolterraHistory(op, J, nu, t, n)
    with pytest.raises(ValueError):
        v.carrier(0.71)
    with pytest.raises(ValueError):
        v.carrier(-0.001)

def test_volterra_uses_no_direct_source(monkeypatch):
    _, op, J = electron_fixture([0.6, 0, 0], 8)

    def forbidden(*a, **k):
        raise AssertionError('Direct RHS or source not allowed')
    monkeypatch.setattr(op, 'rhs', forbidden)
    monkeypatch.setattr(DirectHistory, '__init__', forbidden)
    v = VolterraHistory(op, J, 1.3, 0.5, 32)
    assert np.isfinite(v.moment(0.5)).all()

def test_non_equilibrium_direct_and_memory():
    _, op, J = electron_fixture([0.3, -0.4, 0.2], 8)
    d = DirectHistory(op, J, 1.3, 0.8)
    v = VolterraHistory(op, J, 1.3, 0.8, 64)
    for t in (0.0, 0.13, 0.4, 0.8):
        assert np.max(abs(d.moment(t) - v.moment(t))) < 4e-08
        assert np.max(abs(d.carrier(t) - v.carrier(t))) / np.max(abs(J)) < 4e-08

def test_boosted_equilibrium_finite_time():
    _, op, J = electron_fixture([0, 0, 0.85], 8, {('I', 0, 0): np.sqrt(4 * np.pi)})
    v = VolterraHistory(op, J, 1.3, 1.0, 16)
    assert np.max(abs(v.carrier(1.0) - J)) / np.max(abs(J)) < 2e-11

def test_normal_slice_invariant_not_electron_density():
    _, op, J = electron_fixture([0.6, 0, 0], 10)
    d = DirectHistory(op, J, 1.3, 1.0)
    v = VolterraHistory(op, J, 1.3, 1.0, 64)
    E0 = invariant(op, J)
    assert abs(invariant(op, d.carrier(1.0)) - E0) / abs(E0) < 3e-10
    assert abs(invariant(op, v.carrier(1.0)) - E0) / abs(E0) < 3e-09
    assert abs(np.trace(d.moment(1.0) - d.moment(0.0))) > 0.001

def test_gain_null_initial_I30_survives():
    _, op, J = electron_fixture([0, 0, 0.6], 12, {('I', 3, 0): 0.1})
    assert np.linalg.norm(op.source(J)) < 2e-11
    d = DirectHistory(op, J, 1.3, 0.8)
    v = VolterraHistory(op, J, 1.3, 0.8, 64)
    assert np.max(abs(d.moment(0.8) - v.moment(0.8))) < 3e-09
    assert np.linalg.norm(v.moment(0.8)) > 0.001
    assert np.linalg.norm(v.initial_source(0.8)) > 0.001

def test_prefix_causality_and_offgrid():
    _, op, J = electron_fixture([0.6, 0, 0], 8)
    a = VolterraHistory(op, J, 1.3, 0.4, 16)
    b = VolterraHistory(op, J, 1.3, 0.8, 32)
    assert np.array_equal(a.electron_endpoints, b.electron_endpoints[:17])
    assert np.max(abs(a.moment(0.27) - b.moment(0.27))) < 2e-12

def test_wrong_single_rest_time_detected():
    g, op, J = electron_fixture([0.6, 0, 0], 10)
    d = DirectHistory(op, J, 1.3, 0.8)
    Ye = op.to_electron(J)
    wrong_e = P8.collide(g.n, g.w, Ye, 1.3 * 0.8)
    wrong = VolterraHistory.to_normal(op, wrong_e)
    assert np.max(abs(wrong - d.carrier(0.8))) / np.max(abs(J)) > 0.001
    assert abs(invariant(op, wrong) - invariant(op, J)) > 0.001

def test_weighted_norm_and_screen_positivity():
    _, op, J = electron_fixture([0.3, -0.4, 0.2], 8)
    d = DirectHistory(op, J, 1.3, 0.8)
    v = VolterraHistory(op, J, 1.3, 0.8, 64)
    assert weighted_norm(op, d.carrier(0.8)) < weighted_norm(op, J)
    assert weighted_norm(op, v.carrier(0.8)) < weighted_norm(op, J)
    from bianchi.nonperturbative._core.covariant_oracle import screen
    E = screen(op.n)
    for H in (J, d.carrier(0.8), v.carrier(0.8)):
        H2 = np.einsum('nia,nij,njb->nab', E, PD.hermitian(H), E)
        assert np.linalg.eigvalsh(H2).min() > 0

def test_pairwise_matrix_exponential_oracle():
    from bianchi.nonperturbative._core.matrix_oracle import PairwiseExponential
    _, op, J = electron_fixture([0.3, -0.4, 0.2], 4)
    ex = PairwiseExponential(op.n, op.w, J, op.beta, 1.3)
    d = DirectHistory(op, J, 1.3, 0.6)
    v = VolterraHistory(op, J, 1.3, 0.6, 64)
    assert np.max(abs(ex.carrier(0.6) - d.carrier(0.6))) < 2e-10
    assert np.max(abs(ex.carrier(0.6) - v.carrier(0.6))) < 3e-09

def test_uncompressed_history_assembly():
    from bianchi.nonperturbative._core.matrix_oracle import uncompressed_source
    _, op, J = electron_fixture([0.6, 0, 0], 4)
    v = VolterraHistory(op, J, 1.3, 0.6, 5)
    stages = uncompressed_source(op, J, 1.3, 0.6, 5)
    assert np.max(abs(stages - v.stages)) < 2e-11
