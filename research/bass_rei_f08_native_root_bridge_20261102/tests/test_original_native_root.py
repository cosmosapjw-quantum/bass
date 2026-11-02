"""Real source-native Krawczyk root and science scope tests."""
import csv,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import audit_native_root as AUDIT

class SourceRootTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.data=json.loads((ROOT/"results/RESULT.json").read_text())
    cls.raw=AUDIT.load_csv(ROOT/"results/ROOT_ALL.csv")
    cls.records=AUDIT.load_gz(ROOT/"results/SOURCE_S0_NATIVE_ROOT_PHYSICAL_SUPPORT.csv.gz")
    cls.by={(x["branch"],x["source_model"],int(x["source_step"])):x for x in cls.records}

 def test_original_rust_sha51_and_source12_and_checkpoint4(self):
    self.assertEqual(AUDIT.original_hashes(),{"original_source_sha256.txt":51,
            "ORIGIN_SHA256SUMS.txt":12,"LOCKED_CHECKPOINT_SHA256SUMS.txt":4})

 def test_actual_source_root_16_of_16(self):
    self.assertEqual(len(self.raw),16)
    self.assertEqual(len(self.records),16)
    self.assertEqual(self.data["root_pass"],16)
    self.assertEqual(self.data["root_failure"],0)
    for x in self.raw:
        self.assertEqual(x["root_status"],"PASS")
        self.assertEqual(x["root_error_code"],"NONE")

 def test_original_krawczyk_strict_contraction(self):
    for x in self.raw:
        q=float(x["root_q"])
        self.assertTrue(0<=q<1)
    self.assertLess(self.data["max_Krawczyk_q"],7e-15)

 def test_original_conservative_and_photon_enclosure(self):
    for x in self.raw:
        self.assertEqual(x["root_contains_conservative"],"true")
        self.assertEqual(x["photons_contain_conservative"],"true")
        self.assertLess(float(x["centre_vs_conservative_max_abs"]),5e-13)
        self.assertGreaterEqual(float(x["photon_sum_interval_width_per_H"]),0)

 def test_root_enclosure_widths_original_source(self):
    for x in self.raw:
        self.assertLess(float(x["root_max_relative_gas_width"]),1e-10)
        for f in ("root_width_xHII","root_width_xHeII","root_width_xHeIII","root_width_w_ev_per_H"):
            self.assertGreater(float(x[f]),0)

 def test_actual_real_source_photon_sample_count(self):
    self.assertEqual(self.data["actual_source_packet_records"],70656)
    self.assertEqual(sum(int(x["source_packet_count"]) for x in self.records),70656)
    self.assertEqual(int(self.by["S0_BI","CHARACTERISTIC",160]["source_packet_count"]),20608)
    self.assertEqual(int(self.by["S0_BI","ORIGINAL_HAT",160]["source_packet_count"]),1792)

 def test_real_Bianchi_source_krawczyk_first_and_final(self):
    first=self.by["S0_BI","CHARACTERISTIC",1]
    final=self.by["S0_BI","CHARACTERISTIC",160]
    self.assertAlmostEqual(float(first["native_source_Krawczyk_q"]),2.11157521047382453e-15,delta=1e-22)
    self.assertGreater(float(final["native_source_Krawczyk_q"]),float(first["native_source_Krawczyk_q"]))
    self.assertLess(float(final["native_source_Krawczyk_q"]),7e-15)

 def test_source_exact_characteristics_preserve_physical_support(self):
    for x in self.records:
        frac=float(x["below_physical_floor_fraction"])
        if x["source_model"]=="CHARACTERISTIC":
            self.assertEqual(frac,0.)
            self.assertEqual(float(x["photons_below_physical_floor_per_H"]),0.)
        else:
            self.assertGreater(frac,0.)

 def test_original_58_bi_and_flrw_limit_first(self):
    a=self.by["S0_BI","CHARACTERISTIC",1]
    b=self.by["S0_FLRW","CHARACTERISTIC",1]
    self.assertAlmostEqual(float(a["original_conservative_xHII"]),float(b["original_conservative_xHII"]),delta=3e-13)

 def test_scientific_claim_no_global_interval_promotion(self):
    self.assertEqual(self.data["root_input_parent_enclosure"],"EXACT_F64_POINT_NOT_GLOBAL_PROPAGATED_INTERVAL")
    self.assertEqual(self.data["original_interval_propagation"],"NOT_RUN")
    self.assertEqual(self.data["REI_CENTRAL"],"28/88_REPORTED")
    self.assertEqual(self.data["BASS_UPPER"],"9/15_SCOPED_SOURCE_MAPPED")
    self.assertEqual(self.data["new_canonical_nodes"],0)
    self.assertEqual(self.data["production"],"HOLD")

 def test_adversarial_negative_source_packet_rejected(self):
    self.assertEqual(self.data["negative_source_control"]["status"],"PASS_REJECTED_NEGATIVE_PACKET")
    self.assertNotEqual(self.data["negative_source_control"]["returncode"],0)

 def test_output_source_hashes_and_pr328_parity(self):
    self.assertEqual(self.data["source_capture_manifest_sha256"],
       AUDIT.sha(ROOT/"inputs/actual160/CAPTURE.json"))
    self.assertEqual(self.data["source_raw_root_sha256"],AUDIT.sha(ROOT/"results/ROOT_ALL.csv"))
    self.assertEqual(self.data["data_sha256"],
       AUDIT.sha(ROOT/"results/SOURCE_S0_NATIVE_ROOT_PHYSICAL_SUPPORT.csv.gz"))
    for k in ("xHII","xHeII","xHeIII","w","source_parent_HII","source_parent_w"):
        self.assertEqual(self.data["source_readback_errors_max"][k],0.)

if __name__=="__main__":unittest.main()
