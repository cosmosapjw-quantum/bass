"""New bounded selected-unit controls; no old test discovery or source solve."""
from pathlib import Path
import json
import math
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from tube import exp_linear_integral, physical_bound, require_atomic_interval, load


class TubeControls(unittest.TestCase):
    def test_constant_and_affine_exact_controls(self):
        for p in [0,3,4]:
            a,b=0.,0.0001
            constant=exp_linear_integral(a,b,2.,2.,p)
            expected=2*(b-a) if p==0 else 2*math.expm1(p*(b-a))/p
            self.assertLess(abs(constant/expected-1),5e-15)
        self.assertEqual(exp_linear_integral(0,1,2,4,0),3)

    def test_segment_crossing(self):
        t=load()
        self.assertGreater(len(t.edges),2)
        for k,v in zip(t.knots,t.values):
            self.assertLess(abs(t.departure(k)/v-1),1e-14)
        self.assertLess(t.h-t.lag,0)

    def test_zero_vacuum(self):
        self.assertEqual(exp_linear_integral(0,.01,0,0,3),0)
        self.assertEqual(physical_bound(0,.01,0,0,lambda u:0),0)

    def test_nonfinite_negative_physical_trace(self):
        for a,b in [(math.nan,1),(0,math.inf),(-2,-1)]:
            with self.assertRaises(ValueError): physical_bound(0,.1,a,b,lambda u:0)
        # Negative departure is allowed only when the total trace is certified.
        self.assertEqual(physical_bound(0,.1,-1,-1,lambda u:2),1)

    def test_missing_atomic_packet(self):
        for value in [None,{}, {'x1s_interval':1}]:
            with self.assertRaisesRegex(ValueError,'ATOMIC_INPUT_OPEN'): require_atomic_interval(value)

    def test_redshift_scaling_and_work(self):
        t=load(); N,U=2.,3.
        r=t.transport(N,U)
        self.assertLess(abs(r['number_relative_residual']),2e-13)
        self.assertLess(abs(r['energy_relative_residual']),2e-13)
        self.assertLess(r['signed_propagation_energy_change_per_V0_J_m3'],0)
        self.assertAlmostEqual(r['detR'],math.prod(r['R_diagonal']),places=14)

    def test_native_source_snapshot_constants(self):
        t=load(); s=t.packet['single_snapshot_only']; eta=-math.log1p(s['z']['value'])
        self.assertLess(abs(t.H(eta)/s['H_sInv']['value']-1),2e-11)
        self.assertLess(abs(t.nH(eta)/(s['nH_cm3']['value']*1e6)-1),2e-11)

    def test_manufactured_piecewise_wien_representation(self):
        import mpmath as mp
        import numpy as np
        edges=[0.,0.00004,0.0001]
        values=[2.,2.1,1.9]
        nodes,weights=np.polynomial.legendre.leggauss(24)
        for power in [3,4]:
            primary=[]
            for a,b,fa,fb in zip(edges[:-1],edges[1:],values[:-1],values[1:]):
                u=(a+b)/2+(b-a)/2*nodes
                primary.append(exp_linear_integral(a,b,fa,fb,power)+(b-a)/2*math.fsum(float(w)*math.exp(power*float(t)-2*math.exp(float(t))) for t,w in zip(u,weights)))
            with mp.workdps(60):
                terms=[]
                for a,b,fa,fb in zip(edges[:-1],edges[1:],values[:-1],values[1:]):
                    aa,bb,ff,gg=map(mp.mpf,[a,b,fa,fb])
                    terms.append(mp.quad(lambda u:mp.exp(power*u)*(ff+(gg-ff)*(u-aa)/(bb-aa)+mp.exp(-2*mp.exp(u))),[aa,bb]))
                reference=float(mp.fsum(terms))
            self.assertLess(abs(math.fsum(primary)/reference-1),2e-13)


if __name__=='__main__': unittest.main()
