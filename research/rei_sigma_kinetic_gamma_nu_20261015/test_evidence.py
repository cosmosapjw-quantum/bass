"""Machine-evidence and original-REI-native-bridge data integrity for joint kinetic background."""
from __future__ import annotations
import csv,json,math,hashlib,pathlib,sys,unittest
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from joint_kinetic import source_lock,REI_SOURCE_SHA,verify_original_sources
from run_joint import HEADERS

class JointKineticEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.table=HERE/"evidence/JOINT_CAMPAIGN/REI_GAMMANU_MASSIVE_BACKGROUND.csv"
    cls.result=json.loads((cls.table.parent/"RESULTS.json").read_text())
    cls.native=json.loads((HERE/"evidence/NATIVE_RUST_BRIDGE.json").read_text())
    cls.bench=json.loads((HERE/"evidence/BENCHMARK_REAL.json").read_text())
    with cls.table.open() as f:cls.rows=list(csv.DictReader(f))

 def test_original_canonical_rei_cosmology_and_SOURCE_BYTES(self):
    self.assertEqual(source_lock().omega_r,9.2e-5)
    self.assertIn("source",verify_original_sources()["cosmology"])
    self.assertEqual(self.result["source_parent_BASS_head"],
       "9e50f936f3289cb0c7c8127772cf9fb8d172d7a8")
    self.assertEqual(self.result["source_parent_REI_head"],
       "5d41df647c4fd624d8a1b574f67fdd0b82ff5102")

 def test_source_csv_sha_and_8_401_history_rows(self):
    self.assertEqual(hashlib.sha256(self.table.read_bytes()).hexdigest(),
                     self.result["csv_sha256"])
    self.assertEqual(len(self.rows),8*401)
    self.assertEqual(self.result["n_rows"],len(self.rows))
    self.assertEqual(len(self.result["case_receipts"]),8)
    self.assertEqual(tuple(self.rows[0].keys()),HEADERS)

 def test_per_case_source_clock_positive_and_initial_same(self):
    for i in range(8):
        sl=self.rows[i*401:(i+1)*401]
        self.assertEqual(float(sl[0]["proper_elapsed_s"]),0.)
        self.assertEqual(float(sl[0]["b"]),0.)
        self.assertAlmostEqual(float(sl[-1]["a"]),.2,delta=1e-14)
        times=np.array([float(r["proper_elapsed_s"]) for r in sl])
        self.assertTrue(np.all(np.diff(times)>0))

 def test_gamma_and_neutrino_numbers_are_separate(self):
    for j in range(0,len(self.rows),41):
        z=self.rows[j]
        self.assertLess(abs(float(z["gamma_number_N0"])-1),1e-11)
        self.assertLess(abs(float(z["nu_number_N0"])-1),1e-11)
        self.assertGreater(float(z["radiation_rho_J_m3"]),0)

 def test_native_real_Rust_geometry_Hamiltonian_and_sigma(self):
    n=self.native["physical_checker_output"]
    self.assertEqual(n["rows"],3208)
    self.assertEqual(n["cases"],8)
    self.assertLess(n["max_constraint_relative"],4e-13)
    self.assertLess(n["max_sigma_absolute"],1e-13)
    self.assertEqual(self.native["cargo_positive_exit_code"],0)

 def test_native_rejects_four_physically_corrupted_sources(self):
    xs={e["mutated_field"]:e for e in self.native["negative_inputs"]}
    self.assertEqual(set(xs),{"H_mean_per_s","pi_massive_J_m3","Sigma","gamma_number_N0"})
    for e in xs.values():
        self.assertEqual(e["exit_code"],3)
        self.assertTrue(e["rejection"].startswith("AXBI_JOINT_KINETIC_REJECT:"))

 def test_actual_AX08_zero_source_constrained_to_one_way(self):
    d=self.result["actual_one_way_AX08_electron_donor"]
    self.assertEqual(d["original_real_AX08_rows"],312238)
    self.assertEqual(len(d["original_real_AX08_ZERO_history_sha256"]),64)
    self.assertFalse(d["native_HHe_end_to_end_coupled"])
    self.assertGreater(d["max_relative_saved_source_interpolation_error"],0)
    self.assertLess(d["max_relative_saved_source_interpolation_error"],3e-4)

 def test_matter_initial_stress_is_independent_of_sigma(self):
    e={x["case"]:x for x in self.result["case_receipts"]}
    q=e["BOTH_PRIMORDIAL"]["initial_Pi"]
    self.assertEqual(q["Sigma_ref"],0.)
    self.assertGreater(q["massive_Pi_J_m3"],0)
    self.assertGreater(e["MASSIVE_ONLY"]["Sigma_end"],0)
    self.assertGreater(e["BOTH_PRIMORDIAL"]["Sigma_end"],e["RADIATION_ONLY"]["Sigma_end"])
    self.assertLess(e["BOTH_THOMSON_AX08"]["Sigma_end"],e["BOTH_PRIMORDIAL"]["Sigma_end"])

 def test_native_does_not_claim_real_end_to_end_chemistry(self):
    self.assertFalse(self.native["actual_native_chemistry_Einstein_solver_modified"])
    self.assertEqual(self.result["scientific_admission"],"BACKGROUND_RESEARCH_ONLY")
    self.assertEqual(self.result["full_polarized_photon_Thomson"],"NOT_IMPLEMENTED")

 def test_real_process_parallel_outputs_and_performance_finite(self):
    b=self.bench
    self.assertEqual(b["n_cases"],12)
    self.assertEqual(len(b["process"]),2)
    self.assertLess(b["process"][1]["max_abs_endpoint_disagreement_vs_single"],2e-13)
    self.assertGreater(b["process"][1]["speedup_vs_serial"],1)
    self.assertEqual(b["actual_scope"][:4],"same")

 def test_chunked_original_BASS_moment_precision_and_memory(self):
    b=self.bench["moment_1024"]["comparisons"]
    for n in b:
        self.assertLess(b[n]["max_abs_vs_chunked128"],3e-12)
    self.assertLess(b["chunked128_1024"]["tracemalloc_peak_bytes"],
                    b["full_array_1024"]["tracemalloc_peak_bytes"])
    self.assertLess(b["chunked64_1024"]["tracemalloc_peak_bytes"],
                    b["chunked128_1024"]["tracemalloc_peak_bytes"])

 def test_original_BASS_and_REI_limits_saved(self):
    z=json.loads((HERE/"evidence/SOURCE_REFINEMENT.json").read_text())
    for q in z["BASS_full_massive_and_massless_radiation_source_parity"]:
        self.assertLess(q["absolute_sigma_diff"],1e-11)
        self.assertLess(q["absolute_b_diff"],1e-11)
    self.assertLess(z["REI_original_gamma_nu_without_mass_source_limit"]["state_max_absolute_diff"],5e-12)
    self.assertLess(z["REI_original_gamma_nu_without_mass_source_limit"]["true_exact_physical_limiting_RHS"],1e-15)

 def test_finite_L_and_massive_angle_refinement_is_scoped(self):
    z=json.loads((HERE/"evidence/SOURCE_REFINEMENT.json").read_text())
    t=z["refinement"]
    self.assertEqual(len(t),4)
    self.assertEqual(t[-1]["ellmax"],12)
    self.assertLess(max(x["abs_Sigma_diff_vs_high"] for x in t),2e-12)
    self.assertIsNone(z["fully_selfconsistent_HHe_chemistry"])

 def test_actual_native_pi_tensor_signed_zero(self):
    data=self.result["case_receipts"]
    for v in data:
        z=v["initial_Pi"]["pi_tensor_diag_J_m3"]
        self.assertLess(abs(sum(z)),5e-20)
        self.assertGreater(v["minimum_angular_brightness_sampled"],0)

 def test_native_xact_exact_8_zeros(self):
    p=HERE/"evidence/XACT_JOINT.json"
    r=json.loads(p.read_text())
    self.assertTrue(r["all_zero"])
    self.assertEqual(len(r["checks"]),8)
    self.assertTrue(all(s=="0" for s in r["checks"].values()))

if __name__=="__main__":unittest.main(verbosity=2)
