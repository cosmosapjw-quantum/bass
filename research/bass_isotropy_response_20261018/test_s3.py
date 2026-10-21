"""Independent finite-support, optimization, and collisionless-response tests."""
import math
import unittest
import numpy as np
from scipy.optimize import root
from angular_balance import lrs_rule,project as project2
from angular_p24 import project,feasibility,legendre24
from shear_response import kernels,response,moments,derivative_diagnostics


class Projection24Tests(unittest.TestCase):
    def test_unique_three_z_analytic_solution(self):
        m=np.array([-1,-math.sqrt(.5),0,math.sqrt(.5),1.])
        r=project(m,np.ones(5));expected=np.array([1/30,4/15,2/5,4/15,1/30])
        np.testing.assert_allclose(r.weights,expected,atol=9e-15,rtol=0)

    def test_independent_two_variable_solver(self):
        for b,n in [(.2,8),(.3,8),(-.3,8),(.4,16),(.8,64)]:
            mu,q=lrs_rule(b,n);r=project(mu,q);p2,p4=legendre24(mu)
            P=np.array([p2,p4]).T
            def rhs(lam):
                log=np.log(q)+P@lam;v=np.exp(log-log.max());v/=v.sum()
                return P.T@v
            ref=root(rhs,[0,0],method='hybr',options={'xtol':1e-11})
            self.assertLess(max(abs(rhs(ref.x))),8e-15)
            log=np.log(q)+P@ref.x;w=np.exp(log-log.max());w/=w.sum()
            self.assertLess(max(abs(w-r.weights)),2e-14)

    def test_stationarity_and_KL_pythagorean(self):
        mu,q=lrs_rule(.2,16);r=project(mu,q);p2,p4=legendre24(mu)
        P=np.vstack([np.ones(len(q)),p2,p4])
        v=np.cos(np.arange(len(q)));v=(v+v[::-1])/2
        v-=P.T@np.linalg.solve(P@P.T,P@v)
        v*=.04*r.weights.min()/max(abs(v));w=r.weights+v
        self.assertGreater(w.min(),0)
        self.assertLess(max(abs(P@w-[1,0,0])),4e-15)
        KL=lambda a,b:math.fsum(a*np.log(a/b))
        self.assertLess(abs(KL(w,q)-KL(w,r.weights)-KL(r.weights,q)),3e-15)
        logs=np.log(r.weights/q)-r.multipliers@np.array([p2,p4])
        self.assertLess(float(np.ptp(logs)),3e-15)

    def test_same_support_P2_feasible_P24_infeasible(self):
        mu,q=lrs_rule(.4,8);self.assertLess(abs(project2(mu,q).after),3e-15)
        self.assertEqual(feasibility(mu).status,'INFEASIBLE_P24_UPPER')
        with self.assertRaisesRegex(ValueError,'INFEASIBLE_P24_UPPER'):project(mu,q)

    def test_explicit_lower_and_upper_infeasibility(self):
        for z,status in [([0,.7,1],'INFEASIBLE_P24_LOWER'),([0,.25,.5],'INFEASIBLE_P24_UPPER')]:
            mu=np.sort(np.unique(np.r_[-np.sqrt(z),np.sqrt(z)]))
            self.assertEqual(feasibility(mu).status,status)
            with self.assertRaisesRegex(ValueError,status):project(mu,np.ones(len(mu)))

    def test_boundary_and_rank1_remain_unresolved(self):
        # Exact boundary examples; no zero-weight repair in floating code.
        for z in [[0,.6,1],[0,.3,.6]]:
            mu=np.sort(np.unique(np.r_[-np.sqrt(z),np.sqrt(z)]))
            with self.assertRaisesRegex(ArithmeticError,'UNRESOLVED_NEAR_BOUNDARY'):
                project(mu,np.ones(len(mu)))
        mu,q=lrs_rule(0.,4)
        self.assertEqual(feasibility(mu).status,'FEASIBILITY_UNRESOLVED_RANK1')
        with self.assertRaisesRegex(ArithmeticError,'UNRESOLVED_RANK1'):project(mu,q)

    def test_reflection_not_physical_isotropy(self):
        mu,q=lrs_rule(.2,8)
        with self.assertRaisesRegex(ValueError,'REFLECTION'):project(mu,q*(1+.1*mu))

    def test_input_and_tolerance_contract(self):
        mu,q=lrs_rule(.2,8)
        for tol in [0,-1,float('nan'),1e-14,1e-10]:
            with self.assertRaises(ValueError):project(mu,q,atol=tol)
        for bad in [0,-1,float('nan')]:
            z=q.copy();z[0]=bad
            with self.assertRaises(ValueError):project(mu,z)
        z=q.copy();z[[0,-1]]=np.nextafter(0.,1.);z[[1,-2]]=1e308
        with self.assertRaisesRegex(ArithmeticError,'POSITIVE_SUPPORT_LOSS'):project(mu,z)

    def test_positive_parity_idempotence_inputs_preserved(self):
        mu,q=lrs_rule(.3,8);m0,q0=mu.copy(),q.copy();r=project(mu,q)
        self.assertTrue(np.all(r.weights>0));self.assertLess(max(abs(r.residuals)),3e-15)
        self.assertLess(max(abs(r.weights-r.weights[::-1])),5e-14)
        np.testing.assert_array_equal(project(mu,r.weights).weights,r.weights)
        np.testing.assert_array_equal(mu,m0);np.testing.assert_array_equal(q,q0)


class ShearResponseTests(unittest.TestCase):
    def test_P2_only_exact_slope_counterexample(self):
        m=np.array([-math.sqrt(.5),-math.sqrt(1/6),math.sqrt(1/6),math.sqrt(.5)])
        w=np.ones(4)/4;diag=derivative_diagnostics(m,w);h=1e-5
        measured=(response(h,m,w)['A']-response(-h,m,w)['A'])/(2*h)
        self.assertLess(abs(diag['moments'][2]),2e-16)
        self.assertAlmostEqual(diag['moments'][4],-77/288,14)
        self.assertAlmostEqual(diag['A_prime'],-15/8,14)
        self.assertLess(abs(measured+15/8),5e-10)

    def test_P24_exact_curvature_counterexample(self):
        m=np.array([-1,-math.sqrt(.5),0,math.sqrt(.5),1.])
        w=np.array([1/30,4/15,2/5,4/15,1/30]);diag=derivative_diagnostics(m,w)
        self.assertLess(abs(diag['A_prime']+8/5),1e-15)
        self.assertAlmostEqual(diag['moments'][6],-11/80,14)
        self.assertAlmostEqual(diag['A_second'],19/10,14)
        self.assertGreater(abs(diag['A_second']-16/7),.3)

    def test_exact_energy_identity_frozen_birth(self):
        mu,q=lrs_rule(.3,8);w=project(mu,q).weights
        for d in [-.2,-.01,0,.05,.2]:
            h=1e-6;r,D=kernels(d,mu)
            numerical=(kernels(d+h,mu)[0]-kernels(d-h,mu)[0])/(2*h)
            self.assertLess(max(abs(numerical+2*D)),4e-10)
            Fp=(response(d+h,mu,w)['F']-response(d-h,mu,w)['F'])/(2*h)
            self.assertLess(abs(Fp+2*response(d,mu,w)['G']),3e-10)

    def test_normalized_and_birth_energy_denominators(self):
        mu,q=lrs_rule(.3,8);diag=derivative_diagnostics(mu,q);h=1e-5
        fp=(response(h,mu,q)['A']-response(-h,mu,q)['A'])/(2*h)
        self.assertGreater(abs(diag['moments'][2]),1e-3)
        self.assertLess(abs(fp-diag['A_prime']),3e-9)
        self.assertAlmostEqual(diag['A_prime']-diag['G_prime'],2*diag['moments'][2]**2,14)

    def test_response_domain(self):
        for d in [float('nan'),5]:
            with self.assertRaises(ValueError):kernels(d,[0])
        with self.assertRaises(ValueError):response(.1,[-.5,.5],[-1,2])


if __name__=='__main__':unittest.main(verbosity=2)
