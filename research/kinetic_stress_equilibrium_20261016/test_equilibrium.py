"""Focused standalone source-fidelity and strict convexity checks.
Full 20-test sandbox evidence and immutable parent source in release ZIP.
"""
import math,unittest
import numpy as np
from kinetic_equilibrium import FD96Equilibrium,XMAX

class TestRoot(unittest.TestCase):
  def test_fd96_original_norm(self):
    for m,n,v in [(3,8.107415001491976,.5245200752830639),
                  (30,54.478197513209125,.014042977688245466),
                  (300,540.9644879050254,.00014373652059454067)]:
      f=FD96Equilibrium(m)
      self.assertLess(abs(f.norm/n-1),1e-12)
      self.assertLess(abs(f.initial_v2/v-1),1e-12)

  def test_isotropic_zeros_and_positive_chi(self):
    for m in (3,30,300):
      f=FD96Equilibrium(m)
      for x in (0,.7,XMAX):
        self.assertEqual(f.stress(x,0,0).delta,0)
        self.assertEqual(f.equilibrium(x,0).b_star,0)
        self.assertLess(f.stress(x,0,0).chi_b,0)

  def test_stress_cone(self):
    for m in (3,30,300):
      f=FD96Equilibrium(m)
      for A in (-1,0,.5,2):
        for b in (-.3,0,.3):
          v=f.stress(.7,b,A)
          self.assertTrue(v.p_perp>=0 and v.p_parallel>=0)
          self.assertLessEqual(3*v.pbar,v.rho*(1+1e-12))
          self.assertLess(v.chi_b,0)
          self.assertGreater(v.delta_A,0)

  def test_root_unique_and_signed(self):
    for m in (3,30,300):
      f=FD96Equilibrium(m)
      last=-1e99
      for A in (-1,-.5,0,.5,2):
        v=f.equilibrium(.7,A)
        self.assertGreater(v.b_star,last)
        self.assertLess(abs(v.b_star),1)
        self.assertLess(abs(v.residual_delta)/v.rho_min,1e-12)
        last=v.b_star

  def test_isotropic_linear_bounds(self):
    for m in (3,30,300):
      f=FD96Equilibrium(m)
      for x in (0,.7,XMAX):
        slope,R=f.isotropic_slope(x)
        self.assertTrue(0<R<1 and .1<slope<.125)
        self.assertLess(abs(slope/f.equilibrium(x,0).db_dA-1),1e-12)

  def test_nr_limit(self):
    f=FD96Equilibrium(1e5)
    for A in (-1,-.5,.5,2):
      v=f.equilibrium(.7,A)
      self.assertLess(abs(v.b_star-v.b_nonrel),2e-8)

  def test_susceptibility_and_parameter_derivatives(self):
    for m in (3,30,300):
      f=FD96Equilibrium(m)
      for b,A in ((0,0),(.06,.5),(-.12,-.8)):
        h=2e-5
        fd=(f.stress(.7,b+h,A).delta-f.stress(.7,b-h,A).delta)/(2*h)
        self.assertLess(abs(fd/f.stress(.7,b,A).chi_b-1),6e-9)
      for A in (-.5,0,.5):
        h=1e-4
        fd=(f.equilibrium(.7,A+h).b_star-f.equilibrium(.7,A-h).b_star)/(2*h)
        self.assertLess(abs(fd/f.equilibrium(.7,A).db_dA-1),3e-8)

  def test_massive_pressure_direct_finite_shear(self):
    for m in (3,30,300):
      f=FD96Equilibrium(m)
      for A,b in ((-1,-.1),(.5,.12),(2,.18)):
        self.assertLess(abs(f.stress(.7,b,A).delta-f.stress_direct(.7,b,A)),3e-15)

  def test_domain_rejections(self):
    f=FD96Equilibrium(3)
    for x,b,A in ((0,1.1,0),(-.1,0,0),(0,0,2.1),(XMAX+1e-6,0,0)):
      with self.assertRaises(ValueError): f.stress(x,b,A)
    for m in (0,2.9,1e6):
      with self.assertRaises(ValueError): FD96Equilibrium(m)

if __name__=="__main__":unittest.main()
