"""Scientific regressions for standalone BASS source-equivalent tangent IVP."""
import math
import unittest
import numpy as np
from scipy.integrate import simpson
from kinetic_tangent import (MassiveFD96,EinsteinTangent,AREF,AEND,XMAX,
                             H0,OMEGA_M,OMEGA_R,OMEGA_L)

class TangentTests(unittest.TestCase):
    def test_fd96_norm_matches_published_grid_m30(self):
        # Source-locked PR163 published FD96/GL32 exact grid normalization.
        m=MassiveFD96(30.,32)
        self.assertEqual(len(m.q),96)
        self.assertEqual(len(m.mu),32)
        self.assertAlmostEqual(m.norm,54.478197513209125,places=12)
        self.assertAlmostEqual(m.initial_v2, .014042977688245466,places=15)

    def test_angular_initial_normalization_all_A(self):
        for mass in (3.,30.,300.):
            m=MassiveFD96(mass)
            for A in (-1.,-.5,0.,.5,2.):
                p=m.moments(0,0,A)
                self.assertAlmostEqual(p.rho,1,places=14)
                self.assertAlmostEqual(p.delta,A*m.initial_v2/5,places=14)
                self.assertGreater(p.pbar,0)

    def test_stable_zero_and_strict_susceptibility(self):
        for mass in (3.,30.,300.):
            m=MassiveFD96(mass)
            p=m.moments(.5,0,0)
            self.assertEqual(p.delta,0)
            self.assertLess(p.chi,0)
            b=1e-16
            self.assertLess(m.moments(.5,b,0).delta,0)
            self.assertGreater(m.moments(.5,-b,0).delta,0)
            self.assertLess(abs(m.moments(.5,b,0).delta/(b*p.chi)-1),2e-13)

    def test_stress_derivatives_analytic_fd(self):
        m=MassiveFD96(3.)
        x,b,A=.67,.015,.43
        p=m.moments(x,b,A)
        h=5e-5
        bp=m.moments(x,b+h,A)
        bm=m.moments(x,b-h,A)
        ap=m.moments(x,b,A+h)
        am=m.moments(x,b,A-h)
        self.assertLess(abs((bp.rho-bm.rho)/(2*h)+2*p.delta),2e-9)
        self.assertLess(abs((bp.delta-bm.delta)/(2*h)/p.chi-1),4e-9)
        self.assertLess(abs((ap.rho-am.rho)/(2*h)-p.rho_A),1e-11)
        self.assertLess(abs((ap.delta-am.delta)/(2*h)-p.delta_A),1e-11)

    def test_source_domain_and_mass_budget(self):
        for bad in (-1e-5,1.0,float('nan')):
            with self.assertRaises(ValueError):EinsteinTangent(fraction=bad)
        for badA in (-1.001,2.001,float('nan')):
            with self.assertRaises(ValueError):EinsteinTangent(A=badA)
        with self.assertRaises(ValueError):MassiveFD96(1.)
        with self.assertRaises(ValueError):MassiveFD96(30.,7)
        with self.assertRaises(ValueError):EinsteinTangent(Sigma_ref=.09)

    def test_exact_isotropic_einstein_vlasov_control(self):
        for mass in (3,30,300):
            model=EinsteinTangent(mass=mass,A=0,Sigma_ref=0)
            sol=model.solution(n=23)
            self.assertTrue(np.array_equal(sol.y[0],np.zeros(23)))
            self.assertTrue(np.array_equal(sol.y[1],np.zeros(23)))
            for x in (.0,.4,1.0,XMAX):
                M,H,_,_=model.field(x,0,0)
                a=AREF*math.exp(x)
                exact=H0*math.sqrt(OMEGA_M*(1-model.fraction)/a**3+
                    OMEGA_R/a**4+OMEGA_L+model.cm*M.rho)
                self.assertLess(abs(H/exact-1),5e-15)
            # For massive nonrelativistic-but-warm matter, isotropy is exact
            # but its background is NOT the unmodified cold-dust FLRW clock.
            a=AEND
            original=H0*math.sqrt(OMEGA_M/a**3+OMEGA_R/a**4+OMEGA_L)
            _,H,_,_=model.field(XMAX,0,0)
            self.assertLess(H,original)
        # The frozen AX03 dust+radiation FLRW baseline is recovered only if
        # the kinetic-massive fraction vanishes.
        empty=EinsteinTangent(mass=3.,fraction=0.,A=0,Sigma_ref=0)
        for x in (0,.4,1.,XMAX):
            a=AREF*math.exp(x)
            _,H,_,_=empty.field(x,0,0)
            original=H0*math.sqrt(OMEGA_M/a**3+OMEGA_R/a**4+OMEGA_L)
            self.assertLess(abs(H/original-1),5e-15)

    def test_vanish_matter_fraction_source_parameter_tangent(self):
        m=EinsteinTangent(fraction=0.,A=.6,Sigma_ref=.01)
        sol=m.solution(n=13)
        np.testing.assert_allclose(sol.y[3:],0.,atol=0,rtol=0)

    def test_variational_jacobian_by_finite_difference(self):
        m=EinsteinTangent(mass=3.,A=.4,Sigma_ref=.012)
        x=.55
        sol=m.solution(n=20)
        y=sol.sol(x)
        J=m.jacobian(x,y)
        h=5e-6
        for i in (0,1):
            yp=y.copy();ym=y.copy();yp[i]+=h;ym[i]-=h
            observed=(m.derivative(x,yp)[:3]-m.derivative(x,ym)[:3])/(2*h)
            np.testing.assert_allclose(J[:,i],observed,atol=1e-8,rtol=5e-9)

    def test_tangent_matches_full_trajectory_parameter_difference(self):
        for mass in (3.,30.,300.):
            A=.4;eps=4e-4
            base=EinsteinTangent(mass=mass,A=A,Sigma_ref=.01,orientation=-1)
            center=base.solution(rtol=4e-12,atol=3e-14,n=41)
            plus=EinsteinTangent(mass=mass,A=A+eps,Sigma_ref=.01,orientation=-1).solution(rtol=4e-12,atol=3e-14,n=41)
            minus=EinsteinTangent(mass=mass,A=A-eps,Sigma_ref=.01,orientation=-1).solution(rtol=4e-12,atol=3e-14,n=41)
            observed=(plus.y[:3,-1]-minus.y[:3,-1])/(2*eps)
            predicted=center.y[3:,-1]
            np.testing.assert_allclose(predicted,observed,atol=1.5e-10,rtol=1.5e-6)

    def test_raychaudhuri_consistency_not_hamiltonian_tautology(self):
        m=EinsteinTangent(mass=3.,A=.5,Sigma_ref=.0173196421,orientation=-1)
        sol=m.solution(n=17)
        dx=1e-5
        for i in (2,8,14):
            x=float(sol.t[i]);y=sol.y[:,i];dy=m.derivative(x,y)
            yp=y+dx*dy;ym=y-dx*dy
            Hplus=m.field(x+dx,float(yp[0]),float(yp[1]))[1]
            Hminus=m.field(x-dx,float(ym[0]),float(ym[1]))[1]
            measured=(Hplus-Hminus)/(2*dx)
            expected=m.raychaudhuri(x,y)
            self.assertLess(abs(measured/expected-1),1e-8)

    def test_energy_work_integral_with_nontrivial_shear(self):
        m=EinsteinTangent(mass=3.,A=.6,Sigma_ref=.02,orientation=-1)
        sol=m.solution(n=1401)
        vals=[]
        for x,b,v in zip(sol.t,sol.y[0],sol.y[1]):
            p,H,_,_=m.field(float(x),float(b),float(v))
            vals.append((p.rho,3*(p.rho+p.pbar)+2*m.href*v*p.delta/H))
        vals=np.array(vals)
        residual=vals[-1,0]-vals[0,0]+simpson(vals[:,1],x=sol.t)
        self.assertLess(abs(residual),5e-10)

    def test_resolution_convergence_real_ode(self):
        model=EinsteinTangent(mass=3.,A=.7,Sigma_ref=.012,orientation=1)
        ref=model.solution(rtol=6e-13,atol=3e-14,n=61)
        low=model.solution(rtol=1e-9,atol=1e-12,n=61)
        # Endpoints of b,s,sensitivity are independent of t_eval density.
        self.assertLess(abs(ref.y[0,-1]-low.y[0,-1]),2e-10)
        self.assertLess(abs(ref.y[1,-1]-low.y[1,-1]),2e-10)
        self.assertLess(abs(ref.y[3,-1]-low.y[3,-1]),2e-10)

    def test_initial_quadrupole_tangent_source(self):
        m=EinsteinTangent(mass=30.,A=0,Sigma_ref=0)
        dy=m.derivative(0,m.y0)
        expected=m.g*m.fd.initial_v2/(5*m.href*m.href)
        self.assertLess(abs(dy[4]/expected-1),3e-14)

if __name__=='__main__': unittest.main(verbosity=2)
