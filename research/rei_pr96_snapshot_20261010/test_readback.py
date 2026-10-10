"""Targeted receiver evidence rejection tests; no history solver."""
import tempfile
import unittest
from pathlib import Path

import readback


class RejectionTests(unittest.TestCase):
    def test_wrong_immutable_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input"
            path.write_bytes(b"altered source")
            with self.assertRaisesRegex(ValueError, "IMMUTABLE_SOURCE_MISMATCH"):
                readback.check_hash(path, "0"*64)

    def test_missing_epoch_and_nonfinite_output_rejected(self):
        for output in ("0 1 1 1 1\n", "0 nan 1 1 1\n"*17):
            with self.assertRaisesRegex(ValueError, "RECEIVER_OUTPUT_SHAPE_OR_FINITE"):
                readback.compare(output, [], [], 64*2.220446049250313e-16)

    def test_double_conversion_cannot_pass(self):
        rows = [[float(i), 1., 0., 1., 0., 0.] for i in range(17)]
        refs = [{"ne_m3_decimal": "1000000", "rate_s_inverse_decimal": "1", "archived_ne_m3": 1e6}]*17
        output = "".join(f"{i} 1e12 1e12 1 1\n" for i in range(17))
        with self.assertRaisesRegex(ValueError, "RECEIVER_PARITY"):
            readback.compare(output, rows, refs, 64*2.220446049250313e-16)


if __name__ == "__main__":
    unittest.main()
