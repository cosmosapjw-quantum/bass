"""New KM3 acceptance, not a replay of any parent campaign."""
import numpy as np
import pytest
from bianchi.nonperturbative._core.source_memory import Profile, Geometry, DirectHistory, SourceMemory
from bianchi.nonperturbative._core.polarized_dictionary import Grid, synthesize
from bianchi.q import polarization as P8
from bianchi.nonperturbative._core.volterra_solver import VolterraHistory, solve_global_history

def initial(g):
    return synthesize(g, {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 4, 1): 0.12, ('E', 2, -1): 0.035, ('B', 3, 2): 0.026, ('V', 1, -1): 0.018})

def test_solver_has_no_direct_source_dependency(monkeypatch):

    def forbidden(*args, **kwargs):
        raise AssertionError('Direct source was used by solver')
    monkeypatch.setattr(DirectHistory, '__init__', forbidden)
    monkeypatch.setattr(SourceMemory, 'evaluate_with_source', forbidden)
    monkeypatch.setattr(SourceMemory, 'reconstruct_with_source', forbidden)
    g = Grid(6, 12)
    geo = Geometry(g, Profile('noncommuting'), 0.3)
    h = VolterraHistory(SourceMemory(geo, initial(g)), np.linspace(0, 0.3, 9))
    assert np.isfinite(h.moments).all()
    assert max(h.block_residuals) < 2e-11

def test_compressed_and_full_causal_assembly_match():
    g = Grid(6, 12)
    geo = Geometry(g, Profile('noncommuting'), 0.4)
    mem = SourceMemory(geo, initial(g))
    times = np.linspace(0, 0.4, 5)
    compressed = VolterraHistory(mem, times)
    full, stages = solve_global_history(mem, times)
    assert np.max(np.abs(compressed.moments - full)) < 5e-11
    assert np.max(np.abs(compressed.panels - stages)) < 5e-11

@pytest.mark.parametrize('kind', ['static', 'free'])
def test_analytic_limits(kind):
    g = Grid(6, 12)
    geo = Geometry(g, Profile(kind), 0.4)
    J0 = initial(g)
    h = VolterraHistory(SourceMemory(geo, J0), np.linspace(0, 0.4, 65))
    if kind == 'static':
        expected = P8.collide(g.n, g.w, J0, geo.profile.kappa(0.4))
    else:
        expected = h.memory.reconstruct_with_source(0.4, lambda t: np.zeros((3, 3)), order=4)
    assert np.max(np.abs(h.state(0.4) - expected)) < 3e-09
    assert np.max(np.abs(h.moment(0.4) - geo.moment(0.4, expected))) < 3e-09

def test_endpoint_converges_without_initial_tail_loss():
    g = Grid(6, 12)
    geo = Geometry(g, Profile('noncommuting'), 0.4)
    J0 = initial(g)
    direct = DirectHistory(geo, J0)
    errors = []
    for count in (8, 16, 32):
        h = VolterraHistory(SourceMemory(geo, J0), np.linspace(0, 0.4, count + 1))
        errors.append(np.max(np.abs(h.moment(0.4) - direct.moment(0.4))))
    assert 3.5 < np.log2(errors[0] / errors[1]) < 4.5
    assert errors[-1] < 3e-09

def test_zero_initial_source_does_not_erase_tail():
    g = Grid(8, 16)
    geo = Geometry(g, Profile('lrs'), 0.4)
    tail = synthesize(g, {('I', 4, 0): 0.1})
    mem = SourceMemory(geo, tail)
    assert np.linalg.norm(mem.initial_term(0)) < 2e-11
    h = VolterraHistory(mem, np.linspace(0, 0.4, 33))
    assert np.linalg.norm(h.moment(0.4)) > 0.0001

def test_screen_covariance_and_physical_initial_state():
    from bianchi.nonperturbative._core.polarized_dictionary import hermitian
    g = Grid(8, 16)
    geo = Geometry(g, Profile('noncommuting'), 0.4)
    h = VolterraHistory(SourceMemory(geo, initial(g)), np.linspace(0, 0.4, 33))
    for t in (0, 0.117, 0.4):
        J = h.state(t)
        z = geo.at(t)
        E = z['screen']
        H = np.einsum('nia,nij,njb->nab', E, hermitian(J), E)
        assert np.linalg.eigvalsh(H).min() > 0
        assert np.max(np.abs(np.einsum('nij,nj->ni', J, z['e']))) < 2e-11

def test_invalid_grid_and_out_of_support_fail_closed():
    g = Grid(6, 12)
    geo = Geometry(g, Profile('static'), 0.4)
    mem = SourceMemory(geo, initial(g))
    for t in ([0.1, 0.2], [0.0, 0.3, 0.2], [0.0, np.nan, 0.4], [0.0, 0.5]):
        with pytest.raises(ValueError):
            VolterraHistory(mem, t)
    with pytest.raises(ValueError):
        VolterraHistory(mem, [0.0, 0.4], order=1)
    h = VolterraHistory(mem, [0.0, 0.2, 0.4])
    with pytest.raises(ValueError):
        h.moment(0.41)
    with pytest.raises(ValueError):
        h.state(-0.01)
