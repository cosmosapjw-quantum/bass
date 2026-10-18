import unittest
from source_oracle import Case, predict
from deposition import deposit
class DepositTests(unittest.TestCase):
    def test_positive_source_reproduces_source_count(self):
        c=Case('red',.4,.01,1e-16,1e-19,1e10,qmin=1.)
        state=deposit(c)
        self.assertGreater(float(state.number.sum()),0.0,'Positive native source must add photons')
        p=predict(c)
        self.assertLess(abs(float(state.number.sum())/p['n']-1),3e-13)
if __name__=='__main__':unittest.main(verbosity=2)

import math
import numpy as np
from dataclasses import replace
from scipy.integrate import quad
from deposition import CellState, inventory, simulate, midpoint_cases, continuum_reference

class FiniteIntervalTests(unittest.TestCase):
    def setUp(self):
        self.c=Case('finite',.2,.01,1e-16,1e-19,1e10,nseg=8,nmu=16,nenergy=64,qmin=1.)
    def test_point_inventory_reproduces_parent_oracle(self):
        for b in (-.2,-.01,0,.01,.2):
            c=replace(self.c,b=b);v=inventory(deposit(c),c.x,c.b);r=predict(c)
            for a,k in [('inventory_n','n'),('inventory_u','u'),('delta','delta'),('dipole','dipole')]:
                scale=r['u'] if k in ('u','delta','dipole') else r['n']
                self.assertLess(abs(v[a]-r[k])/scale,4e-14)
    def test_positive_cell_realizability(self):
        st=deposit(self.c);q=np.geomspace(self.c.qmin,self.c.qmax,self.c.nenergy+1)
        self.assertTrue(np.all(st.number>=0))
        self.assertTrue(np.all(st.energy_ref>=q[:-1]*st.number*(1-3e-15)))
        self.assertTrue(np.all(st.energy_ref<=q[1:]*st.number*(1+3e-15)))
    def test_empty_stock_is_admitted(self):
        st=deposit(replace(self.c,dt=0));v=inventory(st,.3,0)
        self.assertEqual(v['inventory_n'],0);self.assertEqual(v['inventory_u'],0)
    def test_nonfinite_or_negative_stock_rejected(self):
        for a in (-1,float('nan')):
            st=CellState(np.full((8,2),a),np.ones((8,2)))
            with self.assertRaises(ValueError):inventory(st,.3,0)
    def test_free_stream_per_H_is_not_a3_diluted(self):
        c=replace(self.c,b=0);st=deposit(c)
        a=inventory(st,c.x,0);z=inventory(st,c.x+.3,0)
        self.assertEqual(z['inventory_n'],a['inventory_n'])
        self.assertAlmostEqual(z['inventory_u']/a['inventory_u'],math.exp(-.3),14)
        # Physical volume energy additionally has n_H proportional to a^-3.
        self.assertAlmostEqual(z['inventory_u']*math.exp(-.9)/a['inventory_u'],math.exp(-1.2),14)
    def test_single_birth_energy_work_ode(self):
        st=deposit(self.c);x=.6;b=.015;v=-.02;h=1e-5
        pm=inventory(st,x-h,b-v*h);pp=inventory(st,x+h,b+v*h);p=inventory(st,x,b)
        fd=(pp['inventory_u']-pm['inventory_u'])/(2*h)
        self.assertLess(abs(fd+p['inventory_u']+2*v*p['delta'])/p['inventory_u'],3e-10)
    def test_birth_superposition_and_work_ledger(self):
        cases=[self.c,replace(self.c,x=.4,b=-.005,dt=2e10)]
        p=simulate(cases,.7,.012)
        self.assertLess(abs(p['number_residual'])/p['ledger_n'],4e-15)
        self.assertLess(abs(p['energy_residual'])/p['ledger_u'],4e-15)
        aa=[simulate([c],.7,.012) for c in cases]
        for k in ('inventory_n','inventory_u','delta','work'):
            self.assertLess(abs(p[k]-sum(a[k] for a in aa))/p['ledger_u'],4e-15)
    def test_configuration_change_rejected(self):
        with self.assertRaisesRegex(ValueError,'CHANGING_DISCRETE_SOURCE'):
            simulate([self.c,replace(self.c,x=.3,fesc=.3)],.5,0)
    def test_nonmonotone_time_rejected(self):
        with self.assertRaisesRegex(ValueError,'NONMONOTONE_TIME'):
            simulate([replace(self.c,x=.4),self.c],.5,0)
        with self.assertRaisesRegex(ValueError,'END_BEFORE_BIRTH'):simulate([self.c],.1,0)
    def test_exact_proper_time_increments(self):
        H0=1e-16;alpha=1.5;g=lambda x:(.01*x,H0*math.exp(-alpha*x),.01*H0*math.exp(-alpha*x))
        cs=midpoint_cases(self.c,g,.2,.6,8)
        exact=(math.exp(alpha*.6)-math.exp(alpha*.2))/(alpha*H0)
        self.assertLess(abs(sum(c.dt for c in cs)/exact-1),5e-15)
    def test_source_time_refinement_at_fixed_angle(self):
        g=lambda x:(0.,1e-16*math.exp(-1.5*x),0.)
        ref=continuum_reference(self.c,g,.2,.8)
        errors=[]
        for n in (4,8,16):
            p=simulate(midpoint_cases(self.c,g,.2,.8,n),.8,0.)
            errors.append(abs(p['inventory_u']/ref['inventory_u']-1))
        self.assertGreater(errors[0]/errors[1],3.8);self.assertGreater(errors[1]/errors[2],3.8)
    def test_birth_frame_cancellation_source_quadrupole(self):
        g=lambda x:(.12,1e-16,0.)
        ref=continuum_reference(self.c,g,.2,.5)
        self.assertEqual(ref['delta'],0.0)
        # Native reference-ray normalization alone is not isotropy.
        c=replace(self.c,nmu=8)
        p=simulate(midpoint_cases(c,g,.2,.5,4),.5,.12)
        self.assertGreater(abs(p['delta']/p['inventory_u']),1e-7)
