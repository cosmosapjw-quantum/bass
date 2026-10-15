"""Physical and numerical stress/backreaction tests, not native HII admission."""
from __future__ import annotations
import math,sys,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import einstein_vlasov_lrs as v

class PhysicalStress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models={(q,A,eta):v.EinsteinVlasovLRS(v.InitialData(q,A,eta),ang_n=64)
          for q,A,eta in [(0,0,0),(0,0,1),(0,1,1),(0,-1,1),
                            (.01,0,0),(.01,0,1),(.01,1,1),(.01,-1,1),
                            (-.01,1,1),(.005,1,.2)]}
    def test_source_lock_and_cosmology(self):
        self.assertEqual(v.LOCK_SHA,"46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0")
        self.assertEqual(v._read_lock()["schema"],"rei.axbi.background_family.v1")

    def test_angular_distribution_positive(self):
        mu=np.linspace(-1,1,1001)
        for A in [-1,-.5,0,.5,1,2]:
            self.assertGreaterEqual(float(np.min(1+A*v._P2(mu))),-2e-15)

    def test_initial_independent_shear_stress(self):
        for q,A,eta in [(0,1,1),(0,-1,1),(.01,1,1),(.01,-1,1),
                        (.01,0,1),(.01,1,.2)]:
            model=v.EinsteinVlasovLRS(v.InitialData(q,A,eta))
            initial=model.at_a(model.aref)
            self.assertLess(abs(initial["s_per_s"]/model.href-q),2e-14)
            self.assertLess(abs(initial["delta_Pparallel_minus_Pperp_J_m3"]/model.energy_r_ref-eta*A/5),4e-14)
            self.assertLess(abs(initial["radiation_M0"]-1),2e-14)

    def test_positive_intensity_and_pressure_energy(self):
        for A in [-1,0,1,2]:
            moments=v.Moments(64)
            for b in [-.25,-.005,0,.01,.25]:
                m,d,pt,pz=moments.evaluate(b,A)
                self.assertGreater(m,0)
                self.assertGreaterEqual(pt,0)
                self.assertGreaterEqual(pz,0)
                self.assertLess(abs((2*pt+pz)/m-1),3e-14)

    def test_analytic_moment_identity_dm0_db_minus_two_pressure(self):
        moments=v.Moments(96)
        for A in [-1,0,1,2]:
            for b in [-.08,0,.07]:
                h=1e-5
                up=moments.evaluate(b+h,A)[0]
                down=moments.evaluate(b-h,A)[0]
                delta=moments.evaluate(b,A)[1]
                self.assertLess(abs((up-down)/(2*h)+2*delta),2e-9)

    def test_same_source_no_double_count_radiation_at_reference(self):
        for model in self.models.values():
            p=model.at_a(model.aref)
            self.assertLess(abs(p["H_per_s"]**2-(model.href**2+model.s_ref**2))/model.href**2,3e-14)

    def test_source_conditionally_reduces_to_original_rei(self):
        for q in [0,.01,-.01,.005]:
            old=v.Background(v.Family(q))
            new=v.EinsteinVlasovLRS(v.InitialData(q,1,0),ang_n=64)
            for a in (.052,.1,.2):
                p=old.at_a(a); z=new.at_a(a)
                self.assertLess(abs(p["proper_elapsed_s"]/max(1,z["t_elapsed_proper_s"])-1),2e-11)
                self.assertLess(abs(p["b"]-z["b"]),2e-11)
                self.assertLess(abs(p["H_mean_per_s"]/z["H_per_s"]-1),2e-14)

    def test_zero_q_A0_is_FLRW_even_with_collisionless_fraction(self):
        p=self.models[(0,0,1)].table(61)
        self.assertLess(np.max(abs(p["s_over_H"])),2e-13)
        self.assertLess(np.max(abs(p["b"])),2e-13)
        self.assertLess(np.max(abs(p["H_per_s"]/p["Hflrw_per_s"]-1)),2e-14)

    def test_q0_anisotropic_stress_generates_shear(self):
        plus=self.models[(0,1,1)].at_a(.2)
        minus=self.models[(0,-1,1)].at_a(.2)
        self.assertGreater(plus["s_over_H"],2.8e-4)
        self.assertLess(minus["s_over_H"],-2.8e-4)
        self.assertGreater(plus["b"],0)
        self.assertLess(minus["b"],0)

    def test_pi_tracefree_and_sigma_pi_contraction(self):
        p=self.models[(.01,1,1)].at_a(.1)
        dp=p["delta_Pparallel_minus_Pperp_J_m3"]
        self.assertLess(abs(2*p["pi_perp_J_m3"]+p["pi_parallel_J_m3"]),1e-20)
        contracted=(-p["s_per_s"])*p["pi_perp_J_m3"]*2+2*p["s_per_s"]*p["pi_parallel_J_m3"]
        self.assertLess(abs(contracted-2*p["s_per_s"]*dp),1e-38)

    def test_hamiltonian_constraint(self):
        for model in self.models.values():
            p=model.table(41)
            self.assertLess(np.max(abs(p["Hamiltonian_residual_s2"]))/(model.href**2),1e-13)

    def test_metric_axis_volume(self):
        for model in self.models.values():
            p=model.table(45)
            self.assertLess(np.max(abs(p["a_perp"]**2*p["a_parallel"]/p["a"]**3-1)),1e-13)
            self.assertLess(np.max(abs((2*p["H_perp_per_s"]+p["H_parallel_per_s"])/3/p["H_per_s"]-1)),1e-13)

    def test_anisotropic_energy_trajectory_conservation(self):
        model=self.models[(.01,1,1)]
        for x in (.2,.7,1.3):
            hh=5e-5
            p=model.at_x(x)
            up=model.at_x(x+hh)["aniso_epsilon_J_m3"]
            down=model.at_x(x-hh)["aniso_epsilon_J_m3"]
            deriv=(np.log(up)-np.log(down))/(2*hh)
            predicted=-4-2*(p["s_per_s"]/p["H_per_s"])*(p["radiation_Mdelta"]/p["radiation_M0"])
            self.assertLess(abs(deriv-predicted),3e-9)

    def test_dH_dln_a_raychaudhuri_consistency(self):
        for q,A,eta in [(0,1,1),(.01,0,1),(.01,1,1),(.01,0,0)]:
            model=self.models[(q,A,eta)]
            for x in (.2,.5,1.1):
                h=1e-5
                deriv=(model.at_x(x+h)["H_per_s"]-model.at_x(x-h)["H_per_s"])/(2*h)
                prediction=model.at_x(x)["dH_dln_a_per_s"]
                self.assertLess(abs(deriv/prediction-1),1e-8)

    def test_moment_vectorization_equals_individual(self):
        g=v.Moments(64);b=np.linspace(-.04,.04,19)
        combined=g.evaluate(b,1)
        for i,x in enumerate(b):
            single=g.evaluate(float(x),1)
            for a,item in zip(combined,single):
                self.assertLess(abs(a[i]-item),2e-15)

    def test_angular_refinement_32_64_128(self):
        for A in (-1,0,1,2):
            for b in (-.1,.01,.12):
                a=v.Moments(32).evaluate(b,A)
                b64=v.Moments(64).evaluate(b,A)
                b128=v.Moments(128).evaluate(b,A)
                self.assertLess(max(abs(x-y) for x,y in zip(a,b64)),2e-13)
                self.assertLess(max(abs(x-y) for x,y in zip(b64,b128)),2e-13)

    def test_solution_refinement_angular_and_time(self):
        for q,A,eta in [(0,1,1),(.01,1,1),(.01,0,1)]:
            a=v.EinsteinVlasovLRS(v.InitialData(q,A,eta),ang_n=32,rtol=5e-11,atol=5e-13)
            b=v.EinsteinVlasovLRS(v.InitialData(q,A,eta),ang_n=128,rtol=8e-13,atol=5e-15)
            pa,pb=a.at_a(.2),b.at_a(.2)
            self.assertLess(abs(pa["s_over_H"]-pb["s_over_H"]),5e-11)
            self.assertLess(abs(pa["b"]-pb["b"]),5e-11)
            self.assertLess(abs(pa["t_elapsed_proper_s"]/pb["t_elapsed_proper_s"]-1),4e-11)

    def test_independent_initial_quadrupole_index(self):
        for eta in (0,.2,.8,1):
            for A in (-1,0,1,2):
                m=v.EinsteinVlasovLRS(v.InitialData(0,A,eta))
                p=m.at_a(m.aref)
                self.assertLess(abs(p["delta_Pparallel_minus_Pperp_J_m3"]/m.energy_r_ref-eta*A/5),6e-14)

    def test_photon_killing_original_limit(self):
        m=self.models[(.01,1,1)]
        for a in (.05,.1,.2):
            current=m.at_a(a)
            for u in (0,.6,1):
                g=m.photon_current_energy_over_initial(a,u)
                R=(np.exp(2*current["b"])*(1-u*u)+np.exp(-4*current["b"])*u*u)**.5
                self.assertLess(abs(g/(m.aref/a*R)-1),1e-15)

    def test_invalid_initial_physics_refused(self):
        for q,A,eta in [(0,2.01,1),(0,-1.01,1),(0,1,1.1),(0,1,-.01),(.02,0,1)]:
            with self.assertRaises(ValueError):v.InitialData(q,A,eta)
        with self.assertRaises(ValueError):v.Moments(0)
        with self.assertRaises(ValueError):v.Moments(4).evaluate(float("nan"),0)

    def test_shear_energy_coupling_not_same_as_naive_fixed_rho(self):
        z=self.models[(.01,1,1)].at_a(.2)
        self.assertLess(z["H_per_s"]/z["Hflrw_per_s"]-1,0)
        self.assertGreater(z["radiation_M0"],0)
        self.assertGreater(abs(z["aniso_epsilon_J_m3"]),1e-20)

if __name__=="__main__":unittest.main(verbosity=2)
