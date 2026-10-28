"""DV2-D scoped checks. No old campaign, native solver or EFE claims."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.classb_streaming import classb_matrix, multiplication_matrix, coefficient_rhs, frozen_map
from bianchi.nonperturbative._core.classb_oracle import direct_rhs, spin_coordinate_rhs
from bianchi.nonperturbative._core.polarized_dictionary import Grid, analyze, synthesize, stokes, source_matrix, hermitian
from bianchi.nonperturbative._core.harmonic_streaming import labels
from bianchi.q import polarization as P8
TOL = 2e-11

@pytest.mark.parametrize('n', [8, 12, 20])
def test_same_physics_rhs(n):
    g = Grid(n, 2 * n)
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 1, 1): 0.16, ('I', 4, 0): 0.12, ('E', 2, 2): 0.2, ('E', 3, -1): 0.03, ('B', 2, -2): 0.06, ('V', 1, 0): 0.04}
    S = np.array([[0.12, 0.07, -0.04], [0.07, -0.21, 0.02], [-0.04, 0.02, 0.09]])
    A = np.array([0.17, -0.21, 0.35])
    H = 0.3
    nu = 0.8
    expected = coefficient_rhs(c, A, H, S, nu, lout=6)
    actual = analyze(g, direct_rhs(g, c, A, H, S, nu), 6)
    assert max((abs(actual.get(k, 0) - v) for k, v in expected.items())) < TOL

@pytest.mark.parametrize('spin', [0, 2])
def test_drift_is_not_antihermitian(spin):
    A = np.array([0.2, -0.31, 0.7])
    B = classb_matrix(spin, 4, 4, A)
    F = multiplication_matrix(spin, 4, 4, A)
    assert np.max(abs(B + B.conj().T - 2 * F)) < TOL
    assert np.linalg.norm(B + B.conj().T) > 0.01

def test_exact_coefficients_and_isotropic_zero():
    a = 0.7
    out = coefficient_rhs({('I', 1, 0): 1.0, ('E', 2, 2): 1.0}, [0, 0, a], lout=3)
    assert abs(out['I', 0, 0] - 2 * a / np.sqrt(3)) < TOL
    assert abs(out['I', 2, 0] + 2 * a / np.sqrt(15)) < TOL
    assert abs(out['B', 2, -2] + 2 * a / 3) < TOL
    z = coefficient_rhs({('I', 0, 0): 1.0}, [0, 0, a], lout=3)
    assert max((abs(v) for v in z.values())) < TOL

def test_screen_connection_and_P8_rates():
    g = Grid(8, 16)
    A = np.array([0.2, -0.4, 0.3])
    Z = np.zeros((3, 3))
    z = np.zeros(3)
    alpha = g.n @ A
    v = alpha[:, None] * g.n - A
    assert np.max(abs(v - P8.direction_rate(g.n, 0.0, Z, z, Z, A))) < TOL
    wdot = g.n * np.sum(g.bt * A, axis=1)[:, None]
    assert np.max(abs(wdot - P8.screen_vector_rate(g.bt, g.n, 0.0, Z, z, Z, A))) < TOL
    c = {('E', 2, 1): 0.3, ('B', 3, -2): 0.2}
    D = direct_rhs(g, c, A)
    coord = spin_coordinate_rhs(g, c, A)
    actual = stokes(g, D)
    assert np.max(abs(coord['P'] - actual[1] - 1j * actual[2])) < TOL
    bad = spin_coordinate_rhs(g, c, A, connection=False)
    assert np.max(abs(bad['P'] - coord['P'])) > 0.001

def test_energy_flux_and_L2():
    g = Grid(12, 24)
    A = np.array([0.17, -0.21, 0.35])
    S = np.diag([0.2, -0.3, 0.1])
    H = 0.3
    nu = 0.8
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 1, 0): 0.3, ('I', 2, -2): 0.11, ('I', 3, 2): 0.07, ('E', 2, 1): 0.04, ('B', 2, -1): 0.03}
    J = synthesize(g, c)
    I = stokes(g, J)[0]
    rho = g.w @ I
    q = np.einsum('n,n,ni->i', g.w, I, g.n)
    pressure = np.einsum('n,n,ni,nj->ij', g.w, I, g.n, g.n)
    pi = pressure - rho * np.eye(3) / 3
    dI = stokes(g, direct_rhs(g, c, A, H, S, nu))[0]
    assert abs(g.w @ dI - (-4 * H * rho - np.sum(S * pi) + 2 * A @ q)) < TOL
    assert np.max(abs(np.einsum('n,n,ni->i', g.w, dI, g.n) - (-(4 * H + nu) * q - S @ q + 3 * pi @ A))) < TOL
    Jd = direct_rhs(g, c, A)
    got = 2 * np.einsum('n,nij,nij->', g.w, J, Jd)
    want = 2 * np.einsum('n,n,nij,nij->', g.w, g.n @ A, J, J)
    assert abs(got - want) < TOL

def test_frozen_area_and_no_lorentz_redshift():
    g = Grid(12, 24)
    A = np.array([0, 0, 0.7])
    t = 0.6
    n, jac = frozen_map(g.n, A, t)
    b = np.tanh(0.7 * t)
    mu = g.n[:, 2]
    assert np.max(abs(n[:, 2] - (mu - b) / (1 - b * mu))) < TOL
    assert np.max(abs(jac - (1 - b * b) / (1 - b * mu) ** 2)) < TOL
    assert np.max(abs(jac - 1)) > 0.1
    assert abs(g.w @ jac - 4 * np.pi) < 3e-10

def test_gain_null_B22_returns_into_source():
    g = Grid(12, 24)
    c = {('B', 2, 2): 0.1}
    A = np.array([0, 0, 0.7])
    J = synthesize(g, c)
    dJ = direct_rhs(g, c, A)
    assert np.linalg.norm(np.einsum('n,nij->ij', g.w, J)) < TOL
    Mdot = np.einsum('n,nij->ij', g.w, dJ)
    predicted = source_matrix({('E', 2, -2): 0.1 * 2 * 0.7 / 3})
    assert np.max(abs(Mdot - predicted)) < TOL
    assert np.linalg.norm(Mdot) > 0.01
    positive = synthesize(g, {**c, ('I', 0, 0): 2 * np.sqrt(4 * np.pi)})
    screen = np.stack([g.bt, g.bp], axis=2)
    assert np.linalg.eigvalsh(np.einsum('nia,nij,njb->nab', screen, hermitian(positive), screen)).min() > 0

def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        classb_matrix(1, 4, 5, [0, 0, 1])
    with pytest.raises(ValueError):
        classb_matrix(2, 4, 5, [0, float('nan'), 1])
    with pytest.raises(ValueError):
        coefficient_rhs({('E', 1, 0): 1}, [0, 0, 1])
    with pytest.raises(ValueError):
        frozen_map([[0, 0, 2]], [0, 0, 1], 0.5)

def test_explicit_component_sign_is_pinned_to_runtime():
    a = 0.7
    n = np.array([[1.0, 0.0, 0.0]])
    w = np.array([[0.0, 0.0, 1.0]])
    Z = np.zeros((3, 3))
    z = np.zeros(3)
    A = np.array([0.0, 0.0, a])
    assert np.max(abs(P8.momentum_rate(n, 0.0, Z, z, Z, A) - np.array([[0.0, 0.0, -a]]))) < TOL
    assert np.max(abs(P8.screen_vector_rate(w, n, 0.0, Z, z, Z, A) - np.array([[a, 0.0, 0.0]]))) < TOL

def test_harmonic_path_never_calls_Cartesian_reference(monkeypatch):

    def forbidden(*args, **kwargs):
        raise RuntimeError('Reference access forbidden')
    monkeypatch.setattr(P8, 'direction_rate', forbidden)
    monkeypatch.setattr(P8, 'tensor_rate', forbidden)
    out = coefficient_rhs({('I', 1, 0): 0.2, ('E', 2, 2): 0.1}, [0.2, -0.3, 0.7], 0.2, np.diag([0.1, 0.2, -0.3]), 0.4, lout=4)
    assert all((np.isfinite(x) for x in out.values()))
