"""AX03 actual source-matched independent Bianchi-I background supplier checks."""
from __future__ import annotations
import csv,hashlib,json,math,sys,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import axbi_provider as bg
import mp_oracle
import rust_parity

class BackgroundSupplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock=bg._read_lock()
        cls.cases=[bg.Background(bg.Family(q)) for q in [0.,.005,-.005,.01,-.01]]
        cls.same=bg.Background(bg.Family(.01,"SameHDiagnostic"))

    def test_exact_original_AX03_source_identity(self):
        self.assertEqual(bg.LOCK_SHA,"46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0")
        self.assertEqual(hashlib.sha256(bg.FROZEN.read_bytes()).hexdigest(),bg.LOCK_SHA)
        self.assertEqual(self.lock["schema"],"rei.axbi.background_family.v1")

    def test_source_changed_fail_closed(self):
        with patch.object(bg,"LOCK_SHA","0"*64):
            with self.assertRaisesRegex(ValueError,"BACKGROUND_LOCK_BYTE_IDENTITY"):
                bg._read_lock()

    def test_correct_family_and_signed_q(self):
        for obj in self.cases:
            self.assertEqual(obj.case.family,"PhysicalDensityFixed")
        with self.assertRaises(ValueError):bg.Family(.012)
        with self.assertRaises(ValueError):bg.Family(float("nan"))
        with self.assertRaises(ValueError):bg.Family(.005,"SameHDiagnostic")
        with self.assertRaises(ValueError):bg.Family(.01,"NonPhysical")

    def test_same_h_is_diagnostic_only(self):
        main=self.cases[-2]
        same=self.same
        p=main.at_a(.2);s=same.at_a(.2)
        self.assertGreater(p["H_mean_per_s"],s["H_mean_per_s"])
        self.assertAlmostEqual(s["H_mean_per_s"],s["H_flrw_per_s"],delta=1e-32)
        self.assertGreater(s["proper_elapsed_s"],p["proper_elapsed_s"])
        self.assertNotAlmostEqual(s["b"],p["b"],delta=1e-8)

    def test_t_zero_and_endpoint_contract(self):
        for bgx in (*self.cases,self.same):
            p=bgx.at_a(bgx.aref)
            self.assertEqual(p["proper_elapsed_s"],0.)
            self.assertEqual(p["b"],0.)
            self.assertEqual(bgx.at_a(bgx.aend)["zbar"],4.)

    def test_mean_shear_constraint_exact_float(self):
        for bk in self.cases:
            for f in (0,.2,.45,.8,1):
                p=bk.at_x(bk.xmax*f)
                h,hf,sh=p["H_mean_per_s"],p["H_flrw_per_s"],p["shear_s_per_s"]
                self.assertLess(abs(h*h-(hf*hf+sh*sh))/h**2,8e-15)
                self.assertLess(abs(p["sigma_tensor_squared_per_s2"]-3*sh*sh)/(h*h),1e-18)

    def test_shear_source_no_stress_q_constant(self):
        for bk in self.cases:
            ref=bk.sref*bk.aref**3
            for a in np.geomspace(bk.aref,bk.aend,37):
                self.assertLess(abs(bk.shear(a)*a**3-ref),1e-34)

    def test_hubble_axes_trace_and_shear(self):
        for bk in self.cases:
            for p in (bk.at_a(.09),bk.at_a(.2)):
                self.assertLess(abs((2*p["H_perp_per_s"]+p["H_parallel_per_s"])/3-p["H_mean_per_s"]),1e-32)
                self.assertLess(abs(p["volume_a_perp2_a_parallel"]/p["a"]**3-1),5e-15)

    def test_signed_H_even_b_odd(self):
        for idx in [1,3]:
            plus,minus=self.cases[idx],self.cases[idx+1]
            for a in (.07,.1,.2):
                p,m=plus.at_a(a),minus.at_a(a)
                self.assertEqual(p["H_mean_per_s"],m["H_mean_per_s"])
                self.assertEqual(p["shear_s_per_s"],-m["shear_s_per_s"])
                self.assertLess(abs(p["b"]+m["b"]),4e-16)
                self.assertLess(abs(p["proper_elapsed_s"]-m["proper_elapsed_s"]),8.0)

    def test_mean_flrw_q_zero(self):
        zero=self.cases[0]
        for a in np.geomspace(zero.aref,zero.aend,8):
            p=zero.at_a(float(a))
            self.assertEqual(p["H_mean_per_s"],p["H_flrw_per_s"])
            self.assertEqual(p["b"],0.)
            self.assertEqual(p["H_perp_per_s"],p["H_parallel_per_s"])

    def test_monotonic_elapsed_proper_time(self):
        for bk in (*self.cases,self.same):
            data=bk.table(501)
            self.assertTrue(np.all(np.diff(data["proper_elapsed_s"])>0))
            self.assertTrue(np.all(data["H_mean_per_s"]>0))
            self.assertTrue(np.all(data["n_H_cm3"]>0))
            self.assertLess(np.max(abs(data["db_dln_a"]-data["sigma_s_over_H"])),1e-15)

    def test_inverse_proper_clock(self):
        for bk in self.cases:
            for f in (.001,.2,.5,.85):
                p=bk.at_x(bk.xmax*f)
                q=bk.at_time(p["proper_elapsed_s"])
                self.assertLess(abs(q["a"]/p["a"]-1),3e-14)
                self.assertLess(abs(q["b"]-p["b"]),1e-12)

    def test_proper_H_He_mass_nuclei(self):
        zero=self.cases[0]
        for a in (.1,.2):
            p=zero.at_a(a)
            ratio=p["n_He_cm3"]/p["n_H_cm3"]
            self.assertAlmostEqual(ratio,self.lock["cosmology"]["X_He4"]/(4*(1-self.lock["cosmology"]["X_He4"])),delta=1e-14)
            self.assertAlmostEqual(p["n_H_cm3"]*a**3,zero.nh0,delta=1e-20)

    def test_mean_CMB_is_reference_not_directional_temperature(self):
        zero=self.cases[0]
        p=zero.at_a(.2)
        self.assertAlmostEqual(p["Tbar_CMB_K"],2.7255/.2,delta=2e-13)
        self.assertNotEqual(self.cases[-2].at_a(.2)["b"],0)

    def test_original_rust_parity_evidence(self):
        j=json.loads((HERE/"evidence/RUST_PARITY_INITIAL.json").read_text())
        self.assertEqual(j["case_count"],6)
        self.assertEqual(j["rows_count"],30)
        self.assertEqual(j["original_rust_sha256"],rust_parity.SOURCE_SHA)
        self.assertLess(j["max_relative_proper_time_diff"],4e-11)
        self.assertLess(j["max_abs_b_diff"],2e-10)
        self.assertEqual(j["cargo_exit_code"],0)

    def test_rust_owner_source_guard(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t)
            src=repo/"rust/rei_microphysics/src"
            src.mkdir(parents=True)
            (src/"axbi_background.rs").write_text("altered source fixture")
            with self.assertRaisesRegex(RuntimeError,"RUST_OWNER_SOURCE_CHANGED"):
                rust_parity.read_owner(repo)

    def test_high_precision_mpmath_independent(self):
        result=json.loads((HERE/"evidence/MP_ORACLE_INITIAL.json").read_text())
        self.assertEqual(result["n_samples"],30)
        self.assertLess(result["max_proper_time_relative_diff"],2e-12)
        self.assertLess(result["max_b_absolute_diff"],3e-13)
        self.assertFalse(result["interval_certification"])

    def test_matter_only_analytic_nonzero_shear_closed_form(self):
        h0=2e-18;a0=1/21;end=.2
        for q in (0,.01,-.01,.1):
            got=bg.matter_only_closed_form(q,a0,end,h0,1)
            Href=h0*math.sqrt(a0**-3)
            def rhs(x,Y):
                a=a0*math.exp(x)
                s=q*Href*math.exp(-3*x)
                H=math.hypot(h0*a**-1.5,s)
                return [1/H,s/H]
            val=solve_ivp(rhs,[0,math.log(end/a0)],[0,0],method="DOP853",rtol=2e-13,atol=1e-16)
            self.assertTrue(val.success)
            self.assertLess(abs(val.y[0,-1]/got["elapsed_proper_s"]-1),5e-12)
            self.assertLess(abs(val.y[1,-1]-got["b"]),5e-13)

    def test_photon_killing_integral_flrw_limit(self):
        zero=self.cases[0]
        out=bg.photon_pullback(zero.at_a(zero.aref),zero.at_a(zero.aend),np.array([-1.,0.,.6,1.]))
        self.assertLess(np.max(abs(out["energy_early_over_face"]-4.2)),1e-14)
        self.assertLess(np.max(abs(out["mu_early"]-np.array([-1,0,.6,1]))),1e-14)
        self.assertLess(np.max(abs(out["jacobian_dOmega_early_over_face"]-1)),1e-14)

    def test_photon_number_phase_volume_exact(self):
        for bk in (*self.cases,self.same):
            end=bk.at_a(bk.aend)
            for f in (0,.2,.6,.85):
                p=bk.at_x(bk.xmax*f)
                o=bg.photon_pullback(p,end,np.linspace(-1,1,21))
                err=np.max(abs(o["number_volume_invariant"]/o["geometry_volume_factor"]-1))
                self.assertLess(err,5e-14)
                self.assertLess(np.max(abs(o["mu_early"])),1+2e-14)

    def test_reflection_parity_under_mu_change(self):
        b=self.cases[-2]
        end=b.at_a(.2);ear=b.at_a(.08)
        plus=bg.photon_pullback(ear,end,+.6)
        minus=bg.photon_pullback(ear,end,-.6)
        self.assertEqual(plus["energy_early_over_face"],minus["energy_early_over_face"])
        self.assertEqual(plus["mu_early"],-minus["mu_early"])

    def test_photon_ray_redshift_derivative(self):
        bk=self.cases[-2];end=bk.at_a(.2)
        x=.5*bk.xmax;h=2e-5
        def local(x):
            p=bk.at_x(x)
            v=bg.photon_pullback(p,end,.6)
            return math.log(v["energy_early_over_face"]),v["mu_early"],p
        m=local(x-h)[0];p=local(x+h)[0]
        _,mu,mid=local(x)
        observed=(p-m)/(2*h)*mid["H_mean_per_s"]
        theory=-(mid["H_mean_per_s"]+mid["shear_s_per_s"]*(3*mu*mu-1))
        self.assertLess(abs(observed/theory-1),3e-9)

    def test_photon_invalid_inputs_rejected(self):
        bk=self.cases[0]
        with self.assertRaises(ValueError):bg.photon_pullback(bk.at_a(.2),bk.at_a(.1),.6)
        with self.assertRaises(ValueError):bg.photon_pullback(bk.at_a(.1),bk.at_a(.2),1.1)
        with self.assertRaises(ValueError):bg.photon_pullback(bk.at_a(.1),bk.at_a(.2),np.nan)

    def test_endpoint_table_and_photon_content_hashes(self):
        parent=HERE/"evidence/AX03_SUPPLIER_TABLES"
        m=json.loads((parent/"AX03_SUPPLIER_CONTRACT.json").read_text())
        self.assertEqual(m["rows_background"],3006)
        self.assertEqual(m["rows_photon"],7530)
        for name,digest in m["file_sha256"].items():
            self.assertEqual(hashlib.sha256((parent/name).read_bytes()).hexdigest(),digest)
        with (parent/"AX03_BACKGROUND.csv").open() as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),3006)
        self.assertEqual(rows[-1]["family"],"SameHDiagnostic")

    def test_benchmark_is_scoped_and_actual(self):
        data=json.loads((HERE/"evidence/BACKGROUND_BENCHMARK.json").read_text())
        self.assertEqual(data["owner_Rust_Simpson"]["n_points_per_case"],501)
        self.assertEqual(data["owner_Rust_Simpson"]["n_cases"],6)
        self.assertGreater(data["query_only_speedup"],1)
        self.assertGreater(data["python_optimized_DOP853"]["one_time_build_all_s"],0)
        self.assertEqual(data["owner_write_count"],0)

    def test_actual_original_rust_igm_inputs_match(self):
        p=json.loads((HERE/"evidence/IGM_RUST_PARITY.json").read_text())
        self.assertEqual(p["original_igm_background_sha256"],"ebe5d4ba0a61133512cecfe50791794a50aa22132bcc5189170e5668cbf1871f")
        self.assertEqual(p["cargo_run_offline_actual_native_status"],"SUCCESS")
        self.assertEqual(len(p["rows"]),11)
        self.assertLess(p["max_relative_input_diff"],1e-13)

    def test_rust_csv_consumer_accepts_and_rejects(self):
        j=json.loads((HERE/"evidence/NATIVE_TABLE_NEGATIVE_LF.json").read_text())
        self.assertEqual(j["positive"]["code"],0)
        self.assertEqual(j["negative"]["code"],3)
        self.assertIn("HAMILTONIAN_SHEAR_CONSTRAINT",j["negative"]["rejection"])
        self.assertTrue(j["original_input_identity_preserved"])
        self.assertEqual(j["positive"]["actual"]["rows"],3006)

    def test_photon_table_consumer_schema_grounds_source(self):
        folder=HERE/"evidence/AX03_SUPPLIER_TABLES"
        meta=json.loads((folder/"AX03_SUPPLIER_CONTRACT.json").read_text())
        self.assertEqual(meta["source_background_family_sha256"],bg.LOCK_SHA)
        self.assertEqual(meta["scientific_locks"]["native_axbi_science_admission"],"NOT_ISSUED")
        self.assertEqual(meta["units"]["proper_elapsed_s"],"SI elapsed proper seconds from zbar20, not absolute age")
        self.assertEqual(meta["native_Rust_integration_status"],"NOT_APPLIED_OWNER_REPO_READ_ONLY")

    def test_invalid_proper_time_domain(self):
        bgx=self.cases[0]
        with self.assertRaises(ValueError):bgx.at_time(-1)
        with self.assertRaises(ValueError):bgx.at_time(bgx.at_a(.2)["proper_elapsed_s"]+10)
        with self.assertRaises(ValueError):bgx.at_x(float("nan"))

    def test_rust_original_vs_vector_performance_scope(self):
        bmk=json.loads((HERE/"evidence/BACKGROUND_BENCHMARK.json").read_text())
        self.assertGreater(bmk["query_only_speedup"],50)
        self.assertGreater(bmk["python_optimized_DOP853"]["one_time_build_all_s"],0)
        self.assertEqual(bmk["owner_Rust_Simpson"]["n_points_per_case"],501)
        self.assertIn("not identical computational algorithm",bmk["comparability"])

    def test_effective_radiation_stress_proxy_only(self):
        j=json.loads((HERE/"evidence/FEEDBACK_PROXY.json").read_text())
        self.assertEqual(len(j["rows"]),5)
        self.assertTrue(j["all_proxy_shear_below_1e_minus4"])
        self.assertTrue(j["all_proxy_energy_below_1e_minus4"])
        self.assertEqual(j["rows"][0]["max_abs_stress_feedback_s_over_H"],0)
        for x in j["rows"][1:]:
            self.assertGreater(x["fraction_of_locked_q_shear_endpoint"],0.008)
            self.assertLess(x["fraction_of_locked_q_shear_endpoint"],0.01)
            self.assertIsNone(x["not_certified"]["gas_ionizing_stress"])

    def test_initially_isotropic_cmb_weak_b_expansion(self):
        import feedback_proxy
        bvals=np.array([1e-5,-1e-5])
        mono,quad=feedback_proxy.angular_moments(bvals,128)
        self.assertTrue(np.all(np.isfinite(mono)))
        self.assertLess(abs(quad[0]/bvals[0]+8/5),1e-4)
        self.assertLess(abs(quad[1]/bvals[1]+8/5),1e-4)

    def test_simpson_owner_moment_order_parity(self):
        import feedback_proxy
        samples=np.array([0,.001,.005,-.005])
        a,b=feedback_proxy.angular_moments(samples,128)
        c,d=feedback_proxy.angular_moments(samples,256)
        self.assertLess(float(np.max(abs(a-c))),2e-13)
        self.assertLess(float(np.max(abs(b-d))),2e-13)

if __name__=="__main__":
    unittest.main(verbosity=2)
