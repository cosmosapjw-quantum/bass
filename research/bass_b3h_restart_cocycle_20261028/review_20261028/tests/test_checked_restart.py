import copy
import json
from pathlib import Path
import sys
import unittest
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from checked_restart import load_for_execution, reward_upper
IDENTITY = {'source':'manufactured-exact-quadratic-v1','frame':'scalar-FLRW',
            'clock':'t/T_global_T2','V0':'1'}

def saved(step=32):
    return json.loads((ROOT/'evidence'/f'checkpoint_{step}.json').read_text())

def load(value, dt=1/128, size=8):
    return load_for_execution(json.dumps(value), IDENTITY, dt, size)

class RestartTests(unittest.TestCase):
    def test_three_original_packets_are_unchanged(self):
        for step in (32,96,192):
            p=saved(step); r=load(p)
            self.assertEqual(r['step'],step)
            self.assertEqual([x.hex() for x in r['y']],p['y'])
            self.assertEqual(r['attempted_work'],p['attempted_work'])
            self.assertEqual(r['t'].hex(),p['t'])
    def test_inconsistent_time_is_refused(self):
        p=saved(); p['t']=(1.25).hex()
        with self.assertRaises(ValueError): load(p)
    def test_inconsistent_step_is_refused(self):
        p=saved(); p['step']+=1
        with self.assertRaises(ValueError): load(p)
    def test_inconsistent_dt_is_refused(self):
        p=saved();p['dt']=(1/64).hex()
        with self.assertRaises(ValueError): load(p)
    def test_coherent_but_wrong_schedule_is_refused(self):
        p=saved();p['dt']=(1/64).hex();p['t']=(.5).hex()
        with self.assertRaises(ValueError): load(p)
    def test_missing_reward_slot_is_refused(self):
        p=saved();p['y'].pop()
        with self.assertRaises(ValueError): load(p)
    def test_nonfinite_state_is_refused(self):
        p=saved();p['y'][0]='nan'
        with self.assertRaises(ValueError): load(p)
    def test_boolean_step_and_work_are_refused(self):
        for field in ('step','attempted_work'):
            p=saved();p[field]=True
            with self.assertRaises(ValueError): load(p)
    def test_identity_and_pending_refusal_retained(self):
        for mutation in ('source','pending'):
            p=saved()
            if mutation=='source':p['identity']['source']='other'
            else:p['pending']=True
            with self.assertRaises(ValueError):load(p)
    def test_zero_cut(self):
        p=saved();p['step']=0;p['t']=(0.).hex();p['attempted_work']=0
        self.assertEqual(load(p)['t'],0.)

class BoundTests(unittest.TestCase):
    def test_zero_gap(self):
        self.assertEqual(reward_upper(2,0,3,5,7,11,13),F(251))
    def test_constant_gap(self):
        self.assertEqual(reward_upper(2,4,3,5,7,11,13),F(311,4))
    def test_zero_duration(self):
        self.assertEqual(reward_upper(0,4,3,5,7,11,13),F(5))
    def test_tiny_gamma_and_huge_gamma_exact(self):
        self.assertEqual(reward_upper('2','1e-100',3,5,7,11,13),F(251))
        g=F(10)**100
        self.assertEqual(reward_upper(2,g,3,5,7,11,13),31+F(187)/g)
    def test_negative_bounds_refused(self):
        args=[2,4,3,5,7,11,13]
        for i in range(len(args)):
            case=args.copy();case[i]=-1
            with self.assertRaises(ValueError):reward_upper(*case)
    def test_direct_reward_term_is_not_discarded(self):
        self.assertEqual(reward_upper('1/2',2,0,0,0,0,'3/2'),F(3,4))

if __name__=='__main__':unittest.main(verbosity=2)
