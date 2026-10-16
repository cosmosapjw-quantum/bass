"""Original-source LRS FD96 kernel physics, causal Volterra and IVP regression."""
from __future__ import annotations
import math
import unittest
import numpy as np
from scipy.integrate import quad
from lrs_retarded import FD96Retarded, XMAX
from reference_kinetic_equilibrium import FD96Equilibrium
from reference_kinetic_tangent import EinsteinTangent

class TestRetarded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m={m:FD96Retarded(m) for m in (3.,30.,300.)}

    def test_original_fd96_normalizations(self):
        refs={3.:8.107415001491976,30.:54.478197513209125,300.:540.9644879050254}
        for m,v in refs.items(): self.assertAlmostEqual(self.m[m].fd.norm/v,1.,places=13)

    def test_equal_matter_energy_to_parent(self):
        for m,f in self.m.items():
            parent=EinsteinTangent(mass=m,A=0.,fraction=.1,Sigma_ref=0.,orientation=1)
            for x in (0.,.4,1.,XMAX):
                c=f.coefficients(x);pm,ph,_,_=parent.field(x,0.,0.,A=0.)
                self.assertLess(abs(c.rho0-pm.rho),3e-15)
                self.assertLess(abs(c.hubble/ph-1),3e-14)

    def test_alpha_kappa_against_original_quadrature(self):
        for m,f in self.m.items():
            for x in (0.,.55,XMAX):
                c=f.coefficients(x);ref=f.fd.stress(x,0.,0.)
                self.assertLess(abs(c.alpha-ref.delta_A),1e-13)
                self.assertLess(abs(c.kappa+ref.chi_b),1e-13)
                self.assertLess(abs(c.alpha-c.pbar0*.6),1e-13)

    def test_positive_susceptibility_and_ratio(self):
        for f in self.m.values():
            for x in (0.,.1,.7,XMAX):
                c=f.coefficients(x)
                self.assertGreater(c.alpha,0)
                self.assertGreater(c.kappa,0)
                self.assertTrue(.1 < c.alpha/c.kappa < .125)

    def test_proven_global_Contraction_and_kappa_decay(self):
        for m,f in self.m.items():
            self.assertLess(f.q_bound,.065)
            for u in np.linspace(0.,XMAX,17):
                c=f.coefficients(u)
                self.assertLessEqual(c.kappa, 1.25*f.kappa0*math.exp(-4*u)*(1+5e-14))
                self.assertLessEqual(f.proven_contraction_bound(u),f.q_bound*(1+3e-14))

    def test_exact_positive_retarded_green_and_causality(self):
        f=self.m[3.]
        for u,x in ((0.,0.),(0.,.2),(.25,.75),(.7,XMAX)):
            g=f.direct_kernel(x,u)
            self.assertGreaterEqual(g,0)
            if u==x:self.assertEqual(g,0)
        with self.assertRaises(ValueError):f.direct_kernel(.1,.2)

    def test_powerlaw_background_closed_kernel(self):
        f=self.m[30.]
        for u,x in ((0.,.5),(.12,.7),(.7,1.)): 
            Hc=2.3e-16; p=1.5; K=f.K
            kernel=K/Hc**2*math.exp((3+p)*u)*(math.exp((p-3)*x)-math.exp((p-3)*u))/(p-3)
            integral=quad(lambda v:math.exp(-3*v)/(Hc*math.exp(-p*v)),u,x,epsrel=1e-11)[0]
            direct=K*math.exp(3*u)/(Hc*math.exp(-p*u))*integral
            self.assertLess(abs(kernel/direct-1),3e-13)

    def test_tangent_ode_initial_conditions(self):
        for f in self.m.values():
            sol=f.tangent_ode(np.linspace(0,XMAX,81))
            self.assertEqual(sol.y[0,0],0.)
            self.assertEqual(sol.y[1,0],0.)
            self.assertTrue(np.all(sol.y[0,1:]>0))

    def test_volterra_vs_dop853(self):
        for f in self.m.values():
            xs=np.linspace(0,XMAX,513)
            p=f.picard(xs);exact=f.tangent_ode(xs)
            self.assertLess(np.max(np.abs(p.b_per_A-exact.y[0])),3e-13)
            self.assertLess(np.max(np.abs(p.s_per_href_per_A-exact.y[1])),1e-13)
            self.assertLess(p.discrete_residual,3e-14)

    def test_volterra_product_integration_fourth_order(self):
        f=self.m[3.]; ref=f.tangent_ode(np.array([0.,XMAX])).y[0,-1]
        errs=[]
        for n in (129,257,513):
            p=f.picard(np.linspace(0,XMAX,n));errs.append(abs(p.b_per_A[-1]-ref))
        self.assertGreater(errs[0]/errs[1],12.)
        self.assertGreater(errs[1]/errs[2],10.)

    def test_picard_bound_actual_converges(self):
        for m,f in self.m.items():
            p=f.picard(np.linspace(0,XMAX,257))
            self.assertLess(p.picard_steps,{3.:7,30.:5,300.:4}[m])
            self.assertLess(p.posterior_discrete_bound,1e-13)
            self.assertLess(abs(p.b_per_A[-1]),abs(p.b_without_feedback_per_A[-1]))

    def test_retarded_response_vs_pr164_tangent(self):
        for m,f in self.m.items():
            parent=EinsteinTangent(mass=m,A=0.,fraction=.1,Sigma_ref=0.,orientation=1).endpoint(rtol=2e-12,atol=2e-14,n=51)
            exact=f.tangent_ode(np.array([0.,XMAX])).y[:,-1]
            self.assertLess(abs(parent['sensitivity_b_A']-exact[0]),1e-12)
            self.assertLess(abs(parent['sensitivity_v_A']-exact[1]),1e-12)

    def test_nonlinear_small_parameter_quadratic_remainder(self):
        f=self.m[3.]
        r1=f.nonlinearity_remainder(.01)['b_absolute_remainder']
        r2=f.nonlinearity_remainder(.02)['b_absolute_remainder']
        self.assertGreater(r2/r1,3.5)
        self.assertLess(r2/r1,4.5)

    def test_isotropic_zero_and_fraction_zero(self):
        f=FD96Retarded(3.,fraction=0.)
        p=f.picard(np.linspace(0,XMAX,81))
        self.assertEqual(f.q_bound,0)
        self.assertTrue(np.all(p.b_per_A==0))
        self.assertTrue(np.all(p.s_per_href_per_A==0))

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):FD96Retarded(1.)
        with self.assertRaises(ValueError):FD96Retarded(3.,fraction=.95)
        f=self.m[3.]
        with self.assertRaises(ValueError):f.coefficients(-.01)
        with self.assertRaises(ValueError):f.picard(np.array([0.,.2,.1,1.]))
        with self.assertRaises(ValueError):f.proven_contraction_bound(XMAX+.1)

if __name__=='__main__':unittest.main(verbosity=2)
