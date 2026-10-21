"""New runner validation regressions; synthetic rows are parser tests only."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from run_native_adapter import REI_SHA, SOURCE_ID, blob, validate_measurements, verify_blob

def synthetic_parser_rows():
    rows=[]
    keys=[(n,96,b,m) for n in (8,16,32) for b in (-.3,0.,.3) for m in ("P2","P2P4")]
    keys.extend((8,24,.3,m) for m in ("P2","P2P4"))
    for n,e,b,m in keys:
        rows.append(dict(schema="bass.angular.native.s3.v1",n_mu=n,n_energy=e,b_birth=b,mode=m,
                         inventory_n=1.,inventory_u=20.,min_weight=.01,weight_p2=0.,weight_p4=0.,
                         ledger_n_residual=0.,ledger_u_residual=0.,derivative_central=-1.6,
                         derivative_legendre=-1.6,photon_vs_source_relative=0.,
                         energy_vs_source_moment_relative=0.,energy_p2=0.,energy_p4=0.))
    rows.append(dict(schema="bass.angular.native.s3.complete.v1",rows=20,owner_commit=REI_SHA,source_id=SOURCE_ID))
    return rows

class RunnerValidationTests(unittest.TestCase):
    def validate(self,rows):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"parser_only.jsonl";p.write_text("\n".join(json.dumps(r) for r in rows)+"\n")
            return validate_measurements(p)
    def test_exact_bytes_and_changed_source(self):
        raw=b"immutable spectral owner\n";entry=dict(path="owner.rs",size=len(raw),sha=blob(raw),sha256=hashlib.sha256(raw).hexdigest())
        self.assertEqual(verify_blob(raw,entry),raw)
        with self.assertRaisesRegex(ValueError,"IMMUTABLE_SOURCE_IDENTITY"):verify_blob(raw+b"\n",entry)
    def test_complete_matrix_parser(self):
        self.assertEqual(self.validate(synthetic_parser_rows())["rows"],20)
    def test_incomplete_or_duplicated_matrix_rejected(self):
        rows=synthetic_parser_rows()
        with self.assertRaisesRegex(ValueError,"MISSING_NATIVE_COMPLETION"):self.validate(rows[:-1])
        rows[0]=copy.deepcopy(rows[1])
        with self.assertRaisesRegex(ValueError,"NATIVE_CASE_IDENTITY"):self.validate(rows)
    def test_nonfinite_and_source_identity_rejected(self):
        rows=synthetic_parser_rows();rows[0]["inventory_n"]=float("nan")
        with self.assertRaisesRegex(ValueError,"NONFINITE_NATIVE_JSON"):self.validate(rows)
        rows=synthetic_parser_rows();rows[-1]["owner_commit"]="0"*40
        with self.assertRaisesRegex(ValueError,"NATIVE_COMPLETION_IDENTITY"):self.validate(rows)
    def test_bad_weight_moment_and_ledger_rejected(self):
        rows=synthetic_parser_rows();rows[0]["weight_p2"]=1e-10
        with self.assertRaisesRegex(ValueError,"NATIVE_WEIGHT_MOMENT"):self.validate(rows)
        rows=synthetic_parser_rows();rows[0]["ledger_u_residual"]=1e-6
        with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_LEDGER"):self.validate(rows)
    def test_native_response_must_match_measured_energy_moments(self):
        rows=synthetic_parser_rows();rows[0]["derivative_central"]=-1.5
        with self.assertRaisesRegex(ValueError,"NATIVE_COLLISIONLESS_DERIVATIVE"):self.validate(rows)

if __name__=="__main__":unittest.main()
