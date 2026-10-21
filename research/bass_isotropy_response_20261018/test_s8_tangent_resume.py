"""Only regression checks for the actual S8 NumPy-bool serialization defect."""
import json
import unittest
import numpy as np
import run_s8_tangent_resume as resume


class SerializationRegression(unittest.TestCase):
    def test_numpy_boolean_preserves_both_pass_and_fail(self):
        for value in (True, False):
            with self.subTest(value=value):
                original = {'gate_results': {'richardson_accuracy': np.bool_(value),
                                             'central_difference_order2': True},
                            'measured_error': 1.0230571945157863e-10}
                with self.assertRaises(TypeError):
                    json.dumps(original, allow_nan=False)
                repaired = resume.normalized_assessment(original)
                serialized = json.loads(json.dumps(repaired, allow_nan=False))
                self.assertIs(serialized['gate_results']['richardson_accuracy'], value)
                self.assertEqual(serialized['measured_error'], original['measured_error'])
                self.assertIs(type(original['gate_results']['richardson_accuracy']), np.bool_)

    def test_nonboolean_is_not_reinterpreted_as_gate(self):
        with self.assertRaisesRegex(TypeError, 'EXPECTED_RICHARDSON_BOOLEAN'):
            resume.normalized_assessment({'gate_results': {'richardson_accuracy': np.float64(1.0)}})


if __name__ == '__main__':
    unittest.main(verbosity=2)

