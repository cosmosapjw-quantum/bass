"""Targeted R9 checks: new export and clock contracts, no old science suite."""
import json
import sys
import unittest
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from fa03_contract import load_contract,evaluate,exact,sqrt_bracket,trace_norm_stokes,ContractHold as FAHold,MAX_EPS,C3
from rei_clock import geometry_clock, milestone_decomposition, ContractHold as REIHold, Background, _input, A_REF
import mpmath as mp

class R9ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=load_contract()
    def test_exact_eps0(self):
        x=evaluate(self.s,'0');self.assertEqual(x['epsilon_exact'],'0')
        self.assertEqual(Fraction(x['predicted_stokes_exact'][0]),self.s.row[0][0])
    def test_eps_endpoints_finite(self):
        for eps in ['-1/10','1/10','0','1/50']:
            o=evaluate(self.s,eps)
            self.assertGreater(Fraction(o['certified_minimum_eigenvalue_lower_exact']),Fraction(12548,100000))
            self.assertLess(Fraction(o['Schatten1_error_bound_exact']),Fraction(475,10**9))
            l,u=map(Fraction,o['certified_polarization_degree_interval_exact'])
            self.assertTrue(Fraction(0)<=l<=u<=Fraction(1))
    def test_error_monotone(self):
        radii=self.s.radii
        for e in (Fraction(0),Fraction(1,100),Fraction(1,20),Fraction(1,10)):
            exact_err=radii[0]+e*radii[1]+e*e*radii[2]/2+C3*e**3
            self.assertEqual(Fraction(evaluate(self.s,e)['Schatten1_error_bound_exact']),exact_err)
    def test_no_float_decimal_mutation(self):
        for eps in (0.1,0.101,-0.101):
            with self.assertRaises(FAHold):evaluate(self.s,eps)
        with self.assertRaises(FAHold):evaluate(self.s,'1/9')
    def test_source_modified_holds(self):
        import shutil,tempfile
        with tempfile.TemporaryDirectory() as d:
            t=Path(d);(t/'reference').mkdir()
            for name in self.s.source_shas:
                shutil.copy2(Path(__file__).parent.parent/'reference'/name,t/'reference'/name)
            p=t/'reference/R7_CROSS_CERTIFICATE.json'
            b=p.read_bytes();p.write_bytes(b.replace(b'"pass": true',b'"pass":false'))
            with self.assertRaises(FAHold):load_contract(t)
    def test_trace_norm_formula(self):
        I=Fraction(4,5);Q=Fraction(3,10);U=Fraction(4,10);V=Fraction(0)
        self.assertEqual(trace_norm_stokes((I,Q,U,V))[1],I)
        self.assertEqual(sqrt_bracket(Fraction(1,4))[0],Fraction(1,2))
        with self.assertRaises(FAHold):sqrt_bracket(Fraction(-1))
    def test_geometry_sign_parity(self):
        plus=geometry_clock('0.2','0.01');minus=geometry_clock('0.2','-0.01')
        self.assertEqual(plus['delta_tau_seconds'],minus['delta_tau_seconds'])
        self.assertTrue(mp.mpf(plus['delta_tau_seconds'])<0)
        self.assertLess(abs(mp.mpf(plus['delta_tau_Julian_years'])-mp.mpf('-7891.36627003021949937')),mp.mpf('1e-12'))
    def test_geometry_q_scaling(self):
        d0=geometry_clock('0.2','0')
        self.assertEqual(d0['delta_tau_seconds'],'0.0')
        a=geometry_clock('0.2','0.005');b=geometry_clock('0.2','0.01')
        self.assertTrue(mp.mpf(b['delta_tau_seconds'])<mp.mpf(a['delta_tau_seconds'])<0)
        self.assertTrue(mp.mpf(a['A4_seconds'])<mp.mpf(a['A2_seconds']))
    def test_clock_starts_at_zero(self):
        self.assertEqual(geometry_clock('1/21','0.01')['delta_tau_seconds'],'0.0')
        with self.assertRaises(REIHold):geometry_clock('1/22','0.01')
        with self.assertRaises(REIHold):geometry_clock('0.20001','0.01')
    def test_clock_refuse_unreviewed(self):
        with self.assertRaises(REIHold):milestone_decomposition('0.09','0.1','0.005')
        with self.assertRaises(REIHold):milestone_decomposition('0.09','0.1','0.005',source_pair_bound=True)
    def test_clock_exact_decomposition_synthetic(self):
        x=milestone_decomposition('0.09','0.1','0.005',source_pair_bound=True,actual_zero_reviewed=True,actual_case_reviewed=True)
        self.assertLess(abs(mp.mpf(x['decomposition_numeric_check_seconds'])),mp.mpf('1e-20'))
    def test_no_wrong_parity_on_abundances(self):
        # A scalar may have an O(q^3) term; tau geometry q-even is separate.
        q=Fraction(1,100)
        X=lambda x:Fraction(2,5)+Fraction(3)*x*x+Fraction(7)*x*x*x
        self.assertNotEqual(X(q),X(-q))
        self.assertEqual((X(q)+X(-q))/2-X(0),Fraction(3)*q*q)
    def test_locked_SHA_lineage(self):
        self.assertEqual(self.s.adopted['decision'],'PROMOTE_FOR_FIXED_36RAY_MODEL_ONLY')
        self.assertEqual(self.s.adopted['parent_pr147'],'e67d6fc6c1ad8b3a219abf72104877da1f267e6d')

if __name__=='__main__':unittest.main(verbosity=2)
