"""Actual REI F08 13.7-eV spectral remap operator tests and original-source controls."""
import csv,gzip,json,math,sys,unittest
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from spectral_support import (
    CHECKPOINT_SHA,RAW,NSTEP,DT,BIRTH_EV,INITIAL_COUNT,SOURCE_RATE,END,THRESHOLD,
    original_checkpoint,source_histories,remap_once,original_redshift_g,original_birth_weights,
    exact_floor,support_statistics,digest,SIM_MODES
)
from s0_source_photon_thomson import sigma_hi

def named_rows(path):
    with gzip.open(path,"rt",newline="") as f:return list(csv.DictReader(f))

class OriginalSourceRemap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h=source_histories()
        cls.check={l:original_checkpoint(l) for l in ("S0_BI","S0_FLRW")}
        cls.data=json.loads((ROOT/"results"/"RESULT.json").read_text())
        cls.time=named_rows(ROOT/"results"/cls.data["time_file"])
        cls.spectrum=named_rows(ROOT/"results"/cls.data["spectrum_file"])
        cls.angular=named_rows(ROOT/"results"/cls.data["angular_file"])

    def test_original_sha_lock_4_and_parent_12(self):
        self.assertEqual(len(CHECKPOINT_SHA),4)
        for n,z in CHECKPOINT_SHA.items():self.assertEqual(digest(RAW/n),z)
        self.assertEqual(len(self.h),2)
        self.assertEqual(len(self.h["S0_BI"].ne),16001)

    def test_falsified_original_checkpoint_sha_fails(self):
        old=CHECKPOINT_SHA["S0_BI-header.jsonl"]
        try:
            CHECKPOINT_SHA["S0_BI-header.jsonl"]="0"*64
            with self.assertRaisesRegex(ValueError,"SOURCE_SHA_FAILURE"):
                original_checkpoint("S0_BI")
        finally:
            CHECKPOINT_SHA["S0_BI-header.jsonl"]=old

    def test_exact_original_checkpoint_shapes(self):
        for c in self.check.values():
            self.assertEqual(c["original"].shape,(128,17))
            self.assertEqual(c["original_guard_n"].shape,(128,))
            self.assertEqual(len(c["energies"]),17)
            self.assertEqual(c["m"],4)
            self.assertGreater(c["original_total_n"],0.05)

    def test_origin_checkpoint_photon_count_vs_curve(self):
        for lab,c in self.check.items():
            target=float(self.h[lab].original[-1]["photon_n"])
            self.assertAlmostEqual(c["original_total_n"]/target,1.,delta=8e-14)

    def test_flrw_bi_source_pair_distinct_geometry(self):
        self.assertEqual(self.h["S0_FLRW"].times,self.h["S0_BI"].times)
        self.assertNotEqual(self.h["S0_FLRW"].H,self.h["S0_BI"].H)
        self.assertEqual(self.h["S0_BI"].H,(1.01e-14,9.9e-15,1e-14))

    def test_true_monochromatic_S0_exact_support(self):
        floor_bi=exact_floor(END,self.h["S0_BI"].H)
        floor_flrw=exact_floor(END,self.h["S0_FLRW"].H)
        self.assertAlmostEqual(floor_bi,12.383882550536338,delta=1e-12)
        self.assertGreater(floor_flrw,floor_bi)
        self.assertGreater(floor_bi,10.)

    def test_first_actual_original_hat_counterexample(self):
        for lab,c in self.check.items():
            j=3*c["m"]
            E=c["energies"]
            self.assertAlmostEqual(E[j],13.7,delta=1e-13)
            self.assertAlmostEqual(E[j-1],13.675,delta=1e-13)
            g=original_redshift_g(c["qhat"],self.h[lab].H,DT)
            lower=(E[j]-E[j]*g)/(E[j]-E[j-1])
            self.assertTrue(np.all((lower>0)&(lower<1)))
            self.assertGreater(E[j]*float(np.min(g)),exact_floor(DT,self.h[lab].H)-1e-12)
            self.assertLess(E[j-1],exact_floor(DT,self.h[lab].H))
            self.assertGreater(INITIAL_COUNT*float(np.mean(lower)),0.00017)

    def test_remap_one_step_number_and_energy_conservation(self):
        c=self.check["S0_BI"];E=c["energies"]
        g=original_redshift_g(c["qhat"],self.h["S0_BI"].H,DT)
        old=np.zeros((128,17));old[:,12]=INITIAL_COUNT/128
        z=np.zeros(128)
        new,gn,gu,err=remap_once(old,z,z,g,E)
        self.assertLess(err,2e-14)
        self.assertAlmostEqual(float(new.sum()+gn.sum()),INITIAL_COUNT,delta=1e-14)
        self.assertAlmostEqual(float((new*E).sum()+gu.sum()),
                               float((old*(E[None,:]*g[:,None])).sum()),delta=1e-14)

    def test_original_hat_generic_vs_two_point_on_all_nodes_one_step(self):
        c=self.check["S0_BI"];E=c["energies"];q=c["qhat"]
        g=original_redshift_g(q,self.h["S0_BI"].H,DT)
        def hat(x,k):
            if k==0:
                if x<=E[0]:return 1.
                if x>=E[1]:return 0.
                return (E[1]-x)/(E[1]-E[0])
            if k==len(E)-1:
                if x>=E[k]:return 1.
                if x<=E[k-1]:return 0.
                return (x-E[k-1])/(E[k]-E[k-1])
            if x<=E[k-1] or x>=E[k+1]:return 0.
            if x<=E[k]:return (x-E[k-1])/(E[k]-E[k-1])
            return (E[k+1]-x)/(E[k+1]-E[k])
        for d in (0,1,37,62,100,127):
            for j in range(1,17):
                x=E[j]*g[d]
                self.assertGreaterEqual(x,E[j-1])
                expected=(E[j]-x)/(E[j]-E[j-1])
                self.assertAlmostEqual(hat(x,j-1),expected,delta=2e-12)
                self.assertAlmostEqual(hat(x,j),1-expected,delta=2e-12)
                self.assertAlmostEqual(sum(hat(x,k) for k in range(17)),1.,delta=1e-12)

    def test_original_birth_weights_normalized(self):
        for lab,c in self.check.items():
            for t in (DT,5e12,END):
                w=original_birth_weights(c["qhat"],self.h[lab].H,t,original_redshift_g(c["qhat"],self.h[lab].H,t))
                self.assertAlmostEqual(float(np.sum(w)),1,delta=2e-14)
                self.assertGreater(float(np.min(w)),0)
            if lab=="S0_FLRW":
                self.assertLess(float(np.std(w)),2e-15)

    def test_original_f08_model_below_physical_support(self):
        for lab,c in self.check.items():
            v=support_statistics(c["original"],c["original_guard_n"],
                                 c["original_guard_u"],c["energies"],END,self.h[lab].H)
            self.assertGreater(v["under_exact_min_fraction"],.23)
            self.assertLess(v["under_exact_min_fraction"],.24)
            self.assertGreater(v["guard_n_per_H"],.0010)
            self.assertGreater(v["exact_min_eV"],12.38)
            self.assertLess(v["guard_u_eV_per_H"]/v["guard_n_per_H"],10.)

    def test_original_no_high_energy_source_tail(self):
        for c in self.check.values():
            self.assertLessEqual(float(c["original"][:,c["energies"]>13.7].sum()),1e-15)

    def test_frozen_HI_original_provider_cutoff(self):
        self.assertEqual(sigma_hi(13.599),0)
        self.assertGreater(sigma_hi(13.6),0)
        self.assertGreater(sigma_hi(13.7),0)
        self.assertEqual(sigma_hi(10),0)

    def test_all_physical_output_rows_and_hashes(self):
        self.assertEqual(self.data["time_rows"],60)
        self.assertEqual(self.data["spectrum_rows"],108)
        self.assertEqual(self.data["angular_rows"],768)
        for key,file in (("time_sha256","time_file"),("spectrum_sha256","spectrum_file"),("angular_sha256","angular_file")):
            self.assertEqual(digest(ROOT/"results"/self.data[file]),self.data[key])
        self.assertEqual(len(self.time),60)
        self.assertEqual(len(self.spectrum),108)
        self.assertEqual(len(self.angular),768)

    def test_passive_source_number_ledger_all_epochs(self):
        for r in self.time:
            if r["mode"]=="PASSIVE_REMAP_ONLY":
                t=float(r["t_proper_s"])
                target=INITIAL_COUNT+SOURCE_RATE*t
                self.assertAlmostEqual(float(r["n_per_H"]),target,delta=2e-13)

    def test_frozen_HI_reproduces_source_level_support(self):
        for lab in ("S0_BI","S0_FLRW"):
            r=next(q for q in self.time if q["mode"]=="FROZEN_HI_IMPLICIT_ABSORPTION" and q["branch"]==lab and q["tick"]=="16000")
            obs=support_statistics(self.check[lab]["original"],self.check[lab]["original_guard_n"],
                 self.check[lab]["original_guard_u"],self.check[lab]["energies"],END,self.h[lab].H)
            # This is an observational closeness classification, not original IVP equivalence.
            self.assertLess(abs(float(r["n_per_H"])-obs["n_per_H"]),1.05e-5)
            self.assertLess(abs(float(r["under_exact_min_fraction"])-obs["under_exact_min_fraction"]),3e-5)
            self.assertLess(abs(float(r["guard_n_per_H"])-obs["guard_n_per_H"]),1e-7)

    def test_redshift_only_remap_ledger_eps(self):
        for c in self.data["stat_records"]:
            if c.get("mode")=="PASSIVE_REMAP_ONLY":
                self.assertLess(c["max_photon_count_ledger_abs"],2e-12)
                self.assertLess(c["max_redshift_number_energy_remap_residual_abs"],2e-14)

    def test_physical_claim_gate_not_canonical(self):
        self.assertEqual(self.data["REI_CENTRAL"],"28/88_REPORTED")
        self.assertEqual(self.data["BASS_UPPER"],"9/15_SCOPED_SOURCE_MAPPED")
        self.assertEqual(self.data["canonical_delta"],0)
        self.assertEqual(self.data["original_F08_admission"],"HOLD")
        self.assertFalse(self.data["original_solver_replayed"])
        self.assertEqual(self.data["production"],"HOLD")

if __name__=="__main__":unittest.main()
