"""Independent small tests for the constrained angular rule, not fluid closure."""
import math
import unittest
import numpy as np
import mpmath as mp
from angular_balance import project,balance,lrs_rule,support_interval

class PropertyTests(unittest.TestCase):
    def test_support_edges_and_signs(self):
        for n in [4,8,16,32,64]:
            lo,hi=support_interval(n)
            for b in [lo-1e-4,hi+1e-4]:
                mu,q=lrs_rule(b,n)
                with self.assertRaisesRegex(ValueError,'INFEASIBLE'):
                    balance(mu,q)
            for b in [lo+.04,hi-.04]:
                mu,q=lrs_rule(b,n);a=balance(mu,q)
                self.assertLess(abs(a@((3*mu**2-1)/2)),3.2e-15)
    def test_variance_and_multiplier_stationarity(self):
        mu,q=lrs_rule(.4,16);s=project(mu,q);p=(3*mu**2-1)/2
        logs=np.log(s.weights/q)-s.multiplier*p
        self.assertLess(float(np.ptp(logs)),1e-14)
        self.assertGreater(s.variance,0)
        self.assertGreater(s.kl,-2e-15)
    def test_KL_pythagorean_feasible_perturbation(self):
        mu,q=lrs_rule(.2,16);s=project(mu,q);p=(3*mu**2-1)/2
        # Null space of the two moment constraints, paired to keep reflection.
        v=np.cos(np.arange(len(q)));v=(v+v[::-1])/2
        A=np.vstack([np.ones(len(q)),p]);v-=A.T@np.linalg.solve(A@A.T,A@v)
        v*=.05*np.min(s.weights)/np.max(abs(v));r=s.weights+v
        self.assertGreater(r.min(),0)
        self.assertLess(np.max(abs(A@r-np.array([1.,0.]))),4e-15)
        kl=lambda u,v: math.fsum(u*np.log(u/v))
        self.assertLess(abs(kl(r,q)-kl(r,s.weights)-kl(s.weights,q)),2e-15)
    def test_mp70_multiplier_reference(self):
        mp.mp.dps=70
        for b,n in [(.2,8),(-.2,8),(.4,16),(.6,16)]:
            mu,q=lrs_rule(b,n);s=project(mu,q)
            p=[mp.mpf(float(v)) for v in ((3*mu**2-1)/2)]
            qq=[mp.mpf(float(v)) for v in q]
            f=lambda l:sum(w*z*mp.exp(l*z) for w,z in zip(qq,p))
            l=mp.findroot(f,(mp.mpf('-.5'),mp.mpf('.5')))
            un=[w*mp.exp(l*z) for w,z in zip(qq,p)];norm=sum(un)
            ref=np.array([float(v/norm) for v in un])
            self.assertLess(np.max(abs(s.weights-ref)),5e-14)
    def test_high_moment_not_erased_by_P2(self):
        mu,q=lrs_rule(.4,8);a=balance(mu,q)
        p4=(35*mu**4-30*mu**2+3)/8
        self.assertGreater(abs(a@p4),1e-3)
        self.assertLess(abs(a@((3*mu**2-1)/2)),4e-15)
    def test_factorized_source_number_energy_pressure(self):
        mu,q=lrs_rule(.2,8);a=balance(mu,q)
        E=np.array([14.,24.,54.,90.]);N=np.array([1.,3.,4.,2.])
        stock=a[:,None]*N
        self.assertAlmostEqual(float(stock.sum()),float(N.sum()),13)
        energy=stock@E
        self.assertAlmostEqual(float(energy.sum()),float(N@E),11)
        self.assertLess(abs(energy@((3*mu**2-1)/2))/float(energy.sum()),4e-15)
    def test_inputs_not_mutated(self):
        mu,q=lrs_rule(.2,16);m0=mu.copy();q0=q.copy();balance(mu,q)
        np.testing.assert_array_equal(mu,m0);np.testing.assert_array_equal(q,q0)
    def test_tolerance_and_domain_controls(self):
        mu,q=lrs_rule(.2,8)
        for tol in [-1,0,float('nan'),1e-4]:
            with self.assertRaises(ValueError):project(mu,q,atol=tol)
        for n in [True,3,4.5,513]:
            with self.assertRaises(ValueError):lrs_rule(.2,n)

if __name__=='__main__':unittest.main(verbosity=2)
