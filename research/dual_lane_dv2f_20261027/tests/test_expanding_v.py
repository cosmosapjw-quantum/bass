"""DV2-F local tests, not a previous BASS scientific campaign."""
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'vendor')]
from expanding_bianchi_v import (CoframeProfile, ExpandingGeometry, CoordinateRays,
    TangentGeometry, ExpandingDirect, ExpandingHarmonic, analytic_rates)
from polarized_dictionary import Grid,synthesize,hermitian
from source_memory import SourceMemory
from volterra_solver import VolterraHistory
from frozen_bianchi_v import FrozenV,Geometry as FrozenGeometry
import polarization as P8


def test_input_validation():
    for kw in ({'h':(1,2)}, {'a0':np.nan}, {'nu0':-.1}, {'nuamp':2}):
        with pytest.raises(ValueError):CoframeProfile(**kw)
    with pytest.raises(ValueError):ExpandingGeometry(Grid(4,8),CoframeProfile(),-.1)


def test_coframe_compatibility():
    p=CoframeProfile()
    for t in (0,.13,.4):
        H,S=p.fields(t)
        assert abs(p.structure_rate(t)+(H+S[2,2])*p.structure(t)[2])<2e-14
        assert p.scales(t).min()>0


def test_coordinate_hamiltonian_and_volume_identity():
    g=Grid(5,10);p=CoframeProfile();geo=ExpandingGeometry(g,p,.25)
    c=CoordinateRays(g.n,p,.25)
    for t in (0,.13,.25):
        z=geo.at(t);n,r,position=c.at(t)
        assert np.max(abs(n-z['e']))<5e-10
        assert np.max(abs(r-z['mu']))<5e-10
        identity=z['jac']*r**3*np.prod(p.scales(t))*np.exp(-2*p.a0*(position-c.z0))
        assert np.max(abs(identity-1))<5e-10


def test_screen_rates_match_p8():
    g=Grid(6,12);p=CoframeProfile();geo=ExpandingGeometry(g,p,.2)
    z=geo.at(.13);H,S=p.fields(.13);A=p.structure(.13)
    v,lr,dE,lj=analytic_rates(z['e'],z['screen'],H,S,A)
    ref=np.stack([P8.screen_vector_rate(z['screen'][:,:,k],z['e'],H,S,np.zeros(3),np.zeros((3,3)),A) for k in range(2)],axis=2)
    assert np.max(abs(ref-dE))<2e-11
    assert np.max(abs(np.einsum('nia,nib->nab',z['screen'],z['screen'])-np.eye(2)))<2e-11


def test_variational_angular_measure():
    g=Grid(5,10);p=CoframeProfile();geo=ExpandingGeometry(g,p,.25);tan=TangentGeometry(g,p,.25)
    assert np.max(abs(tan.area(.25)-geo.at(.25)['jac']))<5e-10
    assert np.max(abs(geo.at(.25)['jac']*geo.at(.25)['mu']**3*np.prod(p.scales(.25))-1))>1e-2


def test_frozen_limit():
    p=CoframeProfile(h=(0,0,0),d=(0,0,0),a0=.7,nu0=0,nuamp=0)
    g=Grid(5,10);geo=ExpandingGeometry(g,p,.3);old=FrozenGeometry(g,FrozenV((0,0,.7),0),.3)
    for key in ('e','screen','jac','mu'):
        assert np.max(abs(geo.at(.3)[key]-old.at(.3)[key]))<5e-10


def test_zero_structure_bianchi_i_limit():
    p=CoframeProfile(a0=0);g=Grid(5,10);geo=ExpandingGeometry(g,p,.3)
    mom=g.n/p.scales(.3);r=np.linalg.norm(mom,axis=1);z=geo.at(.3)
    assert np.max(abs(z['e']-mom/r[:,None]))<5e-10
    assert np.max(abs(z['mu']-r))<5e-10
    assert np.max(abs(z['jac']-1/(np.prod(p.scales(.3))*r**3)))<5e-10


def test_isotropic_conformal_frozen_limit():
    p=CoframeProfile(h=(.25,)*3,d=(.06,)*3);g=Grid(5,10);geo=ExpandingGeometry(g,p,.3)
    eta=quad(lambda t:1/p.scales(t)[0],0,.3,epsabs=1e-13)[0]
    frozen=FrozenGeometry(g,FrozenV((0,0,p.a0),0),1.)
    exact=frozen.at(eta);z=geo.at(.3)
    for key in ('e','screen','jac'):assert np.max(abs(z[key]-exact[key]))<5e-10
    assert np.max(abs(z['mu']-1/p.scales(.3)[0]))<5e-10


def test_volterra_does_not_call_direct(monkeypatch):
    import expanding_bianchi_v as EV
    def forbidden(*args,**kwargs):raise AssertionError('Direct source must not be queried')
    monkeypatch.setattr(EV,'ExpandingDirect',forbidden)
    g=Grid(6,12);geo=ExpandingGeometry(g,CoframeProfile(),.08)
    J=synthesize(g,{('I',0,0):2*np.sqrt(4*np.pi),('E',2,2):.05})
    v=VolterraHistory(SourceMemory(geo,J),np.linspace(0,.08,9))
    assert np.isfinite(v.moment(.08)).all()


def test_short_same_physics_three_lane():
    g=Grid(8,16);p=CoframeProfile();geo=ExpandingGeometry(g,p,.04)
    c={('I',0,0):2*np.sqrt(4*np.pi),('E',2,2):.03};J=synthesize(g,c)
    d=ExpandingDirect(geo,J);h=ExpandingHarmonic(p,c,6,.04)
    v=VolterraHistory(SourceMemory(geo,J),np.linspace(0,.04,9))
    assert np.max(abs(v.moment(.04)-d.moment(.04)))<3e-9
    assert np.max(abs(h.moment(.04)-d.moment(.04)))<3e-8
    z=geo.at(.04);H2=np.einsum('nia,nij,njb->nab',z['screen'],hermitian(d.state(.04)),z['screen'])
    assert np.linalg.eigvalsh(H2).min()>0
