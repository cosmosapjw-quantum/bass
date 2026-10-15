"""Targeted C9 hostile review and source-equivalence tests.

An independent binary64 dyadic reference is used for reduction: tests check
the *operation graph*, not merely agreement between two float64 solvers.
"""
from __future__ import annotations
import json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import deterministic_reducer as d
import spectral_cert as c
import aggregation_roundoff as old
import batch_transport as b
import stokes_vector as s

class C9Adversarial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b.verify()
        cls.result,cls.state,cls.wray,cls.wenergy=d.actual_fa03_reduction(
            eps=[-.1,0,.1],nr=3,nphi=12,steps=64,ne=4,return_inputs=True)

    def test_frozen_physics_source_sha(self):
        self.assertEqual(b.verify(),c.source_lock())
        self.assertEqual(c.B_TRACE_BOUND,F(41931,10000))

    def test_exact_binary64_three_factor_counterexample(self):
        x=d.triple_product_witness()
        self.assertTrue(x["old_claim_refuted"])
        self.assertGreater(x["relative_rounding_error_over_unit_u"],1.0)
        self.assertLess(x["relative_rounding_error_over_unit_u"],2.0)
        self.assertLess(x["ray_weight"],1)
        self.assertLess(x["energy_weight"],1)
        self.assertLess(x["stokes_sample"],1)

    def test_old_gamma_one_failure_reproduced(self):
        # The inherited old gamma_N theorem cannot claim all triple-product
        # contractions for N=1. Two multiplications require 2u analysis.
        x=d.triple_product_witness()
        self.assertGreater(F(x["relative_rounding_error"]),old.gamma(1))
        self.assertLessEqual(F(x["relative_rounding_error"]),d.gamma(2))

    def test_pairwise_depth_and_gamma_correct(self):
        self.assertEqual(d.depth_for(1),0)
        self.assertEqual(d.depth_for(36*4),8)
        self.assertEqual(d.depth_for(480*4),11)
        self.assertEqual(d.gamma(0),0)
        self.assertGreater(d.gamma(13),d.gamma(12))
        with self.assertRaises(ValueError):d.gamma(2**53)

    def test_weight_sum_exact_96bit_rational(self):
        wx=d.exact_inputs_weight_mass(self.wray,self.wenergy)
        expected=sum((F.from_float(float(x)) for x in self.wray),F(0))*sum(
            (F.from_float(float(x)) for x in self.wenergy),F(0))
        self.assertEqual(wx,expected)
        self.assertLess(abs(float(wx)-1),1e-14)

    def test_exact_dyadic_tree_error_below_corrected_bound(self):
        q=d.pairwise_exact_gap(self.state,self.wray,self.wenergy)
        self.assertTrue(q["bound_covers_actual_executed_float"])
        self.assertLess(q["max_stokes_error_decimal"],1e-14)

    def test_pairwise_matches_old_original_spectral_output(self):
        q=d.actual_fa03_reduction(eps=[-.1,0,.1],nr=3,nphi=12,steps=64,ne=4)
        old_result=s.solve_energy_real([-.1,0,.1],nr=3,nphi=12,steps=64,ne=4,output="stokes")
        self.assertLess(np.max(abs(q-old_result)),1e-14)

    def test_pairwise_matches_ref_fa03_jones_in_tracenorm(self):
        q=d.actual_fa03_reduction(eps=[-.1,0,.1],nr=3,nphi=12,steps=64,ne=4)
        cc=s.stokes_to_coherency(q)
        for j,e in enumerate([-.1,0,.1]):
            reference=b.fa03.solve_energy(.008,.01,e,steps=64,nr=3,nphi=12,ne=4)
            self.assertLess(b.trace_norm(reference-cc[j]),3e-13)

    def test_independent_stokes_oracle_einsum_mathfsum_pairwise(self):
        for mode in ("pairwise","numpy_einsum","math_fsum"):
            q=d.actual_fa03_reduction(eps=[-.1,0,.1],nr=3,nphi=12,steps=32,ne=4,mode=mode)
            ref=s.solve_energy_real([-.1,0,.1],nr=3,nphi=12,steps=32,ne=4,output="stokes")
            self.assertLess(np.max(abs(q-ref)),1e-14)

    def test_pairwise_uneven_n_nonpow2(self):
        Y=np.arange(3*5*3*4,dtype=np.float64).reshape(3,5,3,4)/100
        ray=np.array([.1,.1,.2,.3,.3],np.float64)
        energy=np.array([.2,.6,.2],np.float64)
        got=d.pairwise_tensor_sum(Y,ray,energy)
        direct=np.einsum("n,e,mnek->mk",ray,energy,Y,optimize=True)
        self.assertLess(np.max(abs(got-direct)),1e-14)
        self.assertTrue(d.pairwise_exact_gap(Y,ray,energy)["bound_covers_actual_executed_float"])

    def test_negative_weights_rejected(self):
        for arr in [np.array([-1]+[1]*4,np.float64),np.array([np.nan]+[1]*4,np.float64)]:
            Y=np.ones((2,5,4,4),np.float64)
            with self.assertRaises(ValueError):
                d.pairwise_tensor_sum(Y,arr,np.ones(4))

    def test_wrong_shape_and_dtype_rejected(self):
        Y=np.ones((2,3,4,4),np.float64)
        with self.assertRaises(TypeError):d.pairwise_tensor_sum(Y.astype(np.float32),np.ones(3),np.ones(4))
        with self.assertRaises(ValueError):d.pairwise_tensor_sum(Y,np.ones(4),np.ones(4))
        with self.assertRaises(ValueError):d.pairwise_tensor_sum(Y,np.ones(3),np.ones(3))
        with self.assertRaises(ValueError):d.pairwise_tensor_sum(Y.reshape(6,4,4),np.ones(3),np.ones(4))

    def test_nan_inf_source_fails_closed(self):
        Y=np.ones((1,3,4,4),np.float64)
        Y[0,0,0,2]=np.inf
        with self.assertRaises(ValueError):d.pairwise_tensor_sum(Y,np.ones(3),np.ones(4))

    def test_exact_real_source_trace_bound_is_locked(self):
        phys=c.analytic_claims()
        self.assertEqual(phys["L_upper_rational"],"101/100")
        self.assertEqual(phys["min_real_part_absorption_factor"],"411/625")
        self.assertEqual(c.certificate(4),F(13977,488281250000000))

    def test_frozen_original_complex_stokes_rhs_equivalence(self):
        # independent source physics gate already in C7, sampled C9 selectively
        ell,w=b._prepared_rays(3,12)
        data=b.fa02.setup(ell,.008,.01)
        for x in (.5,.7,1.):
            P,H,G,k=b.fa03.fields(x,data)
            self.assertLess(np.max(abs(G+G.swapaxes(-1,-2)-2*H)),1e-14)

    def test_energy_bound_remains_separate_from_time_error(self):
        o=c.analytic_claims()
        self.assertIsNone(o["not_validated"]["time_RK4_global_error"])
        self.assertIsNone(o["not_validated"]["binary64_roundoff"])
        self.assertIsNone(o["not_validated"]["continuous_cap_angular_error"])

    def test_rounding_bound_stokes_not_rounded_coherency(self):
        q=d.scalar_bounds(self.state,self.wray,self.wenergy)
        self.assertIsNone(q["float_matrix_reconstruction_error"])
        self.assertIsNone(q["RK4_roundoff"])
        self.assertEqual(q["ops_per_term_upper"],2+d.depth_for(len(self.wray)*len(self.wenergy)))

    def test_exact_case_scaling_increased_weight_mass(self):
        Y=np.ones((1,1,1,4),np.float64)
        a=np.array([.5],np.float64)
        q=np.array([.25],np.float64)
        v=d.scalar_bounds(Y,a,q)
        self.assertEqual(v["input_weight_mass"],"1/8")
        self.assertEqual(v["ops_per_term_upper"],2)

    def test_error_reducer_method_validation(self):
        with self.assertRaisesRegex(ValueError,"unknown explicit"):
            d.actual_fa03_reduction(mode="not_implemented")
        with self.assertRaises(ValueError):d.actual_fa03_reduction(eps=[.11])
        with self.assertRaises(ValueError):d.actual_fa03_reduction(steps=0)

    def test_target_model_has_source_nonzero_polarization(self):
        a=d.actual_fa03_reduction(eps=[0],steps=32,ne=4)
        I,Q,U,V=a[0]
        self.assertGreater(I,0)
        self.assertGreater(abs(Q)+abs(U)+abs(V),0)
        self.assertGreater(I*I-Q*Q-U*U-V*V,0)

    def test_pairwise_thread_parallel_exact_same_outputs(self):
        for q in [1,2,3]:
            trial=d.pairwise_parallel_by_epsilon(self.state,self.wray,self.wenergy,workers=q)
            self.assertTrue(np.array_equal(trial,self.result))
        with self.assertRaises(ValueError):
            d.pairwise_parallel_by_epsilon(self.state,self.wray,self.wenergy,workers=0)

    def test_parallel_timing_no_false_speedup_claim(self):
        obj=json.loads((HERE/"evidence/PARALLEL_C9.json").read_text())
        self.assertIsNone(obj["whole_solver_thread_speedup_claim"])
        for r in obj["rows"]:
            self.assertTrue(r["exact_array_equal_to_serial"])
            self.assertGreater(r["median_s"],0)

    def test_independent_mp_spectral_oracle_is_scoped_and_safe(self):
        o=json.loads((HERE/"evidence/SPECTRAL_ORACLE.json").read_text())
        self.assertEqual(len(o["runs"]),3)
        for run in o["runs"]:
            self.assertEqual(run["dps"],70)
            self.assertIsNone(run["full_FA03_time_RK4_numeric_certification"])
            for row in run["rows"]:
                self.assertTrue(row["subtheorem_pass"])
                self.assertLess(float(row["true_GL_error_trace_norm"]),
                                float(row["C8_derived_upper"]))

    def test_binary64_reconstructed_polarization_remains_physical(self):
        original=d.actual_fa03_reduction(ne=4,steps=64)
        stokes_out=s.stokes_to_coherency(original)
        for matrix in stokes_out:
            self.assertLess(np.max(abs(matrix-matrix.conj().T)),1e-15)
            self.assertGreater(np.linalg.eigvalsh(matrix).min(),.12)

if __name__=="__main__":
    unittest.main(verbosity=2)
