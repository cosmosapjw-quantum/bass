"""Independent regression of stable Einstein-Vlasov pressure anisotropy."""
import math
import pathlib
import sys
import unittest

import numpy as np

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from stable_moments import StableMassiveMoments
from joint_kinetic import KineticGammaNuMassive,source_lock


class StablePressureDifferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=StableMassiveMoments(30.,angular_n=32)

    def test_isotropic_exact_zero_vs_legacy_residual(self):
        new=self.m.delta_p_stable(.5,0.,0.)
        old=self.m.evaluate(.5,0.,0.)
        self.assertEqual(new,0.)
        self.assertNotEqual(old[2]-old[1],0.)

    def test_small_shear_linear_response_and_sign(self):
        d=self.m.initial_linear_susceptibility(.5)
        self.assertLess(d,0)
        for b in (1e-16,1e-14,1e-12,1e-10,1e-8,-1e-12):
            delta=self.m.delta_p_stable(.5,b,0.)
            self.assertLess(abs(delta/(d*b)-1),max(3e-8,25*abs(b)))
        # At b=1e-16 the legacy pressure subtraction has the WRONG SIGN.
        pp,pa=self.m.evaluate(.5,1e-16,0.)[1:]
        self.assertGreater(pa-pp,0)
        self.assertLess(self.m.delta_p_stable(.5,1e-16,0.),0)

    def test_initial_quadrupole_analytic(self):
        x=.5
        r=math.exp(-x)
        k=(r*self.m.q)**2
        e0=np.hypot(self.m.mass,np.sqrt(k))
        factor=r**3*np.sum(self.m.rw/self.m.norm*k/e0)
        for amp in (-.7,0.,.5,1.):
            delta=self.m.delta_p_stable(x,0,amp)
            self.assertLess(abs(delta-amp*factor/5),3e-17)

    def test_finite_anisotropy_parity_old_source(self):
        for x,b,A in ((0.,.06,.5),(.8,-.02,.1),(.5,.008,-.7)):
            rho,pp,pa,delta=self.m.evaluate_with_delta(x,b,A)
            old=self.m.evaluate(x,b,A)
            np.testing.assert_allclose([rho,pp,pa],old,rtol=6e-14,atol=3e-15)
            self.assertLess(abs(delta-(pa-pp)),3e-16)
            self.assertGreater(rho,0)
            self.assertGreater(pp,0)
            self.assertGreater(pa,0)

    def test_chunked_batch_matches_scalar(self):
        x=np.linspace(0,1.5,17)
        b=np.linspace(-.025,.025,17)
        arr=self.m.evaluate_with_delta(x,b,.4,chunk=4)
        for i in range(17):
            row=self.m.evaluate_with_delta(float(x[i]),float(b[i]),.4)
            np.testing.assert_allclose([z[i] for z in arr],row,atol=3e-15,rtol=4e-14)
        with self.assertRaises(ValueError):
            self.m.evaluate_with_delta(np.array([1.,2.]),np.array([1.]))

    def test_integrated_optin_rei_source_stays_finite(self):
        src=source_lock()
        kwargs=dict(Sigma_ref=0.,orientation=0,kappa_gamma=.2,kappa_nu=.2,
                    massive_fraction=.1,massive_A=.5,m_over_Tref=30.,ellmax=8)
        old=KineticGammaNuMassive(src,**kwargs)
        new=KineticGammaNuMassive(src,**kwargs,stable_massive_pi=True)
        po,vo,_=old.integrate(n=15,rtol=2e-10,atol=4e-13)
        pn,vn,_=new.integrate(n=15,rtol=2e-10,atol=4e-13)
        self.assertLess(abs(vn[-1]["Sigma"]-vo[-1]["Sigma"]),4e-12)
        self.assertLess(abs(vn[-1]["H"]-vo[-1]["H"])/vo[-1]["H"],4e-12)
        self.assertEqual(new.fields(0,new.initial_state())["pi_massive_norm"]>0,True)
        self.assertEqual(new.initial_tensors()["massive_pi_evaluation"],"stable_inverse_energy")
        self.assertEqual(old.initial_tensors()["massive_pi_evaluation"],"legacy_pressure_subtraction")


if __name__=="__main__":
    unittest.main(verbosity=2)
