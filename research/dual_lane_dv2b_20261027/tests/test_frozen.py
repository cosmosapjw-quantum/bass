import sys
from pathlib import Path
import numpy as np
import pytest
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'code'),str(R/'vendor')]
from frozen_bianchi_ii import FrozenProfile,FrozenGeometry,FrozenDirect,FrozenHarmonic,free_eulerian,m0_exact
from polarized_dictionary import Grid,synthesize,source_matrix
from source_memory import SourceMemory
from volterra_solver import VolterraHistory
import polarization as P8

@pytest.mark.parametrize('axis',[[0,0,1],[1,2,-1]])
def test_exact_geometry_and_p8_rates(axis):
 g=Grid(8,16);p=FrozenProfile(.9,0.,axis=tuple(axis));G=FrozenGeometry(g,p,.8)
 z=G.at(.35);dt=2e-6;a=G.at(.35+dt);b=G.at(.35-dt);Z=np.zeros((3,3));v=np.zeros(3)
 assert np.max(abs(z['screen'].transpose(0,2,1)@z['screen']-np.eye(2)))<2e-11
 assert np.max(abs(np.einsum('nia,ni->na',z['screen'],z['e'])))<2e-11
 assert np.max(abs((a['e']-b['e'])/(2*dt)-P8.direction_rate(z['e'],0.,Z,v,p.N,v)))<2e-9
 for j in (0,1):
  assert np.max(abs((a['screen'][:,:,j]-b['screen'][:,:,j])/(2*dt)-P8.screen_vector_rate(z['screen'][:,:,j],z['e'],0.,Z,v,p.N,v)))<2e-9
 assert np.array_equal(z['w'],g.w)

def test_free_characteristic_and_direct():
 g=Grid(8,16);G=FrozenGeometry(g,FrozenProfile(.9,0.),.4)
 c={('I',0,0):2*np.sqrt(4*np.pi),('E',2,1):.06,('B',3,-1):.04,('I',4,2):.1}
 d=FrozenDirect(G,synthesize(g,c));z=G.at(.4)
 assert np.max(abs(d.state(.4)-free_eulerian(z['e'],g.w,c,.9,.4)))<3e-10

def test_exact_m0_collision_block():
 g=Grid(8,16);G=FrozenGeometry(g,FrozenProfile(.9,1.4),.5)
 c={('I',0,0):2*np.sqrt(4*np.pi),('B',2,0):.1}
 h=FrozenHarmonic(G.profile,c,4,.5)
 ex=m0_exact([0,0,.1],.9,1.4,.5)
 assert np.max(abs(np.array([h.coefficients(.5).get((f,2,0),0) for f in ('I','E','B')])-ex))<2e-11

def test_independent_volterra(monkeypatch):
 g=Grid(8,16);G=FrozenGeometry(g,FrozenProfile(.9,1.4),.3)
 c={('I',0,0):2*np.sqrt(4*np.pi),('B',2,0):.1};J=synthesize(g,c)
 def forbidden(*a,**k):raise AssertionError('Direct path forbidden')
 monkeypatch.setattr(FrozenDirect,'__init__',forbidden)
 v=VolterraHistory(SourceMemory(G,J),np.linspace(0,.3,17))
 ex=m0_exact([0,0,.1],.9,1.4,.3);ce={('I',0,0):c['I',0,0],**{(f,2,0):float(x) for f,x in zip(('I','E','B'),ex)}}
 assert np.max(abs(v.moment(.3)-source_matrix(ce)))<3e-8

def test_no_silent_initial_truncation():
 with pytest.raises(ValueError):FrozenHarmonic(FrozenProfile(),{('I',5,0):1.},4,.1)

def test_domain_guards():
 with pytest.raises(ValueError):FrozenProfile(nu=-1.)
 with pytest.raises(ValueError):FrozenProfile(axis=(0,0,0))
 G=FrozenGeometry(Grid(8,16),FrozenProfile(),.4)
 with pytest.raises(ValueError):G.at(.5)
 with pytest.raises(ValueError):SourceMemory(G,np.zeros((1,3,3)))

def test_opacity_integral():
 p=FrozenProfile(variable=True);t=.37;h=1e-6
 assert abs((p.kappa(t+h)-p.kappa(t-h))/(2*h)-p.rate(t))<1e-9

def test_zero_curvature_recovers_p8_static():
 g=Grid(8,16);G=FrozenGeometry(g,FrozenProfile(0.,1.4),.4)
 c={('I',0,0):2*np.sqrt(4*np.pi),('E',2,-1):.04,('B',3,1):.03,('V',1,0):.02}
 J=synthesize(g,c);d=FrozenDirect(G,J)
 assert np.max(abs(d.state(.4)-P8.collide(g.n,g.w,J,.56)))<3e-10

def test_harmonic_does_not_consume_other_solvers(monkeypatch):
 def forbidden(*a,**k):raise AssertionError('reference path forbidden')
 monkeypatch.setattr(FrozenDirect,'__init__',forbidden)
 monkeypatch.setattr(SourceMemory,'kernel',forbidden)
 h=FrozenHarmonic(FrozenProfile(.9,1.4),{('B',2,0):.1},2,.2)
 assert abs(h.coefficients(.2)['E',2,0]-m0_exact([0,0,.1],.9,1.4,.2)[1])<2e-11
