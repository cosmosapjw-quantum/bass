import numpy as np
from scipy.special import sph_harm_y
from bass_r3.qctrl_r4 import (stable_screening_potential,gaunt_p_lambda,nuclear_axis_matrix,
 screening_axis_matrix,axis_potential_matrix,direct_axis_matrix,ly_matrix,StateLayout,
 apply_y_rotation,run_axial_mresolved,run_offaxis,frozen_neutral_target_bound_spectrum)

def test_screening_limit_and_direct_agreement():
 x=np.array([0.,1e-14,1e-8,1e-4,.1,1.])
 v=stable_screening_potential(x)
 assert v[0]==1.0
 small=1-(2/3)*x[2]**2+(2/3)*x[2]**3-(2/5)*x[2]**4
 np.testing.assert_allclose(v[2],small,rtol=1e-14,atol=1e-14)
 direct=(1-np.exp(-2*x[3:]))/x[3:]-np.exp(-2*x[3:])
 np.testing.assert_allclose(v[3:],direct,rtol=5e-12,atol=5e-14)

def test_gaunt_selection_rules_and_monopole():
 assert gaunt_p_lambda(1,2,0,0)==0.0
 assert gaunt_p_lambda(1,1,0,1)==0.0
 np.testing.assert_allclose(gaunt_p_lambda(2,2,1,0),1.0,atol=1e-15)

def test_split_reconstructs_direct_matrix_away_from_singularity():
 r=np.array([.4,.9,1.4,2.3,3.7]);R=1.8
 for m in (0,1,-1):
  S=axis_potential_matrix(r,R,3,m,192,1)
  D=direct_axis_matrix(r,R,3,m,512,1)
  np.testing.assert_allclose(S,D,rtol=3e-9,atol=3e-10)

def test_axis_matrix_hermitian():
 r=np.linspace(.3,4,9)
 for m in range(-3,4):
  W=axis_potential_matrix(r,1.7,3,m,96)
  np.testing.assert_allclose(W,W.transpose(0,2,1),atol=2e-13)

def test_ly_hermitian_and_rotation_unitary():
 layout=StateLayout.build(4);rng=np.random.default_rng(3)
 psi=rng.normal(size=(7,layout.size))+1j*rng.normal(size=(7,layout.size))
 for l in range(5):np.testing.assert_allclose(ly_matrix(l),ly_matrix(l).conj().T,atol=1e-15)
 a=apply_y_rotation(psi,layout,.731)
 np.testing.assert_allclose(np.vdot(a,a),np.vdot(psi,psi),rtol=2e-14,atol=2e-14)
 b=apply_y_rotation(a,layout,-.731)
 np.testing.assert_allclose(b,psi,rtol=2e-13,atol=2e-13)

def test_axial_m_decoupling_tiny():
 res,_=run_axial_mresolved(nr=36,rmax=24,lmax=2,dt=.2,zmax=2.5,energy_keV=100,nangle=32)
 assert res['m_nonzero_probability']<1e-28
 assert abs(res['norm']-1)<5e-12

def test_offaxis_tiny_norm():
 res,_=run_offaxis(nr=30,rmax=20,lmax=2,dt=.2,zmax=2,energy_keV=100,b=1,nangle=28)
 assert abs(res['norm']-1)<5e-12
 assert res['complement_is_ionization'] is False

def test_frozen_neutral_direct_potential_has_no_bound_state_on_refined_box():
 bound,low=frozen_neutral_target_bound_spectrum(nr=500,rmax=60,l=0)
 assert len(bound)==0
 assert low[0]>0

from bass_r3.qctrl_r4 import rotation_matrix_global,axis_operator_global_at_r,direct_operator_global_at_r,scalar_field_from_coeff

def test_three_nontrivial_rotation_covariances_operator_and_expectation():
 layout=StateLayout.build(3);Wz=axis_operator_global_at_r(1.2,2.0,3,128);rng=np.random.default_rng(8)
 c=rng.normal(size=layout.size)+1j*rng.normal(size=layout.size);c/=np.linalg.norm(c)
 for alpha,beta in ((.37,.63),(1.11,.92),(2.2,1.34)):
  U=rotation_matrix_global(layout,alpha,beta,0.0);Wr=U@Wz@U.conj().T
  Wd=direct_operator_global_at_r(1.2,2.0,beta,alpha,3,64,128)
  np.testing.assert_allclose(Wr,Wd,rtol=2e-8,atol=2e-9)
  cr=U@c
  np.testing.assert_allclose(np.vdot(cr,Wr@cr),np.vdot(c,Wz@c),rtol=2e-13,atol=2e-13)

def test_collision_to_gas_rotation_adapter_field_identity():
 layout=StateLayout.build(3);rng=np.random.default_rng(19)
 c=rng.normal(size=layout.size)+1j*rng.normal(size=layout.size)
 alpha,beta=.71,1.03;U=rotation_matrix_global(layout,alpha,beta,0.0);cr=U@c
 # Test active field rotation f_R(n)=f(R^{-1}n) by converting directions with the
 # matching 3D active rotation Rz(alpha) Ry(beta).
 th=np.array([.4,1.1,2.0]);ph=np.array([.2,2.2,5.1])
 n=np.stack([np.sin(th)*np.cos(ph),np.sin(th)*np.sin(ph),np.cos(th)],axis=1)
 ca,sa=np.cos(alpha),np.sin(alpha);cb,sb=np.cos(beta),np.sin(beta)
 Rz=np.array([[ca,-sa,0],[sa,ca,0],[0,0,1.]])
 Ry=np.array([[cb,0,sb],[0,1.,0],[-sb,0,cb]])
 nold=n@(Rz@Ry)  # row vectors: R^{-1} n corresponds to n^T -> Ry^T Rz^T n; row -> n Rz Ry
 thold=np.arccos(np.clip(nold[:,2],-1,1));phold=np.mod(np.arctan2(nold[:,1],nold[:,0]),2*np.pi)
 np.testing.assert_allclose(scalar_field_from_coeff(cr,layout,th,ph),scalar_field_from_coeff(c,layout,thold,phold),rtol=3e-13,atol=3e-13)

def test_bass_scalar_ylm_mu_recurrence_convention():
 # BASS SSOT: mu Y_lm = mu+ Y_{l+1,m} + mu- Y_{l-1,m}.
 th=np.array([.31,.88,1.37,2.41]);ph=np.array([.2,1.1,3.0,5.2]);mu=np.cos(th)
 for l,m in ((1,0),(2,1),(3,-2)):
  lhs=mu*sph_harm_y(l,m,th,ph)
  mup=np.sqrt(((l+1)**2-m*m)/((2*l+1)*(2*l+3)))
  rhs=mup*sph_harm_y(l+1,m,th,ph)
  if l>abs(m):
   mum=np.sqrt((l*l-m*m)/((2*l-1)*(2*l+1)))
   rhs=rhs+mum*sph_harm_y(l-1,m,th,ph)
  np.testing.assert_allclose(lhs,rhs,rtol=2e-14,atol=2e-14)
