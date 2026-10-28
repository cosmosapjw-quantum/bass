"""BF-1 scope-local tests; no kinetic IVP or previous campaign is run."""
import numpy as np
import pytest
from scipy.special import iv
from bianchi.nonperturbative._core.spatial_projection import SpatialProjector, align_carrier, align_rate, physical_from_log_shape, rotation_z, flat_torus_constraints
from bianchi.nonperturbative._core.polarized_dictionary import Grid, synthesize, analyze, hermitian

def test_projection_idempotence_zero_mean_and_reconstruction():
    rng = np.random.default_rng(19)
    f = rng.normal(size=(17, 7, 3, 3))
    p = SpatialProjector(np.exp(rng.normal(size=17)), rng.normal(size=17))
    bg, xi = p.split(f)
    assert np.max(abs(p.project(bg) - bg)) < 2e-11
    assert np.max(abs(p.mean(xi))) < 2e-11
    assert np.max(abs(bg + xi - f)) < 2e-11

def test_bad_measure_and_shape_rejected():
    for w in ([1.0, 0.0], [1.0, -1.0], [1.0, np.nan]):
        with pytest.raises(ValueError):
            SpatialProjector(w)
    p = SpatialProjector([1.0, 2.0])
    with pytest.raises(ValueError):
        p.mean(np.ones((3, 4)))

def test_homogeneous_expanding_volume_cancels_from_normalized_measure():
    p = SpatialProjector.from_log_volume(np.full(12, 2.7), np.full(12, 0.9))
    q = SpatialProjector.from_log_volume(np.full(12, 6.2), np.full(12, 1.3))
    f = np.arange(12.0)
    assert np.max(abs(p.p - q.p)) == 0
    assert abs(p.mean_rate(f, np.zeros_like(f))) < 2e-11

def test_physical_volume_commutator_matches_exact_bessel_mean():
    x = 2 * np.pi * np.arange(64) / 64
    b = 0.65
    bdot = 1.1
    eta = 0.7
    p = SpatialProjector.from_log_volume(b * np.cos(x), 0.9 + bdot * np.cos(x))
    f = 1 + eta * np.cos(x)
    mean = 1 + eta * iv(1, b) / iv(0, b)
    rate = eta * bdot * ((iv(0, b) + iv(2, b)) / (2 * iv(0, b)) - (iv(1, b) / iv(0, b)) ** 2)
    assert abs(p.mean(f) - mean) < 2e-11
    assert abs(p.mean_rate(f, np.zeros_like(f)) - rate) < 2e-11
    assert abs(rate) > 0.1

def test_time_dependent_zero_mean_constraint_differentiates_correctly():
    x = 2 * np.pi * np.arange(24) / 24
    p = SpatialProjector.from_log_volume(0.8 * np.cos(x), 1.2 * np.cos(x))
    f = 1 + 0.6 * np.cos(x)
    rhs = -f ** 3
    bg, xi = p.split(f)
    db, dx = p.split_rhs(f, rhs)
    assert np.max(abs(db + dx - rhs)) < 2e-11
    assert abs(p.mean(dx) + p.mean_pdot(xi)) < 2e-11
    assert abs(p.mean(dx)) > 0.001

def test_frame_and_direction_alignment_before_spatial_mean():
    g = Grid(6, 12)
    x = 2 * np.pi * np.arange(12) / 12
    common = synthesize(g, {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 2, 2): 0.3, ('E', 2, 1): 0.12})
    R, _ = rotation_z(0.6 * np.sin(x))
    Rt = R.transpose(0, 2, 1)
    local = np.einsum('xai,nij,xbj->xnab', Rt, common, Rt)
    nlocal = np.einsum('xai,ni->xna', Rt, g.n)
    restored = align_carrier(local, R, nlocal, g.n)
    assert np.max(abs(restored - common[None])) < 2e-11
    assert np.max(abs(local.mean(0) - common)) > 0.001
    with pytest.raises(ValueError):
        align_carrier(local, R, np.broadcast_to(g.n, nlocal.shape), g.n)

def test_time_dependent_frame_term_is_not_measure_term():
    g = Grid(4, 8)
    x = np.arange(7.0)
    t = 0.37
    omega = 0.4 + 0.1 * np.cos(x)
    R, dR = rotation_z(omega * t, omega)
    Rt = R.transpose(0, 2, 1)
    dRt = dR.transpose(0, 2, 1)
    F = synthesize(g, {('I', 0, 0): np.sqrt(4 * np.pi), ('E', 2, 2): 0.15})
    f = np.einsum('xai,nij,xbj->xnab', Rt, F, Rt)
    df = np.einsum('xai,nij,xbj->xnab', dRt, F, Rt) + np.einsum('xai,nij,xbj->xnab', Rt, F, dRt)
    fixed = align_rate(f, df, R, dR)
    assert np.max(abs(fixed)) < 2e-11
    wrong = np.einsum('xai,xnij,xbj->xnab', R, df, R)
    assert np.max(abs(wrong)) > 0.001

def test_average_physical_carrier_not_log_or_normalized_shape():
    g = Grid(4, 8)
    shape = np.broadcast_to(g.P[None] / 2, (2, len(g.w), 3, 3))
    logs = np.broadcast_to(np.array([0.8, -0.8])[:, None], (2, len(g.w)))
    f = physical_from_log_shape(logs, shape)
    p = SpatialProjector([1.0, 1.0])
    assert np.max(abs(p.mean(f) - np.cosh(0.8) * g.P / 2)) < 2e-11
    assert np.max(abs(p.mean(f) - g.P / 2)) > 0.1
    assert np.linalg.eigvalsh(hermitian(p.split(f)[1])).min() < -0.1
    with pytest.raises(FloatingPointError):
        physical_from_log_shape(np.full((2, len(g.w)), 1000.0), shape)

def test_harmonic_interchange_high_modes_and_psd_mean():
    g = Grid(8, 16)
    x = 2 * np.pi * np.arange(12) / 12
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 4, 0): 0.3, ('E', 2, 2): 0.1, ('B', 3, 1): 0.05, ('V', 1, 1): 0.02}
    f = np.stack([synthesize(g, {k: v * (1 + 0.6 * np.cos(xx)) for k, v in c.items()}) for xx in x])
    p = SpatialProjector(np.ones(len(x)))
    a = analyze(g, p.mean(f), 4)
    ca = [analyze(g, j, 4) for j in f]
    assert max((abs(a[k] - np.mean([v[k] for v in ca])) for k in a)) < 2e-11
    assert abs(a['I', 4, 0] - 0.3) < 2e-11
    assert np.linalg.eigvalsh(hermitian(f)).min() > -2e-11
    assert np.linalg.eigvalsh(hermitian(p.mean(f))).min() > -2e-11

def test_constraint_satisfying_positive_density_data_have_nonzero_mean_constraint():
    nx = 48
    x = 2 * np.pi * np.arange(nx) / nx
    k0 = 0.4
    amp = 0.3
    K = -k0 * np.broadcast_to(np.eye(3), (nx, 3, 3)).copy()
    K[:, 1, 1] += amp * np.cos(x)
    K[:, 2, 2] -= amp * np.cos(x)
    source = 6 * k0 * k0 - 2 * amp * amp * np.cos(x) ** 2
    h, m = flat_torus_constraints(K, source, 2 * np.pi)
    assert np.max(abs(h)) < 2e-11 and np.max(abs(m)) < 2e-11
    assert source.min() > 0
    p = SpatialProjector(np.ones(nx))
    kb = p.mean(K)
    sb = p.mean(source)
    mean_res = np.trace(kb) ** 2 - np.sum(kb * kb) - sb
    assert abs(mean_res - amp * amp) < 2e-11
    assert mean_res > 0.01

def test_positive_metric_average_does_not_impose_constraints():
    x = 2 * np.pi * np.arange(16) / 16
    mats = np.array([np.diag(np.exp([0.8 * np.cos(t), -0.6 * np.sin(t), 0.2 * np.cos(2 * t)])) for t in x])
    p = SpatialProjector.from_log_volume(0.3 * np.cos(x))
    assert np.linalg.eigvalsh(p.mean(mats)).min() > 0
    assert p.mean(mats).shape == (3, 3)

def test_full_nonlinear_rhs_is_projected_without_amplitude_truncation():
    x = 2 * np.pi * np.arange(32) / 32
    f = 1 + 0.8 * np.cos(x)
    p = SpatialProjector(np.ones(len(x)))
    rhs = -f ** 3
    db, dx = p.split_rhs(f, rhs)
    assert np.max(abs(db + dx - rhs)) < 2e-11
    assert abs(db[0] + (1 + 1.5 * 0.8 ** 2)) < 2e-11
    assert abs(db[0] + p.mean(f) ** 3) > 0.9

def test_pdot_callable_and_differentiated_projector_identity():
    p = SpatialProjector([1.0, 2.0, 3.0], [0.5, -0.2, 0.1])
    f = np.arange(6.0).reshape(3, 2)
    derivative = p.pdot(f)
    assert derivative.shape == f.shape
    assert np.max(abs(derivative[0] - p.mean_pdot(f))) < 2e-11
    assert np.max(abs(p.pdot(p.project(f)) + p.project(p.pdot(f)) - p.pdot(f))) < 2e-11
