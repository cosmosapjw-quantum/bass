"""Targeted C5 tests for actual FA03 cap code path, not a science gate."""
import hashlib
import json
import math
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import angular_sweep as m
import numpy as np


class CapC5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ell,cls.w=m.cap_nodes(3,12)
        cls.y64=m.solve_six_at_nodes(cls.ell,cls.w,64)
        cls.y128=m.solve_six_at_nodes(cls.ell,cls.w,128)

    def test_immutable_reference_source_identity(self):
        self.assertEqual(m.verify_source_lock(),m.SOURCE_LOCKS)

    def test_tampered_source_hash_rejected(self):
        x=dict(m.SOURCE_LOCKS)
        x["fa02.py"]="0"*64
        with patch.object(m,"SOURCE_LOCKS",x):
            with self.assertRaisesRegex(RuntimeError,"SOURCE_IDENTITY_MISMATCH"):
                m.verify_source_lock()

    def test_default_cap_nodes_equal_frozen_fa02(self):
        a,b=m.fa02.cap_nodes(.02,3,12)
        self.assertTrue(np.array_equal(self.ell,a))
        self.assertTrue(np.array_equal(self.w,b))

    def test_normalized_cap_exact_first_two_moments(self):
        for nr,nphi in ((2,8),(3,12),(6,24)):
            ell,w=m.cap_nodes(nr,nphi)
            vals=m.geometric_checks(ell,w)
            self.assertTrue((w>0).all())
            self.assertLess(abs(vals["sum_weights"]-1),3e-15)
            self.assertLess(abs(vals["cos_theta_first_moment"]-vals["cos_theta_first_exact"]),3e-15)
            self.assertLess(abs(vals["cos_theta_second_moment"]-vals["cos_theta_second_exact"]),3e-15)
            self.assertGreater(vals["min_sqrt_1_minus_m_y_squared"],.9)

    def test_emitter_nontrivial_angular_structure(self):
        f,_,_,_=m.fa03.fields(.7,m.fa02.setup(self.ell,.008,.01))
        self.assertGreater(float(np.ptp(f[:,0,0].real)),1e-4)

    def test_actual_r7_reference_matches_64_step_rk4(self):
        saved=m.r7_fixed_reference()
        self.assertEqual(saved["rays"],36)
        self.assertEqual(saved["cells_per_ray"],64)
        diff=max(float(np.max(abs(m.stokes(a)-np.array(b))))
                 for a,b in zip(self.y64,saved["reference_stokes_display"]))
        self.assertLess(diff,2e-15)

    def test_parent_gl3x12_six_state_integrator_equivalence(self):
        same=m.fa03.solve_moments(.008,.01,steps=64,nr=3,nphi=12)
        self.assertLess(max(m.trnorm(a-b) for a,b in zip(self.y64,same)),2e-15)

    def test_hermiticity_of_six_states(self):
        for v in self.y128:
            self.assertLess(float(np.linalg.norm(v-v.conj().T)),2e-14)

    def test_theta_quadrature_empirical_does_not_pretend_certificate(self):
        r=m.run_study(steps=64,grids=((3,12),(6,24)),energy_ne=(4,8))
        self.assertIsNone(r["fixed_detector"]["rigorous_continuum_angular_error"])
        self.assertFalse(r["grid_records"][1]["numerical_angular_error_certified"])
        self.assertGreater(r["grid_records"][1]["source_span_at_x_point7"],1e-4)

    def test_rotated_phi_grid_is_same_integral_within_empirical_error(self):
        ell,w=m.cap_nodes(3,12,phase=.37)
        shifted=m.solve_six_at_nodes(ell,w,64)
        self.assertLess(max(m.trnorm(a-b) for a,b in zip(shifted,self.y64)),1e-13)

    def test_angular_change_smaller_than_temporal_64_vs128(self):
        ell,w=m.cap_nodes(6,24)
        larger=m.solve_six_at_nodes(ell,w,64)
        ang=max(m.trnorm(a-b) for a,b in zip(larger,self.y64))
        time=max(m.trnorm(a-b) for a,b in zip(self.y64,self.y128))
        self.assertLess(ang,1e-13)
        self.assertGreater(time,1e-13)
        self.assertLess(ang,time)

    def test_finite_epsilon_zero_resolves_moments(self):
        E=m.energy_solve_at_nodes(self.ell,self.w,0,64,8)
        self.assertLess(m.trnorm(E-self.y64[0]),1e-13)

    def test_finite_non_grey_is_hermitian_and_psd(self):
        for eps in (-.1,.1):
            E=m.energy_solve_at_nodes(self.ell,self.w,eps,64,8)
            self.assertLess(float(np.linalg.norm(E-E.conj().T)),1e-12)
            self.assertGreater(float(np.linalg.eigvalsh(E).min()),.12)
            P=m.polynomial(self.y64,eps)
            self.assertLess(m.trnorm(E-P),1e-5)

    def test_total_reference_holds_exact_angular_only(self):
        cert=m.r7_fixed_reference()
        self.assertIsNone(cert["angular_continuum_error"])
        self.assertIsNone(cert["empirical_provider_error"])
        self.assertEqual(cert["reference_sha256"],
            "bf1141893d81825daa2acbfcfc74325fb6c8a124e3869003ef4f1f7b81339f42")

    def test_input_contract(self):
        for x in ((0,12),(3,0),(-2,8),(3,7)):
            with self.assertRaises(ValueError):
                m.cap_nodes(*x)
        with self.assertRaises(ValueError):
            m.cap_nodes(3,12,delta=0)
        with self.assertRaises(ValueError):
            m.cap_nodes(3,12,delta=.03)
        with self.assertRaises(ValueError):
            m.solve_six_at_nodes(self.ell,self.w,0)
        with self.assertRaises(ValueError):
            m.energy_solve_at_nodes(self.ell,self.w,.2,64,8)
        with self.assertRaises(ValueError):
            m.run_study(steps=32)

if __name__=="__main__":
    unittest.main(verbosity=2)
