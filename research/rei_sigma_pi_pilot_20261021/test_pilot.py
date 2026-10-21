#!/usr/bin/env python3
"""Small numerical-contract and prepared-context equivalence checks; no benchmark."""
import math
import json
import tempfile
from pathlib import Path
import unittest
import numpy as np
import sweep
from sigma_pi_map import initial_seed, invariants


class PilotContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = sweep.PreparedContext()

    def test_signed_grid_positive_family_and_achieved_initial(self):
        cases = sweep.signed_grid()
        self.assertEqual(len(cases), 81)
        self.assertEqual(len({(c['signed_Sigma_requested'], c['signed_Pi_requested']) for c in cases}), 81)
        for case in cases:
            seed = sweep.seed_for(case, self.context)
            self.assertGreaterEqual(seed['common_P2_alpha'], -1)
            self.assertLessEqual(seed['common_P2_alpha'], 2)
            model = self.context.model(sweep.parameters(case['Sigma_half_requested'],
                case['shear_sign_requested'], seed['common_P2_alpha']))
            row = sweep.initial_record(model, model.initial())
            self.assertLessEqual(abs(row['Sigma_half'] - case['Sigma_half_requested']), 3e-13)
            self.assertLessEqual(abs(row['Pi_half'] - case['Pi_half_requested']), 3e-13)
            self.assertAlmostEqual(row['signed_Sigma'], case['signed_Sigma_requested'], delta=3e-13)
            self.assertAlmostEqual(row['signed_Pi'], case['signed_Pi_requested'], delta=3e-13)
            self.assertEqual(row['shear_work_J_m3_s'], 2*row['s_inv_s']*row['D_physical_Pa'])
        self.assertLess(max(abs(sweep.seed_for(c,self.context)['common_P2_alpha']) for c in cases), .411)
        bad = dict(Sigma_half=.004, Pi_half=1., shear_sign=1, stress_sign=-1,
            H_base=self.context.calibration['H_base_per_s'],
            stress_per_alpha=self.context.calibration['stress_per_alpha_Pa'],
            kappa_time=self.context.calibration['kappa_time'])
        with self.assertRaises(ValueError):
            initial_seed(**bad)

    def test_numpy_scalar_export_boundary_stays_strict(self):
        payload = {'gates': {'positive_common_P2_family': np.bool_(True)},
                   'false_gate': np.bool_(False), 'value': np.float64(.4105784436521941),
                   'count': np.int64(64)}
        expected = {'gates': {'positive_common_P2_family': True},
                    'false_gate': False, 'value': .4105784436521941, 'count': 64}
        self.assertEqual(json.loads(sweep.canonical(payload)), expected)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'export.json'
            sweep.write_json(path,payload)
            self.assertEqual(json.loads(path.read_text()), expected)
            for bad in (np.float64(float('nan')), np.float64(float('inf'))):
                with self.assertRaises(ValueError):
                    sweep.canonical({'bad': bad})
                with self.assertRaises(ValueError):
                    sweep.write_json(path,{'bad': bad})
            with self.assertRaises(TypeError):
                sweep.canonical({'bad': object()})

    def test_history_csv_preserves_nested_energies(self):
        row = {'a': .2, 'Hamiltonian_source_J_m3': {'gamma': 1e-12, 'massive': 2e-12}}
        self.assertEqual(sweep.scalar_row(row), {'a': .2,
            'Hamiltonian_source_J_m3.gamma': 1e-12,
            'Hamiltonian_source_J_m3.massive': 2e-12})
        self.assertEqual(row['Hamiltonian_source_J_m3']['gamma'], 1e-12)

    def test_owner_prepared_same_input_short_steps_and_state_isolation(self):
        c = sweep.load_owner()
        case = {'Sigma_half_requested': .004, 'Pi_half_requested': .0004,
                'shear_sign_requested': -1, 'stress_sign_requested': 1}
        seed = sweep.seed_for(case, self.context)
        p = sweep.parameters(.004, -1, seed['common_P2_alpha'])
        original = c.EinsteinBoltzmann(p, a0=.1999, fast_massive=True, source_grid='8X8')
        prepared = self.context.model(p)
        a, b = original.initial(), prepared.initial()
        self.assertEqual(sweep.initial_record(original,a), sweep.initial_record(prepared,b))
        self.assertIsNot(a.gas_and_UV.gas, b.gas_and_UV.gas)
        self.assertIsNot(a.moments, b.moments)
        self.assertIsNot(prepared.massive_weight, original.massive_weight)
        self.assertFalse(prepared.massive.q.flags.writeable)
        dx = c.c13.stable_dx(.1999,.2)/64
        for i in range(2):
            target = .1999*math.exp((i+1)*dx)
            a, ra = original.step(a,target,feedback=True,compress=True)
            b, rb = prepared.step(b,target,feedback=True,compress=True)
            # Same source functions and reduction order should give exactly the
            # same observables; scientific gates below remain the authority.
            self.assertEqual(ra, rb)
            np.testing.assert_array_equal(a.moments,b.moments)
            self.assertEqual((a.a,a.b,a.s,a.H),(b.a,b.b,b.s,b.H))
            self.assertLessEqual(rb['nerr'],5e-12)
            self.assertLessEqual(rb['eerr'],5e-11)
        fresh = self.context.model(p)
        self.assertEqual(fresh.iterations,0)
        self.assertEqual(fresh.rhs_evals,0)
        self.assertNotIn('proxy',fresh.__dict__)
        self.assertIs(fresh.source,prepared.source)
        self.assertIs(fresh.owner,prepared.owner)
        fresh_initial = fresh.initial()
        self.assertEqual(fresh_initial.a,.1999)
        self.assertEqual(fresh_initial.gas_and_UV.photons.packet_count,0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
