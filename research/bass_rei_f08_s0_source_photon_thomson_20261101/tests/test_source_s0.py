#!/usr/bin/env python3
"""Scoped original-source physical tests and falsification controls."""
import csv,gzip,json,math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from s0_source_photon_thomson import (ROOT,SOURCE,SHA,C,SIG_T,BIRTH_EV,
    THRESHOLD,END,gauss_birth_direction_grid,source_histories,redshift,
    threshold_age,sigma_hi,tau_hi,model_epoch,outgoing_gain,split_threshold_births,
    digest)

class PhysicalF08S0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.histories=source_histories()
        cls.result=json.loads((ROOT/"results"/"RESULT.json").read_text())
    def test_frozen_source_sha_exact(self):
        self.assertEqual(len(SHA),12)
        for name,h in SHA.items():
            self.assertEqual(digest(SOURCE/name),h)
    def test_falsified_source_sha_rejected(self):
        old=SHA["S0_BI.csv.gz"]
        try:
            SHA["S0_BI.csv.gz"]="0"*64
            with self.assertRaisesRegex(ValueError,"source SHA256 mismatch"):
                source_histories()
        finally:
            SHA["S0_BI.csv.gz"]=old
    def test_exact_original_charge_identity(self):
        for h in self.histories.values():
            self.assertEqual(len(h.original),16000)
            self.assertEqual(len(h.ne),16001)
            self.assertAlmostEqual(h.times[-1],END)
            self.assertGreater(min(h.nhi),0)
            for i in (0,1,3999,7999,11999,15999):
                x=h.xh[i+1]
                self.assertLessEqual(x,1)
                self.assertGreaterEqual(x,0)
    def test_original_verner_1996_domain(self):
        self.assertEqual(sigma_hi(THRESHOLD-1e-6),0)
        self.assertGreater(sigma_hi(THRESHOLD),0)
        self.assertGreater(sigma_hi(BIRTH_EV),0)
        self.assertLess(sigma_hi(BIRTH_EV),1e-17)
        with self.assertRaises(ValueError):
            sigma_hi(50001)
    def test_exact_null_energy_support_both_geometries(self):
        floor=BIRTH_EV*math.exp(-1.01e-14*END)
        self.assertGreater(floor,12.38)
        self.assertGreater(floor,10)
        for h in self.histories.values():
            for _,_,n,_,_,w in gauss_birth_direction_grid(8,16):
                e=BIRTH_EV*redshift(h.H,n,END)[0]
                self.assertGreaterEqual(e,floor-1e-12)
                self.assertLessEqual(e,BIRTH_EV)
    def test_gauss_quadrature_exact_isotropic_rank_two(self):
        for nmu,nphi in ((4,8),(8,16),(16,32)):
            rows=list(gauss_birth_direction_grid(nmu,nphi))
            self.assertAlmostEqual(sum(v[5] for v in rows),1,delta=1e-13)
            for i in range(3):
                self.assertAlmostEqual(sum(v[5]*v[2][i]**2 for v in rows),1/3,delta=5e-13)
            self.assertAlmostEqual(sum(v[5]*v[2][0]*v[2][1] for v in rows),0,delta=1e-13)
    def test_threshold_split_conserves_birth_number(self):
        t=END;n=64
        src=[(0.,0.05,"initial")]
        src += [((k+.5)*t/n,5e-15*t/n,"continuous") for k in range(n)]
        a=threshold_age(self.histories["S0_BI"].H,(1.,0.,0.))
        pieces=list(split_threshold_births(src,t,a))
        self.assertAlmostEqual(sum(v[1] for _,v in pieces),0.1,delta=1e-14)
        self.assertGreaterEqual(len(pieces),len(src))
        self.assertLessEqual(len(pieces),len(src)+1)
    def test_cutoff_photo_absorption_zero_if_no_interval(self):
        h=self.histories["S0_BI"];n=(1.,0.,0.)
        m=threshold_age(h.H,n)
        self.assertEqual(tau_hi(h,END,END,n,m),0.)
        self.assertGreater(tau_hi(h,0,END,n,m,16),0.)
    def test_FLRW_null_polarization_on_physical_source(self):
        h=self.histories["S0_FLRW"]
        p=model_epoch(h,2.5e12,16,8,16,8)
        m=p["source_matrix_3x3"]
        tr=sum(m[i][i] for i in range(3))
        for i in range(3):
            self.assertAlmostEqual(m[i][i]/tr,1/3,delta=1e-12)
        mm=tuple(x for row in m for x in row)
        I,Q,U,frac=outgoing_gain(mm,p["pre_first_scatter_unscattered_u_ev_per_H"],
                  h.ne[4000],.2,.4)
        self.assertLess(frac,1e-11)
    def test_BI_physical_source_polarizes_and_positive_matrix(self):
        h=self.histories["S0_BI"]
        p=model_epoch(h,2.5e12,16,8,16,8)
        mm=tuple(x for row in p["source_matrix_3x3"] for x in row)
        I,Q,U,frac=outgoing_gain(mm,p["pre_first_scatter_unscattered_u_ev_per_H"],
                  h.ne[4000],.2,.4)
        self.assertGreater(frac,1e-7)
        self.assertLess(frac,1.)
        self.assertGreater(I,math.hypot(Q,U))
    def test_original_guard_v_exact_physics(self):
        f=self.result["epochs"][3]
        self.assertGreater(f["original_lower_guard_n_fraction"],0.01)
        self.assertGreater(f["exact_null_minimum_E_ev"],12.3)
        self.assertEqual(f["model_photons_below_10eV_per_H"],0)
        self.assertEqual(self.result["new_canonical_nodes"],0)
        self.assertEqual(self.result["reference_S0_rei_scientific_admission"],"HOLD")
    def test_source_photon_n_U_compare_not_claimed_equal(self):
        f=self.result["epochs"][3]
        self.assertGreater(f["original_survivor_n_per_H"],0)
        self.assertGreater(f["model_survivor_n_per_H"],0)
        self.assertTrue(math.isfinite(f["model_minus_original_n_rel"]))
        self.assertGreater(abs(f["model_minus_original_n_rel"]),0.01)
        self.assertGreater(f["model_gamma_HI_per_s"],0)
    def test_full_4096_sky_rows_audited(self):
        p=ROOT/"results"/self.result["sky_filename"]
        self.assertEqual(digest(p),self.result["sky_sha256"])
        with gzip.open(p,"rt",newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),4096)
        for r in rows:
            I=float(r["out_gain_I_ev_per_H_s_sr"])
            Q=float(r["out_gain_Q_ev_per_H_s_sr"])
            U=float(r["out_gain_U_ev_per_H_s_sr"])
            P=float(r["out_gain_P_over_I"])
            self.assertTrue(math.isfinite(I) and math.isfinite(Q) and math.isfinite(U))
            self.assertGreaterEqual(I+1e-35,math.hypot(Q,U))
            self.assertAlmostEqual(P,math.hypot(Q,U)/I,delta=1e-13)
        # The source is isotropic under FLRW; no fake polarization may survive.
        fl=[r for r in rows if r["branch"]=="S0_FLRW"]
        bi=[r for r in rows if r["branch"]=="S0_BI"]
        self.assertLess(max(float(r["out_gain_P_over_I"]) for r in fl),1e-11)
        self.assertGreater(max(float(r["out_gain_P_over_I"]) for r in bi),1e-6)
    def test_total_incoming_moment_trace(self):
        for row in self.result["epochs"]:
            M=row["source_matrix_3x3"]
            self.assertAlmostEqual(sum(M[i][i] for i in range(3)),
                 row["pre_first_scatter_unscattered_u_ev_per_H"],delta=5e-13)
    def test_original_source_no_production_mutation(self):
        self.assertEqual(self.result["production"],"HOLD")
        self.assertEqual(self.result["REI_central"],"28/88_REPORTED")
        self.assertEqual(self.result["BASS_upper"],"9/15_SCOPED_SOURCE_MAPPED")
        self.assertFalse(self.result["full_photon_angular_source_equivalence"])
if __name__=="__main__":
    unittest.main()
