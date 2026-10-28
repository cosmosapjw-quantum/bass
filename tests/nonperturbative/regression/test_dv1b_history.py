import numpy as np
import pytest
from bianchi.nonperturbative._core.harmonic_history import HarmonicHistory
from bianchi.nonperturbative._core.source_memory import Profile
from bianchi.nonperturbative._core.polarized_dictionary import collision_coefficients

def test_static_exact_collision():
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 2, 1): 0.1, ('E', 2, 1): -0.04, ('B', 3, -2): 0.03, ('V', 1, 1): 0.07, ('I', 4, 0): 0.13}
    p = Profile('static')
    h = HarmonicHistory(p, c, 4, 0.35)
    expect = collision_coefficients(c, p.kappa(0.35))
    assert max((abs(v - expect.get(k, 0)) for k, v in h.coefficients(0.35).items())) < 2e-11

def test_scalar_and_polarized_rhs_reuse():
    from bianchi.nonperturbative._core.harmonic_streaming import coefficient_rhs
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 4, 0): 0.13, ('E', 2, 2): 0.12, ('B', 3, -1): 0.03, ('V', 1, 1): 0.04}
    p = Profile('noncommuting')
    h = HarmonicHistory(p, c, 6, 0.03)
    H, S = p.fields(0.0)
    want = coefficient_rhs(c, H, S, p.rate(0.0), lout=6)
    got = h.unpack(h.rhs(0.0, h.initial_vector))
    assert max((abs(v - want.get(k, 0.0)) for k, v in got.items())) < 2e-11

def test_independent_of_direct_and_volterra(monkeypatch):
    from bianchi.nonperturbative._core.source_memory import DirectHistory
    from bianchi.nonperturbative._core.volterra_solver import VolterraHistory

    def forbidden(*a, **kw):
        raise AssertionError('reference called from harmonic solve')
    monkeypatch.setattr(DirectHistory, '__init__', forbidden)
    monkeypatch.setattr(VolterraHistory, '__init__', forbidden)
    h = HarmonicHistory(Profile('static'), {('I', 0, 0): 1.0}, 4, 0.05)
    assert abs(h.coefficients(0.05)['I', 0, 0] - 1) < 2e-11

def test_isotropic_collisionless_redshift():

    class P:

        def fields(self, t):
            return (0.3, np.zeros((3, 3)))

        def rate(self, t):
            return 0.0
    c = {('I', 0, 0): 1.0, ('E', 2, 1): 0.1, ('V', 3, 1): 0.04}
    h = HarmonicHistory(P(), c, 4, 0.3)
    assert max((abs(v - c.get(k, 0.0) * np.exp(-1.2 * 0.3)) for k, v in h.coefficients(0.3).items())) < 2e-11

def test_state_and_continuum_source():
    from bianchi.nonperturbative._core.polarized_dictionary import Grid, synthesize
    from bianchi.nonperturbative._core.harmonic_history import direction_view
    g = Grid(12, 24)
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('E', 2, 1): 0.1, ('V', 1, -1): 0.03}
    h = HarmonicHistory(Profile('static'), c, 4, 0.1)
    v = direction_view(g.n, g.w)
    J = h.state(0.1, v)
    assert np.max(np.abs(J - synthesize(g, h.coefficients(0.1)))) < 2e-11
    assert np.max(np.abs(np.einsum('n,nij->ij', g.w, J) - h.moment(0.1))) < 2e-11

def test_initial_gain_null_tail_is_retained():
    c = {('I', 4, 0): 0.13}
    h = HarmonicHistory(Profile('lrs'), c, 6, 0.08)
    assert np.linalg.norm(h.moment(0)) < 2e-11
    assert abs(h.moment(0.08)[2, 2]) > 0.0001
    assert np.linalg.norm([v for (f, l, m), v in h.coefficients(0.08).items() if l == 6]) > 0.0001

@pytest.mark.parametrize('cutoff', [2, 9])
def test_invalid_initial_projection_rejected(cutoff):
    with pytest.raises(ValueError):
        HarmonicHistory(Profile('static'), {('I', 4, 0): 0.13}, cutoff, 0.1)

def test_out_of_support_rejected():
    h = HarmonicHistory(Profile('static'), {}, 4, 0.1)
    with pytest.raises(ValueError):
        h.coefficients(0.1001)

def test_exact_low_moment_balance():
    from bianchi.nonperturbative._core.harmonic_history import intensity_moments
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 1, -1): 0.04, ('I', 2, 0): 0.07, ('I', 4, 0): 0.13, ('E', 2, 2): 0.12}
    p = Profile('noncommuting')
    h = HarmonicHistory(p, c, 4, 0.05)
    t = 0.05
    cc = h.coefficients(t)
    d = h.unpack(h.rhs(t, h.solution.sol(t)))
    rho, q, pi = intensity_moments(cc)
    dr, dq, _ = intensity_moments(d)
    H, S = p.fields(t)
    nu = p.rate(t)
    assert abs(dr + 4 * H * rho + np.einsum('ij,ij->', S, pi)) < 2e-11
    assert np.max(np.abs(dq + (4 * H + nu) * q + S @ q)) < 2e-11

def test_strict_numpy_scalar_serialization():
    import json
    from bianchi.nonperturbative._core.reporting import json_scalar
    assert json.loads(json.dumps({'flag': np.bool_(True), 'value': np.float64(2.0)}, default=json_scalar)) == {'flag': True, 'value': 2.0}
    with pytest.raises(TypeError):
        json.dumps({'bad': object()}, default=json_scalar)
