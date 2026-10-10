import io
from decimal import Decimal
import unittest
import zipfile
import readback as v1
from readback_v2 import binary64_rows


class Binary64OracleTests(unittest.TestCase):
    def test_frozen_large_boundary_counterexample(self):
        with zipfile.ZipFile(v1.CONTRACT['archive']) as z:
            data = z.read('research/broad_history_20261010/evidence/RUN002/flrw_BASS_CELLS.csv')
        raw = v1.parse_cells(data)
        with self.assertRaisesRegex(AssertionError, 'PRODUCER_DEPTH'):
            v1.reference(raw)
        # Recorded first false failure retains its exact large-boundary tokens.
        cell = raw[1235]
        self.assertGreater(cell[0], Decimal('1e13'))
        converted = binary64_rows(data)
        self.assertEqual(converted[1235][0], Decimal.from_float(float(cell[0])))
        v1.reference(converted)
        wrong = [row[:] for row in converted]
        wrong[1235][5] *= Decimal('1.01')
        with self.assertRaisesRegex(AssertionError, 'PRODUCER_DEPTH'):
            v1.reference(wrong)


if __name__ == '__main__':
    unittest.main()
