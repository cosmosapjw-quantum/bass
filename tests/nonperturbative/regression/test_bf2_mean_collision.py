"""BF2 scoped tests. No spatial kinetic or Einstein evolution is invoked."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.mean_collision import split_collision, mean_electron_current, force_budget
from bianchi.nonperturbative._core.spatial_projection import SpatialProjector, align_carrier, rotation_z
from bianchi.nonperturbative._core.polarized_dictionary import Grid, synthesize, analyze, hermitian
from bianchi.nonperturbative._core.tilted_collision import TiltedThomson, radiation_tensor
from bianchi.nonperturbative._core.covariant_oracle import pairwise_rhs

def field(g, c=None):
    return synthesize(g, {('I', 0, 0): 2 * np.sqrt(4 * np.pi), **(c or {})})

def test_uniform_coefficients_commute():
    g = Grid(8, 16)
    p = SpatialProjector([1, 2, 3])
    J = np.stack([field(g, {('I', 2, 0): a, ('E', 2, 1): 0.03}) for a in (-0.2, 0.1, 0.3)])
    b = np.tile([0.2, -0.1, 0.05], (3, 1))
    r = split_collision(g.n, g.w, J, [1.3] * 3, b, p)
    assert np.max(abs(r.mean_collision - r.baseline)) < 2e-11
    for a in (r.opacity_correlation, r.velocity_dispersion, r.velocity_radiation):
        assert np.max(abs(a)) < 2e-11

def test_exact_two_cell_polarized_covariance():
    g = Grid(12, 24)
    p = SpatialProjector([1, 1])
    amp = 0.3
    eps = 0.2
    nu = 1.3
    T = synthesize(g, {('I', 2, 0): 1.0})
    J0 = field(g)
    J = np.stack([J0 + amp * T, J0 - amp * T])
    r = split_collision(g.n, g.w, J, nu * np.array([1 + eps, 1 - eps]), np.zeros((2, 3)), p)
    expected = nu * eps * amp * TiltedThomson(g.n, g.w, [0, 0, 0]).rhs(T, 1.0)
    assert np.max(abs(r.opacity_correlation - expected)) < 2e-11
    c = analyze(g, r.mean_collision, 2)
    assert abs(c['I', 2, 0] + 0.9 * nu * eps * amp) < 2e-11
    assert abs(c['E', 2, 0] + np.sqrt(6) / 10 * nu * eps * amp) < 2e-11

def test_exact_all_channel_rest_basis():
    g = Grid(8, 16)
    p = SpatialProjector([1, 1])
    op = TiltedThomson(g.n, g.w, [0, 0, 0])
    for f in ('I', 'E', 'B', 'V'):
        for l in range(5):
            if f in ('E', 'B') and l < 2:
                continue
            for m in range(-l, l + 1):
                T = synthesize(g, {(f, l, m): 1.0})
                J = np.stack([field(g) + 0.05 * T, field(g) - 0.05 * T])
                r = split_collision(g.n, g.w, J, [1.4, 0.6], np.zeros((2, 3)), p)
                assert np.max(abs(r.opacity_correlation - 0.02 * op.rhs(T, 1.0))) < 2e-11

def test_finite_velocity_decomposition_and_reference_independence():
    g = Grid(12, 24)
    p = SpatialProjector([1, 2, 1])
    nu = [0.7, 1.1, 1.8]
    b = np.array([[0.35, 0, 0.1], [-0.2, 0.25, 0.05], [0.1, -0.3, 0.15]])
    J = np.stack([field(g, {('I', 2, 1): a, ('E', 2, 0): a / 4}) for a in (-0.2, 0.15, 0.3)])
    r = split_collision(g.n, g.w, J, nu, b, p)
    q = split_collision(g.n, g.w, J, nu, b, p, reference_beta=[0, 0, 0])
    for x in (r, q):
        assert np.max(abs(x.baseline + x.opacity_correlation + x.velocity_dispersion + x.velocity_radiation - x.mean_collision)) < 2e-11
        assert np.max(abs(x.fluctuation_rate + x.background_rate[None] - x.local_collision)) < 2e-11
    assert np.max(abs(r.mean_collision - q.mean_collision)) < 2e-11
    assert np.max(abs(r.baseline - q.baseline)) > 0.0001

def test_counterstreaming_heating_not_mean_velocity_collision():
    g = Grid(48, 96)
    p = SpatialProjector([1, 1])
    beta = 0.6
    nu = 1.3
    J0 = field(g)
    r = split_collision(g.n, g.w, np.stack([J0, J0]), [nu, nu], [[0, 0, beta], [0, 0, -beta]], p)
    F = radiation_tensor(g.n, g.w, r.mean_collision)[0]
    rho = 8 * np.pi
    expected = 4 / 3 * nu * rho * (1 - beta ** 2) ** (-1.5) * beta ** 2
    assert abs(F[0] - expected) / (nu * rho) < 5e-10
    assert np.max(abs(F[1:])) / (nu * rho) < 5e-10
    assert np.max(abs(r.baseline)) < 2e-11
    assert r.current_opacity == pytest.approx(nu / np.sqrt(1 - beta ** 2))

def test_current_surrogate_normalization_accounted_separately():
    g = Grid(24, 48)
    p = SpatialProjector([1, 1])
    J0 = field(g, {('I', 2, 0): 0.3})
    r = split_collision(g.n, g.w, np.stack([J0, J0]), [1, 1], [[0.4, 0, 0], [-0.4, 0, 0]], p)
    assert np.max(abs(r.current_surrogate + r.current_density_correction - r.baseline)) < 2e-11
    assert np.max(abs(r.current_density_correction)) > 0.0001

def test_common_frame_alignment_of_collision():
    g = Grid(12, 24)
    p = SpatialProjector([1, 2])
    rot, _ = rotation_z([0.4, -0.7])
    J = np.stack([field(g, {('I', 2, 1): 0.2}), field(g, {('E', 2, -1): 0.1})])
    beta = np.array([[0.25, 0.1, 0.05], [-0.2, 0.1, 0.1]])
    nu = [1.0, 1.4]
    nloc = np.einsum('xji,nj->xni', rot, g.n)
    jloc = np.einsum('xai,xnab,xbj->xnij', rot, J, rot)
    bloc = np.einsum('xji,xj->xi', rot, beta)
    cloc = np.stack([TiltedThomson(nloc[x], g.w, bloc[x]).rhs(jloc[x], nu[x]) for x in range(2)])
    mapped = align_carrier(cloc, rot, nloc, g.n)
    r = split_collision(g.n, g.w, J, nu, beta, p)
    assert np.max(abs(mapped - r.local_collision)) < 2e-11

def test_moving_measure_is_not_a_collision_correlation():
    g = Grid(8, 16)
    p = SpatialProjector([1, 2], [0.4, -0.2])
    J = np.stack([field(g, {('I', 2, 0): 0.3}), field(g, {('I', 2, 0): -0.2})])
    r = split_collision(g.n, g.w, J, [1, 1], np.zeros((2, 3)), p)
    assert np.max(abs(r.measure_term - p.mean_pdot(J))) < 2e-11
    assert np.max(abs(p.mean(r.fluctuation_rate) + p.mean_pdot(J))) < 2e-11
    assert np.max(abs(r.background_rate - r.mean_collision)) > 0.0001

def test_pairwise_reference_without_source_factorization():
    g = Grid(8, 16)
    p = SpatialProjector([1, 2])
    b = [[0.2, 0.1, 0], [-0.15, 0.1, 0.2]]
    nu = [0.8, 1.4]
    J = np.stack([field(g, {('E', 2, 0): 0.1}), field(g, {('B', 2, 1): 0.05, ('I', 1, 0): 0.1})])
    r = split_collision(g.n, g.w, J, nu, b, p)
    other = np.stack([pairwise_rhs(g.n, g.w, J[x], b[x], nu[x]) for x in range(2)])
    assert np.max(abs(p.mean(other) - r.mean_collision)) < 2e-11

def test_local_force_elasticity_does_not_imply_mean_frame_elasticity():
    g = Grid(48, 96)
    p = SpatialProjector([1, 1])
    J = np.stack([field(g), field(g)])
    b = np.array([[0, 0, 0.6], [0, 0, -0.6]])
    r = split_collision(g.n, g.w, J, [1.3, 1.3], b, p)
    d = force_budget(g.n, g.w, J, [1.3, 1.3], b, p, r)
    assert d['max_relative_force_residual'] < 5e-10
    assert d['max_relative_local_elasticity'] < 5e-10
    assert abs(d['mean_frame_elastic_defect']) > 1
    assert abs(d['velocity_force_correlation'] - d['mean_frame_elastic_defect']) < 2e-09

def test_vacuum_and_invalid_inputs():
    g = Grid(8, 16)
    p = SpatialProjector([1, 1])
    J = np.stack([field(g)] * 2)
    r = split_collision(g.n, g.w, J, [0, 0], np.zeros((2, 3)), p)
    assert np.array_equal(r.local_collision, np.zeros_like(J))
    assert r.current_opacity == 0
    with pytest.raises(ValueError):
        split_collision(g.n, g.w, J, [-1, 1], np.zeros((2, 3)), p)
    with pytest.raises(ValueError):
        split_collision(g.n, g.w, J, [1, 1], [[1, 0, 0], [0, 0, 0]], p)
    with pytest.raises(ValueError):
        split_collision(g.n, g.w, J[:1], [1, 1], np.zeros((2, 3)), p)

def test_split_keeps_signed_fluctuations_and_physical_background():
    g = Grid(8, 16)
    p = SpatialProjector([1, 1])
    T = synthesize(g, {('I', 2, 0): 0.5})
    J = np.stack([field(g) + T, field(g) - T])
    r = split_collision(g.n, g.w, J, [1.2, 0.8], np.zeros((2, 3)), p)
    E = np.stack([g.bt, g.bp], axis=-1)

    def mins(a):
        return np.linalg.eigvalsh(np.einsum('nia,nij,njb->nab', E, hermitian(a), E)).min()
    assert mins(r.mean_carrier) > 0 and mins(J[0]) > 0 and (mins(J[1]) > 0)
    assert mins(J[0] - r.mean_carrier) < 0
    assert np.max(abs(p.mean(J - r.mean_carrier))) < 2e-11

def test_two_cell_semigroup_generates_correlation_from_uniform_radiation():
    from bianchi.q import polarization as P8
    g = Grid(12, 24)
    p = SpatialProjector([1, 1])
    J0 = field(g, {('I', 2, 0): 0.3})
    mean_nu = 1.3
    delta = 0.65
    t = 0.8
    cells = np.stack([P8.collide(g.n, g.w, J0, (mean_nu + s * delta) * t) for s in [1, -1]])
    r = split_collision(g.n, g.w, cells, [mean_nu + delta, mean_nu - delta], np.zeros((2, 3)), p)
    coeff = analyze(g, r.mean_carrier, 2)
    expected = 0.3 * (6 / 7 * np.exp(-mean_nu * t) * np.cosh(delta * t) + 1 / 7 * np.exp(-0.3 * mean_nu * t) * np.cosh(0.3 * delta * t))
    assert abs(coeff['I', 2, 0] - expected) < 2e-11
    naive = P8.collide(g.n, g.w, J0, mean_nu * t)
    assert np.max(abs(r.mean_carrier - naive)) > 0.0001
    assert np.max(abs(r.opacity_correlation)) > 0.0001

def test_exact_spatial_memory_identity_with_full_initial_complement():
    from bianchi.q import polarization as P8
    from numpy.polynomial.legendre import leggauss
    g = Grid(8, 16)
    p = SpatialProjector([1, 1])
    op = TiltedThomson(g.n, g.w, [0, 0, 0])
    mean_nu = 1.3
    delta = 0.65
    t = 0.7
    J0 = field(g, {('I', 2, 0): 0.3, ('E', 2, 1): 0.02})
    xi = synthesize(g, {('I', 3, 0): 0.07})

    def expL(J, q):
        return P8.collide(g.n, g.w, J, q)

    def meanat(s):
        return 0.5 * (expL(J0 + xi, (mean_nu + delta) * s) + expL(J0 - xi, (mean_nu - delta) * s))
    cells = np.stack([expL(J0 + xi, (mean_nu + delta) * t), expL(J0 - xi, (mean_nu - delta) * t)])
    direct = p.mean(np.stack([op.rhs(cells[i], mean_nu + sgn * delta) for i, sgn in enumerate([1, -1])]))
    x, w = leggauss(16)
    memory = np.zeros_like(J0)
    for s, ww in zip(t * (x + 1) / 2, t * w / 2):
        memory += ww * delta ** 2 * op.rhs(op.rhs(expL(meanat(s), mean_nu * (t - s)), 1.0), 1.0)
    initial = delta * op.rhs(expL(xi, mean_nu * t), 1.0)
    reconstructed = op.rhs(meanat(t), mean_nu) + initial + memory
    assert np.max(abs(direct - reconstructed)) < 2e-11
    assert np.max(abs(initial)) > 0.0001
