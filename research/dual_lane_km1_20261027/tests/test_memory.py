"""KM1 bounded tests, not prior DL1/DL2 campaigns or a production solver."""
import sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'vendor')]
from polarized_dictionary import Grid,synthesize,hermitian
import polarization as P8
from source_memory import Profile,Geometry,DirectHistory,SourceMemory

@pytest.fixture(scope='module')
def fixture():
    g=Grid(6,12); p=Profile('noncommuting'); geo=Geometry(g,p,.5)
    J=synthesize(g,{('I',0,0):2*np.sqrt(4*np.pi),('I',4,0):.1,
                    ('E',2,1):.04,('B',3,-2):.03,('V',1,0):.02})
    h=DirectHistory(geo,J); return g,p,geo,J,h,SourceMemory(geo,J)


def test_geometry_transversality_and_source_matched_screen_rate(fixture):
    g,p,geo,J,h,mem=fixture
    for t in (0.,.2,.5):
        z=geo.at(t); S=z['screen']; e=z['e']; H,sig=p.fields(t)
        assert np.max(np.abs(np.einsum('nia,nib->nab',S,S)-np.eye(2)))<2e-11
        assert np.max(np.abs(np.einsum('ni,nia->na',e,S)))<2e-11
        direct=P8.screen_vector_rate(S[:,:,0],e,H,sig,np.zeros(3),np.zeros((3,3)),np.zeros(3))
        assert np.max(np.abs(direct-geo.screen_rate(t,z)[:,:,0]))<2e-11


def test_kernel_diagonal_uses_raw_deformed_weights(fixture):
    g,p,geo,J,h,mem=fixture; M=np.arange(9).reshape(3,3)/9
    for t in (0.,.5):
        z=geo.at(t); P=np.eye(3)-np.einsum('ni,nj->nij',z['e'],z['e'])
        want=p.rate(t)*3/(8*np.pi)*np.einsum('n,nia,ab,nbj->ij',z['w'],P,M,P)
        actual=(mem.kernel(t,t)@M.ravel()).reshape(3,3)
        assert np.max(np.abs(actual-want))<2e-11


def test_native_volterra_identity_from_direct_source(fixture):
    g,p,geo,J,h,mem=fixture
    for t in (.2,.5):
        reconstructed=mem.evaluate_with_source(t,h.moment,24)
        assert np.max(np.abs(reconstructed-h.moment(t)))<3e-9
        assert np.max(np.abs(mem.reconstruct_with_source(t,h.moment,24)-h.state(t)))<3e-9


def test_exact_static_collision_limit():
    g=Grid(6,12); p=Profile('static'); geo=Geometry(g,p,.5)
    J=synthesize(g,{('I',0,0):np.sqrt(4*np.pi),('I',2,-1):.2,('B',3,2):.04})
    h=DirectHistory(geo,J)
    assert np.max(np.abs(h.state(.5)-P8.collide(g.n,g.w,J,p.kappa(.5))))<3e-10


def test_free_streaming_limit():
    g=Grid(6,12); geo=Geometry(g,Profile('free'),.5)
    J=synthesize(g,{('I',0,0):np.sqrt(4*np.pi),('E',2,1):.1})
    h=DirectHistory(geo,J); mem=SourceMemory(geo,J)
    assert np.max(np.abs(mem.kernel(.5,.2)))==0
    assert np.max(np.abs(h.moment(.5)-mem.initial_term(.5)))<3e-9


def test_gain_null_initial_tail_returns_and_must_not_be_deleted():
    g=Grid(6,12);geo=Geometry(g,Profile('lrs'),.5)
    J=synthesize(g,{('I',4,0):.1})
    mem=SourceMemory(geo,J);h=DirectHistory(geo,J)
    assert np.max(np.abs(h.moment(0.)))<2e-11
    assert np.linalg.norm(mem.initial_term(.5))>1e-4
    assert np.linalg.norm(h.moment(.5))>1e-4
    assert np.max(np.abs(mem.evaluate_with_source(.5,h.moment,24)-h.moment(.5)))<3e-9


def test_bad_time_queries_rejected(fixture):
    *_,mem=fixture
    with pytest.raises(ValueError): mem.kernel(.1,.2)
    with pytest.raises(ValueError): mem.kernel(.6,.2)
    with pytest.raises(ValueError): mem.initial_term(-.1)


def test_frobenius_kernel_bound(fixture):
    *_,mem=fixture
    for t,s in ((.5,0.),(.5,.3),(.5,.5)):
        assert np.linalg.norm(mem.kernel(t,s),2)<=mem.kernel_bound(t,s)*(1+1e-10)
