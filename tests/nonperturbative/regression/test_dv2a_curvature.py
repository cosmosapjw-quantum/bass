import numpy as np
import pytest
from bianchi.nonperturbative._core.curvature_streaming import curvature_matrix, curvature_rhs, rank_one
from bianchi.nonperturbative._core.curvature_oracle import direct_curved_rhs
from bianchi.nonperturbative._core.polarized_dictionary import Grid, analyze, synthesize
from bianchi.q import polarization as P8
ATOL = 2e-11

@pytest.mark.parametrize('axis', [[0, 0, 1], [1, 0, 0], [0.3, -0.4, 0.5]])
def test_all_channels_against_p8(axis):
    N = rank_one(0.7, axis)
    g = Grid(12, 24)
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 1, 1): 0.12, ('I', 4, 0): 0.13, ('E', 2, 0): 0.1, ('E', 2, 2): 0.07, ('B', 3, -1): 0.04, ('V', 3, 2): 0.05}
    want = analyze(g, direct_curved_rhs(g, c, 0.0, np.zeros((3, 3)), N), 5)
    got = curvature_rhs(c, N, 5)
    assert max((abs(v - got.get(k, 0.0)) for k, v in want.items())) < ATOL

def test_axisymmetric_E20_generates_B20():
    got = curvature_rhs({('E', 2, 0): 1.0}, np.diag([0, 0, 0.7]), 3)
    assert abs(got['B', 2, 0] + 0.7) < ATOL
    assert max((abs(v) for k, v in got.items() if k != ('B', 2, 0))) < ATOL

def test_scalar_monopole_and_unpolarized_do_not_polarize():
    got = curvature_rhs({('I', 0, 0): 1.0}, rank_one(0.7, [1, 2, 3]), 3)
    assert max((abs(v) for v in got.values())) < ATOL
    got = curvature_rhs({('I', 4, 2): 1.0}, rank_one(0.7, [1, 2, 3]), 5)
    assert max((abs(v) for k, v in got.items() if k[0] in ('E', 'B', 'V'))) < ATOL

@pytest.mark.parametrize('spin', [0, 2])
def test_skew_hermitian_generator(spin):
    A = curvature_matrix(spin, 5, 5, rank_one(0.7, [1, 2, 3]))
    assert np.max(np.abs(A + A.conj().T)) < ATOL

def test_signed_strength_and_axis_sign():
    a = np.array([1.0, 2.0, 3.0])
    N = rank_one(0.7, a)
    A = curvature_matrix(2, 4, 5, N)
    assert np.max(np.abs(A + curvature_matrix(2, 4, 5, -N))) < ATOL
    assert np.max(np.abs(A - curvature_matrix(2, 4, 5, rank_one(0.7, -a)))) < ATOL

def test_invalid_curvature_rejected():
    with pytest.raises(ValueError):
        curvature_matrix(2, 4, 5, np.diag([1, 1, 0]))
    with pytest.raises(ValueError):
        rank_one(0.7, [0, 0, 0])
    with pytest.raises(ValueError):
        curvature_matrix(2, 4, 9, np.diag([0, 0, 1]))

def test_generator_has_no_direct_or_quadrature_calls(monkeypatch):

    def forbidden(*a, **kw):
        raise AssertionError('direct call in analytic generator')
    monkeypatch.setattr(P8, 'direction_rate', forbidden)
    monkeypatch.setattr(P8, 'tensor_rate', forbidden)
    monkeypatch.setattr(Grid, '__init__', forbidden)
    A = curvature_matrix(2, 4, 5, rank_one(0.29, [0.2, 0.8, 0.1]))
    assert np.linalg.norm(A) > 0

def test_combined_operator_with_shear_and_collision():
    from bianchi.nonperturbative._core.harmonic_streaming import coefficient_rhs
    g = Grid(12, 24)
    S = np.array([[0.2, 0.11, -0.07], [0.11, -0.12, 0.04], [-0.07, 0.04, -0.08]])
    N = rank_one(0.7, [1, 2, 3])
    c = {('I', 0, 0): 2 * np.sqrt(4 * np.pi), ('I', 4, 0): 0.1, ('E', 2, 2): 0.07, ('B', 3, -1): 0.04}
    got = coefficient_rhs(c, 0.3, S, 0.8, lout=6)
    C = curvature_rhs(c, N, 6)
    for k, v in C.items():
        got[k] = got.get(k, 0) + v
    want = analyze(g, direct_curved_rhs(g, c, 0.3, S, N, 0.8), 6)
    assert max((abs(v - got.get(k, 0.0)) for k, v in want.items())) < ATOL

def test_initial_B20_gain_null_returns_to_source():
    from bianchi.nonperturbative._core.polarized_dictionary import source_matrix, stf_basis
    g = Grid(12, 24)
    c = {('B', 2, 0): 0.1}
    N = rank_one(0.7, [0, 0, 1])
    J = synthesize(g, c)
    assert np.max(np.abs(np.einsum('n,nij->ij', g.w, J))) < ATOL
    Mdot = np.einsum('n,nij->ij', g.w, direct_curved_rhs(g, c, 0.0, np.zeros((3, 3)), N))
    target = 0.1 * 0.7 * np.sqrt(4 * np.pi / 5) * stf_basis()[2]
    assert np.max(np.abs(Mdot - target)) < ATOL
    assert np.max(np.abs(Mdot - source_matrix(curvature_rhs(c, N, 3)))) < ATOL
    assert np.linalg.norm(Mdot) > 0.1
