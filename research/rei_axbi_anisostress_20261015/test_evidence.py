"""C5/C7 actual source execution evidence gates for pi background supplier."""
from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
EV=HERE/"evidence"

class SourceEvidence(unittest.TestCase):
    def test_independent_Rust_8_cases(self):
        p=json.loads((EV/"RUST_NATIVE_PARITY.json").read_text())
        self.assertEqual(p["n_positive_source_cases"],8)
        self.assertEqual(p["native_actual_rustc_exit_code"],0)
        self.assertLess(p["max_absolute_b_difference"],1e-11)
        self.assertLess(p["max_absolute_s_over_H_difference"],1e-11)
        self.assertLess(p["max_relative_proper_time_difference"],1e-10)
    def test_native_REI_typed_backgroundpoint_bridge(self):
        p=json.loads((EV/"REI_RUST_BRIDGE.json").read_text())
        self.assertEqual(p["rows"],8517)
        self.assertEqual(p["reconstructed_original_geometry"],8517)
        self.assertEqual(p["original_stressfree_Rust_samples"],5)
        self.assertLess(p["max_H_rel"],1e-13)
        self.assertLess(p["max_b_abs"],1e-11)
        self.assertFalse(p["production_driver_replaced"])
    def test_native_consumer_real_positive_negative(self):
        j=json.loads((EV/"NATIVE_CSV_NEGATIVE.json").read_text())
        self.assertEqual(j["positive_returncode"],0)
        self.assertEqual(j["positive"]["rows"],8517)
        self.assertEqual(j["negative_H_returncode"],3)
        self.assertIn("NATIVE_EINSTEIN_HAMILTONIAN",j["negative_H"])
        self.assertEqual(j["negative_pi_returncode"],3)
        self.assertIn("PI_TRACE_NONZERO",j["negative_pi"])
        self.assertTrue(j["positive_input_unchanged"])
    def test_exact_xact_pi_shear_contraction(self):
        x=json.loads((EV/"XACT_STRESS.json").read_text())
        self.assertTrue(x["all_exact_zero"])
        self.assertEqual(len(x["residuals"]),8)
        self.assertTrue(all(q=="0" for q in x["residuals"].values()))
    def test_timed_vectorization_and_nonpromoted_threads(self):
        z=json.loads((EV/"BENCHMARK_CPU.json").read_text())
        self.assertIsNone(z["native_AX08_coupled_science_solver_speedup"])
        m=z["moment_loop"]
        self.assertGreater(m["vector_speedup"],10)
        self.assertGreater(m["chunked_speedup"],10)
        self.assertLess(m["tracemalloc_chunked_bytes"],m["tracemalloc_vector_bytes"]/2)
        self.assertLess(m["max_abs_chunk_disagreement"],2e-14)
        p={x["threads"]:x for x in z["separate_17_case_ODE_solves"]}
        self.assertEqual(set(p),{1,2,4})
        self.assertGreater(p[2]["median_seconds"],p[1]["median_seconds"])
    def test_frozen_input_table_Jacobian_publication(self):
        import sys
        sys.path.insert(0,str(HERE))
        import einstein_vlasov_lrs as e
        j=json.loads((EV/"AX03_INITIAL_PI_TABLES/AX03_INITIAL_PI_CONTRACT.json").read_text())
        self.assertEqual(j["original_AX03_lock_sha256"],e.LOCK_SHA)
        self.assertEqual(j["case_count"],17)
        self.assertEqual(j["trajectory_rows"],8517)
        self.assertEqual(j["ray_rows"],8585)
        for f,hash_ in j["SHA256"].items():
            self.assertEqual(hashlib.sha256((EV/"AX03_INITIAL_PI_TABLES"/f).read_bytes()).hexdigest(),hash_)
    def test_scientific_scope_not_full_EOR(self):
        j=json.loads((EV/"AX03_INITIAL_PI_TABLES/AX03_INITIAL_PI_CONTRACT.json").read_text())
        self.assertEqual(j["scientific_admission"],"BACKGROUND_ONLY_EXPLORATORY_NO_OBSERVED_EOR")
        self.assertEqual(j["assumptions"]["collisionless_radiation_backreaction"],"SELF_CONSISTENT_UNDER_THIS_INITIAL_DISTRIBUTION")
        self.assertEqual(j["assumptions"]["full_CMB_neutrino_and_ionizing_stress"],"NOT_MODELLED_FULLY")
if __name__=="__main__":unittest.main(verbosity=2)
