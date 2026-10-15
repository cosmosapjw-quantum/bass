"""Actual source-locked gamma/nu + massive FD Einstein Bianchi I science regressions."""
from __future__ import annotations
import json,math,pathlib,sys,unittest
from unittest.mock import patch
import numpy as np
from scipy.constants import sigma as stefan,c as speedc

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from joint_kinetic import (
 KineticGammaNuMassive,source_lock,verify_original_sources,
 REI_SOURCE_SHA,AX03_SOURCE_SHA,actual_AX08_electron_donor)
from species_hierarchy import SpeciesHierarchy
from sigma_matter import InitialStress,EinsteinVlasovSigmaMatter

class JointKineticScience(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=source_lock()
        cls.params=dict(Sigma_ref=0.,orientation=0,kappa_gamma=.2,kappa_nu=.2,
                        massive_fraction=.1,massive_A=.5,m_over_Tref=30.,ellmax=8)
        cls.model=KineticGammaNuMassive(cls.source,**cls.params)
        cls.solve,cls.rows,cls.wall=cls.model.integrate(n=81)

    def test_both_original_source_hashes_checked(self):
        l=verify_original_sources()
        self.assertEqual(l['schema'],'rei.axbi.background_family.v1')
        self.assertEqual(REI_SOURCE_SHA["species_hierarchy.py"],
                         "ced7906b35c26d8d0374ee8ce7f67ceb957b51a63d44e5a2661997b7e46983c5")

    def test_byte_tamper_is_rejected(self):
        import joint_kinetic as j
        with patch.dict(j.REI_SOURCE_SHA,{"species_hierarchy.py":"0"*64}):
            with self.assertRaisesRegex(RuntimeError,"REI_ORIGINAL_BOLTZMANN_SOURCE_SHA_CHANGED"):
                j.verify_original_sources()

    def test_deduplicated_Omega_m(self):
        p=self.model
        self.assertAlmostEqual(p.matter_dust_omega+p.source.omega_m*p.fm,
                               p.source.omega_m,delta=1e-15)
        self.assertGreater(p.mass_normalizer,0)
        self.assertLess(p.fm,p.matter_max_fraction)
        f=p.fields(0,p.initial_state())
        h0=p.source.href
        expected=h0*math.sqrt(1+p.initial_state()[2]**2)
        self.assertLess(abs(f['H']/expected-1),5e-13)

    def test_gamma_neutrino_source_radiation_partition(self):
        m=self.model
        self.assertLess(abs(m.f_gamma+m.f_nu-1),1e-14)
        self.assertLess(abs(m.f_gamma-.5917144338784673),4e-14)
        self.assertEqual(m.omega_gamma+m.omega_nu,m.source.omega_r)

    def test_independent_initial_Pi_and_sigma(self):
        f=self.model.initial_tensors()
        self.assertEqual(f["Sigma_ref"],0.)
        self.assertGreater(f["gamma_Pi_J_m3"],0)
        self.assertGreater(f["nu_Pi_J_m3"],0)
        self.assertGreater(f["massive_Pi_J_m3"],0)
        self.assertLess(abs(sum(f["pi_tensor_diag_J_m3"])),1e-20)
        self.assertLess(abs(f["total_Pi_J_m3"]-sum(f[k] for k in (
            "gamma_Pi_J_m3","nu_Pi_J_m3","massive_Pi_J_m3"))),1e-22)

    def test_massive_initial_pi_FD_pressure_normalization(self):
        m=self.model;f=m.fields(0,m.initial_state())
        # Pressure anisotropy Pi=pbar_massive * A/5 for initial positive P2.
        expect=f["pbar_massive_norm"]*m.Am/5
        self.assertLess(abs(f["pi_massive_norm"]-expect)/abs(expect),2e-13)

    def test_vlasov_massive_positive_thermal_pressure(self):
        for f in self.rows:
            self.assertGreater(f["rho_massive_norm"],0)
            self.assertGreater(f["pm_perp_norm"],0)
            self.assertGreater(f["pm_parallel_norm"],0)
            self.assertGreater(f["H"],0)
            self.assertLess(abs(f['H']-math.sqrt(f['H2']))/f['H'],1e-13)

    def test_Boltzmann_number_zero_mode_both_species(self):
        for f in self.rows:
            self.assertLess(abs(f["N_gamma"][0]-1),2e-13)
            self.assertLess(abs(f["N_nu"][0]-1),2e-13)

    def test_gamma_nu_energy_work_and_shear_Einstein(self):
        for i in (0,10,40,80):
            q=self.model.constraint_and_work(float(self.solve.t[i]),self.solve.y[:,i])
            self.assertLess(abs(q['gamma_monopole_work_residual']),3e-14)
            self.assertLess(abs(q['nu_monopole_work_residual']),3e-14)
            self.assertLess(abs(q['shear_Einstein_rhs_residual']),3e-14)

    def test_exact_massive_collisionless_continuity_finite_difference(self):
        m=self.model
        x=float(self.solve.t[55]); y=self.solve.y[:,55]
        phys=m.fields(x,y);yp=m.rhs(x,y);eps=2e-5
        fp=m.fields(x+eps,y+eps*yp)
        fm=m.fields(x-eps,y-eps*yp)
        observed=(fp["rho_massive_norm"]-fm["rho_massive_norm"])/(2*eps)
        theory=-3*(phys["rho_massive_norm"]+phys["pbar_massive_norm"])-6*(phys["s"]/phys["H"])*phys["pi_massive_norm"]
        self.assertLess(abs(observed/theory-1),2e-8)

    def test_Raychaudhuri_with_two_source_work_ledgers(self):
        m=self.model
        x=float(self.solve.t[43]); y=self.solve.y[:,43]
        yp=m.rhs(x,y);de=1e-5
        f=m.fields(x,y);fp=m.fields(x+de,y+de*yp)
        fm=m.fields(x-de,y-de*yp)
        hd=(fp["H"]-fm["H"])/(2*de)
        self.assertLess(abs(hd/f["meanH_prime_x"]-1),2e-8)

    def test_initial_Sigma_orientation_is_signed(self):
        m=self.model
        f=m.fields(0,m.initial_state())
        self.assertEqual(f["s"],0.)
        self.assertEqual(f["Sigma"],0.)
        q=.01; sig=math.sqrt(3)*q/math.hypot(1,q)
        pos=KineticGammaNuMassive(self.source,Sigma_ref=sig,orientation=1,
                    kappa_gamma=0.,kappa_nu=0.,massive_fraction=0.)
        neg=KineticGammaNuMassive(self.source,Sigma_ref=sig,orientation=-1,
                    kappa_gamma=0.,kappa_nu=0.,massive_fraction=0.)
        self.assertEqual(pos.fields(0,pos.initial_state())['s'],
                        -neg.fields(0,neg.initial_state())['s'])

    def test_no_stress_initial_is_exact_FLRW_when_sigma_zero(self):
        m=KineticGammaNuMassive(self.source)
        s,rows,_=m.integrate(n=21)
        self.assertEqual(s.y[1,-1],0.)
        self.assertEqual(rows[-1]['Sigma'],0.)
        self.assertLess(abs(rows[-1]['H']/(
            m.source.h0*math.sqrt(m.source.omega_m/.2**3+
            m.source.omega_r/.2**4+m.source.omega_lambda))-1),3e-14)

    def test_prior_REI_photon_neutrino_limit_when_massive_zero(self):
        m=KineticGammaNuMassive(self.source,Sigma_ref=0,orientation=0,
                 kappa_gamma=.2,kappa_nu=.2,massive_fraction=0.,ellmax=8)
        old=SpeciesHierarchy(self.source,float(verify_original_sources()['cosmology']['Tcmb0_K']),
                    ellmax=8,Sigma_ref=0.,orientation=0,
                    kappa_gamma=.2,kappa_nu=.2)
        s,rows,_=m.integrate(n=51,rtol=2e-12,atol=8e-14)
        so,ro,_=old.integrate(n=51,rtol=2e-12,atol=8e-14)
        self.assertLess(np.max(abs(s.y-so.y)),2e-12)
        self.assertLess(abs(rows[-1]["Sigma"]-ro[-1]["Sigma"]),2e-12)

    def test_original_BASS_full_kinetic_massless_limit(self):
        m=self.model
        old=EinsteinVlasovSigmaMatter(InitialStress(
            Sigma_ref=0.,shear_orientation=1,radiation_fraction=1,
            radiation_A=.2,massive_matter_fraction=.1,
            massive_matter_A=.5,mass_over_Tref=30.))
        f=old.at_x(old.xmax)
        self.assertLess(abs(self.rows[-1]["Sigma"]-f["Sigma"]),5e-12)
        self.assertLess(abs(self.solve.y[1,-1]-f["b"]),5e-12)

    def test_positive_reconstruction_of_two_source_brightnesses(self):
        for i in (0,20,40,80):
            z=self.solve.y[:,i]
            self.assertGreater(self.model.minimum_angular_brightness(z,order=64),0)

    def test_matter_mass_fraction_rejects_baryon_double_count(self):
        with self.assertRaises(ValueError):
            KineticGammaNuMassive(self.source,massive_fraction=1.)
        with self.assertRaises(ValueError):
            KineticGammaNuMassive(self.source,massive_fraction=-.1)
        with self.assertRaises(ValueError):
            KineticGammaNuMassive(self.source,massive_A=3.)

    def test_physical_bad_source_angular_distribution_rejected(self):
        with self.assertRaises(ValueError):KineticGammaNuMassive(self.source,kappa_gamma=1.)
        with self.assertRaises(ValueError):KineticGammaNuMassive(self.source,kappa_nu=-.7)
        with self.assertRaises(ValueError):KineticGammaNuMassive(self.source,m_over_Tref=1.)

    def test_rei_kinetic_IS_NOT_scientific_completion(self):
        t=self.model.initial_tensors()
        self.assertFalse(self.model.ne_source is not None)
        self.assertIn("gamma-only",t["Thomson_species"])
        self.assertGreater(self.rows[-1]["Sigma"],self.rows[0]["Sigma"])

    def test_source_scalar_quantum_number_and_stress_signs(self):
        m=self.model
        t=m.fields(0,m.initial_state())
        self.assertLess(abs(t["pi_massive_norm"]-
            (t["pm_parallel_norm"]-t["pm_perp_norm"])/3),5e-15)
        self.assertLess(abs(t["pi_gamma_norm"]-
            m.omega_gamma*(.2/5)/(3*m.source.aref**4)),5e-15)

if __name__=="__main__":
    unittest.main(verbosity=2)
