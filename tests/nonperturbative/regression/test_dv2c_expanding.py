"""DV2C new scope-local tests; parent campaigns are not invoked."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.expanding_bianchi_ii import CoframeProfile, ExpandingGeometry, ExpandingDirect, CoordinateRays, TangentGeometry, analytic_rates
from bianchi.nonperturbative._core.polarized_dictionary import Grid, synthesize
from bianchi.nonperturbative._core.frozen_bianchi_ii import FrozenProfile, FrozenGeometry
from bianchi.nonperturbative._core.source_memory import SourceMemory
from bianchi.nonperturbative._core.volterra_solver import VolterraHistory
from bianchi.q import polarization as P8

def test_coframe_identity():
    p = CoframeProfile()
    for t in (0.0, 0.17, 0.4):
        a = p.scales(t)
        H, S = p.fields(t)
        N = p.curvature(t)
        assert abs(N[2, 2] - 0.9 * a[2] / (a[0] * a[1])) < 2e-14
        assert abs(p.curvature_rate(t) - (-H + 2 * S[2, 2]) * N[2, 2]) < 2e-14

@pytest.mark.parametrize('h', [0.0, 0.3])
def test_exact_frozen_conformal_limit(h):
    g = Grid(6, 12)
    p = CoframeProfile(h=(h,) * 3, d=(0.0,) * 3, nu0=0.0, nuamp=0.0)
    geo = ExpandingGeometry(g, p, 0.4)
    eta = 0.4 if h == 0 else -np.expm1(-h * 0.4) / h
    fr = FrozenGeometry(g, FrozenProfile(0.9, 0.0), eta)
    z = geo.at(0.4)
    f = fr.at(eta)
    assert np.max(abs(z['e'] - f['e'])) < 3e-10
    assert np.max(abs(z['screen'] - f['screen'])) < 3e-10
    assert np.max(abs(z['mu'] - np.exp(-h * 0.4))) < 3e-10
    assert np.max(abs(z['jacobian'] - 1.0)) < 3e-10

def test_coordinate_hamiltonian_reference():
    g = Grid(4, 8)
    p = CoframeProfile()
    geo = ExpandingGeometry(g, p, 0.3)
    ref = CoordinateRays(g.n, p, 0.3)
    n, r = ref.at(0.3)
    z = geo.at(0.3)
    assert np.max(abs(n - z['e'])) < 3e-10
    assert np.max(abs(r - z['mu'])) < 3e-10

def test_variational_area_and_volume_identity():
    g = Grid(4, 8)
    p = CoframeProfile()
    geo = ExpandingGeometry(g, p, 0.4)
    var = TangentGeometry(g, p, 0.4)
    z = geo.at(0.4)
    assert np.max(abs(var.area(0.4) - z['jacobian'])) < 3e-10
    assert np.max(abs(z['jacobian'] * z['mu'] ** 3 * np.prod(p.scales(0.4)) - 1)) < 3e-10

def test_analytic_screen_and_direction_match_p8():
    g = Grid(6, 12)
    p = CoframeProfile()
    H, S = p.fields(0.2)
    N = p.curvature(0.2)
    E = np.stack([g.bt, g.bp], axis=2)
    de, dl, dE, dj = analytic_rates(g.n, E, H, S, N)
    zz = np.zeros(3)
    assert np.max(abs(de - P8.direction_rate(g.n, H, S, zz, N, zz))) < 2e-11
    for j in range(2):
        assert np.max(abs(dE[:, :, j] - P8.screen_vector_rate(E[:, :, j], g.n, H, S, zz, N, zz))) < 2e-11

def test_free_full_carrier():
    g = Grid(6, 12)
    p = CoframeProfile(nu0=0.0, nuamp=0.0)
    geo = ExpandingGeometry(g, p, 0.2)
    J0 = synthesize(g, {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('E', 2, 1): 0.02, ('V', 1, 0): 0.01})
    ref = ExpandingDirect(geo, J0)
    assert np.max(abs(ref.state(0.2) - geo.free_state(0.2, J0))) < 3e-10

def test_memory_without_direct_constructor(monkeypatch):
    from bianchi.nonperturbative._core import expanding_bianchi_ii as mod
    monkeypatch.setattr(mod, 'ExpandingDirect', lambda *a, **k: (_ for _ in ()).throw(AssertionError('direct source forbidden')))
    g = Grid(6, 12)
    geo = ExpandingGeometry(g, CoframeProfile(), 0.1)
    J0 = synthesize(g, {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('B', 2, 0): 0.03})
    v = VolterraHistory(SourceMemory(geo, J0), np.linspace(0, 0.1, 9))
    assert np.isfinite(v.moment(0.1)).all()
    assert max(v.endpoint_consistency) < 2e-11

def test_domain_rejections():
    with pytest.raises(ValueError):
        CoframeProfile(h=(float('nan'), 0.0, 0.0))
    with pytest.raises(ValueError):
        CoframeProfile(nu0=-1.0)
    with pytest.raises(ValueError):
        CoframeProfile(h=(1.0, 2.0))
    g = Grid(4, 8)
    geo = ExpandingGeometry(g, CoframeProfile(), 0.1)
    with pytest.raises(ValueError):
        geo.at(0.2)
