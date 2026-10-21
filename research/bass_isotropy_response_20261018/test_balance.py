import unittest
import numpy as np
from numpy.polynomial.legendre import leggauss
from angular_balance import balance

def rule(b,n):
    m,w=leggauss(n)
    R=np.sqrt(np.exp(2*b)*(1-m*m)+np.exp(-4*b)*m*m)
    q=w/R**3;q/=q.sum()
    return np.exp(-2*b)*m/R,q

class BalanceTests(unittest.TestCase):
    def test_geometric_false_quadrupole_removed(self):
        for b in [-.2,.2,.4]:
            mu,q=rule(b,8);p=(3*mu*mu-1)/2
            self.assertGreater(abs(q@p),1e-8)
            a=balance(mu,q)
            self.assertLess(abs(a@p),3.1e-15)
            self.assertLess(abs(a.sum()-1),5e-16)
            self.assertTrue(np.all(a>0))
    def test_infeasible_positive_support_rejected(self):
        for b in [-.6,.6,1.]:
            mu,q=rule(b,8)
            with self.assertRaisesRegex(ValueError,'INFEASIBLE_ANGULAR_SUPPORT'):
                balance(mu,q)
    def test_asymmetric_source_not_silently_isotropized(self):
        mu,q=rule(.2,8);q=q*(1+.1*mu);q/=q.sum()
        with self.assertRaisesRegex(ValueError,'REFLECTION'):
            balance(mu,q)
    def test_invalid_prior_rejected(self):
        mu,q=rule(0,8)
        for k in [-1.,0.,float('nan')]:
            z=q.copy();z[0]=k
            with self.assertRaises(ValueError):balance(mu,z)
    def test_equilibrium_prior_unchanged(self):
        mu,q=rule(0,16)
        np.testing.assert_allclose(balance(mu,q),q,atol=2e-16,rtol=0)
    def test_parity_and_positive_pressures(self):
        mu,q=rule(.3,16);a=balance(mu,q)
        self.assertLess(abs(a@mu),1e-15)
        self.assertLess(np.max(abs(a-a[::-1])),1e-15)
        self.assertGreater(float(a@(mu*mu)),0)
    def test_idempotent(self):
        mu,q=rule(.2,8);a=balance(mu,q)
        np.testing.assert_allclose(balance(mu,a),a,atol=5e-16,rtol=0)

if __name__=='__main__':unittest.main(verbosity=2)
