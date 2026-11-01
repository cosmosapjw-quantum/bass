"""Original Type-II chart source model, independent nonproduction verifier."""
import math, unittest
import verify_original_fixture as v

class TypeIIPreflightTests(unittest.TestCase):
    def test_all_401_original_like_states(self):
        t,s=v.rk4_fixture();self.assertEqual(len(s),401)
        self.assertAlmostEqual(t[-1],.2,places=14)
        for x in s:
            h=v.metric_mock(x)
            recovered=v.decode_mock(h)
            self.assertLess(max(abs(a-b) for a,b in zip(recovered,x)),2e-14)
            om,raw,b=v.from_four(x[0],x[1],x[3],x[4]);self.assertLess(abs(raw-x[2]),1e-12)
            self.assertGreater(om,0)
    def test_actual_first_original_source_state(self):
        y=v.source_rhs(v.INITIAL)
        expected=(-0.0336177132003016,0.0245403512235811,0.036593148186233285,
             0.01170272685712611,-0.016845446584938688)
        self.assertLess(max(abs(a-b) for a,b in zip(y,expected)),3e-14)
    def test_analytic_quadratic_positive_root(self):
        for n1 in (.1,.3,.8,1.0):
            for v2 in (-.5,-.3,0,.02,.1,.5):
                om,s13,b=v.from_four(.1,.02,n1,v2,1.3)
                a=1-.1**2-.02**2-n1**2/12
                self.assertLess(abs(om+b*om*om-a),5e-14)
                self.assertLess(abs(v.gauss_omega((.1,.02,s13,n1,v2))-om),5e-14)
    def test_wrong_shear_sign_and_normalization(self):
        h=v.metric_mock(v.INITIAL);h['shear5'][3]*=-1
        with self.assertRaisesRegex(v.BadPhysicalState,'CODAZZI'):v.decode_mock(h)
        h=v.metric_mock(v.INITIAL);h['shear5'][3]/=math.sqrt(3)
        with self.assertRaisesRegex(v.BadPhysicalState,'CODAZZI'):v.decode_mock(h)
    def test_no_typeII_at_n1_zero(self):
        with self.assertRaisesRegex(v.BadPhysicalState,'TYPE_I_BOUNDARY'):
            v.from_four(0,0,0,.01)
    def test_nonzero_off_slice_rejected(self):
        h=v.metric_mock(v.INITIAL);h['v3'][0]=.01
        with self.assertRaisesRegex(v.BadPhysicalState,'OFF_SLICE'):v.decode_mock(h)
    def test_wrong_units_rejected(self):
        h=v.metric_mock(v.INITIAL);h['norm']='RINGSTROM'
        with self.assertRaisesRegex(v.BadPhysicalState,'WRONG_CONVENTION'):v.decode_mock(h)
    def test_wrong_omega_rejected(self):
        h=v.metric_mock(v.INITIAL);h['omega']+=.01
        with self.assertRaisesRegex(v.BadPhysicalState,'GAUSS'):v.decode_mock(h)
    def test_hubble_clock_and_rate_dimensional(self):
        c=299792458.; ne=1e8; sigma=6.6524587321e-29; H=2e-14
        nu=ne*sigma*c/H
        self.assertAlmostEqual(nu,ne*sigma*c/H)
        self.assertAlmostEqual(1e13*H,.2)
        self.assertGreater(abs(nu*(1-.1*.6)-nu*(1-.1*.6)**2),1.0)
    def test_bad_velocity_domain(self):
        with self.assertRaisesRegex(v.BadPhysicalState,'TACHYONIC'):
            v.from_four(.1,.1,.8,1.0)

if __name__=='__main__':unittest.main()