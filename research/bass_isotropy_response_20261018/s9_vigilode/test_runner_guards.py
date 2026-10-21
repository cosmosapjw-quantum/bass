"""Focused prepublication regressions: stale build, test-only, truncated raw.

No compiler, AD callback or differential equation is run by these tests.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from build_binding import CLIENT_FILES,attest_build,source_identity,validate_attestation
from campaign import record_case_output

class BuildBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.binary=self.root/'old_existing_binary';self.binary.write_bytes(b'bounded synthetic binary fixture')
        self.receipt={'schema':'BASS_S9_PREPARATION_V1','status':'prepared',
            'client_source_sha256':{p:hashlib.sha256(p.encode()).hexdigest() for p in CLIENT_FILES},
            'balance_owner_sha256':'b'*64,'vigilode_source':'a'*40,'vigilode_tree':'c'*40,
            'source_files_verified':178,'source_bytes':5196962,
            'binary':{'path':str(self.binary),'sha256':hashlib.sha256(self.binary.read_bytes()).hexdigest()},
            'commands':[{'command':['cargo','build','--locked','--bin','bass-s9-vigilode'],'exit_code':0}]}
        self.identity=source_identity(self.receipt)
    def tearDown(self): self.temp.cleanup()

    def test_test_only_cannot_attest_an_existing_binary(self):
        self.receipt['commands']=[{'command':['cargo','test','--locked','--test','adapter_contracts'],'exit_code':0}]
        for mode in ['fresh_build','verified_prior_build']:
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'NO_SUCCESSFUL_LOCKED_BINARY_BUILD'):
                attest_build(self.receipt,self.binary,self.identity,mode=mode,origin_receipt_sha256='e'*64)

    def test_stale_client_source_cannot_reuse_a_matching_old_binary(self):
        changed=copy.deepcopy(self.identity);changed['client_source_sha256']['src/lib.rs']='d'*64
        with self.assertRaisesRegex(ValueError,'COMPILED_CLIENT_OR_OWNER_SOURCE_MISMATCH'):
            attest_build(self.receipt,self.binary,changed,mode='verified_prior_build',origin_receipt_sha256='e'*64)

    def test_changed_binary_cannot_reuse_a_genuine_source_receipt(self):
        self.binary.write_bytes(b'a different executable')
        with self.assertRaisesRegex(ValueError,'COMPILED_BINARY_BYTES_MISMATCH'):
            attest_build(self.receipt,self.binary,self.identity,mode='verified_prior_build',origin_receipt_sha256='e'*64)

    def test_failed_unlocked_or_wrong_target_builds_do_not_attest(self):
        records=[{'command':['cargo','build','--locked','--bin','bass-s9-vigilode'],'exit_code':101},
                 {'command':['cargo','build','--bin','bass-s9-vigilode'],'exit_code':0},
                 {'command':['cargo','build','--locked','--bin','another-target'],'exit_code':0}]
        for record in records:
            self.receipt['commands']=[record]
            with self.subTest(record=record),self.assertRaisesRegex(ValueError,'NO_SUCCESSFUL_LOCKED_BINARY_BUILD'):
                attest_build(self.receipt,self.binary,self.identity,mode='fresh_build')

    def test_explicit_genuine_build_reuse_records_no_new_compilation(self):
        attestation=attest_build(self.receipt,self.binary,self.identity,
            mode='verified_prior_build',origin_receipt_sha256='e'*64)
        current=copy.deepcopy(self.receipt);current.update({'schema':'BASS_S9_PREPARATION_V2',
            'commands':[],'binary_attestation':attestation})
        self.assertFalse(validate_attestation(current,self.binary)['new_compilation_performed'])
        self.assertEqual(current['binary_attestation']['mode'],'verified_prior_build')
        with self.assertRaisesRegex(ValueError,'NO_BINARY_BUILD_IN_CURRENT_INVOCATION'):
            attest_build(current,self.binary,self.identity,mode='fresh_build')

    def test_campaign_requires_explicit_v2_attestation(self):
        with self.assertRaisesRegex(ValueError,'EXPLICIT_BINARY_BUILD_ATTESTATION_REQUIRED'):
            validate_attestation(self.receipt,self.binary)

class RawReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def folder(self,name,raw):
        folder=self.root/name;folder.mkdir();(folder/'RAW.json').write_bytes(raw)
        (folder/'console.log').write_bytes(b'original console evidence\n')
        return folder
    def assess(self,folder,observer,code=0):
        process={'command':['synthetic-no-execution'],'exit_code':code,'elapsed_seconds':0.0}
        return record_case_output(folder,process,{}, {},{'name':folder.name},observer=observer)
    def assert_next_case_runs(self):
        folder=self.folder('next_case',b'{}')
        def observed(*args):
            self.assertTrue((folder/'PROCESS.json').is_file())
            return {'case':'next_case','status':'completed','completed':True,'all_quality_gates':True}
        result=self.assess(folder,observed)
        self.assertTrue(result['completed'])
        self.assertTrue(json.loads((folder/'ASSESSMENT.json').read_text())['completed'])

    def test_truncated_raw_is_typed_preserved_and_next_case_continues(self):
        data=b'{"truncated":';folder=self.folder('truncated',data)
        result=self.assess(folder,lambda *args:self.fail('truncated JSON must not reach observer'),code=124)
        self.assertEqual(result['failure']['kind'],'raw_readback_or_observer_failure')
        self.assertEqual(result['failure']['stage'],'raw_json_parse')
        self.assertEqual((folder/'RAW.json').read_bytes(),data)
        self.assertEqual((folder/'console.log').read_bytes(),b'original console evidence\n')
        process=json.loads((folder/'PROCESS.json').read_text())
        self.assertEqual(process['exit_code'],124);self.assertIn('raw_sha256',process)
        self.assert_next_case_runs()

    def test_observer_exception_keeps_process_and_raw(self):
        folder=self.folder('observer_error',b'{"status":"completed"}')
        def broken(*args):
            self.assertTrue((folder/'PROCESS.json').exists())
            raise ArithmeticError('synthetic observer rejection')
        result=self.assess(folder,broken)
        self.assertEqual(result['failure']['stage'],'observer')
        self.assertEqual(result['failure']['error_type'],'ArithmeticError')
        self.assert_next_case_runs()

    def test_nonfinite_observer_serialization_is_typed_and_continues(self):
        folder=self.folder('nonfinite_summary',b'{}')
        result=self.assess(folder,lambda *args:{'status':'completed','completed':True,'bad':float('nan')})
        self.assertEqual(result['failure']['stage'],'assessment_serialization')
        self.assertFalse(json.loads((folder/'ASSESSMENT.json').read_text())['completed'])
        self.assertEqual((folder/'RAW.json').read_bytes(),b'{}')
        self.assert_next_case_runs()

    def test_nonzero_process_cannot_keep_quality_pass(self):
        folder=self.folder('exit_disagreement',b'{}')
        result=self.assess(folder,lambda *args:{'status':'completed','completed':True,'all_quality_gates':True},code=1)
        self.assertFalse(result['completed']);self.assertFalse(result['all_quality_gates'])
        self.assertEqual(result['failure']['kind'],'process_return_inconsistency')

if __name__=='__main__': unittest.main(verbosity=2)
