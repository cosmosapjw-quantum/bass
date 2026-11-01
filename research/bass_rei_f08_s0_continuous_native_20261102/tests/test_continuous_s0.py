import csv,gzip,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import audit_continuous as A
from continuous_s0 import SCHEMA,solve,INITIAL_COUNT,source_packets,temperature

class ContinuousS0(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.summary=json.loads((ROOT/"results/RESULT.json").read_text())
  cls.rows=A.rows(ROOT/"results"/cls.summary["trajectory_file"])
  cls.diff=A.rows(ROOT/"results"/cls.summary["comparison_file"])
  cls.data={(q["branch"],q["model"],int(q["step"])):q for q in cls.rows}
  cls.owner={n:A.load_original(n) for n in ("S0_BI","S0_FLRW")}

 def test_original_rust_and_hhe_sha67(self):
  self.assertEqual(A.original_source_locks(),[12,51,4])

 def test_model_units_and_scientific_bound(self):
  self.assertEqual(self.summary["schema"],SCHEMA)
  self.assertEqual(self.summary["steps_per_model"],160)
  self.assertFalse(self.summary["new_canonical_nodes"])
  self.assertEqual(self.summary["REI_CENTRAL"],"28/88_REPORTED")
  self.assertEqual(self.summary["BASS_UPPER"],"9/15_SCOPED_SOURCE_MAPPED")
  self.assertEqual(self.summary["original_F08_scientific_admission"],"HOLD")
  self.assertEqual(self.summary["production"],"HOLD")

 def test_actual_640_consecutive_source_matter_states(self):
  self.assertEqual(len(self.rows),640)
  self.assertEqual(self.summary["actual_original_native_gas_chemistry_steps"],640)
  for b in ("S0_BI","S0_FLRW"):
   for m in ("CHARACTERISTIC","ORIGINAL_HAT"):
    self.assertEqual(sorted(k[2] for k in self.data if k[:2]==(b,m)),list(range(1,161)))

 def test_320_paired_causal_comparisons(self):
  self.assertEqual(len(self.diff),320)
  self.assertEqual({x["branch"] for x in self.diff},{"S0_BI","S0_FLRW"})
  for q in self.diff:
   k=(q["branch"],int(q["step"]))
   a,b=self.data[k[0],"CHARACTERISTIC",k[1]],self.data[k[0],"ORIGINAL_HAT",k[1]]
   self.assertAlmostEqual(float(q["delta_xHII"]),float(a["xHII"])-float(b["xHII"]),delta=3e-14)

 def test_frozen_parent_no_stepping_return(self):
  for b in ("S0_BI","S0_FLRW"):
   for m in ("CHARACTERISTIC","ORIGINAL_HAT"):
    old=.9
    for step in range(1,161):
     r=self.data[b,m,step]
     nx=float(r["xHII"])
     expected=old+float(r["stage_HI_photo_per_H"])+float(r["stage_HI_collision_per_H"])-float(r["stage_HI_recombination_per_H"])
     self.assertLess(abs(expected-nx),5e-13)
     old=nx

 def test_global_HHe_photon_and_energy_ledger(self):
  for r in self.rows:
   self.assertLess(abs(float(r["cumulative_photon_count_residual_per_H"])),1e-12)
   self.assertLess(abs(float(r["cumulative_total_energy_residual_ev_per_H"])),6e-12)
   self.assertLess(float(r["stage_native_residual"]),1e-15)
   self.assertLess(int(r["stage_native_root_iterations"]),201)

 def test_source_photon_support_vs_original_hat(self):
  for b in ("S0_BI","S0_FLRW"):
   for t in (1,8,64,160):
    self.assertLessEqual(float(self.data[b,"CHARACTERISTIC",t]["below_exact_support_N_per_H"]),1e-18)
    self.assertGreater(float(self.data[b,"ORIGINAL_HAT",t]["below_exact_support_N_per_H"]),0.)

 def test_helium_fraction_and_thermal_domain(self):
  for r in self.rows:
   HII,HeII,HeIII=[float(r[x]) for x in ("xHII","xHeII","xHeIII")]
   self.assertTrue(0<HII<1 and 0<HeII<1 and 0<HeIII<1)
   self.assertLess(HeII+HeIII,1)
   self.assertTrue(30000<float(r["T_K"])<110000)
   self.assertAlmostEqual(temperature((HII,HeII,HeIII),float(r["w_ev_per_H"])),float(r["T_K"]),delta=2e-7)

 def test_actual_S0_source_0to160_count(self):
  for r in self.rows:
   t=float(r["proper_t_s"])
   born=.05+5e-15*t
   N=float(r["N_photons_per_H"])
   A=float(r["HI_He_photo_absorbed_cumulative_per_H"])
   self.assertAlmostEqual(N+A,born,delta=1e-12)

 def test_original_source_owner_reference_snapshots(self):
  for b in ("S0_BI","S0_FLRW"):
   for step in (1,8,32,64,160):
    r=self.data[b,"CHARACTERISTIC",step]
    v=self.owner[b][step-1]
    self.assertEqual(float(r["original_F08_xHII"]),float(v["x_HII"]))
    self.assertAlmostEqual(float(r["original_F08_T_K"]),float(v["temperature_K"]),delta=1e-10)

 def test_first_step_equal_to_inherited_native_one_step_source(self):
  p=ROOT.parent/"bass_rei_f08_native_hhe_firststage_20261101"/"results/native_stage.csv"
  with p.open() as f: lines=list(csv.DictReader(f))
  for b in ("S0_BI","S0_FLRW"):
   old=next(r for r in lines if r["branch"]==b and r["tick"]=="0" and r["model"]=="CHARACTERISTIC")
   now=self.data[b,"CHARACTERISTIC",1]
   self.assertAlmostEqual(float(old["xHII_after"]),float(now["xHII"]),delta=4e-15)
   self.assertAlmostEqual(float(old["T_after_K"]),float(now["T_K"]),delta=2e-8)

 def test_nonzero_160_step_HII_and_temperature_response(self):
  r=next(x for x in self.diff if x["branch"]=="S0_BI" and x["step"]=="160")
  self.assertGreater(float(r["delta_xHII"]),3.0e-6)
  self.assertLess(float(r["delta_T_K"]),-0.07)
  self.assertLess(float(r["delta_photon_n_per_H"]),0.)

 def test_prefix64_readback_when_present(self):
  prefix=ROOT/"results_prefix64/RESULT.json"
  if not prefix.is_file():self.skipTest("prefix control not generated")
  report=A.audit(ROOT/"results",check_prefix=True)
  self.assertTrue(report["prefix"]["ran"])
  self.assertEqual(report["prefix"]["rows"],256)

 def test_original_nonacceptance_and_bounded_horizon(self):
  self.assertEqual(self.summary["owner_full_F08_RK_MPRK_interval_root"],"NOT_REPLAYED")
  with self.assertRaises(ValueError):
   solve(161,ROOT/"impossible",Path("/tmp/noexe"))

if __name__=="__main__":unittest.main()
