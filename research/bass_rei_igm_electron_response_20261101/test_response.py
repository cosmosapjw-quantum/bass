"""Scientific controls on BASS original KM2N electron-susceptibility operator."""
from __future__ import annotations
import math,os,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import response_kernel as r
class ModelTests(unittest.TestCase):
    def test_immutable_authority(self):
        self.assertEqual(r.OWNER,'4137f942d2a95999f4e6627b71042e98f7afc1b7')
        self.assertEqual((r.PANELS,r.GL,r.END),(40,8,.25))
    def test_constant_hazard_probability(self):
        for h in [.1,1.,5.,40.]:
            U=.25;p=-math.expm1(-h*U)
            self.assertAlmostEqual(p,1-math.exp(-h*U),delta=2e-15)
    def test_analytic_last_event_time(self):
        h=5.;U=.25
        exact=U/(-math.expm1(-h*U))-1/h
        x,w=np.polynomial.legendre.leggauss(24);u=U*(1+x)/2
        g=h*np.exp(-h*(U-u))
        self.assertAlmostEqual(float(np.sum(w*U/2*u*g)/(-math.expm1(-h*U))),exact,delta=1e-14)
    def test_constant_hazard_analytic_mean_derivative(self):
        h=7.;U=.25
        fun=lambda eps:U/(-math.expm1(-(1+eps)*h*U))-1/((1+eps)*h)
        e=1e-5;fd=(fun(e)-fun(-e))/(2*e)
        a=math.exp(-h*U);exact=h*(1/h**2-U**2*a/(1-a)**2)
        self.assertAlmostEqual(fd,exact,delta=4e-11)
    def test_window_endpoint_probability_variation(self):
        tau=3.2;dp=.17;e=1e-5
        P=lambda eps:-math.expm1(-(tau+eps*dp))
        self.assertAlmostEqual((P(e)-P(-e))/(2*e),math.exp(-tau)*dp,delta=2e-11)
    def test_retarded_survival_sign(self):
        h,tau,fut=3.,2.,.3;e=1e-5
        g=lambda eps:(1+eps)*h*math.exp(-tau-eps*fut)
        self.assertAlmostEqual((g(e)-g(-e))/(2*e),h*math.exp(-tau)*(1-fut),delta=1e-10)
    def test_rei_HHe_contract_only(self):
        y=.079;x=np.array([.9,.4,.05]);dx=np.array([.001,-.002,.0004])
        electron=x[0]+y*(x[1]+2*x[2])
        predicted=(dx[0]+y*(dx[1]+2*dx[2]))/electron
        actual=((x[0]+dx[0]+y*(x[1]+dx[1]+2*(x[2]+dx[2])))/electron)-1
        self.assertAlmostEqual(predicted,actual,delta=2e-16)
    def test_source_tamper_fail_closed(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'bad.zip';f.write_bytes(b'forged')
            with self.assertRaisesRegex(ValueError,'original outer SHA'):
                r.source(f)
    def test_original_source_50_members(self):
        z=r.source(os.environ['BASS_ORIGINAL_S2'])
        self.assertIn('MANIFEST.json',z.namelist())
    def test_original_GL12(self):
        import tempfile
        z=r.source(os.environ['BASS_ORIGINAL_S2'])
        with tempfile.TemporaryDirectory() as d:
            x=r.compute(z,12,d)
            self.assertEqual(x['rays'],288)
            self.assertLess(x['max_panel_actual_source_fd_error'],1e-10)
            self.assertAlmostEqual(x['tau_mean_sky'],7.283254163753941,delta=1e-12)
    def test_original_GL16_and_sign_change(self):
        import tempfile
        z=r.source(os.environ['BASS_ORIGINAL_S2'])
        with tempfile.TemporaryDirectory() as d:
            x=r.compute(z,16,d)
            self.assertEqual(x['rays'],512)
            self.assertLess(x['max_tau_original_gauss_error'],1e-12)
            self.assertLess(x['d_mean_u_d_earliest_panel_sky'],0)
            self.assertGreater(x['d_mean_u_d_latest_panel_sky'],0)
            self.assertAlmostEqual(x['conditional_last_scatter_mean_u_sky'],.1785083546659884,delta=1e-12)
if __name__=='__main__':unittest.main()
