"""Physics gates: original BASS J hierarchy and full massive Vlasov Einstein constraints."""
import csv
import json
import hashlib
import math
import sys
import unittest
import numpy as np
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import sigma_matter as a
from bianchi.matter import hierarchy as H
from bianchi.matter import freestream as fs

def fd_aniso(A):
    def source(Q,NH):
        P2=(3*NH[:,2]**2-1)/2
        return fs.f_fermi_dirac(Q)[:,None]*(1+A*P2)[None,:]
    return source

class SigmaMassivePhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sig=a.sigma_from_legacy_q(.01)
        cls.sample=a.EinsteinVlasovSigmaMatter(a.InitialStress(cls.sig,1,.5,.2,.1,.5,30.))
        cls.zero=a.EinsteinVlasovSigmaMatter(a.InitialStress(0.))
    def test_original_AX03_frozen_source(self):
        self.assertEqual(a.LOCK_SHA,"46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0")
        self.assertEqual(a.radiation._read_lock()["schema"],"rei.axbi.background_family.v1")
    def test_sigma_conversion_exact_LRS(self):
        for q in (.0,.005,.01):
            sigma=a.sigma_from_legacy_q(q)
            self.assertLess(abs(a.signed_q_from_sigma(sigma,1)-q),1e-15)
            self.assertLess(abs(a.signed_q_from_sigma(sigma,-1)+q),1e-15)
        with self.assertRaises(ValueError):a.signed_q_from_sigma(2.,1)
        with self.assertRaises(ValueError):a.signed_q_from_sigma(.01,0)
    def test_sigma_initial_constraint(self):
        for o in (1,-1):
            conf=a.InitialStress(self.sig,o)
            sol=a.EinsteinVlasovSigmaMatter(conf)
            init=sol.at_x(0)
            self.assertLess(abs(init["Sigma"]/conf.Sigma_ref-1),2e-14)
            self.assertEqual(int(math.copysign(1,init["s_per_s"])),o)
            self.assertLess(abs(init["constraint_rel"]),2e-14)
    def test_baseline_FLRW_zero(self):
        for x in [0,.15,.7,self.zero.xmax]:
            p=self.zero.at_x(x)
            self.assertEqual(p["Sigma"],0.)
            self.assertEqual(p["b"],0.)
            self.assertEqual(p["Pi_r_J_m3"],0.)
            self.assertEqual(p["Pi_m_J_m3"],0.)
    def test_stress_free_original_REI_AX03_q_signed(self):
        for q in [0,.005,-.005,.01,-.01]:
            sigma=a.sigma_from_legacy_q(q)
            cfg=a.InitialStress(sigma,1 if q>=0 else -1)
            kin=a.EinsteinVlasovSigmaMatter(cfg)
            original=a.radiation.Background(a.radiation.Family(q))
            for f in (.0,.35,.75,1.):
                x=f*kin.xmax
                n=kin.at_x(x);o=original.at_x(x)
                self.assertLess(abs(n["b"]-o["b"]),2e-11)
                self.assertLess(abs(n["proper_elapsed_s"]-o["proper_elapsed_s"])/max(1,o["proper_elapsed_s"]),2e-11)
                self.assertLess(abs(n["H_mean_per_s"]/o["H_mean_per_s"]-1),1e-12)
    def test_radiation_only_parent_Einstein_Vlasov(self):
        sigma=a.sigma_from_legacy_q(.01)
        initial=a.InitialStress(sigma,1,.5,.2,0.,0.,30.)
        new=a.EinsteinVlasovSigmaMatter(initial)
        old=a.radiation.EinsteinVlasovLRS(a.radiation.InitialData(.01,.2,.5),ang_n=32)
        for f in (0,.15,.7,1):
            a0=new.at_x(f*new.xmax);b0=old.at_x(f*old.xmax)
            self.assertLess(abs(a0["b"]-b0["b"]),2e-11)
            self.assertLess(abs(a0["H_mean_per_s"]/b0["H_per_s"]-1),5e-12)
    def test_massive_positive_normalized_reference(self):
        for mass in (3.,30.,1000.):
            m=a.MassiveMoments(mass)
            for A in (-1,.0,.5,2.):
                rho,pp,pa=m.evaluate(0.,0.,A)
                self.assertLess(abs(rho-1),1e-13)
                self.assertTrue(0<pp<1 and 0<pa<1)
                self.assertLess(abs((pa-pp)/3-A*m.initial_mean_v2/15),2e-13)
    def test_original_BASS_massive_kinetic_hierarchy_J(self):
        m=a.MassiveMoments(30.,angular_n=32)
        for A in (.0,.5,-.6):
            f=fd_aniso(A)
            initial=float(H.J_moment([1,1,1],30.,0,0,f,backend="python"))
            for x,b in [(0.,0.),(.35,.003),(1.,-.007)]:
                avec=np.array([math.exp(x-b),math.exp(x-b),math.exp(x+2*b)])
                j0=float(H.J_moment(avec,30.,0,0,f,backend="python"))
                j1=float(H.J_moment(avec,30.,0,1,f,backend="python"))
                pi=H.J_moment(avec,30.,2,0,f,backend="python")
                rho,pp,pa=m.evaluate(x,b,A)
                self.assertLess(abs(j0/initial-rho),5e-12)
                self.assertLess(abs(j1/(3*initial)-(2*pp+pa)/3),5e-12)
                self.assertLess(abs(pi[2,2]/initial-2*(pa-pp)/3),5e-12)
                self.assertLess(abs(pi[0,0]/initial+(pa-pp)/3),5e-12)
    def test_massive_energy_continuity(self):
        m=a.MassiveMoments(30.)
        for A in (-.5,0,.8):
            for x,b,s_over_H in [(.05,.001,.015),(.65,.02,-.005)]:
                d=1e-5
                r,pp,pa=m.evaluate(x,b,A)
                rp=m.evaluate(x+d,b+s_over_H*d,A)[0]
                rm=m.evaluate(x-d,b-s_over_H*d,A)[0]
                deriv=(rp-rm)/(2*d)
                rhs=-3*(r+(2*pp+pa)/3)-2*s_over_H*(pa-pp)
                self.assertLess(abs(deriv-rhs)/max(1e-12,abs(rhs)),3e-9)
    def test_massless_radiation_source_identity(self):
        mom=self.sample.rad
        for b,A in [(.01,.2),(-.03,-.5)]:
            h=1e-6
            M,P,*_=mom.evaluate(b,A)
            der=(mom.evaluate(b+h,A)[0]-mom.evaluate(b-h,A)[0])/(2*h)
            self.assertLess(abs(der+2*P),2e-9)
    def test_total_einstein_shear_source_initial(self):
        p=self.sample.at_x(0.)
        s=p["s_per_s"];H0=p["H_mean_per_s"]
        totalPi=p["Pi_r_J_m3"]+p["Pi_m_J_m3"]
        expected=-3*s+(8*math.pi*a.G_SI/a.C_SI**2)*totalPi/H0
        self.assertLess(abs((p["ds_dln_a_per_s"]-expected)/max(abs(s),1e-27)),5e-12)
        self.assertLess(abs(p["Sigma"]-self.sig),1e-14)
    def test_total_constraint_independent_H_raychaudhuri(self):
        sol=self.sample
        for f in (.2,.4,.7):
            x=f*sol.xmax
            p=sol.at_x(x)
            dx=4e-5
            der=(sol.at_x(x+dx)["H_mean_per_s"]-sol.at_x(x-dx)["H_mean_per_s"])/(2*dx)
            self.assertLess(abs(der/p["dH_dln_a_per_s"]-1),6e-8)
            self.assertLess(abs(p["constraint_rel"]),3e-15)
    def test_initial_pi_tensor_independent(self):
        init=self.sample.initial_tensors()
        for which in ("radiation","matter"):
            pi=init[f"initial_{which}_pi_diag_J_m3"]
            self.assertLess(abs(sum(pi)),1e-23)
            self.assertGreater(abs(init[f"initial_{which}_Pi_J_m3"]),0)
        self.assertGreater(init["initial_matter_Pi_J_m3"],0)
    def test_direct_stress_ratio_input_reconstruction(self):
        ref=self.sample
        init=ref.initial_tensors()
        er=init["initial_epsilon_r_kin_J_m3"]/.5
        em=init["initial_epsilon_m_kin_J_m3"]/.1
        cfg=a.InitialStress.from_stress_ratios(ref.initial.Sigma_ref,1,
            init["initial_radiation_Pi_J_m3"]/er,
            init["initial_matter_Pi_J_m3"]/em,.5,.1,30.)
        self.assertAlmostEqual(cfg.radiation_A,.2,delta=2e-14)
        self.assertAlmostEqual(cfg.massive_matter_A,.5,delta=2e-14)
    def test_shear_generated_from_zero_initial_sigma(self):
        for Ar,Am,fr,fm in [(1.,0.,1.,0.),(0.,1.,0.,.25),(0.,0.,0.,0.)]:
            sol=a.EinsteinVlasovSigmaMatter(a.InitialStress(0.,1,fr,Ar,fm,Am,10))
            z=sol.at_x(sol.xmax)
            if Ar!=0 or Am!=0:
                self.assertGreater(z["Sigma"],1e-8)
                self.assertGreater(z["b"],0)
            else:self.assertEqual(z["Sigma"],0)
    def test_massive_cold_limit_suppresses_pi(self):
        for mass in (30.,300.,3000.):
            m=a.MassiveMoments(mass)
            print("MASSIVE_COLD",mass,m.initial_mean_v2)
        self.assertGreater(a.MassiveMoments(30).initial_mean_v2,50*a.MassiveMoments(300).initial_mean_v2)
        self.assertLess(a.MassiveMoments(3000).initial_mean_v2,2e-6)
    def test_non_baryonic_budget_double_counting_guard(self):
        bad=(.315-.0493092305)/.315+.001
        with self.assertRaises(ValueError):
            a.InitialStress(.01,massive_matter_fraction=bad)
        with self.assertRaises(ValueError):a.InitialStress(.01,radiation_A=3)
        with self.assertRaises(ValueError):a.InitialStress(.01,massive_matter_A=-2)
    def test_signed_shear_even_H_zero_initial_pi(self):
        up=a.EinsteinVlasovSigmaMatter(a.InitialStress(self.sig,1))
        dn=a.EinsteinVlasovSigmaMatter(a.InitialStress(self.sig,-1))
        for frac in (0,.3,1.):
            p=up.at_x(frac*up.xmax);m=dn.at_x(frac*dn.xmax)
            self.assertLess(abs(p["H_mean_per_s"]/m["H_mean_per_s"]-1),1e-15)
            self.assertLess(abs(p["b"]+m["b"]),1e-13)
            self.assertLess(abs(p["signed_s_over_H"]+m["signed_s_over_H"]),1e-15)
    def test_full_report_source_not_ionized(self):
        z=self.sample.at_x(self.sample.xmax)
        self.assertGreater(z["n_H_cm3"],0)
        self.assertGreater(z["n_He_cm3"],0)
        self.assertNotIn("x_HII",z)
        self.assertNotIn("evidence_of_observational_detection",z)

    def test_native_original_REI_crate_bridge_positive_negative(self):
        receipt=json.loads((HERE/"evidence/NATIVE_REI_BRIDGE.json").read_text())
        self.assertEqual(receipt["result"]["rows"],7014)
        self.assertEqual(receipt["result"]["cases"],14)
        self.assertEqual(receipt["result"]["original_Rust_AX03_parity_samples"],5)
        self.assertLess(receipt["result"]["max_original_H_relative_diff"],1e-12)
        self.assertTrue(receipt["no_owner_source_mutation"])
        for neg in receipt["negative_controls"]:
            self.assertEqual(neg["exit_code"],3)
            self.assertIn("AXBI_SIGMA_MASSIVE_REJECT",neg["message"])
        self.assertEqual(len(receipt["negative_controls"]),3)
    def test_model_export_physical_double_source_contract(self):
        folder=HERE/"evidence/SIGMA_MATTER_TABLES"
        meta=json.loads((folder/"AX03_SIGMA_MATTER_CONTRACT.json").read_text())
        self.assertEqual(meta["n_cases"],14)
        self.assertEqual(meta["history_rows"],7014)
        self.assertEqual(meta["source_family_sha256"],a.LOCK_SHA)
        self.assertIn("FD momentum quadrature",meta["source_massive_quadrature"])
        self.assertEqual(hashlib.sha256((folder/"AX03_SIGMA_MASSIVE_HISTORIES.csv").read_bytes()).hexdigest(),meta["history_sha256"])
        with (folder/"AX03_SIGMA_MASSIVE_HISTORIES.csv").open() as f:
            table=list(csv.DictReader(f))
        self.assertEqual(len(table),7014)
        self.assertNotIn("q_ref",table[0])
        for r in table[::501]:
            sigma=float(r["Sigma_ref"])
            self.assertLess(abs(float(r["Sigma"])-sigma),2e-13)
            self.assertLess(abs(float(r["Pi_total_J_m3"])-float(r["Pi_m_J_m3"])-float(r["Pi_r_J_m3"])),1e-20)
    def test_true_convergence_sampled_not_global(self):
        obj=json.loads((HERE/"evidence/CONVERGENCE.json").read_text())
        self.assertIsNone(obj["whole_kinetic_ODE_interval_certification"])
        self.assertEqual(len(obj["cases"]),16)
        for row in obj["cases"]:
            self.assertLess(row["diff"]["b_absolute"],1e-10)
            self.assertLess(row["diff"]["Sigma_absolute"],1e-10)
            self.assertLess(row["diff"]["proper_time_relative"],5e-11)
    def test_benchmark_same_source_and_worker_scope(self):
        obj=json.loads((HERE/"evidence/MASSIVE_BENCHMARK.json").read_text())
        self.assertEqual(obj["moments_input"]["n"],1024)
        self.assertEqual(obj["ode_case_count"],14)
        self.assertIsNone(obj["native_REI_ion_history_speedup"])
        items={r["method"]:r for r in obj["moments"]}
        self.assertLess(items["chunk128_vector"]["tracemalloc_peak_bytes"],
                        items["full_vector_1024"]["tracemalloc_peak_bytes"])
        self.assertTrue(all(r["maximum_absolute_difference_vs_scalar"]<6e-14 for r in items.values()))
        self.assertTrue(all(r["max_source_endpoint_error"]<1e-13 for r in obj["ode"]))
if __name__=="__main__":unittest.main(verbosity=2)
