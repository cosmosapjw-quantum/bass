"""Packaging controls only; never a scientific accuracy test."""
from pathlib import Path
import shutil
import tempfile
import unittest
from prepare_git import prepare_history
HERE = Path(__file__).resolve().parent
DATA = HERE / 'evidence/S3_CAMPAIGN_FINAL'
class GitRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root/'evidence/S3_CAMPAIGN_FINAL'
        self.data.mkdir(parents=True)
        shutil.copy2(DATA/'HISTORY.csv.gz',self.data/'HISTORY.csv.gz')
    def tearDown(self):
        self.temp.cleanup()
    def test_missing_csv_restored_and_idempotent(self):
        prepare_history(self.root)
        p=self.data/'HISTORY.csv'
        self.assertTrue(p.is_file(), 'Git-only checkout needs exact CSV restored')
        self.assertEqual(p.read_bytes(),(DATA/'HISTORY.csv').read_bytes())
        before=p.stat().st_mtime_ns
        prepare_history(self.root)
        self.assertEqual(p.stat().st_mtime_ns,before)
    def test_existing_changed_csv_rejected_unchanged(self):
        p=self.data/'HISTORY.csv';p.write_bytes(b'changed,source\n')
        with self.assertRaisesRegex(ValueError,'EXISTING_HISTORY_HASH'):
            prepare_history(self.root)
        self.assertEqual(p.read_bytes(),b'changed,source\n')
    def test_changed_compressed_input_rejected(self):
        p=self.data/'HISTORY.csv.gz';p.write_bytes(b'wrong archive')
        with self.assertRaisesRegex(ValueError,'COMPRESSED_HISTORY_HASH'):
            prepare_history(self.root)
        self.assertFalse((self.data/'HISTORY.csv').exists())
if __name__=='__main__':unittest.main(verbosity=2)
