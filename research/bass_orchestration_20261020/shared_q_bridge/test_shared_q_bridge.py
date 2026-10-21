#!/usr/bin/env python3
"""Focused independent-oracle tests; no cosmological history is executed."""
import ctypes as C
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parent
class Rate(C.Structure):
    _fields_ = [(n, C.c_double) for n in ('Q','S','donor_dt','radiation_dt','donor_dx','radiation_dx')] + [('kind',C.c_int),('flags',C.c_int)]
class Jump(C.Structure):
    _fields_ = [(n,C.c_double) for n in ('donor','radiation','requested','debit','credit','defect')]

class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.so = Path(cls.temp.name)/'bridge.so'
        cls.command = ['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fPIC','-shared',str(HERE/'shared_q_bridge.c'),'-lm','-o',str(cls.so)]
        cls.build = subprocess.run(cls.command,capture_output=True,text=True,check=True)
        cls.lib=C.CDLL(str(cls.so))
        cls.rate=cls.lib.bass_q_normalize
        cls.rate.argtypes=[C.c_double]*3+[C.c_int]*3+[C.POINTER(Rate)]
        cls.rate.restype=C.c_int
        cls.event=cls.lib.bass_q_transfer_event
        cls.event.argtypes=[C.c_double]*3+[C.POINTER(Jump)]
        cls.event.restype=C.c_int
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def check_rate(self,n,q,h,clock=1,kind=1):
        r=Rate(); self.assertEqual(self.rate(n,q,h,clock,1,kind,C.byref(r)),0)
        with localcontext() as ctx:
            ctx.prec=100
            energy=Decimal.from_float(n)*Decimal.from_float(q)*Decimal('1.602176634e-19')
            hh=Decimal.from_float(h)
            qref=float(energy if clock==1 else energy*hh)
            sref=float(energy/hh if clock==1 else energy)
        # Rounded subnormals may differ by one ULP; normal values use relative bound.
        self.assertLessEqual(abs(r.Q-qref),max(abs(qref)*8e-16,math.ulp(qref)))
        self.assertLessEqual(abs(r.S-sref),max(abs(sref)*8e-16,math.ulp(sref)))
        self.assertEqual(r.donor_dt+r.radiation_dt,0.)
        self.assertEqual(r.donor_dx+r.radiation_dx,0.)
        self.assertEqual(r.kind,kind)
        return r
    def test_proper_clock_decimal_oracle(self):
        for x in [(1e3,2e-15,1e-17),(1,1,1),(1e300,1e20,1),(1e300,1e-300,1),(1e-300,1e300,1),(1e200,1e100,1e100)]:
            with self.subTest(x=x): self.check_rate(*x)
    def test_lna_clock_decimal_oracle(self):
        for x in [(1e3,200,1e-17),(1e200,1e100,1e-100),(1e-200,1e-100,1e100)]:
            with self.subTest(x=x): self.check_rate(*x,clock=2,kind=2)
    def test_explicit_units_no_extra_normalization(self):
        # nH is supplied in proper m^-3. The adapter applies only exact eV->J.
        r=self.check_rate(1e6,13.6,1e-17)
        self.assertAlmostEqual(r.Q/(1e6*13.6*1.602176634e-19),1.,places=15)
    def test_zero_and_subnormal(self):
        for n,q in [(0,2),(2,0),(-0.,1)]:
            r=self.check_rate(n,q,1); self.assertEqual(r.Q,0); self.assertEqual(r.flags,0)
        r=self.check_rate(1,1e-300,1); self.assertEqual(r.flags,1)
    def test_invalid_inputs_transactional(self):
        inputs=[(-1,1,1,1,1,1),(1,-1,1,1,1,1),(1,1,0,1,1,1),
                (1,1,-1,1,1,1),(math.nan,1,1,1,1,1),(1,math.inf,1,1,1,1),
                (1,1,math.inf,1,1,1),(1,1,1,9,1,1),(1,1,1,1,9,1),(1,1,1,1,1,9)]
        for x in inputs:
            r=Rate(11,12,13,14,15,16,17,18); before=bytes(r)
            self.assertEqual(self.rate(*x,C.byref(r)),1); self.assertEqual(bytes(r),before)
        self.assertEqual(self.rate(1,1,1,1,1,1,None),1)
    def test_true_range_failure_transactional(self):
        for x in [(1e308,1e308,1),(1e-300,1e-300,1),(1e20,1,1e-320)]:
            r=Rate(11,12,13,14,15,16,17,18); before=bytes(r)
            self.assertEqual(self.rate(*x,1,1,1,C.byref(r)),2); self.assertEqual(bytes(r),before)
    def test_frozen_event_and_depletion(self):
        for d,r,x in [(10,2,.5),(10,2,10),(10,2,0)]:
            j=Jump(); self.assertEqual(self.event(d,r,x,C.byref(j)),0)
            self.assertEqual(j.donor+j.radiation,d+r); self.assertEqual(j.defect,0)
    def test_event_rounding_defect_exposed(self):
        j=Jump(); self.assertEqual(self.event(1,1e20,.25,C.byref(j)),0)
        self.assertEqual(j.debit,.25); self.assertEqual(j.credit,0); self.assertEqual(j.defect,-.25)
        k=F(3,7)
        actual_change=-k*((F(j.donor)+F(j.radiation))-(F(1)+F(1e20)))
        self.assertEqual(actual_change,-k*F(j.defect))
    def test_event_subulp_loss_survives_increment_cancellation(self):
        j=Jump(); self.assertEqual(self.event(1e20,1.,1e19,C.byref(j)),0)
        self.assertEqual(j.credit-j.debit,0.)
        actual=(F(j.donor)+F(j.radiation))-(F(1e20)+F(1.))
        self.assertEqual(F(j.defect),actual)
        self.assertEqual(j.defect,-1.)
    def test_event_failures_transactional(self):
        for d,r,x,status in [(1,2,2,3),(1,-2,1,1),(1,2,-1,1),(1,math.inf,0,1),(1e308,1e308,1e308,2)]:
            j=Jump(11,12,13,14,15,16); before=bytes(j)
            self.assertEqual(self.event(d,r,x,C.byref(j)),status); self.assertEqual(bytes(j),before)
        self.assertEqual(self.event(1,2,0,None),1)
    def test_constraint_polynomial_rational_oracle(self):
        # Independent exact rational substitution of all five evolution equations.
        for i in range(1,26):
            h,s,k,ud,ur,pd,pi,q,lam=[F((j+2)*i+1,(j+1)*7) for j in range(9)]
            constraint=h*h-s*s-k*(ud+ur)-lam
            hd=-h*h-2*s*s-k*(ud+2*ur+3*pd)/2+lam
            sd=-3*h*s+k*pi
            dd=-3*h*(ud+pd)-q
            rd=-4*h*ur-2*s*pi+q
            self.assertEqual(2*h*hd-2*s*sd-k*(dd+rd)+2*h*constraint,0)
            mismatch=F(i,17)
            self.assertEqual(2*h*hd-2*s*sd-k*(dd+rd+mismatch)+2*h*constraint,-k*mismatch)

if __name__=='__main__':
    started=time.perf_counter()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BridgeTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={'status':'PASS_SCOPED' if result.wasSuccessful() else 'FAIL',
             'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
             'wall_s':time.perf_counter()-started,'compiler':subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],
             'python':sys.version,'command':'python3 shared_q_bridge/test_shared_q_bridge.py',
             'scope':'C99 algebraic normalization and frozen-volume event; no native dynamics/history execution',
             'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'shared_q_bridge.c',HERE/'shared_q_bridge.h',Path(__file__).resolve()]}}
    (HERE/'TEST_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
