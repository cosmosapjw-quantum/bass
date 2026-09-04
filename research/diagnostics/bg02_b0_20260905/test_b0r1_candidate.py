"""Behavioral tests of a component/reference candidate, not native xAct tests."""
from pathlib import Path
from functools import lru_cache
import importlib.util
import itertools
import os
import sys
import unittest
import sympy as s
from audit_bg02_b0 import Geometry

ROOT = Path(__file__).resolve().parent
TARGET = Path(os.environ.get('BG02_CANDIDATE', str(ROOT/'candidate'/'typed_views.py')))

@lru_cache(None)
def fixture(label):
    t,x,y,z=s.symbols('tau x y z', real=True)
    if label=='V': g=s.diag(-1,s.exp(2*t),s.exp(-2*x),s.exp(-2*x))
    elif label=='gradient': g=s.diag(-1,1,(1+t*x)**2,(1+t*x)**2)
    elif label=='FLRW': g=s.diag(-1,s.exp(2*t),s.exp(2*t),s.exp(2*t))
    else: raise ValueError(label)
    geo=Geometry(g,(t,x,y,z)); p={t:0,x:0}
    h=Geometry(g[1:4,1:4],(x,y,z)); K=s.diff(h.g,t)/2
    kt=s.simplify(s.trace(h.inv*K))
    def dk(i,j,k):
        return s.diff(K[j,k],h.q[i])-sum(h.gamma(m,i,j)*K[m,k]+h.gamma(m,i,k)*K[j,m] for m in range(3))
    div=s.simplify(sum(h.inv[b,c]*dk(c,0,b) for b in range(3) for c in range(3))).subs(p)
    grad=s.diff(kt,x).subs(p)
    B=s.ImmutableDenseNDimArray([s.simplify(geo.r(*ix).subs(p)) for ix in itertools.product(range(4),repeat=4)],(4,4,4,4))
    return B, geo.inv.subs(p), geo.ricci().subs(p), div, grad

class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TARGET.is_file(),'typed-view correction candidate is not implemented')
        spec=importlib.util.spec_from_file_location('b0r1_candidate',TARGET)
        self.m=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=self.m;spec.loader.exec_module(self.m)

    def test_view_roundtrip_preserves_components(self):
        B,_,_,_,_=fixture('V');v=self.m.CurvatureView
        X=self.m.convert_riemann(B,source=v.BASS_DERIVATIVE_FIRST,target=v.XACT_RAW)
        self.assertEqual(X,-B)
        self.assertEqual(self.m.convert_riemann(X,source=v.XACT_RAW,target=v.BASS_DERIVATIVE_FIRST),B)

    def test_physical_ricci_is_invariant_not_negated(self):
        B,inv,ric,_,_=fixture('V');v=self.m.CurvatureView
        X=self.m.convert_riemann(B,source=v.BASS_DERIVATIVE_FIRST,target=v.XACT_RAW)
        self.assertEqual(self.m.physical_ricci(B,inv,view=v.BASS_DERIVATIVE_FIRST),ric)
        self.assertEqual(self.m.physical_ricci(X,inv,view=v.XACT_RAW),ric)
        self.assertNotEqual(ric,-ric)

    def test_bianchi_v_momentum_geometric_sign(self):
        _,_,ric,div,grad=fixture('V');kg,q=s.symbols('kappa_G q')
        result=self.m.momentum_from_positive_k(divergence_k=div,gradient_k=grad,kappa_g=kg,flux=q)
        self.assertEqual(s.expand(result-(-ric[1,0]-kg*q)),0)
        self.assertEqual(s.expand(result-(div-grad-kg*q)),4)

    def test_inhomogeneous_gradient_sign(self):
        _,_,ric,div,grad=fixture('gradient');kg,q=s.symbols('kappa_G q')
        result=self.m.momentum_from_positive_k(divergence_k=div,gradient_k=grad,kappa_g=kg,flux=q)
        self.assertEqual(s.expand(result-(-ric[1,0]-kg*q)),0)
        self.assertEqual(grad,2)

    def test_flrw_control_and_matter_sign(self):
        _,_,ric,div,grad=fixture('FLRW');kg,q=s.symbols('kappa_G q')
        result=self.m.momentum_from_positive_k(divergence_k=div,gradient_k=grad,kappa_g=kg,flux=q)
        self.assertEqual(result,-kg*q)
        self.assertEqual(result.subs(q,0),0)
        self.assertEqual(ric[1,0],0)

    def test_class_b_divergence_is_not_momentum(self):
        A,n22,n23,n33,u,v,w,d1,d2,kg,q=s.symbols('A n22 n23 n33 s12 s13 s23 s11 s22 kappa_G q3')
        a=[A,0,0];n=s.Matrix([[0,0,0],[0,n22,n23],[0,n23,n33]])
        sigma=s.Matrix([[d1,u,v],[u,d2,w],[v,w,-d1-d2]])
        def C(k,i,j):return sum(s.LeviCivita(i,j,l)*n[l,k] for l in range(3))+a[i]*int(k==j)-a[j]*int(k==i)
        def gamma(k,i,j):return (C(k,i,j)-C(i,j,k)+C(j,k,i))/2
        divergence=s.expand(sum(gamma(2,b,d)*sigma[d,b]+gamma(b,b,d)*sigma[2,d] for b in range(3) for d in range(3)))
        self.assertEqual(s.expand(divergence-(n22*u+(n23-3*A)*v)),0)
        result=self.m.class_b_momentum3(a_b1=A,n_b22=n22,n_b23=n23,sigma12=u,sigma13=v,kappa_g=kg,flux3=q)
        self.assertEqual(s.expand(result+divergence+kg*q),0)
        mutant=self.m.class_b_momentum3(a_b1=A,n_b22=n22,n_b23=n23,sigma12=u,sigma13=0,kappa_g=kg,flux3=q)
        self.assertEqual(s.expand(result-mutant+(n23-3*A)*v),0)

    def test_unknown_or_untyped_view_rejected(self):
        B,inv,_,_,_=fixture('V')
        for bad in ['XACT_RAW',None,1]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):self.m.physical_ricci(B,inv,view=bad)

    def test_invalid_component_layout_rejected(self):
        v=self.m.CurvatureView
        with self.assertRaises(ValueError):self.m.convert_riemann(s.Array([1,2]),source=v.XACT_RAW,target=v.BASS_DERIVATIVE_FIRST)
        B,_,_,_,_=fixture('V')
        with self.assertRaises(ValueError):self.m.physical_ricci(B,s.eye(3),view=v.XACT_RAW)

    def test_missing_or_nonscalar_inputs_fail_closed(self):
        with self.assertRaises(TypeError):self.m.momentum_from_positive_k(divergence_k=0,gradient_k=0,kappa_g=1)
        with self.assertRaises(ValueError):self.m.momentum_from_positive_k(divergence_k=s.Matrix([1,2]),gradient_k=0,kappa_g=1,flux=0)

if __name__=='__main__':unittest.main(verbosity=2)
