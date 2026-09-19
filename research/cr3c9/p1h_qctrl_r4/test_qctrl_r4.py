import numpy as np
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
