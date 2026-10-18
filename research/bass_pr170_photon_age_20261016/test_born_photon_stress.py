"""Focused independent checks for exact non-tilted Bianchi-I photon age cohorts."""
import math
import unittest
import numpy as np
from born_photon_stress import (angular_f_delta,angular_direct,small_d_series,
                                BornIsotropicRadiation,XMAX)


def smooth_b(x,amp=0.12):
    x=np.asarray(x)
    return amp*(0.75*np.sin(2.3*x)+0.35*x)


def smooth_bp(x,amp=0.12):
    x=np.asarray(x)
    return amp*(0.75*2.3*np.cos(2.3*x)+0.35)


def positive_s(x):
    x=np.asarray(x)
    return 0.22*(1+0.25*np.sin(3.7*x)+0.1*x)


class PhotonSourceTests(unittest.TestCase):
    def profile(self,amp=0.12,rho0=.9,n_birth=64,n_mu=64):
        return BornIsotropicRadiation(lambda x:smooth_b(x,amp),positive_s,
            rho_old=rho0,n_birth=n_birth,n_mu=n_mu,
            bprime=lambda x:smooth_bp(x,amp))

    def test_zero_anisotropy_has_exact_zero_pressure(self):
        self.assertEqual(angular_f_delta(0.0),(1.,0.))
        self.assertEqual(angular_f_delta(np.zeros(3))[1].tolist(),[0.]*3)

    def test_near_zero_stress_rationalization(self):
        for d in (-1e-15,1e-15,1e-13,-1e-13):
            f,delta=angular_f_delta(d,32)
            self.assertEqual(f,1.0)
            self.assertAlmostEqual(delta/d,-1.6,delta=3e-12)

    def test_direct_quadrature_finite_anisotropy(self):
        for d in (-.32,-.12,.04,.2,.34):
            F,D=angular_f_delta(d,64)
            f,dr=angular_direct(d,128)
            self.assertLess(abs(F-f),3e-14)
            self.assertLess(abs(D-dr),5e-14)

    def test_massless_source_strict_stress_opposes_deformation(self):
        for d in np.linspace(-.7,.7,31):
            F,D=angular_f_delta(float(d),96)
            self.assertGreaterEqual(F,1-5e-15)
            if d!=0:self.assertLess(D*d,0.)

    def test_stress_monotonicity(self):
        ds=np.linspace(-.6,.6,105)
        _,D=angular_f_delta(ds,96)
        self.assertTrue(np.all(np.diff(D)<0.))

    def test_small_d_taylor_coefficients(self):
        for d in (-.015,-.007,.008,.016):
            F,D=angular_f_delta(d,96)
            f,t=small_d_series(d)
            self.assertLess(abs(F-f),2.3*d**4)
            self.assertLess(abs(D-t),8.*abs(d)**3)

    def test_rho_exact_over_isotropic_energy(self):
        model=self.profile()
        for x in np.linspace(0.,XMAX,14):
            p=model.point(float(x))
            self.assertGreaterEqual(p.rho+2e-14,p.isotropic_rho)
            self.assertGreater(p.rho,0.)

    def test_source_at_birth_has_zero_quadrupole(self):
        model=BornIsotropicRadiation(smooth_b,positive_s,rho_old=0.,bprime=smooth_bp)
        p=model.point(0.)
        self.assertEqual((p.rho,p.delta,p.isotropic_rho,p.memory_b),(0.,0.,0.,0.))

    def test_constant_b_exact_flrw(self):
        model=BornIsotropicRadiation(lambda x:np.asarray(x)*0+.2,
              lambda x:np.asarray(x)*0+.3,rho_old=2.5,bprime=lambda x:np.asarray(x)*0.)
        for x in (.1,.5,1.):
            p=model.point(x)
            expected=2.5*math.exp(-4*x)+.3*(-math.expm1(-4*x))/4
            self.assertAlmostEqual(p.rho,expected,delta=5e-13)
            self.assertLess(abs(p.delta),1e-15)

    def test_ode_two_moments_vs_independent_age_quadrature(self):
        model=self.profile()
        xs=np.linspace(0,XMAX,15)
        sol=model.memory_ode(xs)
        for j,x in enumerate(xs):
            pt=model.point(float(x))
            self.assertAlmostEqual(pt.isotropic_rho,sol.y[0,j],delta=4e-12)
            self.assertAlmostEqual(pt.memory_b,sol.y[1,j],delta=4e-12)
            self.assertAlmostEqual(pt.delta_linear,-8/5*(pt.isotropic_rho*pt.b-pt.memory_b),delta=1e-15)

    def test_energy_continuity_finite_difference(self):
        model=self.profile()
        for x in (.1,.3,.65,1.1):
            h=6e-6
            deriv=(model.point(x+h).rho-model.point(x-h).rho)/(2*h)
            self.assertLess(abs(deriv-model.energy_rhs(x)),4e-9)

    def test_whole_history_physical_volume_energy_ledger(self):
        model=self.profile(n_birth=72,n_mu=64)
        q=model.ledger(1.1,80)
        self.assertLess(abs(q['energy_residual']),7e-11)
        self.assertGreater(q['emission_integral'],0.)

    def test_linear_error_is_second_order(self):
        diff=[]
        for amp in (.08,.04,.02):
            p=self.profile(amp=amp).point(.83)
            diff.append(abs(p.delta-p.delta_linear))
        self.assertGreater(diff[0]/diff[1],3.65)
        self.assertGreater(diff[1]/diff[2],3.8)

    def test_quadratic_stress_improves_accuracy(self):
        p=self.profile(amp=.1).point(.94)
        self.assertLess(abs(p.delta-p.delta_quadratic),abs(p.delta-p.delta_linear)*0.15)
        self.assertLess(abs(p.rho-p.rho_quadratic),1e-3)

    def test_refinement_birth_integral(self):
        refs=self.profile(n_birth=192,n_mu=128).point(1.25)
        errors=[]
        for n in (8,12,16):
            p=self.profile(n_birth=n,n_mu=128).point(1.25)
            errors.append(max(abs(p.rho-refs.rho),abs(p.delta-refs.delta)))
        self.assertLess(errors[-1],1.0e-12)
        self.assertLess(errors[1],errors[0])

    def test_refinement_angular_integral(self):
        d=.36
        f,d0=angular_f_delta(d,256)
        e16=abs(angular_f_delta(d,16)[1]-d0)
        e32=abs(angular_f_delta(d,32)[1]-d0)
        self.assertLess(e32,1e-10)
        self.assertLess(e32,e16)

    def test_source_shape_and_sign_rejections(self):
        with self.assertRaises(ValueError):BornIsotropicRadiation(smooth_b,lambda x:-np.ones_like(x)).point(.2)
        with self.assertRaises(ValueError):BornIsotropicRadiation(smooth_b,lambda x:np.ones((2,2))).point(.2)

    def test_b_shape_and_nan_rejections(self):
        with self.assertRaises(ValueError):BornIsotropicRadiation(lambda x:np.array([float('nan')]),positive_s)
        with self.assertRaises(ValueError):angular_f_delta(float('nan'))
        with self.assertRaises(ValueError):angular_f_delta(2.1)

    def test_invalid_mu_and_birth_orders(self):
        with self.assertRaises(ValueError):angular_f_delta(.1,2)
        with self.assertRaises(ValueError):BornIsotropicRadiation(smooth_b,positive_s,n_birth=3)

    def test_momentum_pressure_positive(self):
        model=self.profile()
        for x in (.1,.5,1.2):
            p=model.point(x)
            self.assertGreaterEqual((p.rho-p.delta)/3,-1e-14)
            self.assertGreaterEqual((p.rho+2*p.delta)/3,-1e-14)

if __name__=='__main__':unittest.main()
