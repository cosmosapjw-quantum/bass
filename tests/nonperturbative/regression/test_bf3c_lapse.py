"""BF3-C bounded collisionless characteristic acceptance, independent references."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.lapse_transport import PeriodicLapse, TetradHistory, screen_basis, radial_exact
from bianchi.nonperturbative._core.independent_oracles import HamiltonianHistory, CoordinateParallelHistory, ReducedMeasureHistory
from bianchi.nonperturbative._core.polarized_dictionary import hermitian

def sample():
    pos = np.array([[0.3, 0.2, 0.1], [1.1, -0.1, 0.4], [2.2, 0.8, -0.2], [4.4, 0.1, 0.2]])
    n = np.array([[0.6, 0.8, 0.0], [-0.4, 0.3, np.sqrt(0.75)], [0.2, -0.8, np.sqrt(0.32)], [-0.5, -0.5, np.sqrt(0.5)]])
    return (pos, n)

def test_invalid_inputs_and_domain():
    with pytest.raises(ValueError):
        PeriodicLapse(np.nan)
    with pytest.raises(ValueError):
        PeriodicLapse(0.5, cbar=0)
    p, n = sample()
    m = PeriodicLapse(0.45)
    with pytest.raises(ValueError):
        TetradHistory(m, p, n * 1.1, 0.2)
    with pytest.raises(ValueError):
        HamiltonianHistory(m, p, n * 0, 0.2)
    h = TetradHistory(m, p, n, 0.2)
    with pytest.raises(ValueError):
        h.at(0.3)

def test_constant_lapse_exact_clock_and_translation():
    p, n = sample()
    m = PeriodicLapse(0.0, offset=0.3, cbar=0.7)
    h = TetradHistory(m, p, n, 0.6)
    q = h.at(0.6)
    assert np.max(abs(q['x'] - (p + 0.6 * 0.7 * np.exp(0.3) * n))) < 2e-11
    assert np.max(abs(q['n'] - n)) < 2e-11
    assert np.max(abs(q['r'] - 1)) < 2e-11
    assert np.max(abs(q['screen'] - h.screen0)) < 2e-11

def test_canonical_killing_transverse_and_orbit_parity():
    p, n = sample()
    m = PeriodicLapse(0.55, cbar=0.9)
    h = TetradHistory(m, p, n, 1.2)
    k = HamiltonianHistory(m, p, n, 1.2)
    for t in np.linspace(0, 1.2, 7):
        q = h.at(t)
        z = k.at(t)
        pn = q['r'][:, None] * q['n']
        assert np.max(abs(q['x'] - z['x'])) < 2e-09
        assert np.max(abs(pn - z['p'])) < 2e-09
        assert np.max(abs(m.N(q['x'][:, 0]) * q['r'] - m.N(p[:, 0]))) < 2e-09
        assert np.max(abs(pn[:, 1:] - n[:, 1:])) < 2e-09

def test_coordinate_parallel_transport_screen():
    p, n = sample()
    m = PeriodicLapse(-0.6, cbar=1.1)
    h = TetradHistory(m, p, n, 1.0)
    c = CoordinateParallelHistory(m, p, n, 1.0, screen0=h.screen0)
    q = h.at(1.0)
    z = c.at(1.0)
    assert np.max(abs(q['x'] - z['x'])) < 2e-09
    assert np.max(abs(q['n'] - z['n'])) < 2e-09
    assert np.max(abs(q['screen'] - z['screen'])) < 2e-09
    assert z['null_error'] < 2e-09 and z['orthogonality_error'] < 2e-09
    assert z['parallel_gram_error'] < 2e-09

def test_exact_radial_quadrature_and_gravitational_redshift():
    m = PeriodicLapse(0.7, cbar=0.8)
    for sign in (-1, 1):
        p = np.array([[0.4, 0, 0.0]])
        h = TetradHistory(m, p, [[sign, 0, 0]], 1.1)
        ex, er = radial_exact(m, 0.4, sign, 1.1)
        q = h.at(1.1)
        assert abs(q['x'][0, 0] - ex) < 2e-09
        assert abs(q['r'][0] - er) < 2e-09
        assert np.max(abs(q['screen'] - h.screen0)) < 2e-09
        assert abs(q['r'][0] - 1) > 0.001

def test_canonical_six_dimensional_symplectic_volume():
    p, n = sample()
    m = PeriodicLapse(0.65)
    h = HamiltonianHistory(m, p, n, 1.0, tangent=True)
    z = h.at(1.0)
    F = z['tangent']
    O = np.block([[np.zeros((3, 3)), np.eye(3)], [-np.eye(3), np.zeros((3, 3))]])
    assert np.max(abs(F.swapaxes(1, 2) @ O @ F - O)) < 2e-08
    assert np.max(abs(np.linalg.det(F) - 1)) < 2e-08

def test_coupled_space_angle_measure_not_angular_only():
    m = PeriodicLapse(0.55)
    h = ReducedMeasureHistory(m, [0.3, 1.1, 2.2, 4.4], [0.4, -0.3, 0.6, -0.7], 1.2)
    z = h.at(1.2)
    F = z['tangent']
    r = z['r']
    det = np.linalg.det(F)
    assert np.max(abs(det * r ** 3 - 1)) < 2e-08
    assert np.max(abs(F[:, 1, 1] * r ** 3 - 1)) > 0.001
    assert np.max(abs(F[:, 0, 0] * F[:, 1, 1] - det)) > 0.001
    assert np.max(abs(F[:, 0, 0] * F[:, 1, 1] - F[:, 0, 1] * F[:, 1, 0] - det)) < 2e-11

def test_turning_point_from_killing_and_transverse_momentum():
    m = PeriodicLapse(0.55)
    p = np.array([[np.pi / 2, 0, 0.0]])
    h = TetradHistory(m, p, [[-0.6, 0.8, 0.0]], 4.0)
    from scipy.optimize import brentq
    ts = np.linspace(0, 4, 81)
    mu = np.array([h.at(t)['n'][0, 0] for t in ts])
    ii = np.where(mu[:-1] * mu[1:] < 0)[0]
    assert len(ii) > 0
    t = brentq(lambda u: h.at(u)['n'][0, 0], ts[ii[0]], ts[ii[0] + 1], xtol=1e-13)
    q = h.at(t)
    expected = np.arccos(np.log(1.25) / 0.55)
    assert abs(q['x'][0, 0] - expected) < 2e-09
    assert abs(m.N(q['x'][0, 0]) - 1.25) < 2e-09

def test_full_iquv_transport_and_screen_positivity():
    p, n = sample()
    m = PeriodicLapse(0.55)
    h = TetradHistory(m, p, n, 0.9)
    X = np.array([[0.65, -0.06], [0.12, 0.35]])
    q = h.at(0.9)
    J = h.carrier(0.9, X)
    H = hermitian(J)
    E = q['screen']
    B = E.swapaxes(1, 2) @ H @ E / q['r'][:, None, None] ** 4
    assert np.max(abs(B - hermitian(X))) < 2e-08
    assert np.min(np.linalg.eigvalsh(E.swapaxes(1, 2) @ H @ E)) > 0
    assert np.max(abs(J @ q['n'][:, :, None])) < 2e-09
    assert np.max(abs(np.trace(J, axis1=1, axis2=2) - q['r'] ** 4)) < 2e-09

def test_static_radiation_equilibrium_f_of_killing_energy():
    p, n = sample()
    m = PeriodicLapse(0.8)
    h = TetradHistory(m, p, n, 1.3)
    q = h.at(1.3)
    f0 = np.exp(-m.N(p[:, 0]))
    f1 = np.exp(-m.N(q['x'][:, 0]) * q['r'])
    assert np.max(abs(f0 - f1)) < 2e-09
    I0 = m.N(p[:, 0]) ** (-4)
    assert np.max(abs(q['r'] ** 4 * I0 - m.N(q['x'][:, 0]) ** (-4))) < 2e-08

def test_backward_flow_and_periodic_lift():
    p, n = sample()
    m = PeriodicLapse(0.45)
    h = TetradHistory(m, p, n, 0.8)
    q = h.at(0.8)
    b = TetradHistory(m, q['x'], q['n'], -0.8, screen0=q['screen'])
    z = b.at(-0.8)
    assert np.max(abs(z['x'] - p)) < 2e-09
    assert np.max(abs(z['n'] - n)) < 2e-09
    assert np.max(abs(q['r'] * z['r'] - 1)) < 2e-09
    assert np.max(abs(z['screen'] - h.screen0)) < 2e-09
    pp = p.copy()
    pp[:, 0] += 2 * np.pi
    hp = TetradHistory(m, pp, n, 0.8).at(0.8)
    assert np.max(abs(hp['x'] - q['x'] - [2 * np.pi, 0, 0])) < 2e-09

def test_killing_energy_integral_from_independent_measure():
    m = PeriodicLapse(0.55)
    x = np.repeat(np.arange(8) * 2 * np.pi / 8, 8)
    mu, w = np.polynomial.legendre.leggauss(8)
    mus = np.tile(mu, 8)
    weights = np.tile(w, 8) * 2 * np.pi / 8
    h = ReducedMeasureHistory(m, x, mus, 0.8)
    z = h.at(0.8)
    I0 = 2 + 0.3 * np.cos(x) + 0.2 * mus
    initial = np.sum(weights * m.N(x) * I0)
    final = np.sum(weights * m.N(z['x']) * z['r'] ** 4 * I0 * np.linalg.det(z['tangent']))
    assert abs(final / initial - 1) < 2e-08
    wrong = np.sum(weights * m.N(z['x']) * z['r'] ** 4 * I0 * z['tangent'][:, 1, 1])
    assert abs(wrong / initial - 1) > 0.001

def test_missing_acceleration_screen_is_detected():
    p, n = sample()
    m = PeriodicLapse(0.55)
    h = TetradHistory(m, p, n, 1.0)
    q = h.at(1.0)
    leak = np.einsum('ni,nij->nj', q['n'], h.screen0)
    assert np.max(abs(leak)) > 0.01
    assert np.max(abs(m.N(q['x'][:, 0]) - m.N(p[:, 0]))) > 0.01
