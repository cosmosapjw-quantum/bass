"""BF3-A tests only; historical campaigns are not invoked."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.spatial_transport import FourierLine, Opacity, DiagonalProfile, Transport, PhysicalHistory, CharacteristicHistory, fixture
from bianchi.nonperturbative._core.polarized_dictionary import Grid, collision_coefficients, synthesize, hermitian
from bianchi.nonperturbative._core.source_memory import DirectHistory
from bianchi.nonperturbative._core.spatial_projection import SpatialProjector

def setup(kind='expanding', nx=9, nt=4, end=0.16, opacity=None):
    p = DiagonalProfile(kind=kind)
    return Transport(Grid(nt, 2 * nt), nx, p, end, opacity or Opacity())

def test_fourier_derivative_and_periodic_mean():
    l = FourierLine(15)
    f = np.sin(3 * l.x) + 0.4 * np.cos(5 * l.x)
    assert np.max(abs(l.derivative(f) - (3 * np.cos(3 * l.x) - 2 * np.sin(5 * l.x)))) < 2e-13
    assert abs(l.derivative(f).mean()) < 2e-14

def test_galerkin_product_does_not_alias():
    l = FourierLine(9)
    f = np.cos(4 * l.x)
    out = l.multiply(f, {2: 0.5, -2: 0.5})
    assert np.max(abs(out - 0.5 * np.cos(2 * l.x))) < 2e-14
    assert np.max(abs(out - f * np.cos(2 * l.x))) > 0.1

def test_direction_dependent_shift_group():
    l = FourierLine(13)
    f = np.stack([np.cos(l.x), np.sin(3 * l.x)], axis=1)
    d = np.array([0.13, -0.41])
    back = l.shift(l.shift(f, d), -d)
    assert np.max(abs(back - f)) < 2e-14

def test_geometry_displacement_exact_limits():
    for kind in ('static', 'isotropic'):
        op = setup(kind, opacity=Opacity(base=0.0))
        t = op.end
        h = 0 if kind == 'static' else 0.25
        integral = t if h == 0 else -np.expm1(-h * t) / h
        assert np.max(abs(op.displacement(t) - op.g.n[:, 0] * integral)) < 2e-12
        assert np.max(abs(op.geo.at(t)['mu'] - np.exp(-h * t))) < 2e-12

def test_collisionless_exact_translation():
    op = setup('static', opacity=Opacity(base=0.0))
    j = fixture(op.g, op.line.x)
    direct = PhysicalHistory(op, j)
    exact = op.line.shift(j, -op.displacement(op.end))
    assert np.max(abs(direct.state(op.end) - exact)) < 2e-10

def test_isotropic_free_translation_and_dilution():
    op = setup('isotropic', opacity=Opacity(base=0.0))
    j = fixture(op.g, op.line.x)
    direct = PhysicalHistory(op, j)
    exact = np.exp(-4 * 0.25 * op.end) * op.line.shift(j, -op.displacement(op.end))
    assert np.max(abs(direct.state(op.end) - exact)) < 2e-10

def test_static_rest_semigroup_for_spatially_constant_state():
    op = setup('static', opacity=Opacity(base=1.2, contrast=0.0, second=0.0, modulation=0.0))
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('E', 2, 1): 0.2, ('V', 1, -1): 0.1, ('I', 4, 0): 0.1}
    j = np.broadcast_to(synthesize(op.g, c), (op.line.n, len(op.g.w), 3, 3)).copy()
    d = PhysicalHistory(op, j)
    exact = synthesize(op.g, collision_coefficients(c, 1.2 * op.end))
    assert np.max(abs(d.state(op.end) - exact[None])) < 2e-10

def test_independent_characteristic_solver(monkeypatch):
    op = setup()
    j = fixture(op.g, op.line.x)
    d = PhysicalHistory(op, j).state(op.end)

    def forbidden(*a, **kw):
        raise AssertionError('Direct reference must not be called')
    monkeypatch.setattr(PhysicalHistory, '__init__', forbidden)
    c = CharacteristicHistory(op, j, 32)
    assert np.max(abs(c.state(op.end) - d)) < 2e-08

def test_mean_split_and_local_energy_balance():
    op = setup()
    j = fixture(op.g, op.line.x)
    d = PhysicalHistory(op, j)
    j = d.state(op.end)
    b = op.budgets(op.end, j)
    assert b['mean_streaming_abs'] < 2e-11
    assert b['mean_collision_identity_abs'] < 2e-11
    assert b['local_energy_minus_collision_abs'] < 2e-11
    assert b['mean_energy_minus_collision_abs'] < 2e-11
    assert b['covariance_source_norm'] > 0.001

def test_signed_fluctuation_and_initial_high_mode():
    op = setup()
    j = fixture(op.g, op.line.x)
    p = SpatialProjector(np.ones(op.line.n))
    bg, fl = p.split(j)
    assert np.max(abs(bg + fl - j)) < 1e-14
    assert np.max(abs(p.mean(fl))) < 1e-14
    eig = np.linalg.eigvalsh(np.einsum('nia,xnij,njb->xnab', op.geo.screen0, hermitian(j), op.geo.screen0))
    eigf = np.linalg.eigvalsh(np.einsum('nia,xnij,njb->xnab', op.geo.screen0, hermitian(fl), op.geo.screen0))
    assert eig.min() > 0 and eigf.min() < -0.01

def test_homogeneous_limit_matches_existing_history():
    op = setup(opacity=Opacity(base=1.2, contrast=0.0, second=0.0, modulation=0.15))
    j0 = fixture(op.g, op.line.x).mean(axis=0)
    j = np.broadcast_to(j0, (op.line.n,) + j0.shape).copy()
    a = PhysicalHistory(op, j)
    b = DirectHistory(op.geo, j0)
    assert np.max(abs(a.state(op.end) - b.state(op.end)[None])) < 2e-10

def test_invalid_domains_and_inputs():
    with pytest.raises(ValueError):
        FourierLine(8)
    with pytest.raises(ValueError):
        Opacity(base=-1.0)
    with pytest.raises(ValueError):
        Opacity(contrast=0.95, second=0.2)
    op = setup()
    with pytest.raises(ValueError):
        PhysicalHistory(op, np.ones((2, 3)))
    with pytest.raises(ValueError):
        op.displacement(op.end + 1.0)

def test_nontransverse_initial_carrier_is_rejected_not_projected():
    op = setup()
    j = fixture(op.g, op.line.x)
    j += 0.02 * np.einsum('ni,nj->nij', op.g.n, op.g.n)[None]
    with pytest.raises(ValueError, match='transverse'):
        CharacteristicHistory(op, j, 4)
    with pytest.raises(ValueError, match='transverse'):
        PhysicalHistory(op, j)
