"""Changed-dependency checks only; no 729-case or full-history rerun."""
import json
import math
from pathlib import Path
import struct
import unittest

import numpy as np
import cached_context as fast


class ExactCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = fast.split.PreparedContext()
        cls.cached = fast.PreparedContext(cache_size=128)
        cls.results = {'kernel_points': 0, 'kernel_bit_mismatches': 0,
                       'short_cases': [], 'historical_sweep_reruns': 0,
                       'timing_benchmarks': 0}

    def test_kernel_binary_identity_and_domain(self):
        for alpha_m, alpha_r in [(0., 0.), (.8, -.8), (-.8, .8), (2., -1.)]:
            params = fast.split.parameters(.004, 1, alpha_m, alpha_r)
            a, b = self.original.model(params), self.cached.model(params)
            for x in [0., math.nextafter(0., 1.), .000500125, .01, 1., 4.]:
                for shear in [-1., -.001, -0., 0., .001, 1.]:
                    expected = a.massive_source_3moments(x, shear)
                    for _ in range(2):
                        actual = b.massive_source_3moments(x, shear)
                        self.assertEqual(struct.pack('>3d', *expected), struct.pack('>3d', *actual))
                    self.results['kernel_points'] += 1
            self.assertGreater(b.moment_cache_info()['hits'], 0)
            for x, shear in [(float('nan'), 0.), (0., float('inf')), (-1., 0.), (4.1, 0.), (0., 1.1)]:
                with self.assertRaises(ValueError):
                    b.massive_source_3moments(x, shear)

    def test_signed_zero_adjacent_keys_eviction_and_freshness(self):
        context = fast.PreparedContext(cache_size=2)
        params = fast.split.parameters(0., 0, .8, -.8)
        model = context.model(params)
        for x, b in [(0., 0.), (0., -0.), (math.nextafter(0., 1.), 0.)]:
            model.massive_source_3moments(x, b)
        self.assertEqual(model.moment_cache_info()['misses'], 3)
        self.assertEqual(model.moment_cache_info()['evictions'], 1)
        self.assertEqual(model.moment_cache_info()['entries'], 2)
        model.massive_source_3moments(0., 0.)
        self.assertEqual(model.moment_cache_info()['misses'], 4)
        fresh = context.model(params)
        self.assertEqual(fresh.moment_cache_info()['entries'], 0)
        self.assertNotIn('proxy', fresh.__dict__)
        self.assertIsNot(model.massive_weight, fresh.massive_weight)
        self.assertIsNot(model.massive, fresh.massive)

    def test_bound_inputs_are_immutable_and_replacement_rejected(self):
        params = fast.split.parameters(0., 0, .8, -.8)
        for field in ['massive_q2', 'massive_weight']:
            model = self.cached.model(params)
            model.massive_source_3moments(0., 0.)
            array = getattr(model, field)
            with self.assertRaises(ValueError):
                array.setflags(write=True)
            setattr(model, field, array.copy())
            with self.assertRaisesRegex(ValueError, 'BINDING_CHANGED'):
                model.massive_source_3moments(0., 0.)
        model = self.cached.model(params)
        with self.assertRaises(ValueError):
            model.massive.mu2.setflags(write=True)
        model.massive.mass = 31.
        with self.assertRaisesRegex(ValueError, 'BINDING_CHANGED'):
            model.massive_source_3moments(0., 0.)
        for capacity in [0, -1, 4097, True, 1.5]:
            with self.assertRaises(ValueError):
                fast.PreparedContext(cache_size=capacity)

    def test_readonly_array_metadata_mutation_rejected(self):
        params = fast.split.parameters(0., 0, .8, -.8)
        for field in ['mu2', 'massive_q2', 'massive_weight']:
            for mutation in ['dtype', 'shape', 'strides']:
                with self.subTest(field=field, mutation=mutation):
                    model = self.cached.model(params)
                    model.massive_source_3moments(0., 0.)
                    array = model.massive.mu2 if field == 'mu2' else getattr(model, field)
                    if mutation == 'dtype':
                        array.dtype = np.dtype('uint64')
                    elif mutation == 'shape':
                        array.shape = (array.size,) if array.ndim > 1 else (array.size, 1)
                    else:
                        array.strides = tuple(0 for _ in array.strides)
                    with self.assertRaisesRegex(ValueError, 'BINDING_CHANGED'):
                        model.massive_source_3moments(0., 0.)

    def test_two_actual_short_steps_opposite_cancellation_and_isotropic(self):
        owner = fast.split.prior.load_owner()
        dx = owner.c13.stable_dx(.1999, .2) / 64
        coordinates = [(0., 0., 0.), (0., .0004, -.0004), (0., -.0004, .0004),
                       (.004, .0004, -.0004), (-.004, -.0004, .0004)]
        for sigma, pm, pr in coordinates:
            case = next(c for c in fast.split.signed_grid() if
                        (c['signed_Sigma_requested'], c['signed_Pi_m_requested'],
                         c['signed_Pi_r_requested']) == (sigma, pm, pr))
            seed = fast.split.seed_for(case, self.cached)
            params = fast.split.parameters(abs(sigma), int(np.sign(sigma)), seed['alpha_m'], seed['alpha_r'])
            reference, candidate = self.original.model(params), self.cached.model(params)
            left, right = reference.initial(), candidate.initial()
            self.assertEqual(fast.split.initial_record(reference, left), fast.split.initial_record(candidate, right))
            for step in range(2):
                target = .1999 * math.exp((step + 1) * dx)
                left, expected = reference.step(left, target, feedback=True, compress=True)
                right, actual = candidate.step(right, target, feedback=True, compress=True)
                self.assertEqual(expected, actual)
                self.assertEqual(left.moments.tobytes(), right.moments.tobytes())
                self.assertEqual((left.a, left.b, left.s, left.H), (right.a, right.b, right.s, right.H))
                self.assertLessEqual(actual['nerr'], 5e-12)
                self.assertLessEqual(actual['eerr'], 5e-11)
            info = candidate.moment_cache_info()
            self.assertGreater(info['hits'], 0)
            self.results['short_cases'].append({'case_id': case['case_id'], 'steps': 2,
                'row_and_state_binary_identity': True, 'cache': info,
                'owner_rhs_calls': candidate.rhs_evals,
                'nerr': float(actual['nerr']), 'eerr': float(actual['eerr'])})

    @classmethod
    def tearDownClass(cls):
        path = Path(__file__).parent / 'evidence/CACHE_CHECK.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(cls.results, indent=2) + '\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
