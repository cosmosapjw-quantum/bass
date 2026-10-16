"""Scoped original PR164 Einstein source and massless photon response integration."""
import math,unittest
import numpy as np
from run_bass_campaign import build_case,refinement
from coupled_lrs_gamma import integrate,gamma_contraction_bound
from born_photon_stress import BornIsotropicRadiation,XMAX

class OriginalBassPhotonCampaign(unittest.TestCase):
 def test_pr164_bass_endpoint_signed(self):
  for mass in (3.,30.):
   for A in (-.5,.5):
    rows,summary=build_case(mass,A,'old_only',nodes=17,n_birth=32,n_mu=48)
    self.assertGreater(rows[-1]['b']*A,0.)
    self.assertLess(abs(rows[-1]['b']),.003)
    self.assertLess(abs(summary['ledger']['energy_residual']),3e-10)
 def test_linear_age_memory_per_original_lrs_geometry(self):
  rows,s=build_case(3.,.5,'old_plus_source',nodes=65)
  self.assertLess(s['max_memory_U_M_vs_independent_DOP853'],5e-10)
  self.assertLess(s['max_fractional_linear_error'],1e-3)
 def test_radiation_pressure_opposes_signed_b(self):
  for A in (-.5,.5):
   rows,s=build_case(3.,A,'old_only',nodes=33)
   for r in rows[1:]:
    self.assertLess(r['photon_delta']*r['b'],0.)
 def test_bolometric_old_and_newborn_add_without_double_count(self):
  r0,_=build_case(3.,.5,'old_only',nodes=13,n_birth=48)
  r1,_=build_case(3.,.5,'source_only',nodes=13,n_birth=48)
  rt,_=build_case(3.,.5,'old_plus_source',nodes=13,n_birth=48)
  for a,b,c in zip(r0,r1,rt):
   self.assertLess(abs(a['photon_rho']+b['photon_rho']-c['photon_rho']),3e-14)
   self.assertLess(abs(a['photon_delta']+b['photon_delta']-c['photon_delta']),3e-14)

 def test_radiation_energy_out_of_background(self):
  rows,s=build_case(30.,.5,'old_only',nodes=29)
  self.assertLess(s['conditional_full_old_radiation_vs_massive_delta_ratio_endpoint'],0.)
  self.assertLess(abs(s['conditional_full_old_radiation_vs_massive_delta_ratio_endpoint']),.05)
 def test_manufactured_two_axis_quadrature_refinement(self):
  r=refinement()['table']
  self.assertGreater(r[0]['delta_abs_err'],r[1]['delta_abs_err'])
  self.assertLess(r[7]['delta_abs_err'],1e-8)
  self.assertLess(r[9]['delta_abs_err'],1e-12)
 def test_existing_old_Omega_r_fraction_zero_reduces_to_pr169(self):
  for m in (3.,30.,300.):
   p=integrate(m,0.)
   self.assertLess(np.max(abs(p.b_per_A-p.b_shear_from_matter_only)),2e-13)
 def test_free_stream_radiation_damps_massive_forced_shear(self):
  for m in (3.,30.,300.):
   p=integrate(m,1.)
   self.assertGreater(p.b_per_A[-1],0.)
   self.assertLess(p.b_per_A[-1],p.b_shear_from_matter_only[-1])
   self.assertLess(p.universal_q_bound,.2)
 def test_continuous_gamma_strength_changes_smoothly(self):
  p=[integrate(3.,g).b_per_A[-1] for g in (0.,.2,.5,1.)]
  self.assertTrue(np.all(np.diff(p)<0.))
 def test_gamma_source_fraction_domain(self):
  with self.assertRaises(ValueError): integrate(3.,-1e-6)
  with self.assertRaises(ValueError): integrate(3.,1.0001)
 def test_universal_contraction_bound_is_small(self):
  self.assertEqual(gamma_contraction_bound(0.,.1),0.)
  self.assertGreater(gamma_contraction_bound(1.,.1),0.)
  self.assertLess(gamma_contraction_bound(1.,.1),.01)

if __name__=='__main__':unittest.main()
