"""Focused frozen-contract tests, run only through the metered child wrapper."""
from pathlib import Path
import itertools
import json
import math
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import cohort_input_error as c
p=c.p

def sphere_monomial(powers):
    if any(k%2 for k in powers):return 0.
    def oddprod(k):return math.prod(range(1,k+1,2))
    return math.prod(oddprod(k-1) for k in powers)/oddprod(sum(powers)+1)

class FiniteInputTests(unittest.TestCase):
    def setUp(self):
        raw=c.nominal_data();r=raw['G3'];self.S=np.asarray(r['S']);self.R=np.asarray(r['R']);self.B=r['source_aware']['selected']['B_T'];self.raw=raw
    def test_sixth_monomials_and_source_formula(self):
        n,A=p.sphere_rule(4)
        for degree in range(7):
            for i in range(degree+1):
                for j in range(degree-i+1):
                    powers=(i,j,degree-i-j);actual=float(np.sum(A*np.prod(n**np.asarray(powers),axis=1)))
                    self.assertLessEqual(abs(actual-sphere_monomial(powers)),p.ROUND)
        U=np.array([[1/5,1/7,-1/11],[1/7,-1/8,1/13],[-1/11,1/13,-3/40]])
        R=np.array([[1/2,1/9,0],[0,3/5,1/10],[1/12,0,7/10]])
        integrand=np.einsum('ni,ij,nj->n',n,U,n)**2*np.sum((n@R.T)**2,axis=1)
        self.assertLessEqual(abs(float(A@integrand)-c.source_term(U,R)**2),p.ROUND)
    def test_kernel_zero_parallel_antiparallel(self):
        for v,w in [(np.zeros(3),np.zeros(3)),(np.zeros(3),np.array([1.,2.,3.])),(np.array([2.,0,0]),np.array([1.,0,0])),(np.array([2.,0,0]),np.array([-1.,0,0])),(np.array([1.,2.,0]),np.array([0.,1.,3.]))]:
            lhs=float(np.linalg.norm(c.kernel(v)-c.kernel(w),'fro'));rhs=c.SQRT2*float(np.linalg.norm(v-w))
            self.assertLessEqual(lhs,rhs+p.ROUND)
        self.assertAlmostEqual(float(np.linalg.norm(c.kernel([2,0,0])-c.kernel([1,0,0]),'fro')),c.SQRT2)
    def test_determinant_all_mixed_terms(self):
        R=np.diag([.5,.6,.7]);dR=np.diag([.01,.02,.03]);value,terms=c.determinant_difference(R,dR)
        exact=.6*.7*.01+.5*.7*.02+.5*.6*.03+.7*.01*.02+.6*.01*.03+.5*.02*.03+.01*.02*.03
        self.assertAlmostEqual(value,exact,places=17);self.assertTrue(all(t>0 for t in terms))
        tiny=1e-16*np.eye(3);delta,_=c.determinant_difference(R,tiny);self.assertGreater(delta,0)
        self.assertLessEqual(abs(delta-(.6*.7+.5*.7+.5*.6)*1e-16),1e-31)
    def test_exact_isotropic_density_map_and_source_limits(self):
        S=np.diag([.3,-.1,-.2]);R=.7*np.eye(3);T=np.zeros((4,4));T[0,0]=.7;T[1:,1:]=.7*(np.eye(3)/3+2*S/15)
        n,A=p.sphere_rule(4);actual=p.moments(S,R,n,A)['T'];self.assertLessEqual(float(np.max(np.abs(actual-T)))/.7,p.ROUND)
        for S1,R1,n1 in [(S,R,1.001),(S,.999*R,1.),(.999*S,R,1.)]:
            pair=c.pair(S,R,1.,S1,R1,n1,0.);T1=p.moments(S1,R1,n,A)['T'];q0=p.EB*np.linalg.det(R)*T;q1=p.EB*n1*np.linalg.det(R1)*T1
            self.assertLessEqual(float(np.linalg.norm(q1-q0,'fro')),pair['tensor_bound']+c.EPS_FP*q1[0,0])
        scale=.999;pair=c.pair(S,R,1.,S,scale*R,1.,0.);T1=p.moments(S,scale*R,n,A)['T']
        self.assertLessEqual(float(np.max(np.abs(pair['W1']*T1-scale**4*pair['W0']*T)))/(pair['W0']*.7),p.ROUND)
    def test_missing_negative_nonfinite_radii(self):
        self.assertEqual(c.ball(self.S,self.R,1.,self.B)['status'],'INPUT_ERROR_UNSPECIFIED')
        for bad in [-1.,float('nan'),float('inf')]:
            for key in ['eR','eS','en']:
                radii=dict(eR=0.,eS=0.,en=0.);radii[key]=bad
                with self.assertRaises(ValueError):c.ball(self.S,self.R,1.,self.B,**radii)
    def test_source_determinant_density_domain_errors(self):
        for S in [self.S+np.array([[0,.01,0],[0,0,0],[0,0,0]]),self.S+.01*np.eye(3),np.diag([-1.01,.5,.51])]:
            with self.assertRaises(ValueError):c.endpoint(S,self.R,1.)
        for R in [np.zeros((3,3)),np.diag([-.5,.5,.5]),1.01*np.eye(3),np.diag([.1,.5,.5])]:
            with self.assertRaises(ValueError):c.endpoint(self.S,R,1.)
        for nb in [-1.,float('nan')]:
            with self.assertRaises(ValueError):c.endpoint(self.S,self.R,nb)
        with self.assertRaises(ValueError):c.endpoint(self.S,self.R,0.,True)
        vacuum=c.pair(self.S,self.R,1.,self.S,self.R,0.,self.B)
        self.assertEqual(vacuum['composition']['status'],'NONPOSITIVE_ENERGY_LOWER_BOUND')
    def test_zero_mixture_and_denominator(self):
        row=c.pair(self.S,self.R,1.,self.S,self.R,1.,self.B)
        with self.assertRaises(ValueError):c.mixture([row],[0.])
        with self.assertRaises(ValueError):c.mixture([row],[-1.])
        self.assertEqual(c.compose(0.,1.,1.,1.)['status'],'NONPOSITIVE_ENERGY_LOWER_BOUND')
    def test_source_zero_ball_vs_valid_one_sided_pair(self):
        r=self.raw['G5'];S=np.asarray(r['S']);R=np.asarray(r['R']);pair=c.pair(S,R,1.,.999*S,.9995*R,1.001,0.)
        self.assertGreater(pair['U_pair'],0)
        self.assertEqual(c.ball(S,R,1.,0.,**pair['radii'])['status'],'NOT_COVERED_BY_PHYSICAL_BALL')
        self.assertEqual(c.ball(S,R,1.,0.,eR=0.,eS=1e-16,en=0.)['status'],'NOT_COVERED_BY_PHYSICAL_BALL')
    def test_frame_normalization_positivity(self):
        n,A=p.sphere_rule(4);Ob=p.OY;Of=p.OX;S=Ob@self.S@Ob.T;R=Of@self.R@Ob.T;d=p.moments(S,R,n@Ob.T,A);base=p.moments(self.S,self.R,n,A);O=np.eye(4);O[1:,1:]=Of
        self.assertLessEqual(float(np.max(np.abs(d['T']-O@base['T']@O.T)))/d['F'],p.ROUND)
        self.assertGreaterEqual(d['minimum_q'],0.);self.assertGreaterEqual(d['minimum_A'],0.);self.assertLessEqual(abs(d['normalization']-1),p.ROUND)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FiniteInputTests))
    out=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),scientific_execution='METERED_CHILD_REQUIRED')
    (c.ROOT/'results/TEST_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');sys.exit(not result.wasSuccessful())
