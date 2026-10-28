"""DV2-F scope tests; historical campaigns are not invoked."""
import sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'vendor')]
from expanding_bianchi_v import (CoframeProfile,ExpandingGeometry,CoordinateRays,TangentGeometry,
    ExpandingDirect,ExpandingHarmonic,analytic_rates,conformal_exact_geometry,conformal_dipole)
from polarized_dictionary import Grid,synthesize
from harmonic_history import direction_view
from frozen_bianchi_v import FrozenV,Geometry as FrozenGeometry
from source_memory import SourceMemory
from volterra_solver import VolterraHistory
import polarization as P8

def field():return {('I',0,0):2*np.sqrt(4*np.pi),('I',1,0):.09,('I',4,0):.05,('E',2,2):.025,('B',2,-1):.02,('V',1,1):.01}

@pytest.fixture(scope='module')
def base():
 g=Grid(8,16);p=CoframeProfile();geo=ExpandingGeometry(g,p,.15)
 return g,p,geo

def test_coframe_constraint():
 p=CoframeProfile()
 for t in (0.,.1,.4):
  H,S=p.fields(t)
  assert np.max(abs(p.structure_rate(t)+(H*np.eye(3)+S)@p.structure(t)))<2e-14
  assert np.all(p.scales(t)>0)

def test_frozen_limit():
 g=Grid(8,16);p=CoframeProfile(h=(0,0,0),d=(0,0,0));geo=ExpandingGeometry(g,p,.2)
 f=FrozenGeometry(g,FrozenV(A=(0,0,p.a0)),.2)
 for k in ('e','screen','mu','jac'):
  assert np.max(abs(geo.at(.2)[k]-f.at(.2)[k]))<5e-10

def test_zero_A_bianchi_I_limit():
 g=Grid(8,16);p=CoframeProfile(a0=0);geo=ExpandingGeometry(g,p,.15);z=geo.at(.15)
 mom=g.n/p.scales(.15);r=np.linalg.norm(mom,axis=1)
 assert np.max(abs(z['e']-mom/r[:,None]))<5e-10
 assert np.max(abs(z['mu']-r))<5e-10
 assert np.max(abs(z['jac']-np.exp(-sum(p.logs(.15)))/r**3))<5e-10

def test_conformal_exact_geometry():
 g=Grid(8,16);p=CoframeProfile(h=(.3,)*3,d=(0,)*3,nu0=0,nuamp=0);geo=ExpandingGeometry(g,p,.2)
 exact=conformal_exact_geometry(g,p,.2)
 for k in ('e','screen','mu','jac'):
  assert np.max(abs(geo.at(.2)[k]-exact[k]))<5e-10

def test_coordinate_rays_and_volume_measure(base):
 g,p,geo=base;coord=CoordinateRays(g.n,p,.15)
 for t in (0.,.075,.15):
  e,r,zz=coord.at(t);z=geo.at(t)
  assert np.max(abs(e-z['e']))<5e-10
  assert np.max(abs(r-z['mu']))<5e-10
  invariant=z['jac']*r**3*np.exp(sum(p.logs(t))-2*p.a0*(zz-coord.z0))
  assert np.max(abs(invariant-1))<5e-10

def test_tangent_area(base):
 g,p,geo=base;ta=TangentGeometry(g,p,.15)
 assert np.max(abs(ta.area(.15)-geo.at(.15)['jac']))<5e-10

def test_screen_rate_matches_p8(base):
 g,p,geo=base;z=geo.at(.15);H,S=p.fields(.15)
 v,lr,de,lj=analytic_rates(z['e'],z['screen'],H,S,p.structure(.15))
 for k in (0,1):
  ref=P8.screen_vector_rate(z['screen'][:,:,k],z['e'],H,S,np.zeros(3),np.zeros((3,3)),p.structure(.15))
  assert np.max(abs(ref-de[:,:,k]))<2e-11
 assert np.max(abs(np.einsum('nia,nib->nab',z['screen'],z['screen'])-np.eye(2)))<2e-11

def test_free_conformal_dipole():
 g=Grid(12,24);p=CoframeProfile(h=(.3,)*3,d=(0,)*3,nu0=0,nuamp=0);geo=ExpandingGeometry(g,p,.2)
 J0=P8.unpolarized(g.n,2+.3*g.n[:,2]);direct=ExpandingDirect(geo,J0)
 z=geo.at(.2);I=np.trace(direct.state(.2),axis1=1,axis2=2)
 rho=float(z['w']@I);qz=float(z['w']@(I*z['e'][:,2]));er,eq=conformal_dipole(p,.2)
 assert abs(rho-er)<5e-10 and abs(qz-eq)<5e-10

def test_independent_volterra_against_direct(base,monkeypatch):
 g,p,geo=base;J=synthesize(g,field());direct=ExpandingDirect(geo,J)
 def forbidden(*a,**k):raise AssertionError('Direct cannot be used by Volterra')
 monkeypatch.setattr(ExpandingDirect,'__init__',forbidden)
 v=VolterraHistory(SourceMemory(geo,J),np.linspace(0,.15,17))
 assert np.max(abs(v.moment(.15)-direct.moment(.15)))<3e-9

def test_harmonic_same_physics_short_path():
 g=Grid(12,24);p=CoframeProfile();geo=ExpandingGeometry(g,p,.08);J=synthesize(g,field());d=ExpandingDirect(geo,J)
 h=ExpandingHarmonic(p,field(),6,.08)
 assert np.max(abs(h.moment(.08)-d.moment(.08)))<3e-7

def test_invalid_support_and_inputs(base):
 g,p,geo=base
 with pytest.raises(ValueError):CoframeProfile(nu0=-1)
 with pytest.raises(ValueError):CoframeProfile(h=(1,2))
 with pytest.raises(ValueError):geo.at(-.1)
 with pytest.raises(ValueError):ExpandingGeometry(g,p,float('nan'))
 with pytest.raises(ValueError):ExpandingHarmonic(p,{('I',9,0):1.},4,.1)
