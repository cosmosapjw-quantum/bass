"""BF3-B acceptance: independent retarded source history, no old science reruns."""
import numpy as np
import pytest
from scipy.linalg import expm
from bianchi.nonperturbative._core.spatial_transport import Transport, DiagonalProfile, Opacity, FourierLine, PhysicalHistory, CharacteristicHistory, fixture
from bianchi.nonperturbative._core.polarized_dictionary import Grid, synthesize, collision_coefficients
from bianchi.nonperturbative._core.spatial_memory import LossPropagator, SpatialMemory, SpatialVolterra, fft_field, real_field

def setup(kind='expanding', nx=7, nt=4, end=0.12, opacity=None):
    op = Transport(Grid(nt, nt * 2), nx, DiagonalProfile(kind=kind), end, opacity or Opacity())
    loss = LossPropagator(op)
    return (op, loss)

def test_toeplitz_matches_dealiased_parent_and_positive_loss():
    op, loss = setup()
    rng = np.random.default_rng(71)
    f = rng.normal(size=(op.line.n, op.nq, 2, 2))
    t = 0.06
    expected = op.line.multiply(f, op.opacity.coefficients(t))
    got = real_field(np.einsum('kl,lqab->kqab', loss.opacity_matrix(t), fft_field(f)))
    assert np.max(abs(got - expected)) < 2e-11
    V = loss.opacity_matrix(t)
    assert np.max(abs(V - V.conj().T)) < 2e-14
    assert np.linalg.eigvalsh(V).min() > 0

def test_uniform_loss_reproduces_retarded_translation():
    op, loss = setup(opacity=Opacity(contrast=0.0, second=0.0))
    t, s = (0.12, 0.047)
    U = loss.transition(t, s)
    phase = np.exp(-1j * op.line.k[None, :] * (op.displacement(t) - op.displacement(s))[:, None])
    attenuation = np.exp(-op.profile.kappa(t) + op.profile.kappa(s))
    exact = phase[:, :, None] * np.eye(op.line.n)[None] * attenuation
    assert np.max(abs(U - exact)) < 2e-10

def test_loss_composition_contractivity_and_retardation():
    op, loss = setup()
    a, b, c = (0.12, 0.073, 0.014)
    assert np.max(abs(loss.transition(a, c) - loss.transition(a, b) @ loss.transition(b, c))) < 2e-11
    assert np.linalg.svd(loss.transition(a, c), compute_uv=False).max() < 1 + 2e-11
    with pytest.raises(ValueError):
        loss.transition(0.01, 0.02)
    with pytest.raises(ValueError):
        loss.transition(0.2, 0.0)

def test_free_carrier_translation_and_redshift():
    op, loss = setup(opacity=Opacity(base=0.0))
    j = fixture(op.g, op.line.x)
    mem = SpatialMemory(loss, j)
    v = SpatialVolterra(mem, 3)
    X0 = op.pull(0.0, j)
    exact = op.push(op.end, op.line.shift(X0, -op.displacement(op.end)))
    assert np.max(abs(v.state(op.end) - exact)) < 2e-09

def test_homogeneous_static_full_polarized_semigroup():
    op, loss = setup('static', opacity=Opacity(base=1.2, contrast=0.0, second=0.0, modulation=0.0))
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 2, 0): 0.2, ('E', 2, 1): 0.13, ('V', 1, -1): 0.05}
    j = np.broadcast_to(synthesize(op.g, c), op.shape).copy()
    v = SpatialVolterra(SpatialMemory(loss, j), 12)
    exact = synthesize(op.g, collision_coefficients(c, 1.2 * op.end))
    assert np.max(abs(v.state(op.end) - exact[None])) < 2e-09

def test_independent_spatial_source_solver(monkeypatch):
    op, loss = setup(nx=9)
    j = fixture(op.g, op.line.x)
    ref = PhysicalHistory(op, j).state(op.end)

    def forbidden(*a, **kw):
        raise AssertionError('Radiation PDE/RHS may not be used by source solver')
    monkeypatch.setattr(PhysicalHistory, '__init__', forbidden)
    monkeypatch.setattr(CharacteristicHistory, '__init__', forbidden)
    monkeypatch.setattr(op, 'physical_rhs', forbidden)
    monkeypatch.setattr(op, 'characteristic_rhs', forbidden)
    v = SpatialVolterra(SpatialMemory(loss, j), 12)
    assert np.max(abs(v.state(op.end) - ref)) < 2e-08
    assert v.max_endpoint_source_residual < 2e-11

def test_retarded_global_history_and_offgrid_reconstruction():
    op, loss = setup()
    v = SpatialVolterra(SpatialMemory(loss, fixture(op.g, op.line.x)), 6)
    for t in [0.037, op.end]:
        full = v.full_history_source(t)
        assert np.max(abs(full - v.source(t))) < 2e-10
    assert v.max_panel_condition < 20.0

def test_periodic_mean_and_collision_covariance():
    op, loss = setup()
    v = SpatialVolterra(SpatialMemory(loss, fixture(op.g, op.line.x)), 12)
    b = op.budgets(op.end, v.state(op.end))
    assert b['mean_streaming_abs'] < 2e-11
    assert b['mean_collision_identity_abs'] < 2e-11
    assert b['covariance_source_norm'] > 0.001

def test_spatial_mixing_returns_initial_source_null_radiation():
    op, loss = setup('static', nx=9, nt=6, opacity=Opacity(base=0.0))
    j = 0.1 * np.cos(op.line.x)[:, None, None, None] * synthesize(op.g, {('I', 4, 0): 1.0})[None]
    assert np.max(abs(j)) > 0.01
    v = SpatialVolterra(SpatialMemory(loss, j), 4)
    assert np.max(abs(op.source(0.0, j))) < 2e-14
    assert np.max(abs(v.source(op.end))) > 1e-06

def test_projected_path_attenuation_is_not_finite_galerkin_loss():
    op, loss = setup('static', nx=5)
    V = loss.opacity_matrix(0.0) / op.opacity.scale(0.0)
    f = np.zeros(5, complex)
    f[2] = 0.5
    f[-2] = 0.5
    h = 0.2
    galerkin = expm(-h * V) @ f
    x = 2 * np.pi * np.arange(1024) / 1024
    exact = np.exp(-h * (1 + 0.65 * np.cos(x) + 0.1 * np.sin(2 * x))) * np.cos(2 * x)
    coeff = np.fft.fft(exact) / 1024
    projected = coeff[np.array([0, 1, 2, -2, -1])]
    assert np.max(abs(projected - galerkin)) > 0.0001

def test_causal_prefix_is_unchanged_at_panel_boundaries():
    op, loss = setup(end=0.12)
    j = fixture(op.g, op.line.x)
    mem = SpatialMemory(loss, j)
    a = SpatialVolterra(mem, 6)
    b = SpatialVolterra(mem, 3, end=0.06)
    assert np.max(abs(a.source(0.06) - b.source(0.06))) < 2e-12

def test_invalid_inputs_and_no_silent_projection():
    op, loss = setup()
    j = fixture(op.g, op.line.x)
    bad = j + 0.01 * np.einsum('ni,nj->nij', op.g.n, op.g.n)[None]
    with pytest.raises(ValueError, match='transverse'):
        SpatialMemory(loss, bad)
    mem = SpatialMemory(loss, j)
    with pytest.raises(ValueError):
        SpatialVolterra(mem, 0)
    with pytest.raises(ValueError):
        SpatialVolterra(mem, 2, order=1)
    v = SpatialVolterra(mem, 2)
    with pytest.raises(ValueError):
        v.state(op.end + 0.1)

def test_uniform_opacity_retarded_kernel_is_spatially_nonlocal():
    op, loss = setup('static', nx=9, nt=6, end=0.2, opacity=Opacity(base=1.2, contrast=0.0, second=0.0, modulation=0.0))
    mem = SpatialMemory(loss, fixture(op.g, op.line.x))
    F = np.exp(1j * np.outer(op.line.x, op.line.k))
    Finv = F.conj().T / op.line.n

    def gridkernel(t, s):
        K = mem.kernel(t, s).reshape(op.line.n, 9, op.line.n, 9)
        return np.einsum('xk,kalb,ly->xyab', F, K, Finv, optimize=True)
    mask = ~np.eye(op.line.n, dtype=bool)
    assert np.max(abs(gridkernel(0.2, 0.05)[mask])) > 0.0001
    assert np.max(abs(gridkernel(0.1, 0.1)[mask])) < 2e-11
