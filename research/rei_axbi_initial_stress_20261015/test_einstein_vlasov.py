"""R5/C5-C7 physically scoped tests for new initial pi_ab Einstein–Vlasov lane."""
from __future__ import annotations
import json,math,sys,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import einstein_vlasov as v
import vector_batch as batch
from axbi_provider import Background,Family,LOCK_SHA

class StressInitialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot=json.loads((HERE/"evidence/PILOT.json").read_text())
        cls.source=v._read_lock()
    def test_frozen_AX03_source_hash(self):
        self.assertEqual(self.pilot["lock_sha256"],LOCK_SHA)
        self.assertEqual(v.LOCK_SHA,LOCK_SHA)
        self.assertEqual(self.source["schema"],"rei.axbi.background_family.v1")
    def test_initial_pi_is_independent_from_q(self):
        for q in [0,.005,-.005,.01,-.01]:
            for k in [-.2,0,.2]:
                initial=v.Initial(q,k)
                self.assertAlmostEqual(initial.initial_pi_over_rad_energy,k/15,delta=1e-15)
                m,p=v.moments(0,k,order=64)
                self.assertLess(abs(m-1),2e-14)
                self.assertLess(abs(p-k/15),2e-14)
    def test_distribution_W_is_positive(self):
        for k in [-.5,0,.5]:
            u=np.linspace(-1,1,501)
            self.assertGreaterEqual(float(np.min(1+k*v.p2(u))),.499999)  # k=-1/2, mu=+/-1 has W=1/2
    def test_reject_negative_distribution_or_bad_q(self):
        for q,k in [(0,.501),(0,-.501),(.123,.2),(.01,float('nan'))]:
            with self.assertRaises(ValueError):v.Initial(q,k)
        with self.assertRaises(ValueError):v.moments(.3,.2)
    def test_moment_energy_exact_identity(self):
        for b in [-.01,-.003,0,.001,.008]:
            for k in [-.2,0,.2]:
                h=2e-5
                m1=v.moments(b+h,k)[0]
                m0=v.moments(b-h,k)[0]
                P=v.moments(b,k)[1]
                self.assertLess(abs((m1-m0)/(2*h)+6*P),3e-9)
    def test_positive_radiation_pressure_dominant_energy(self):
        for b in [-.02,0,.03]:
            for k in [-.5,0,.5]:
                M,P=v.moments(b,k)
                self.assertGreater(M,0)
                self.assertLess(abs(P/M),1/3)
    def test_numeric_source_constraint(self):
        for row in self.pilot["cases"]:
            solver=v.KineticStressBackground(v.Initial(row["q_ref"],row["kappa"]))
            for x in np.linspace(0,solver.xmax,33):
                f=solver.fields(float(x))
                H2=solver.h0**2*(solver.om/f["a"]**3+solver.ol+solver.orad/f["a"]**4*f["radiation_monopole_M"])+f["s_per_s"]**2
                self.assertLess(abs(f["h_per_s"]**2/H2-1),2e-14)
                self.assertAlmostEqual(f["pi_ab_over_crit_today"][0]+f["pi_ab_over_crit_today"][1]+f["pi_ab_over_crit_today"][2],0,delta=5e-17)
    def test_exact_radiation_flrw_equilibrium(self):
        solver=v.KineticStressBackground(v.Initial(0.,0.))
        for x in np.linspace(0,solver.xmax,9):
            f=solver.fields(float(x))
            self.assertEqual(f["b"],0)
            self.assertEqual(f["s_per_s"],0)
            self.assertEqual(f["radiation_P"],0)
            ref=Background(Family(0.)).at_a(f["a"])
            self.assertLess(abs(f["elapsed_proper_s"]/max(1,ref["proper_elapsed_s"])-1) if x else 0,3e-12)
    def test_initial_stress_generates_shear(self):
        r=v.KineticStressBackground(v.Initial(0,.2)).at_a(.2)
        self.assertGreater(r["b"],8e-5)
        self.assertGreater(r["s_per_s"]/r["h_per_s"],5e-5)
    def test_initial_zero_stress_can_gain_radiation_quadrupole(self):
        r=v.KineticStressBackground(v.Initial(.005,0.)).at_a(.2)
        self.assertGreater(abs(r["radiation_P"]),.0005)
        frozen=Background(Family(.005)).at_a(.2)
        self.assertGreater(abs(r["b"]-frozen["b"]),1e-6)
    def test_vector_RK4_vs_dop853_10(self):
        r=batch.solve_many(steps=256,order=32)
        for i,(q,k) in enumerate(batch.CASES):
            ref=v.KineticStressBackground(v.Initial(q,k)).at_a(.2)
            self.assertLess(abs(r["b_end"][i]-ref["b"]),1e-11)
            self.assertLess(abs(r["s_over_H"][i]-ref["s_per_s"]/ref["h_per_s"]),1e-11)
            self.assertLess(abs(r["elapsed_proper_s"][i]/ref["elapsed_proper_s"]-1),1e-10)
    def test_angular_Gauss_resolution(self):
        for b in [-.01,.001,.01]:
            for k in [-.2,.2]:
                low=v.moments(b,k,order=16)
                high=v.moments(b,k,order=128)
                self.assertLess(abs(low[0]-high[0]),5e-14)
                self.assertLess(abs(low[1]-high[1]),5e-14)
    def test_kinetic_moment_derivative_for_energy(self):
        for k in [0,.2,-.2]:
            for b in [-.02,.007]:
                eps=1e-5
                Mplus=v.moments(b+eps,k)[0]
                Mminus=v.moments(b-eps,k)[0]
                _,P=v.moments(b,k)
                self.assertLess(abs((Mplus-Mminus)/(2*eps)+6*P),2e-9)
    def test_angular_positive_weights_normalized(self):
        for n in (16,32,64,128):
            u,w=v.gauss64(n)
            self.assertLess(abs(w.sum()-1),2e-14)
            self.assertTrue((w>0).all())
    def test_real_signed_physical_clocks_and_positivity(self):
        for row in self.pilot["cases"]:
            m=v.KineticStressBackground(v.Initial(row["q_ref"],row["kappa"]))
            f=m.table(101)
            self.assertTrue(np.all(np.diff(f["elapsed_proper_s"])>0))
            self.assertTrue(np.all(f["h_per_s"]>0))
            self.assertTrue(np.all(f["radiation_monopole_M"]>0))
    def test_momentum_stress_reference_bianchi_convention(self):
        z=v.KineticStressBackground(v.Initial(.005,.2)).at_a(.2)
        self.assertLess(abs(2*z["h_perp_per_s"]+z["h_parallel_per_s"]-3*z["h_per_s"])/z["h_per_s"],1e-14)
        self.assertGreater(z["a_perp"],0)
        self.assertLess(abs((z["a_perp"]**2*z["a_parallel"])/(z["a"]**3)-1),1e-14)
    def test_numerical_benchmark_vs_original_algorithm_scope(self):
        j=json.loads((HERE/"evidence/VECTOR_BENCH.json").read_text())
        self.assertEqual(len(j["cases"]),10)
        self.assertIsNone(j["native_REI_solver_speedup"])
        self.assertIn(j["fastest_passed"],j["tested"])
        self.assertLess(j["tested"][j["fastest_passed"]]["max_b_abs_delta_vs_DOP853"],2e-9)
    def test_source_bound_scoped_not_full_ionizing_radiation(self):
        self.assertNotEqual(self.source["cosmology"]["radiation_scope"],"fully coupled ionizing photons")
if __name__=="__main__":unittest.main(verbosity=2)
