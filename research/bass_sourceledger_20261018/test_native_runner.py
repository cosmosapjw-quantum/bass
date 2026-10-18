"""Runner/reader infrastructure tests using explicit synthetic witnesses.

These are NOT native Rust measurements and never promoted as such.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from native_runner import (validate_native,compiler_executable,stage_owner,REI_SHA,
                           SOURCE_ID,SCHEMA,COMPLETE,strict_json)
from source_oracle import Case
from deposition import simulate

class ProtocolTests(unittest.TestCase):
    def setUp(self):
        c=Case('synthetic',.3,.02,1e-16,1e-19,1e12,nseg=4,nmu=8,nenergy=32,qmin=1.,qmax=512.)
        self.expected={'synthetic':simulate([c],.4,.025)}
        self.row={k:v for k,v in self.expected['synthetic'].items() if k not in ('scope',)}
        self.probe='a'*64
        self.row.update(schema=SCHEMA,owner_sha=REI_SHA,probe_sha=self.probe,source_id=SOURCE_ID)
        self.end=dict(schema=COMPLETE,count=1,owner_sha=REI_SHA,probe_sha=self.probe)
    def encoded(self,row=None,end=None):
        return json.dumps(self.row if row is None else row)+'\n'+json.dumps(self.end if end is None else end)+'\n'
    def check(self,text):return validate_native(text,self.expected,REI_SHA,self.probe)
    def test_valid_synthetic_protocol_only(self):
        v=self.check(self.encoded())
        self.assertEqual(v['cases'],1)
        self.assertLess(max(v['defects'][0]['normalized_differences'].values()),1e-14)
    def test_zero_test_cargo_exit_is_not_evidence(self):
        for text in ('','running 0 tests\ntest result: ok. 0 passed; 0 failed\n',json.dumps(self.end)):
            with self.assertRaises(ValueError):self.check(text)
    def test_tampered_compiled_owner_or_probe_rejected(self):
        for name in ('owner_sha','probe_sha','source_id'):
            row=dict(self.row);row[name]='wrong'
            with self.assertRaises(ValueError):self.check(self.encoded(row))
    def test_missing_or_duplicate_rows(self):
        for text in (json.dumps(self.row),json.dumps(self.row)+'\n'+self.encoded()):
            with self.assertRaises(ValueError):self.check(text)
    def test_wrong_birth_or_complete_count(self):
        row=dict(self.row);row['births']=0
        with self.assertRaises(ValueError):self.check(self.encoded(row))
        end=dict(self.end);end['count']=0
        with self.assertRaises(ValueError):self.check(self.encoded(end=end))
    def test_nonfinite_and_duplicate_json_fields_rejected(self):
        for name in ('delta','inventory_u','work'):
            row=dict(self.row);row[name]=float('nan')
            with self.assertRaises(ValueError):self.check(self.encoded(row))
        with self.assertRaisesRegex(ValueError,'DUPLICATE_JSON_KEY'):
            strict_json('{"schema":"a","schema":"b"}')
    def test_disturbed_moment_fails_parity(self):
        for name in ('inventory_n','inventory_u','delta','work'):
            row=deepcopy(self.row);row[name]+=max(abs(row['ledger_u']),1e-30)*1e-7
            with self.assertRaises(ValueError):self.check(self.encoded(row))
    def test_ray_shape_and_positivity(self):
        for vector in ([],[-1.]*8,[float('inf')]*8):
            row=deepcopy(self.row);row['ray_number']=vector
            with self.assertRaises(ValueError):self.check(self.encoded(row))
    def test_raw_ledgers_must_recompute(self):
        row=deepcopy(self.row);row['energy_residual']=row['ledger_u']*1e-12
        with self.assertRaisesRegex(ValueError,'INCONSISTENT'):self.check(self.encoded(row))
    def test_no_compiler_artifact_means_no_native_program(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError,'NO_UNIQUE_NATIVE_EXECUTABLE'):
                compiler_executable('running 0 tests\n',Path(t))
    def test_compiler_artifact_exact_executable(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);exe=root/'native';exe.write_text('#!/bin/sh\n');exe.chmod(0o755)
            row={'reason':'compiler-artifact','target':{'name':'bass_sourceledger_probe','kind':['bin']},'executable':str(exe)}
            self.assertEqual(compiler_executable(json.dumps(row),root),exe)
            with self.assertRaisesRegex(ValueError,'INVALID_NATIVE_EXECUTABLE'):
                compiler_executable(json.dumps(row),root/'another')

class NativeStagingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.repo=self.root/'git';self.repo.mkdir()
        def cmd(*args):return subprocess.run(['git','-C',str(self.repo),*args],check=True,capture_output=True).stdout.decode().strip()
        self.cmd=cmd;cmd('init','-q');cmd('config','user.name','Synthetic Test');cmd('config','user.email','test@example.invalid')
        crate=self.repo/'rust/rei_microphysics';(crate/'src').mkdir(parents=True)
        (crate/'Cargo.toml').write_text('[package]\nname="synthetic_only"\nversion="0.1.0"\nedition="2021"\n')
        (crate/'src/lib.rs').write_text('const X:&str=include_str!("../../../research/input.json");\n')
        (self.repo/'research').mkdir();(self.repo/'research/input.json').write_text('{"fixture":"synthetic_not_real_native"}\n')
        cmd('add','.');cmd('commit','-qm','fixture');self.sha=cmd('rev-parse','HEAD')
        self.pins={'lib.rs':hashlib.sha256((crate/'src/lib.rs').read_bytes()).hexdigest()}
    def tearDown(self):self.temp.cleanup()
    def test_exact_git_blob_and_recursive_include_not_dirty_file(self):
        (self.repo/'research/input.json').write_text('DIRTY DO NOT COPY')
        out=self.root/'staged';r=stage_owner(self.repo,out,self.sha,self.pins)
        self.assertEqual(r['source_files'],3)
        self.assertEqual((out/'research/input.json').read_text(),'{"fixture":"synthetic_not_real_native"}\n')
        self.assertEqual((self.repo/'research/input.json').read_text(),'DIRTY DO NOT COPY')
    def test_preexisting_staging_rejected(self):
        out=self.root/'staged';out.mkdir()
        with self.assertRaises(FileExistsError):stage_owner(self.repo,out,self.sha,self.pins)
    def test_mismatched_source_pin_rejected_before_write(self):
        out=self.root/'staged'
        with self.assertRaisesRegex(ValueError,'PINNED_NATIVE_SOURCE'):
            stage_owner(self.repo,out,self.sha,{'lib.rs':'0'*64})
        self.assertFalse(out.exists())
    def test_repo_escaping_include_rejected(self):
        p=self.repo/'rust/rei_microphysics/src/lib.rs'
        p.write_text('const X:&str=include_str!("../../../../secret");\n')
        self.cmd('add','.');self.cmd('commit','-qm','escape')
        with self.assertRaisesRegex(ValueError,'INCLUDE_ESCAPES_REPO'):
            stage_owner(self.repo,self.root/'staged',self.cmd('rev-parse','HEAD'),{})
    def test_dynamic_include_rejected_not_guessed(self):
        p=self.repo/'rust/rei_microphysics/src/lib.rs';p.write_text('include!(concat!("a", "b"));\n')
        self.cmd('add','.');self.cmd('commit','-qm','dynamic')
        with self.assertRaisesRegex(ValueError,'NONLITERAL_INCLUDE'):
            stage_owner(self.repo,self.root/'staged',self.cmd('rev-parse','HEAD'),{})
if __name__=='__main__':unittest.main(verbosity=2)
