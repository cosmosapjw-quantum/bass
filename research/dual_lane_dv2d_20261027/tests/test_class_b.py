"""Scoped class-B instantaneous tests; no prior campaign is invoked."""
import sys
from pathlib import Path
import numpy as np
import pytest
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'code'),str(R/'vendor')]
from class_b_streaming import class_b_matrix,class_b_rhs,geometry_rates,frozen_map,rate_moments
from class_b_oracle import direct_rhs,projected_rhs,coordinate_rate
from polarized_dictionary import Grid,synthesize,source_matrix,hermitian,stokes
from harmonic_streaming import labels
import polarization as P8

@pytest.mark.parametrize('nt',[8,12,20])
def test_same_physics_rhs(nt):
 g=Grid(nt,2*nt);c={('I',0,0):2*np.sqrt(4*np.pi),('I',1,0):.17,('I',2,1):.09,('I',4,0):.08,('E',2,2):.11,('B',3,-1):.06,('V',1,1):.04}
 A=np.array([.4,-.3,.2]);S=np.array([[.2,.05,-.04],[.05,-.13,.02],[-.04,.02,-.07]])
 pred=class_b_rhs(c,A,H=.3,S=S,nu=.8,lout=6);actual=projected_rhs(g,c,A,H=.3,S=S,nu=.8,lout=6)
 assert max(abs(pred.get(k,0)-v) for k,v in actual.items())<2e-11
 screen=np.stack([g.bt,g.bp],axis=2);J=synthesize(g,c)
 assert np.linalg.eigvalsh(np.einsum('nia,nij,njb->nab',screen,hermitian(J),screen)).min()>0


def test_exact_signed_coefficients_and_isotropy():
 A=[0,0,.7];a=class_b_rhs({('I',1,0):1},A)
 assert abs(a['I',0,0]-1.4/np.sqrt(3))<2e-11
 assert abs(a['I',2,0]+1.4/np.sqrt(15))<2e-11
 b=class_b_rhs({('E',2,2):1},A)
 assert abs(b['B',2,-2]+1.4/3)<2e-11
 assert max(abs(x) for x in class_b_rhs({('I',0,0):1},A).values())<2e-11


def test_geometry_and_coordinate_independence():
 g=Grid(8,16);H=.3;S=np.diag([.2,-.1,-.1]);A=np.array([0,0,.7])
 v,B,div,logr=geometry_rates(g.n,H,S,A)
 assert np.max(abs(v-P8.direction_rate(g.n,H,S,np.zeros(3),np.zeros((3,3)),A)))<2e-11
 for W in (g.bt,g.bp):
  assert np.max(abs(np.einsum('nij,nj->ni',B,W)-P8.screen_vector_rate(W,g.n,H,S,np.zeros(3),np.zeros((3,3)),A)))<2e-11
 physical_dp=coordinate_rate(g.n,[1.2,.9,1.1],H+np.diag(S),.7*1.1,.2)
 expected=logr[:,None]*g.n+v
 assert np.max(abs(physical_dp-expected))<2e-11


def test_energy_flux_and_measure():
 g=Grid(12,24);c={('I',0,0):2*np.sqrt(4*np.pi),('I',1,1):.2,('I',2,-2):.1,('I',3,0):.05,('E',2,1):.1}
 A=np.array([.4,-.3,.2]);H=.3;S=np.diag([.2,-.1,-.1]);nu=.8
 J=synthesize(g,c);rhs=direct_rhs(g,c,A,H=H,S=S,nu=nu)
 rho,q,pi=rate_moments(g,J);dr,dq,_=rate_moments(g,rhs)
 assert abs(dr-(-4*H*rho-np.einsum('ij,ij',S,pi)+2*A@q))<2e-11
 assert np.max(abs(dq-(-(4*H+nu)*q-S@q+3*pi@A)))<2e-11


def test_gain_null_B_return():
 g=Grid(12,24);c={('B',2,2):.1};A=[0,0,.7]
 assert np.linalg.norm(source_matrix(c))==0
 d=class_b_rhs(c,A);assert abs(d['E',2,-2]-.14/3)<2e-11
 md=np.einsum('n,nij->ij',g.w,direct_rhs(g,c,A))
 assert np.max(abs(md-source_matrix(d)))<2e-11
 assert np.linalg.norm(md)>1e-2


def test_frozen_map_jacobian_and_not_doppler():
 g=Grid(12,24);a=.7;t=.3;n,j=frozen_map(g.n,a,t)
 assert np.max(abs(np.linalg.norm(n,axis=1)-1))<2e-11
 h=1e-5;vp=(frozen_map(g.n,a,t+h)[0]-frozen_map(g.n,a,t-h)[0])/(2*h)
 expected=geometry_rates(n,0,np.zeros((3,3)),[0,0,a])[0]
 assert np.max(abs(vp-expected))<5e-8
 assert abs(np.dot(g.w,j)-4*np.pi)<2e-11
 assert np.max(abs(j-1))>1e-2


def test_analytic_generator_does_not_call_P8_or_grid(monkeypatch):
 def forbidden(*a,**kw):raise AssertionError('analytic lane called oracle')
 monkeypatch.setattr(P8,'direction_rate',forbidden)
 monkeypatch.setattr(P8,'tensor_rate',forbidden)
 monkeypatch.setattr(Grid,'__init__',forbidden)
 m=class_b_matrix(2,4,5,[.4,-.3,.2]);assert np.isfinite(m).all()


def test_non_antihermitian_and_spin_selection():
 A=[.4,-.3,.2];K=class_b_matrix(2,4,4,A);lab=labels(2,4)
 assert np.max(abs(K+K.conj().T))>1e-2
 for i,(l,m) in enumerate(lab):
  for j,(lp,mp) in enumerate(lab):
   if abs(l-lp)!=1:assert abs(K[i,j].real)<2e-11
   if l!=lp:assert abs(K[i,j].imag)<2e-11


def test_invalid_inputs_are_rejected():
 for a in ([1,2],[1,2,np.nan]):
  with pytest.raises(ValueError):class_b_matrix(2,4,5,a)
 with pytest.raises(ValueError):class_b_rhs({('E',1,0):1},[0,0,1])
 with pytest.raises(ValueError):class_b_rhs({('I',7,0):1},[0,0,1])
 with pytest.raises(ValueError):class_b_rhs({},[0,0,1],S=np.eye(3))
