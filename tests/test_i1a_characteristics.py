"""I1a · class A 특성곡선 커널 (65차) — PLAN §1 게이트 전부."""
import numpy as np
import pytest

from bianchi.matter import class_a_char as CH


def test_symbolic_frame_covariance_and_cross_form():
    from audit.i1_characteristics_derivation import (
        class_a_cross_form_symbolic, frame_covariance_exact_points)
    for res in frame_covariance_exact_points(3):
        assert all(r == 0 for r in res)
    assert all(r == 0 for r in class_a_cross_form_symbolic())


def test_symbolic_viii_and_general_metric():
    from audit.i1_characteristics_derivation import (
        type_ii_general_metric_symbolic, type_viii_exact_point)
    resid, signs = type_viii_exact_point()
    assert all(r == 0 for r in resid)
    assert min(signs) < 0 < max(signs)
    assert all(r == 0 for r in type_ii_general_metric_symbolic())


def test_n_term_preserves_magnitude_instantaneously():
    rng = np.random.default_rng(3)
    Nf = rng.standard_normal((3, 3))
    Nf = 0.5 * (Nf + Nf.T)
    for m in (0.0, 0.7):
        for _ in range(5):
            p = rng.standard_normal(3)
            r = CH.characteristic_rhs_class_a(p, 0.0, np.zeros((3, 3)),
                                              np.zeros(3), Nf, m)
            assert abs(float(p @ r)) <= 1e-15 * (p @ p)


def test_bianchi_i_matches_matrix_exponential():
    from scipy.linalg import expm
    rng = np.random.default_rng(5)
    S = rng.standard_normal((3, 3))
    S = 0.2 * (S + S.T)
    S -= np.trace(S) / 3.0 * np.eye(3)
    H = 0.4

    def bg(t):
        return H, S, np.zeros(3), np.zeros(3)

    p0 = rng.standard_normal(3)
    for m in (0.0, 1.3):
        got = CH.evolve_characteristic(p0, bg, m, 0.0, 1.0, nsteps=256)
        want = expm(-(H * np.eye(3) + S) * 1.0) @ p0
        assert np.abs(got - want).max() <= 1e-10


def test_rotation_covariance_pins_r_sign():
    import jax.numpy as jnp
    from scipy.linalg import expm as sexpm

    from bianchi.conventions import rotation_matrix
    R = np.array([0.3, -0.5, 0.2])

    def bg(t):
        return 0.0, np.zeros((3, 3)), R, np.zeros(3)

    p0 = np.array([0.7, -0.2, 0.4])
    got = CH.evolve_characteristic(p0, bg, 0.0, 0.0, 1.0, nsteps=256)
    W = np.asarray(rotation_matrix(jnp.asarray(R)))
    want = sexpm(W * 1.0) @ p0
    assert np.abs(got - want).max() <= 1e-10


def test_type_ii_killing_conservation():
    bg, a_of = CH.diag_triad_background([0.8, 0.0, 0.0], [0.6, 0.4, 0.3])
    rng = np.random.default_rng(7)
    p0 = rng.standard_normal(3)
    for m in (0.0, 0.9):
        pT = CH.evolve_characteristic(p0, bg, m, 0.0, 2.0, nsteps=512)
        c0 = a_of(0.0)[0] * p0[0]
        cT = a_of(2.0)[0] * pT[0]
        assert abs(cT - c0) <= 1e-12 * max(1.0, abs(c0))


def _invariant_law_route(p0_inv, n, c_exp, mass, t1, nsteps, t_ref=1.0):
    eps = {}
    for a, b, c, s in [(0, 1, 2, 1), (1, 2, 0, 1), (2, 0, 1, 1),
                       (0, 2, 1, -1), (2, 1, 0, -1), (1, 0, 2, -1)]:
        eps[(a, b, c)] = s
    n = np.asarray(n, float)
    c_exp = np.asarray(c_exp, float)

    def C(cc, bb, ii):
        return eps.get((bb, ii, cc), 0.0) * n[cc]

    def f(p, t):
        a2 = (t_ref + t) ** (2 * c_exp)
        pu = p / a2
        E = np.sqrt(mass * mass + float(p @ pu))
        return np.array([sum(C(cc, bb, ii) * p[cc] * pu[bb]
                             for bb in range(3) for cc in range(3))
                         for ii in range(3)]) / E

    p = np.asarray(p0_inv, float).copy()
    dt = t1 / nsteps
    for k in range(nsteps):
        s = k * dt
        k1 = f(p, s)
        k2 = f(p + 0.5 * dt * k1, s + 0.5 * dt)
        k3 = f(p + 0.5 * dt * k2, s + 0.5 * dt)
        k4 = f(p + dt * k3, s + dt)
        p = p + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return p


@pytest.mark.parametrize("name,n", [
    ("I", [0.0, 0.0, 0.0]), ("II", [0.9, 0.0, 0.0]),
    ("VI0", [0.0, 0.7, -0.5]), ("VII0", [0.0, 0.7, 0.5]),
    ("VIII", [-0.6, 0.8, 0.5]), ("IX", [0.6, 0.8, 0.5])])
def test_six_types_two_routes(name, n):
    c_exp = [0.55, 0.35, 0.25]
    bg, a_of = CH.diag_triad_background(n, c_exp)
    rng = np.random.default_rng(11)
    p0hat = rng.standard_normal(3)
    mass, t1 = 0.6, 1.5
    got = CH.evolve_characteristic(p0hat, bg, mass, 0.0, t1, nsteps=1024)
    p0_inv = a_of(0.0) * p0hat
    pT_inv = _invariant_law_route(p0_inv, n, c_exp, mass, t1, nsteps=1024)
    want = pT_inv / a_of(t1)
    assert np.abs(got - want).max() <= 1e-12, name


def test_back_trace_round_trip():
    bg, _ = CH.diag_triad_background([0.6, 0.8, 0.5], [0.5, 0.4, 0.3])
    rng = np.random.default_rng(13)
    P0 = rng.standard_normal((5, 3))
    PT = CH.evolve_characteristic(P0, bg, 0.4, 0.0, 1.2, nsteps=512)
    back = CH.back_trace(PT, bg, 0.4, 1.2, nsteps=512)
    assert np.abs(back - P0).max() <= 1e-12


def test_rk4_fourth_order_convergence():
    bg, _ = CH.diag_triad_background([0.6, -0.8, 0.5], [0.5, 0.4, 0.3])
    p0 = np.array([0.8, -0.3, 0.5])
    errs, orders = CH.solver_accuracy(p0, bg, 0.0, 1.0, base=16, levels=5)
    assert errs[0] > errs[-1]
    assert all(3.8 <= o <= 4.2 for o in orders[:2]), orders
