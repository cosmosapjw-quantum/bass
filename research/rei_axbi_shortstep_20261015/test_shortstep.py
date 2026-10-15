"""Source-locked AX03 short-step numerical C8 regression and real Rust parity."""
from __future__ import annotations
import json,math,sys,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import shortstep as s
import mp_shortstep as oracle
from axbi_provider import Background,Family,LOCK_SHA,photon_pullback,_read_lock

class ShortStepC8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample=json.loads((HERE/"evidence/MP80_SHORTSTEP.json").read_text())
        cls.rust=json.loads((HERE/"evidence/RUST_GL4_90.json").read_text())
        cls.back={q:Background(Family(q)) for q in [0,.005,-.005,.01,-.01]}
        cls.same=Background(Family(.01,"SameHDiagnostic"))
        cls.clock={q:s.HermiteClock(x) for q,x in cls.back.items()}

    def test_exact_family_sha(self):
        self.assertEqual(s.LOCK_SHA,LOCK_SHA)
        self.assertEqual(_read_lock()["schema"],"rei.axbi.background_family.v1")

    def test_oracle_90_source_locked_cases(self):
        a=self.sample
        self.assertEqual(a["n_cases"],6)
        self.assertEqual(a["n_intervals"],90)
        self.assertLess(a["max_relative_time_error"]["gauss4"],4e-13)
        self.assertLess(a["max_relative_b_error"]["gauss4"],4e-13)

    def test_python_GL4_Hermite_vs_mp80_scoped_gates(self):
        a=self.sample
        self.assertLess(a["max_relative_time_error"]["Hermite501"],1e-9)
        self.assertLess(a["max_relative_b_error"]["Hermite501"],1e-9)
        self.assertGreater(a["max_relative_time_error"]["naive_cumulative_subtraction"],1)
        self.assertGreater(a["cases_naive_exceeds_1e-8_but_gauss_within_1e-10"],50)
        self.assertIsNone(a["true_certified_global_error"])

    def test_gl4_gl8_same_local_source(self):
        for q in [0,.005,-.005,.01,-.01]:
            bg=self.back[q]
            for a0,a1 in [(.05,.05000001),(.1,.1001),(.18,.180000001)]:
                v=s.gauss_increment(bg,a0,a1,order=4)
                ref=s.gauss_increment(bg,a0,a1,order=8)
                self.assertLess(abs(v[0]/ref[0]-1),2e-13)
                if q:
                    self.assertLess(abs(v[1]/ref[1]-1),2e-13)
                else:self.assertEqual(v[1],0.)

    def test_rust_real_stdlib_90_parity(self):
        z=self.rust
        self.assertEqual(z["native_positive_exit_code"],0)
        self.assertEqual(z["n_rows"],90)
        self.assertEqual(z["actual_Rust_exit_for_invalid_q"],3)
        self.assertEqual(z["invalid_q_rejection"],"AXBI_SHORTSTEP_REJECT:Q_NOT_FROZEN")
        self.assertLess(z["maximum_Rust_dt_relative_diff_mp80"],1e-12)
        self.assertLess(z["maximum_Rust_db_relative_diff_mp80"],1e-12)

    def test_actual_below_one_ulp_time_subtraction_hazard(self):
        bg=self.back[.01]
        a0=.1
        a1=np.nextafter(a0,math.inf)
        dt=s.gauss_increment(bg,a0,a1)[0]
        old=bg.at_a(a1)["proper_elapsed_s"]-bg.at_a(a0)["proper_elapsed_s"]
        self.assertTrue(3.5<dt<3.6)
        self.assertEqual(old,4)
        self.assertGreater(abs(old/dt-1),.1)

    def test_stable_nextafter_works_at_all_3_scales(self):
        for a0 in (.05,.1,.18):
            for q in [0,.005,-.005,.01,-.01]:
                bg=self.back[q]
                a1=np.nextafter(a0,math.inf)
                dt,db=s.gauss_increment(bg,a0,a1)
                self.assertGreater(dt,0)
                self.assertTrue(np.isfinite([dt,db]).all())
                self.assertEqual(math.copysign(1,db) if q else 0,math.copysign(1,q) if q else 0)

    def test_hermite_monotone_positive_clock_derivative(self):
        for clock in self.clock.values():
            for coeff in clock.ct:
                self.assertGreater(s._min_derivative(coeff),0)
            if clock.bg.case.q_ref==0:
                self.assertTrue((clock.cb==0).all())

    def test_hermite_derivative_matches_physical_H(self):
        for q,clock in self.clock.items():
            for a in np.geomspace(clock.bg.aref,clock.bg.aend,31)[1:-1]:
                got,dba=clock.derivative(a)
                p=clock.bg.at_a(float(a))
                self.assertLess(abs(got*p["H_mean_per_s"]-1),2e-8)
                self.assertLess(abs(dba-p["sigma_s_over_H"]),1e-8)

    def test_hermite_point_agrees_original_source(self):
        for q,clock in self.clock.items():
            for a in (.06,.1,.19):
                ti,bi=clock.point(a)
                ref=clock.bg.at_a(a)
                self.assertLess(abs(ti-ref["proper_elapsed_s"])/max(1,abs(ref["proper_elapsed_s"])),5e-10)
                self.assertLess(abs(bi-ref["b"]),2e-11)

    def test_stable_Gauss_finite_additivity(self):
        bg=self.back[.01]
        for a0,mid,a2 in [(.05,.09,.13),(.1,.100001,.100002),(.17,.18,.2)]:
            t1,b1=s.gauss_increment(bg,a0,mid)
            t2,b2=s.gauss_increment(bg,mid,a2)
            t,b=s.gauss_increment(bg,a0,a2)
            self.assertLess(abs((t1+t2)/t-1),2e-12)
            self.assertLess(abs((b1+b2)/b-1),2e-12)

    def test_cross_multiple_Hermite_cells(self):
        bg=self.back[.01]
        clock=self.clock[.01]
        t,b=clock.increment(.06,.19)
        g,gb=s.gauss_increment(bg,.06,.19)
        self.assertLess(abs(t/g-1),1e-9)
        self.assertLess(abs(b/gb-1),1e-9)

    def test_signed_q_time_even_b_odd(self):
        for q in (.005,.01):
            xp=self.back[q];xm=self.back[-q]
            for a0,a1 in [(.06,.07),(.1,.10001),(.1,float(np.nextafter(.1,math.inf)))]:
                tp,bp=s.gauss_increment(xp,a0,a1)
                tm,bm=s.gauss_increment(xm,a0,a1)
                self.assertEqual(tp,tm)
                self.assertEqual(bp,-bm)

    def test_cumulative_clock_monotone_for_Hermite(self):
        for clock in self.clock.values():
            x=np.geomspace(clock.bg.aref,clock.bg.aend,99)
            vals=np.array([clock.point(a)[0] for a in x])
            self.assertTrue(np.all(np.diff(vals)>0))

    def test_photon_Killing_finite_scale_vs_frozen(self):
        bg=self.back[.01]
        for a0,a1 in [(.05,.1),(.1,.10001)]:
            f=s.photon_short_logmap(bg,a0,a1,np.array([-1,-.6,0,.6,1]))
            old=photon_pullback(bg.at_a(a0),bg.at_a(a1),np.array([-1,-.6,0,.6,1]))
            self.assertLess(np.max(abs(f["log_energy_early_over_late"]-np.log(old["energy_early_over_face"]))),2e-14)
            self.assertLess(np.max(abs(f["mu_early"]-old["mu_early"])),3e-14)

    def test_photon_phasevolume_exact_log_identity(self):
        bg=self.back[.01]
        for a0,a1 in [(.05,.1),(.1,.10001),(.1,float(np.nextafter(.1,math.inf)))]:
            f=s.photon_short_logmap(bg,a0,a1,np.linspace(-1,1,21))
            self.assertLess(np.max(abs(f["number_phase_volume_log_residual"])),5e-14)

    def test_photon_sign_parity(self):
        bg=self.back[.01]
        out=s.photon_short_logmap(bg,.1,.10001,np.array([-.6,.6]))
        self.assertEqual(out["log_energy_early_over_late"][0],out["log_energy_early_over_late"][1])
        self.assertEqual(out["mu_early"][0],-out["mu_early"][1])

    def test_one_source_diagnostic_counterfactual_separation(self):
        bg=self.same;phy=self.back[.01]
        a0=.1;a1=.11
        dt,_=s.gauss_increment(bg,a0,a1)
        df,_=s.gauss_increment(phy,a0,a1)
        self.assertGreater(dt,df)

    def test_invalid_data_fails_closed(self):
        bg=self.back[.01]
        for a0,a1 in [(.1,.01),(.1,.3),(.1,math.nan),(.1,math.inf)]:
            with self.assertRaises(ValueError):
                s.gauss_increment(bg,a0,a1)
        with self.assertRaises(ValueError):s.gauss_increment(bg,.1,.2,order=1)
        with self.assertRaises(ValueError):s.gauss_increment(bg,.1,.2,max_step_x=0)
        with self.assertRaises(ValueError):s.stable_dx(.2,.1)

    def test_stale_input_not_silently_clipped(self):
        bg=self.back[.01]
        with self.assertRaises(ValueError):s.HermiteClock(bg,n=0)
        with self.assertRaises(ValueError):s.HermiteClock(bg,n=32770)
        with self.assertRaises(ValueError):s.HermiteClock(bg).point(.3)

    def test_benchmark_provenance_is_scoped(self):
        j=json.loads((HERE/"evidence/BENCHMARK_CACHED.json").read_text())
        self.assertEqual(j["paired_intervals"],90)
        self.assertIsNone(j["whole_REI_solver_speedup"])
        self.assertTrue(j["conclusions"]["gauss4_satisfies_prior_stable_relative_target_1e-9"])

    def test_increment_zero_endpoint_same(self):
        bg=self.back[.01];clock=self.clock[.01]
        self.assertEqual(s.gauss_increment(bg,.1,.1),(0.,0.))
        self.assertEqual(clock.increment(.1,.1),(0.,0.))

    def test_true_vector_Gauss4_vs_mp80_all_90(self):
        j=self.sample
        groups={}
        for r in j["rows"]:
            groups.setdefault((r["q"],r["family"]),[]).append(r)
        for (q,family),vals in groups.items():
            bg=self.back[q] if family=="PhysicalDensityFixed" else self.same
            a0=np.array([v["a0"] for v in vals])
            a1=np.array([v["a1"] for v in vals])
            dt,db=s.gauss_batch(bg,a0,a1,order=4)
            self.assertEqual(len(dt),len(vals))
            for index,v in enumerate(vals):
                self.assertLess(abs(dt[index]/float(v["mp_t_sec"])-1),2e-12)
                if float(v["mp_b"])!=0:
                    self.assertLess(abs(db[index]/float(v["mp_b"])-1),2e-12)
                else:self.assertEqual(db[index],0.)

    def test_vector_GL4_matches_scalar_on_multiple_panels(self):
        bg=self.back[.01]
        a0=np.array([.05,.06,.1])
        a1=np.array([.1,.12,.2])
        dt,db=s.gauss_batch(bg,a0,a1,order=4)
        for i in range(3):
            scalar=s.gauss_increment(bg,a0[i],a1[i],order=4)
            self.assertLess(abs(dt[i]/scalar[0]-1),2e-12)
            self.assertLess(abs(db[i]/scalar[1]-1),2e-12)

    def test_vector_GL4_invalid_cases(self):
        bg=self.back[.01]
        for a0,a1 in [
          (np.array([]),np.array([])),
          (np.array([.1]),np.array([.1,.2])),
          (np.array([.1]),np.array([float("nan")])),
          (np.array([.1]),np.array([.3])),
          (np.array([.2]),np.array([.1]))]:
            with self.assertRaises(ValueError):s.gauss_batch(bg,a0,a1)

    def test_vectorized_threading_is_measured_and_not_promoted(self):
        j=json.loads((HERE/"evidence/BENCHMARK_VECTOR.json").read_text())
        self.assertEqual(j["paired_intervals"],90)
        self.assertIsNone(j["whole_REI_solver_speedup"])
        for worker in [1,2,4]:
            k=f"gauss4_vector_workers{worker}"
            self.assertLess(j["timings"][k]["max_relative_disagreement_to_scalar_GL4"],3e-13)
        self.assertGreater(j["timings"]["gauss4_vector_workers2"]["median_s"],
                           j["timings"]["gauss4_vector_workers1"]["median_s"])

    def test_cached_Gauss_rule_immutable(self):
        v,w=s._gauss_rule(4)
        self.assertFalse(v.flags.writeable)
        self.assertFalse(w.flags.writeable)
        self.assertIs(s._gauss_rule(4)[0],v)

    def test_background_fixed_a_and_fixed_t_clock_shift_distinct(self):
        j=json.loads((HERE/"evidence/CLOCK_SHIFT.json").read_text())
        self.assertIsNone(j["actual_ionizing_HII_or_Tgas_comparison"])
        pp={r["q"]:r for r in j["rows"]}
        self.assertEqual(pp[.01]["end_delta_time_same_a_s"],pp[-.01]["end_delta_time_same_a_s"])
        self.assertLess(pp[.01]["end_delta_time_same_a_s"],0)
        self.assertGreater(pp[.01]["max_abs_delta_ln_a_at_fixed_time"],1e-6)
        self.assertEqual(pp[.01]["n_valid_fixed_t"],500)
        # Leading even-in-q clock drift with quartic corrections, not exact q^2.
        self.assertLess(abs(pp[.01]["end_delta_time_same_a_s"]/pp[.005]["end_delta_time_same_a_s"]-4),.001)

    def test_prior_original_REI_shortstep_subtraction_hold_is_preserved(self):
        d=json.loads((HERE/"evidence/REI_OLD_CLOCK_HOLD.json").read_text())
        self.assertEqual(d["source_status"],"COMPONENT_GATES_PASS_SHORT_STEP_SUBTRACTION_HOLD")
        self.assertGreater(d["short_step_hold_count"],100)
        self.assertGreater(d["max_direct_subtraction_relative_error"],1e-8)
        self.assertLess(d["max_stable_increment_relative_error"],1e-9)
        self.assertFalse(d["this_C8_changes_original_driver"])

if __name__=="__main__":
    unittest.main(verbosity=2)
