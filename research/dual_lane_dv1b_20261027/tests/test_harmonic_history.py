"""New DV1-B tests only; no previous campaign is replayed."""
from pathlib import Path
import sys
import numpy as np
import pytest
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'code'),str(R/'vendor')]
from harmonic_history import HarmonicHistory, GalerkinSystem, point_grid, kinetic_moments
from source_memory import Profile,Geometry,DirectHistory,SourceMemory
from polarized_dictionary import Grid,synthesize,collision_coefficients,source_matrix
from harmonic_streaming import coefficient_rhs

C={('I',0,0):2*np.sqrt(4*np.pi),('I',4,0):.15,('I',1,1):.03,
   ('E',2,2):.03,('E',2,-1):.025,('B',3,2):.015,('V',1,-1):.02}

def test_cached_generator_matches_parent_on_retained_modes():
    sysm=GalerkinSystem(4); y=sysm.pack(C); H,S=Profile().fields(.17)
    actual=sysm.unpack(sysm.rhs(.17,y,Profile()))
    expected=coefficient_rhs(C,H,S,Profile().rate(.17),lout=4)
    assert max(abs(actual.get(k,0)-v) for k,v in expected.items())<2e-11

def test_static_exact_polarized_semigroup():
    h=HarmonicHistory(Profile('static'),C,4,.2)
    ref=collision_coefficients(C,Profile('static').kappa(.2))
    assert max(abs(v-ref.get(k,0.)) for k,v in h.coefficients(.2).items())<1e-10

@pytest.mark.parametrize('L',[4,6,8])
def test_initial_carrier_and_source_preserved(L):
    h=HarmonicHistory(Profile(),C,L,.05);g=Grid(10,20)
    assert np.max(abs(h.state(g,0)-synthesize(g,C)))<2e-11
    assert np.max(abs(h.moment(0)-source_matrix(C)))<2e-11

def test_harmonic_solver_cannot_use_direct_or_memory_source(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('forbidden reference call')
    monkeypatch.setattr(DirectHistory,'__init__',forbidden)
    monkeypatch.setattr(SourceMemory,'__init__',forbidden)
    h=HarmonicHistory(Profile(),C,4,.03)
    assert np.isfinite(h.moment(.03)).all()

def test_cutoff_does_not_silently_delete_initial_tail():
    with pytest.raises(ValueError,match='initial'):HarmonicHistory(Profile(),C,2,.05)
    with pytest.raises(ValueError):GalerkinSystem(9)
    h=HarmonicHistory(Profile(),C,4,.05)
    with pytest.raises(ValueError):h.coefficients(-.01)
    with pytest.raises(ValueError):h.coefficients(.1)

def test_sampling_and_kinetic_moments_are_consistent():
    g=Grid(12,24);h=HarmonicHistory(Profile('static'),C,4,.05)
    q=point_grid(g.n,g.w)
    assert np.max(abs(h.state(q,0)-synthesize(g,C)))<2e-11
    m=kinetic_moments(q,h.state(q,0))
    assert abs(m['rho']-4*np.pi*2)<2e-11
    assert abs(np.trace(m['pi']))<2e-11

def test_initial_source_null_tail_is_kept_and_generates_source():
    c={('I',4,0):.15};h=HarmonicHistory(Profile('lrs'),c,6,.15)
    assert np.linalg.norm(h.moment(0))<2e-11
    assert np.linalg.norm(h.moment(.15))>1e-4
