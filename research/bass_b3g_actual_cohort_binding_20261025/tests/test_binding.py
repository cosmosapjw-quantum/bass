"""One focused suite. Synthetic metadata/oracles never admit physical inputs."""
from pathlib import Path
import copy
from decimal import Decimal,localcontext
from fractions import Fraction
import math
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from binding import ROOT,birth_moments,bind_birth,read_json,reused_modules,write_json
from transport import diagonal_bound,diagonal_records,determinant_bound,duhamel
from geometry import si_to_core,core_to_si
from readiness import DonorBinding,finite_donor_readiness,native_source_binding,RADIUS_FIELDS


def dexp(value):
    with localcontext() as ctx:
        ctx.prec=70
        return float(Decimal(str(value)).exp())


class BindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.finite,cls.core=reused_modules()

    def test_birth_independent_rational_angular_oracle(self):
        # Isotropic second/fourth moments, computed as exact rational tensors.
        S=np.diag([Fraction(3,10),Fraction(-1,10),Fraction(-1,5)]).astype(float)
        T,pi=birth_moments(S,5.,7.)
        expected=np.array([float(Fraction(35,3)+Fraction(14,3)*v) for v in [Fraction(3,10),Fraction(-1,10),Fraction(-1,5)]])
        np.testing.assert_allclose(np.diag(T[1:,1:]),expected,rtol=3e-16,atol=0)
        self.assertEqual(T[0,0],35.);np.testing.assert_array_equal(T[0,1:],np.zeros(3))
        np.testing.assert_allclose(pi,35*2*S/15,rtol=3e-16,atol=0)
        self.assertLess(pi[2,2],0.)

    def test_actual_saved_birth_is_not_multiplied_by_duration(self):
        fixture=read_json('inputs/b3c/raw/VALIDATION.json')['fixtures'][0]
        receipt=read_json('inputs/b3c/raw/ISO_N256_SOURCE_HISTORY.json')[0]
        row=bind_birth(receipt,fixture,{'test':'saved original receipt'},self.finite)
        self.assertEqual(row['n_b_m3'],receipt['ledger']['down_m3'])
        self.assertEqual(row['T_J_m3'][0,0],fixture['card']['energy_J']*receipt['ledger']['down_m3'])
        self.assertEqual(row['fixed_energy_B3f_ball']['status'],'INPUT_ERROR_UNSPECIFIED')
        self.assertIsNone(row['physical_radii']['eE'])
        bad=copy.deepcopy(receipt);bad['ledger']['up_m3']=1.
        with self.assertRaises(ValueError):bind_birth(bad,fixture,{},self.finite)
        # Last actual birth catches endpoint subtraction versus authoritative dt.
        last=read_json('inputs/b3c/raw/ISO_N256_SOURCE_HISTORY.json')[-1]
        row=bind_birth(last,fixture,{'test':'last actual saved receipt'},self.finite)
        expected=fixture['L_m']*last['source_subflow_duration_tau']/299792458.
        self.assertEqual(row['source_subflow_duration_tau'],last['source_subflow_duration_tau'])
        self.assertLessEqual(abs(row['proper_seconds']/expected-1),512*np.finfo(float).eps)
        self.assertEqual(row['interval_endpoint_subtraction_minus_source_duration_tau'],
            last['interval_end_tau']-last['interval_start_tau']-last['source_subflow_duration_tau'])

    def test_diagonal_finite_bound_decimal_oracle(self):
        a=np.array([-.2,.4,1.1]);e=np.array([.03,.2,.1])
        row=diagonal_bound(a,e)
        expected=max(dexp(-v)*(dexp(r)-1) for v,r in zip(a,e))
        self.assertAlmostEqual(row['eR'],expected,places=15)
        # Exact endpoint perturbation a-e saturates the maximum component bound.
        delta=np.exp(-(a-e))-np.exp(-a)
        self.assertLessEqual(float(np.max(np.abs(delta))),row['eR']*(1+4e-15))
        self.assertGreater(row['eR'],float(np.max(np.exp(-a)*e)))

    def test_transport_domains_and_missing_bound(self):
        self.assertIsNone(diagonal_bound([0,0,0],None)['eR'])
        for a,e in [([0,0],[0,0,0]),([0,0,0],[-1,0,0]),([0,0,0],[0,complex(1),0]),([-1000,0,0],[0,0,0]),([0,0,0],[1000,0,0])]:
            with self.assertRaises(ValueError):diagonal_bound(a,e)
        row=diagonal_records([0,0,0],[.1,0,0],[.2,0,0],provenance='SYNTHETIC analytic test radii')
        self.assertAlmostEqual(row['composed']['eR'],dexp(.3)-1,places=15)
        self.assertEqual(row['physical']['e_i'][0],.1)

    def test_determinant_STF_oracle_and_hypothesis(self):
        row=determinant_bound(.2,.1,beta_exactly_stf=True)
        self.assertAlmostEqual(row['bound'],dexp(-.6)*(dexp(.3)-1),places=15)
        with self.assertRaises(ValueError):determinant_bound(.2,.1,beta_exactly_stf=False)
        self.assertIsNone(determinant_bound(.2,None,beta_exactly_stf=True)['bound'])

    def test_positive_transport_underflow_refused(self):
        cases=[
            lambda:diagonal_bound([800.,0.,0.],[700.,0.,0.]),
            lambda:diagonal_bound([700.,0.,0.],[1e-30,0.,0.]),
            lambda:determinant_bound(300.,100.,beta_exactly_stf=True),
            lambda:determinant_bound(200.,1e-100,beta_exactly_stf=True),
            lambda:duhamel(1.,-800.,0.,1.,0.,1.,0.,envelope_provenance='SYNTHETIC underflow'),
            lambda:duhamel(1.,-700.,0.,1.,0.,1e-30,0.,envelope_provenance='SYNTHETIC underflow'),
            lambda:duhamel(1.,0.,1e-200,1e-200,0.,envelope_provenance='SYNTHETIC underflow'),
            lambda:duhamel(1e-30,0.,0.,0.,1e-300,envelope_provenance='SYNTHETIC underflow')]
        for function in cases:
            with self.assertRaisesRegex(ValueError,'underflow'):function()

    def test_duhamel_zero_negative_and_positive_growth(self):
        for mhat in [-.2,-.7,.3]:
            # eta=.2; m=0 at mhat=-.2, constant physical/numerical forcing.
            row=duhamel(2.,mhat,.2,3.,.4,.1,.05,envelope_provenance='SYNTHETIC exact constant envelopes')
            m=mhat+.2
            integral=2. if m==0 else (dexp(2*m)-1)/m
            self.assertAlmostEqual(row['physical_bound'],dexp(2*m)*.1+.6*integral,places=14)
            self.assertAlmostEqual(row['numerical_bound'],dexp(2*m)*.05+.4*integral,places=14)
        row=duhamel(0.,-.3,.2,3.,.4,.1,.05,envelope_provenance='SYNTHETIC zero interval')
        self.assertEqual(row['physical_bound'],.1);self.assertEqual(row['numerical_bound'],.05)
        with self.assertRaises(ValueError):duhamel(-1.,0.,0.,0.,0.,envelope_provenance='invalid')

    def test_geometry_units_and_rate_state_separation(self):
        # Distinct c and L catch omission of c or L and treating rates as stress.
        scale=self.core.FixedScale(7.,c=5.,G=3.)
        T=np.zeros((3,4,4));T[:,0,0]=[13.,17.,19.]
        T[0,0,1:]=T[0,1:,0]=[2.,-3.,4.]
        T[2,1:,1:]=np.diag([8.,6.,5.])
        rate=np.array([[0.,0.,0.,0.],[-11.,2.,-4.,6.],[11.,-2.,4.,-6.]])
        rho,flux,source=si_to_core(scale,T,rate,self.core)
        alpha=8*math.pi*3*7**2/5**4
        np.testing.assert_allclose(rho,alpha*np.array([13.,17.,19.]),rtol=1e-15)
        np.testing.assert_allclose(flux[0],alpha*np.array([2.,-3.,4.]),rtol=1e-15)
        np.testing.assert_allclose(source.energy_transfer,alpha*7/5*rate[:,0],rtol=1e-15)
        np.testing.assert_allclose(source.momentum_transfer,alpha*7/5*rate[:,1:],rtol=1e-15)
        _,_,zero=si_to_core(scale,T,np.zeros((3,4)),self.core)
        np.testing.assert_array_equal(source.pi,zero.pi)
        np.testing.assert_array_equal(source.pressure,zero.pressure)
        np.testing.assert_allclose(core_to_si(scale,rho,flux,source),T,rtol=1e-15,atol=1e-15)

    def test_unbalanced_and_asymmetric_refusal(self):
        scale=self.core.FixedScale(7.,c=5.,G=3.)
        T=np.zeros((2,4,4));T[:,0,0]=1.
        q=np.zeros((2,4));q[0,0]=1.
        with self.assertRaises(ValueError):si_to_core(scale,T,q,self.core)
        T[0,1,2]=.01
        with self.assertRaises(ValueError):si_to_core(scale,T,np.zeros((2,4)),self.core)

    def test_exact_isotropic_tensor_keeps_zero_pi(self):
        scale=self.core.FixedScale(7.,c=5.,G=3.)
        T=np.zeros((1,4,4));T[0,0,0]=.37
        T[0,1:,1:]=np.eye(3)*(.37/3)
        _,_,source=si_to_core(scale,T,np.zeros((1,4)),self.core)
        np.testing.assert_array_equal(source.pi,np.zeros((1,3,3)))

    def test_near_isotropic_tensor_preserves_signed_pi(self):
        scale=self.core.FixedScale(7.,c=5.,G=3.)
        u=np.spacing(1.)
        T=np.zeros((1,4,4));T[0,0,0]=3.+u
        T[0,1:,1:]=np.diag([1.,1.,1.+u])
        _,_,source=si_to_core(scale,T,np.zeros((1,4)),self.core)
        expected=scale.density_factor*np.diag([-u/3,-u/3,2*u/3])
        np.testing.assert_array_equal(source.pi[0],expected)
        self.assertLess(source.pi[0,0,0],0.)
        self.assertGreater(source.pi[0,2,2],0.)

    def test_readiness_synthetic_structure_is_not_actual_admission(self):
        metadata={k:'SYNTHETIC explicitly owned test metadata' for k in DonorBinding.__dataclass_fields__ if k not in ['physical_error_radii','evidence_class']}
        row=finite_donor_readiness(DonorBinding(**metadata,evidence_class='SYNTHETIC_TEST_METADATA'))
        self.assertEqual(row['missing_structural_fields'],[])
        self.assertFalse(row['physical_finite_absorption'])
        self.assertEqual(row['uncertainty_certification'],'INPUT_ERROR_UNSPECIFIED')
        metadata['donor_cells_to_incoming_face']=None
        row=finite_donor_readiness(DonorBinding(**metadata,evidence_class='ACTUAL_BOUND_FINITE_DONOR'))
        self.assertEqual(row['missing_structural_fields'],['donor_cells_to_incoming_face'])
        self.assertFalse(row['physical_finite_absorption'])
        metadata['donor_cells_to_incoming_face']='SYNTHETIC test mapping'
        complete=finite_donor_readiness(DonorBinding(**metadata,evidence_class='ACTUAL_BOUND_FINITE_DONOR'))
        self.assertTrue(complete['input_candidate_ready'])
        self.assertFalse(complete['physical_finite_absorption'])
        with self.assertRaises(ValueError):finite_donor_readiness(DonorBinding(**metadata,physical_error_radii={'source':-1.}))

    def test_native_Wien_and_standalone_Planck_separate(self):
        nr='inputs/rec_native/research/rec_line_native_owner_20261023'
        state=read_json(nr+'/inputs/STORED_NATIVE_LYA_STATE.json');facts=read_json(nr+'/provenance/SOURCE_PARTITION_FACTS.json')
        row=native_source_binding(state,facts,read_json('inputs/rec_history/HISTORY_ADMISSION.json'))
        with localcontext() as ctx:
            ctx.prec=70
            x=Decimal('10.198714553953742')/Decimal(state['meta']['TR_eV_rescaled'])
            w=(-x).exp();planck=1/(x.exp()-1);d=Decimal(state['meta']['Dfplus_Lya'])
            self.assertAlmostEqual(row['native_total_occupation_Wien']/float(w+d),1.,places=15)
            self.assertAlmostEqual(row['standalone_LINE01_total_occupation_Planck']/float(planck+d),1.,places=15)
            self.assertGreater(planck,w)  # Total may round equal at binary64; laws remain distinct.
        self.assertEqual(row['existing_instantaneous_ledger'],facts['native_line_components_decimal70'])
        self.assertEqual(row['native_constants']['native_hPc_eV_cm'],.0001239841874331)
        self.assertFalse(row['finite_donor_readiness']['physical_finite_absorption'])
        self.assertEqual(len(row['history_owner_reuse']['query_rows']),313)


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BindingTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    write_json(ROOT/'results/TEST_RESULTS.json',dict(schema='B3G_FOCUSED_TESTS_V1',tests_run=result.testsRun,
        failures=[dict(test=str(t),traceback=s) for t,s in result.failures],
        errors=[dict(test=str(t),traceback=s) for t,s in result.errors],passed=result.wasSuccessful(),
        synthetic_fixtures_are_actual_input_admissions=False))
    sys.exit(0 if result.wasSuccessful() else 1)
