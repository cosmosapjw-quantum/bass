"""Validation of typed *proposed* receiver table, not Rust-native adoption."""
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from export_rei_bridge import generate,HEADER

class BridgeTests(unittest.TestCase):
    def test_eight_source_lanes_and_signed_geometry(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'bridge'
            meta=generate(out,41)
            self.assertEqual(meta['rows'],8*41)
            self.assertEqual(meta['csv_sha256'],hashlib.sha256((out/'PROPOSED_REI_BACKGROUND.csv').read_bytes()).hexdigest())
            with (out/'PROPOSED_REI_BACKGROUND.csv').open() as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(set(rows[0]),set(HEADER))
            self.assertEqual(rows[0]['case'],'COLD_FLRW')
            self.assertTrue(all(float(x['Sigma'])>=0 for x in rows))
            self.assertTrue(all(float(x['H_mean_per_s'])>0 for x in rows))
            minus=[r for r in rows if r['case']=='SIGNED_MINUS']
            plus=[r for r in rows if r['case']=='SIGNED_PLUS']
            self.assertLess(float(minus[0]['signed_s_over_H']),0)
            self.assertGreater(float(plus[0]['signed_s_over_H']),0)
            self.assertAlmostEqual(float(minus[0]['Sigma']),float(plus[0]['Sigma']),places=12)
            self.assertTrue(all(float(r['H_perp_per_s'])>0 and float(r['H_parallel_per_s'])>0 for r in rows))
            self.assertLess(max(x['max_independent_Raychaudhuri_rel_error'] for x in meta['cases_receipt']),1e-8)
            with self.assertRaises(FileExistsError):generate(out,41)

if __name__=='__main__':unittest.main(verbosity=2)
