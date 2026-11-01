"""Original source-pinned REI Rust native H/He stage response acceptance tests."""
from pathlib import Path
import csv,gzip,json,math,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import audit_native_coupling as audit

def open_csv(path):
 with Path(path).open("rt",newline="") as f:return list(csv.DictReader(f))

class CoupledNativeSourceScience(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.native=open_csv(ROOT/"results/native_stage.csv")
  cls.paired=cls.native_index={(x["branch"],int(x["tick"]),x["model"]):x for x in cls.native}
  cls.summary=json.loads((ROOT/"results/RESULT.json").read_text())
  with gzip.open(ROOT/"results"/cls.summary["physical_response_file"],"rt",newline="") as f:
   cls.response=list(csv.DictReader(f))
  cls.prov=json.loads((ROOT/"inputs/STAGE_INPUT_PROVENANCE.json").read_text())
  cls.high=open_csv(ROOT/"results/native_high_stage.csv")
  cls.highindex={(x["branch"],int(x["tick"]),x["model"]):x for x in cls.high}
  cls.source= audit.source_reference()

 def test_scientific_source_owner_51_and_F08_12_plus4_sha(self):
  self.assertEqual(audit.load_originals(),51)
  self.assertEqual(len(self.source["S0_BI"]),16000)
  self.assertEqual(len(self.source["S0_FLRW"]),16000)

 def test_native_Rust_run_real_20_scenario_records(self):
  self.assertEqual(len(self.native),20)
  self.assertEqual(len(self.native_index),20)
  self.assertEqual(len(self.response),10)
  self.assertEqual(len(self.high),12)
  self.assertEqual(self.summary["paired_physics_rows"],10)

 def test_real_source_provenance_bytes_and_time(self):
  self.assertEqual(self.prov["stage_input_sha256"],audit.digest(ROOT/"inputs/native_stage_cases.txt"))
  self.assertEqual(self.prov["original_ticks"],[0,800,1600,6400,15999])
  self.assertEqual(self.prov["source_parent_head"],"c0e965ba21892346feef9ecb2389932c34f3fc82")
  self.assertEqual(len(self.prov["cases"]),20)
  self.assertEqual(self.prov["birth_gauss_nodes"],128)

 def test_native_source_same_original_material_parent_pair(self):
  for b in audit.BKG:
   for tick in audit.TICKS:
    m=self.native_index[(b,tick,"CHARACTERISTIC")]
    f=self.native_index[(b,tick,"ORIGINAL_HAT_FROZEN_HI")]
    for key in ("t_s","dt_s","nH_cm3","T_before_K"):
     self.assertEqual(float(m[key]),float(f[key]),(b,tick,key))
    self.assertEqual(float(m["dt_s"]),625000000.)
    if tick>0:
     self.assertAlmostEqual(float(m["T_before_K"]),float(self.source[b][tick-1]["temperature_K"]),delta=5e-7)

 def test_native_original_chemical_HI_budget(self):
  for r in self.native:
   d=(float(r["dxHII"])-float(r["HI_abs_per_H"])
       -float(r["HI_collision_per_H"])+float(r["HI_recombination_per_H"]))
   self.assertLess(abs(d),4e-15)

 def test_native_original_photon_and_total_energy_conservation(self):
  for r in self.native:
   before=float(r["N_before_per_H"])
   after=float(r["N_after_per_H"])
   taken=sum(float(r[x]) for x in ("HI_abs_per_H","HeI_abs_per_H","HeII_abs_per_H"))
   self.assertLess(abs(before-after-taken),2e-13)
   self.assertLess(abs(float(r["photon_count_residual"])),2e-13)
   self.assertLess(abs(float(r["energy_residual_ev_per_H"])),8e-13)
   self.assertLess(float(r["stage_residual"]),1e-14)
   self.assertLessEqual(int(r["iterations"]),200)

 def test_native_helium_and_temperature_physical(self):
  for r in self.native:
   s=[float(r[k]) for k in ("xHII_after","xHeII_after","xHeIII_after")]
   self.assertTrue(all(0<=v<=1 for v in s))
   self.assertLessEqual(s[1]+s[2],1+1e-12)
   self.assertGreater(float(r["T_after_K"]),30000)
   self.assertLess(float(r["T_after_K"]),110000)

 def test_real_BI_native_firststage_finite_response(self):
  p={(r["branch"],int(r["original_parent_tick"])):r for r in self.response}
  self.assertGreater(float(p["S0_BI",800]["delta_HII_native_coupled"]),5e-6)
  self.assertLess(float(p["S0_BI",1600]["delta_HII_native_coupled"]),-1e-6)
  self.assertLess(float(p["S0_BI",800]["delta_T_after_K"]),-.1)
  self.assertGreater(float(p["S0_BI",1600]["delta_T_after_K"]),.02)
  self.assertGreater(float(p["S0_BI",6400]["delta_HII_native_coupled"]),0)

 def test_FLRW_Bianchi_at_initial_is_same_limit(self):
  for m in ("CHARACTERISTIC","ORIGINAL_HAT_FROZEN_HI"):
   a=self.native_index["S0_BI",0,m]
   b=self.native_index["S0_FLRW",0,m]
   self.assertAlmostEqual(float(a["dxHII"]),float(b["dxHII"]),delta=5e-15)
   self.assertAlmostEqual(float(a["T_after_K"]),float(b["T_after_K"]),delta=5e-8)

 def test_exact_characteristic_has_no_disallowed_photons(self):
  for r in self.native:
   if r["model"]=="CHARACTERISTIC":
    self.assertLess(float(r["below_physical_support_N_per_H"]),1e-18)
  self.assertGreater(float(self.native_index["S0_BI",0,"ORIGINAL_HAT_FROZEN_HI"]["below_physical_support_N_per_H"]),1.7e-4)

 def test_high_source_gl_quadrature_checks_signs(self):
  for b in audit.BKG:
   for tick in (800,1600,15999):
    a=self.native_index[b,tick,"CHARACTERISTIC"]
    h=self.highindex[b,tick,"CHARACTERISTIC"]
    x=self.highindex[b,tick,"ORIGINAL_HAT_FROZEN_HI"]
    initial_delta=(float(a["xHII_after"])-float(self.native_index[b,tick,"ORIGINAL_HAT_FROZEN_HI"]["xHII_after"]))
    revised_delta=float(h["xHII_after"])-float(x["xHII_after"])
    self.assertGreater(initial_delta*revised_delta,0)
    self.assertLess(abs(float(a["HI_gamma_in_s_inv"])/float(h["HI_gamma_in_s_inv"])-1),.02)

 def test_derived_physics_file_id_and_CI_gate(self):
  self.assertEqual(self.summary["schema"],audit.SCHEMA)
  self.assertEqual(self.summary["source_sensitivity_count"],6)
  self.assertEqual(audit.digest(ROOT/"results"/self.summary["physical_response_file"]),self.summary["physical_response_sha256"])
  self.assertEqual(self.summary["REI_CENTRAL"],"28/88_REPORTED")
  self.assertEqual(self.summary["BASS_UPPER"],"9/15_SCOPED_SOURCE_MAPPED")
  self.assertEqual(self.summary["canonical_delta"],0)
  self.assertEqual(self.summary["production"],"HOLD")
  self.assertEqual(self.summary["state_claim"],"NATIVE_OLD_RUST_HHE_COUPLED_ONE_STEP_EACH_PARENT_NOT_FULL_NEW_CONTINUOUS_IVP")

if __name__=="__main__":unittest.main()
