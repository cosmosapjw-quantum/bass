from pathlib import Path
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'vendor')]
from harmonic_streaming import streaming_matrix, labels, coefficient_rhs, collision_rhs
from direct_oracle import direct_rhs, projected_rhs, spin_coordinate_rhs
from polarized_dictionary import Grid,synthesize,stokes

S=np.array([[.31,.17,-.09],[.17,-.12,.11],[-.09,.11,-.19]])
TOL=2e-11

@pytest.mark.parametrize('spin',[0,2])
def test_gaunt_action_matches_cartesian_p8(spin):
    g=Grid(12,24)
    for l in range(spin,5):
        for m in range(-l,l+1):
            c={(('I' if spin==0 else 'E'),l,m):1.}
            got=projected_rhs(g,c,.4,S,0.,6)
            want=coefficient_rhs(c,.4,S,0.,6)
            assert max(abs(got[k]-want.get(k,0.)) for k in got)<TOL

@pytest.mark.parametrize('field',['I','E','B','V'])
def test_isotropic_limit(field):
    c={(field,3,2):1.}
    got=coefficient_rhs(c,.7,np.zeros((3,3)),0.,5)
    assert max(abs(v-(-2.8 if k==(field,3,2) else 0.)) for k,v in got.items())<TOL


def test_screen_connection_matches_p8_tensor_route():
    g=Grid(12,24);c={('E',3,2):.2,('B',2,-1):.3,('I',0,0):4.,('V',2,1):.04}
    Jdot=direct_rhs(g,c,.4,S,0.)
    I,Q,U,V=stokes(g,Jdot)
    expected=spin_coordinate_rhs(g,c,.4,S)
    assert np.max(np.abs((Q+1j*U)-expected['P']))<TOL
    assert np.max(np.abs(I-expected['I']))<TOL
    assert np.max(np.abs(V-expected['V']))<TOL


def test_same_physics_collision_rhs():
    g=Grid(12,24);c={('E',2,-1):.2,('B',4,1):.3,('I',2,2):.4,('V',1,1):.08}
    got=projected_rhs(g,c,.4,S,1.7,6)
    want=coefficient_rhs(c,.4,S,1.7,6)
    assert max(abs(v-want.get(k,0.)) for k,v in got.items())<TOL


def test_spin_selection_and_nonzero_eb():
    a=streaming_matrix(2,4,6,0.,S)
    lo,li=labels(2,6),labels(2,4)
    for i,(l,m) in enumerate(lo):
        for j,(lp,mp) in enumerate(li):
            if abs(l-lp)>2: assert abs(a[i,j])<TOL
            if (l-lp)%2==0: assert abs(a[i,j].imag)<TOL
            else: assert abs(a[i,j].real)<TOL
    assert np.max(np.abs(a.imag))>1e-3


def test_invalid_domain_rejected():
    with pytest.raises(ValueError): streaming_matrix(1,4,6,.4,S)
    with pytest.raises(ValueError): streaming_matrix(2,4,9,.4,S)
    with pytest.raises(ValueError): streaming_matrix(2,4,6,.4,S+np.eye(3))
    with pytest.raises(ValueError): collision_rhs({},-1.)
