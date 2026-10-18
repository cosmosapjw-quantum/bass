import unittest
import numpy as np
from source_oracle import rays

class RaysTests(unittest.TestCase):
    def test_uses_one_local_solid_angle_jacobian(self):
        _,mu,w,j=rays(.4,.2,32)
        self.assertLess(abs(np.dot(w,(3*mu*mu-1)/2)),2e-13)
        mu0,_=np.polynomial.legendre.leggauss(32)
        self.assertGreater(np.max(abs(mu-mu0)),.1)
if __name__=='__main__':unittest.main(verbosity=2)

from dataclasses import replace
from scipy.integrate import quad
from source_oracle import Case,predict,spectral,moments,shape,verify_source_files,KT,AREF
import math
class SourceTests(unittest.TestCase):
    def setUp(self):self.c=Case('signed',.5,.01,1e-16,-1e-19,1e11)
    def test_source_pins(self):self.assertEqual(len(verify_source_files()),3)
    def test_exact_kt_constants(self):self.assertEqual(KT,(1.380649e-16/1.602176634e-12)*50000)
    def test_monopole_normalization_is_not_isotropic_quadrupole(self):
        _,mu,w,_=rays(.8,.2,8)
        self.assertAlmostEqual(float(sum(w)),1,14)
        self.assertGreater(abs(float(w@((3*mu*mu-1)/2))),1e-3)
    def test_continuum_angular_jacobian(self):
        for b in (-.4,-.05,0,.05,.4):
            def j(t):return (math.exp(2*b)*(1-t*t)+math.exp(-4*b)*t*t)**-1.5
            def m(t):return t*math.exp(-2*b)*(j(t)**(1/3))
            self.assertLess(abs(quad(j,-1,1,epsabs=3e-13,epsrel=3e-13)[0]/2-1),2e-12)
            self.assertLess(abs(quad(lambda t:j(t)*(3*m(t)**2-1)/2,-1,1,epsabs=3e-13,epsrel=3e-13)[0]/2),2e-12)
    def test_missing_and_double_jacobian_negative_controls(self):
        b=1e-5;mu,w= np.polynomial.legendre.leggauss(64);w=w/2
        R=np.sqrt(np.exp(2*b)*(1-mu*mu)+np.exp(-4*b)*mu*mu);m=mu*np.exp(-2*b)/R
        p=(3*m*m-1)/2
        for power,expect in ((0,-6/5),(2,6/5)):
            weights=w*R**(-3*power);weights/=sum(weights)
            self.assertLess(abs(float(weights@p)/b-expect),4e-5)
    def test_gl_refinement(self):
        defects=[]
        for n in (8,16,32):
            _,m,w,_=rays(.8,.2,n);defects.append(abs(float(w@((3*m*m-1)/2))))
        self.assertGreater(defects[0],100*defects[1]);self.assertLess(defects[2],2e-13)
    def test_isotropic_reference_spectral_matches_quad(self):
        p=predict(replace(self.c,x=0,b=0))
        exact=quad(lambda e:float(shape(e))*e,13.6,100,epsabs=1e-10)[0]/quad(lambda e:float(shape(e)),13.6,100,epsabs=1e-10)[0]
        self.assertLess(abs(p['source_mean_energy']/exact-1),2e-10)
        self.assertLess(abs(p['delta'])/p['u'],3e-14)
    def test_injection_positive_support_and_moments(self):
        p=predict(self.c)
        self.assertGreater(p['n'],0);self.assertGreater(p['u'],13.6*p['n']);self.assertLess(p['u'],100*p['n'])
        self.assertLess(abs(p['dipole'])/p['u'],1e-14)
    def test_dt_linearity(self):
        p=predict(self.c);q=predict(replace(self.c,dt=2*self.c.dt))
        for k in ('n','u','delta'):self.assertAlmostEqual(q[k],2*p[k],delta=abs(p['u'])*2e-14)
    def test_per_h_vs_volume_density_once(self):
        p=predict(self.c);q=predict(replace(self.c,nh0=2*self.c.nh0))
        self.assertAlmostEqual(q['n'],p['n']/2,delta=1e-18)
        self.assertAlmostEqual(q['S_ev_cm3_per_x'],p['S_ev_cm3_per_x'],delta=1e-16)
    def test_zero_dt(self):
        p=predict(replace(self.c,dt=0));self.assertEqual((p['n'],p['u'],p['delta']),(0,0,0))
    def test_outside_support_reject(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_OUTSIDE_GRID'):predict(replace(self.c,x=0,b=.2))
    def test_nonfinite_and_resolution_domain(self):
        for kw in ({'H':float('nan')},{'nh0':0},{'nmu':12},{'dt':-1},{'b':.5},{'nseg':True}):
            with self.assertRaises(ValueError):predict(replace(self.c,**kw))
    def test_grid_preserves_scalar_source_to_fixed_precision(self):
        for ne in (32,64,128):
            p=predict(replace(self.c,nenergy=ne))
            self.assertLess(abs(p['n_relative_source_error']),2e-10)
            self.assertLess(abs(p['u_relative_source_error']),2e-10)
