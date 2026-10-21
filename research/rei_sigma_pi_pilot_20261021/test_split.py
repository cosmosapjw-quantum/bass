#!/usr/bin/env python3
"""Targeted split mapping, unchanged-owner equivalence, and actual export checks."""
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np
import split_sweep as split
import sweep as prior


class SplitContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = split.PreparedContext()

    def test_all_729_initial_coordinates_and_positive_families(self):
        cases = split.signed_grid()
        self.assertEqual(len(cases),729)
        self.assertEqual(len({(c['signed_Sigma_requested'],c['signed_Pi_m_requested'],
                               c['signed_Pi_r_requested']) for c in cases}),729)
        self.assertEqual(sum(c['nominal_cancellation'] for c in cases),81)
        nonzero_cancellation = 0
        for case in cases:
            seed = split.seed_for(case,self.context)
            self.assertTrue(-1 <= seed['alpha_m'] <= 2)
            self.assertTrue(-1 <= seed['alpha_r'] <= 2)
            model = self.context.model(split.parameters(case['Sigma_half_requested'],
                case['shear_sign_requested'],seed['alpha_m'],seed['alpha_r']))
            actual = split.initial_record(model,model.initial())
            split.initial_checks(case,actual)
            self.assertEqual(actual['D_total_Pa'],actual['D_m_Pa']+actual['D_r_Pa'])
            self.assertTrue(math.isclose(actual['Pi_total_half'],abs(actual['signed_Pi_total']),
                                         rel_tol=8*np.finfo(float).eps,abs_tol=1e-30))
            if case['nominal_cancellation'] and case['Pi_m_half_requested'] > 0:
                nonzero_cancellation += 1
                self.assertLessEqual(actual['Pi_total_half'],3e-13)
                self.assertGreater(actual['Pi_m_half'],0.)
                self.assertGreater(actual['Pi_r_half'],0.)
                self.assertGreater(actual['cancellation_fraction'],1-1e-8)
                self.assertIn('UNRESOLVED',actual['Pi_total_orientation_status'])
        self.assertEqual(nonzero_cancellation,72)
        bad = dict(cases[-1]);bad['Pi_m_half_requested']=.01
        with self.assertRaises(ValueError):
            split.seed_for(bad,self.context)

    def test_two_opposite_seed_inputs_owner_equivalence_and_actual_export(self):
        owner = prior.load_owner()
        dx = owner.c13.stable_dx(.1999,.2)/64
        for direction in (-1,1):
            case = next(c for c in split.signed_grid() if
                c['signed_Sigma_requested'] == direction*.004 and
                c['signed_Pi_m_requested'] == direction*.0004 and
                c['signed_Pi_r_requested'] == -direction*.0004)
            seed = split.seed_for(case,self.context)
            params = split.parameters(.004,direction,seed['alpha_m'],seed['alpha_r'])
            self.assertLess(params.massive_quadrupole*params.gamma_quadrupole,0)
            self.assertEqual(params.gamma_quadrupole,params.nu_quadrupole)
            original = owner.EinsteinBoltzmann(params,a0=.1999,fast_massive=True,source_grid='8X8')
            prepared = self.context.model(params)
            left,right = original.initial(),prepared.initial()
            initial = split.initial_record(prepared,right)
            self.assertEqual(split.initial_record(original,left),initial)
            self.assertIsNot(left.moments,right.moments)
            self.assertIsNot(original.massive_weight,prepared.massive_weight)
            self.assertIsNot(left.gas_and_UV.gas,right.gas_and_UV.gas)
            self.assertFalse(prepared.massive.q.flags.writeable)
            rows = []
            for i in range(2):
                target = .1999*math.exp((i+1)*dx)
                left,expected = original.step(left,target,feedback=True,compress=True)
                right,actual = prepared.step(right,target,feedback=True,compress=True)
                self.assertEqual(expected,actual)
                np.testing.assert_array_equal(left.moments,right.moments)
                actual.update({'a':right.a,'s_inv_s':right.s,'b':right.b})
                split.normalize_row(actual)
                rows.append(actual)
                self.assertLessEqual(actual['nerr'],5e-12)
                self.assertLessEqual(actual['eerr'],5e-11)
                self.assertEqual(actual['D_r_Pa'],actual['Pi_gamma']+actual['Pi_nu']+actual['Pi_UV'])
            # Export real opposite-alpha initial and evolved states, including
            # every owner row field, via the same strict worker boundary.
            payload = {'case':case,'seed':seed,'initial':initial,
                'owner_result':{'config':params.__dict__,'history':rows,'final':rows[-1]},
                'gates':{'positive':np.bool_(True)},'count':np.int64(2)}
            decoded = json.loads(split.canonical(payload))
            self.assertIs(decoded['gates']['positive'],True)
            self.assertEqual(decoded['owner_result']['final']['signed_Pi_m'],rows[-1]['signed_Pi_m'])
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory)/'actual_opposite_export.json'
                split.write_json(output,payload)
                self.assertEqual(json.loads(output.read_text()),decoded)
            fresh = self.context.model(params)
            self.assertNotIn('proxy',fresh.__dict__)
            self.assertEqual((fresh.iterations,fresh.rhs_evals),(0,0))
            self.assertIs(fresh.source,prepared.source)
            self.assertIs(fresh.owner,prepared.owner)
        for bad in (np.float64(float('nan')),np.float64(float('inf'))):
            with self.assertRaises(ValueError):
                split.canonical({'bad':bad})
        with self.assertRaises(TypeError):
            split.canonical({'bad':object()})

    def test_split_guard_and_tensor_sum_not_norm_sum(self):
        params = split.parameters(.004,1,.8,-.8)
        from dataclasses import replace
        with self.assertRaises(ValueError):
            self.context.model(replace(params,nu_quadrupole=.8))
        row = {'s_inv_s':1e-20,'H':1e-17,'Pi_massive':1e-12,
               'Pi_gamma':-4e-13,'Pi_nu':-6e-13,'Pi_UV':0.}
        split.normalize_row(row)
        self.assertEqual(row['D_total_Pa'],0.)
        self.assertEqual(row['Pi_total_half'],0.)
        self.assertGreater(row['Pi_component_norm_sum'],0.)
        self.assertEqual(row['cancellation_fraction'],1.)
        self.assertEqual(row['shear_work_total_J_m3_s'],0.)


if __name__ == '__main__':
    unittest.main(verbosity=2)
