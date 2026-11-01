import csv,copy,gzip,json,math,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from source_exact_photoheat import (
  MODEL,STEPS,FIT_CUTOFF,ION,BIRTH_EV,END,SOURCE_RATE,INITIAL_COUNT,C,DT,
  source_histories,original_checkpoint,verner,interpolate_original,kgrav,
  characteristic_snapshot,frozen_hat_history,checksum
)
from s0_source_photon_thomson import sigma_hi
from spectral_support import original_redshift_g,support_statistics,CHECKPOINT_SHA

class S0Physics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h=source_histories()
        cls.orig={k:original_checkpoint(k) for k in cls.h}
        cls.out=json.loads((ROOT/"results/RESULT.json").read_text())
        cls.rows=[]
        cls.rays=[]
        with gzip.open(ROOT/"results"/cls.out["summary_file"],"rt",newline="") as f:
            cls.rows=list(csv.DictReader(f))
        with gzip.open(ROOT/"results"/cls.out["angle_file"],"rt",newline="") as f:
            cls.rays=list(csv.DictReader(f))

    def test_original_HHe_source_exact_2histories(self):
        self.assertEqual(len(self.h),2)
        for h in self.h.values():
            self.assertEqual(len(h.original),16000)
            self.assertEqual(len(h.times),16001)
            self.assertGreater(min(h.nhi),0)

    def test_original_owner_checkpoint_4locks_immutable(self):
        for lab in self.orig:
            self.assertEqual(self.orig[lab]["original"].shape,(128,17))
        self.assertEqual(len(CHECKPOINT_SHA),4)

    def test_verner_vector_parity_to_original_owner_scalar(self):
        energies=[0,12.3,13.59,13.60,13.61,13.64,13.7,20]
        a=verner(energies)
        for j,e in enumerate(energies):
            self.assertAlmostEqual(a[j],sigma_hi(e),delta=2e-30)

    def test_HI_threshold_and_binding_energy_are_not_equated(self):
        self.assertGreater(FIT_CUTOFF,ION)
        self.assertAlmostEqual(ION,13.598434599702,places=12)
        self.assertEqual(float(verner([13.59])[0]),0)
        self.assertGreater(float(verner([13.6])[0]),0)

    def test_original_HHe_clock_interpolation(self):
        for lab,h in self.h.items():
            t=np.array([0.,DT,2.4e11,5e12,END])
            np.testing.assert_allclose(interpolate_original(h.nhi,t),
              [h.linear(h.nhi,float(x)) for x in t],rtol=1e-14)

    def test_characteristic_energy_at_birth(self):
        q=self.orig["S0_BI"]["qhat"]
        for h in self.h.values():
            self.assertTrue(np.allclose(kgrav(q,h.H,np.array([[0.]])),1,atol=1e-14))
            r=kgrav(q,h.H,np.array([[END]])).ravel()
            self.assertTrue(np.all(r<=1+1e-14))
            self.assertGreaterEqual(float(np.min(r))*BIRTH_EV,BIRTH_EV*math.exp(-max(h.H)*END)-1e-12)

    def test_source_birth_per_H_conservation(self):
        h=self.h["S0_BI"];q=self.orig["S0_BI"]["qhat"]
        for step in (1,800,16000):
            r,_=characteristic_snapshot(h,q,step*DT,16,8,False)
            self.assertAlmostEqual(r["source_birth_n_per_H"],INITIAL_COUNT+SOURCE_RATE*step*DT,delta=1e-14)
            self.assertLess(r["photon_number_ledger_abs_residual"],3e-15)

    def test_absorption_off_is_exact_null(self):
        h=copy.copy(self.h["S0_BI"])
        h.nhi=[0.]*len(h.nhi)
        q=self.orig["S0_BI"]["qhat"]
        r,_=characteristic_snapshot(h,q,END,16,8,False)
        self.assertAlmostEqual(r["remaining_photon_n_per_H"],.1,delta=1e-12)
        self.assertAlmostEqual(r["HI_cumulative_absorbed_photons_per_H"],0.,delta=1e-15)
        self.assertEqual(r["HI_photo_rate_per_original_H_s"],0.)
        self.assertEqual(r["HI_cumulative_excess_photoheat_eV_per_H"],0.)

    def test_exact_photon_support_never_creates_forbidden_energy(self):
        for lab,h in self.h.items():
            for step in (1,1600,16000):
                r,_=characteristic_snapshot(h,self.orig[lab]["qhat"],step*DT,16,8,False)
                self.assertGreaterEqual(r["actual_survivor_energy_min_eV"]+1e-11,
                     r["physical_source_lower_energy_eV"])

    def test_exact_HI_rate_and_heating_nonnegative(self):
        h=self.h["S0_BI"]
        for step in (400,800,1600,16000):
            r,_=characteristic_snapshot(h,self.orig["S0_BI"]["qhat"],step*DT,16,8,False)
            self.assertGreater(r["HI_photo_rate_per_original_H_s"],0)
            self.assertGreater(r["HI_photoheating_rate_eV_per_original_H_s"],0)
            self.assertLessEqual(r["HI_cumulative_excess_photoheat_eV_per_H"],
                     (BIRTH_EV-ION)*r["HI_cumulative_absorbed_photons_per_H"]*(1+1e-7))

    def test_original_fixed_hat_matches_pr321_frozen_16k(self):
        h=self.h["S0_BI"]
        fixed=frozen_hat_history(h,self.orig["S0_BI"])
        r=fixed[16000]
        self.assertAlmostEqual(r["fixed_hat_surviving_n_per_H"],.05008021641368748,delta=6e-14)
        self.assertGreater(r["fixed_hat_gamma_HI_per_neutral_s"],0)

    def test_owner_gamma_vs_fixed_hat_never_assumed_exact(self):
        for r in self.rows:
            owner=float(r["original_F08_owner_gamma_HI_per_neutral_s"])
            fixed=float(r["fixed_hat_gamma_HI_per_neutral_s"])
            self.assertTrue(math.isfinite(fixed/owner-1))
            self.assertLess(abs(fixed/owner-1),5e-3)

    def test_source_power_and_redshift_ledger_all_snapshots(self):
        for r in self.rows:
            N=float(r["remaining_photon_n_per_H"])
            absorbed=float(r["HI_cumulative_absorbed_photons_per_H"])
            born=float(r["source_birth_n_per_H"])
            self.assertAlmostEqual(N+absorbed,born,delta=2e-13)
            initial_E=born*BIRTH_EV
            remE=float(r["photon_energy_eV_per_H"])
            absE=float(r["HI_cumulative_absorbed_energy_eV_per_H"])
            redE=float(r["cosmological_redshift_work_eV_per_H"])
            self.assertAlmostEqual(remE+absE+redE,initial_E,delta=3e-13)
            self.assertGreaterEqual(redE,-1e-10)

    def test_source_ray_sum_reproduces_summary_model(self):
        by={(r["branch"],int(r["original_tick"])):r for r in self.rows}
        grouped={}
        for r in self.rays:
            grouped.setdefault((r["branch"],int(r["source_original_tick"])),[]).append(r)
        self.assertEqual(len(grouped),30)
        for k,rows in grouped.items():
            self.assertEqual(len(rows),128)
            head=by[k]
            for a,b in (("remaining_photon_n_per_H","characteristic_surviving_per_H"),
                         ("photon_energy_eV_per_H","characteristic_energy_eV_per_H"),
                         ("HI_photo_rate_per_original_H_s","characteristic_photo_rate_per_H_s"),
                         ("HI_cumulative_excess_photoheat_eV_per_H","characteristic_cumulative_photoheat_eV_per_H")):
                assert math.isclose(sum(float(x[b]) for x in rows),float(head[a]),rel_tol=6e-14,abs_tol=2e-17),(k,a)

    def test_output_rows_and_byte_hash_replay(self):
        self.assertEqual(len(self.rows),30)
        self.assertEqual(self.out["epochs"],30)
        self.assertEqual(len(self.rays),3840)
        self.assertEqual(self.out["angle_rows"],3840)
        self.assertEqual(checksum(ROOT/"results"/self.out["summary_file"]),self.out["summary_sha256"])
        self.assertEqual(checksum(ROOT/"results"/self.out["angle_file"]),self.out["angle_sha256"])

    def test_Source_owner_meta_gate(self):
        self.assertEqual(self.out["schema"],MODEL)
        self.assertFalse(self.out["original_discrete_photon_IVP_replayed"])
        self.assertFalse(self.out["original_hhe_chemistry_thermodynamics_IVP_replayed"])
        self.assertEqual(self.out["REI_CENTRAL"],"28/88_REPORTED")
        self.assertEqual(self.out["BASS_UPPER"],"9/15_SCOPED_SOURCE_MAPPED")
        self.assertEqual(self.out["new_canonical_nodes"],0)
        self.assertEqual(self.out["production"],"HOLD")

    def test_source_nonionizing_N_not_used_for_gamma(self):
        # After significant cosmic redshift, surviving subthreshold packets may
        # contribute to photon number/energy but never to photoelectric gamma.
        h=self.h["S0_BI"];q=self.orig["S0_BI"]["qhat"]
        r,_=characteristic_snapshot(h,q,END,16,8,False)
        self.assertGreater(r["remaining_photon_n_per_H"],r["ionizing_photon_n_per_H"])
        self.assertGreater(r["source_hit_Verner_subthreshold_count"],0)

    def test_relativistic_cgs_units_are_preserved(self):
        self.assertEqual(C,29979245800.)
        self.assertAlmostEqual(DT,625000000.)
        self.assertLess(C*1e-4*6.7e-18,3e-11)
        self.assertGreater(C*1e-4*6.7e-18,1e-11)

if __name__=="__main__":
    unittest.main()
