"""Software-contract tests only. Synthetic subprocesses are NOT native xAct evidence.

Run with: python3 -B research/diagnostics/bg02_b0_20260905/native/test_receipt_accounting.py
No Wolfram installation, scientific calculation, provider, or repository mutation
outside each test's temporary directory is required.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('bg02_launcher_under_test', HERE / 'run_native.py')
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)
IDS = json.loads((HERE / 'CONTRACT.json').read_text(encoding='utf-8'))['required_ids']


class ReceiptAccountingTests(unittest.TestCase):
    def api(self, name):
        value = getattr(LAUNCHER, name, None)
        self.assertTrue(callable(value), 'missing receipt-contract API: ' + name)
        return value

    def test_partial_boolean_results_survive(self):
        r = self.api('summarize_checks')(IDS, {IDS[0]: True, IDS[1]: False})
        self.assertEqual((r['tests_succeeded'], r['tests_failed'], r['tests_not_evaluated']), (1, 1, 10))
        self.assertEqual(r['failed_ids'], [IDS[1]])
        self.assertEqual(r['not_evaluated_ids'], IDS[2:])
        self.assertFalse(r['exact_test_ids'])

    def test_no_receipt_is_not_twelve_failures(self):
        r = self.api('summarize_checks')(IDS, {})
        self.assertEqual((r['tests_succeeded'], r['tests_failed'], r['tests_not_evaluated']), (0, 0, 12))

    def test_nonboolean_values_are_not_evaluated(self):
        r = self.api('summarize_checks')(IDS, {IDS[0]: 1, IDS[1]: 'True', IDS[2]: None})
        self.assertEqual((r['tests_succeeded'], r['tests_failed'], r['tests_not_evaluated']), (0, 0, 12))
        self.assertEqual(r['invalid_result_ids'], IDS[:3])
        self.assertFalse(r['exact_test_ids'])

    def test_unknown_id_is_retained_but_not_admitted(self):
        checks = {key: True for key in IDS}
        checks['UNDECLARED_CHECK'] = True
        r = self.api('summarize_checks')(IDS, checks)
        self.assertEqual(r['tests_succeeded'], 12)
        self.assertEqual(r['unexpected_ids'], ['UNDECLARED_CHECK'])
        self.assertFalse(r['exact_test_ids'])

    def test_all_failures_are_observed_not_missing(self):
        r = self.api('summarize_checks')(IDS, dict.fromkeys(IDS, False))
        self.assertEqual((r['tests_succeeded'], r['tests_failed'], r['tests_not_evaluated']), (0, 12, 0))
        self.assertTrue(r['exact_test_ids'])

    def test_unknown_required_set_does_not_invent_zero_missing(self):
        r = self.api('summarize_checks')(None, {})
        self.assertIsNone(r['tests_not_evaluated'])
        self.assertFalse(r['required_ids_known'])
        self.assertFalse(r['exact_test_ids'])

    def test_duplicate_required_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            self.api('summarize_checks')([IDS[0], IDS[0]], {})

    def test_setup_warning_in_stdout_is_observed(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            warning = 'Verbose::shdw: Symbol Verbose appears in multiple contexts.'
            (out / 'stdout.log').write_text('package banner\n' + warning + '\n', encoding='utf-8')
            (out / 'stderr.log').write_text('', encoding='utf-8')
            hits = self.api('collect_rendered_messages')(out)
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0], {'file': 'stdout.log', 'line': 2, 'text': warning})

    def test_stderr_warning_is_observed_without_rewriting_log(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            raw = b'  Power::infy: Infinite expression.\n'
            (out / 'stdout.log').write_bytes(b'normal output\n')
            (out / 'stderr.log').write_bytes(raw)
            hits = self.api('collect_rendered_messages')(out)
            self.assertEqual(hits[0]['file'], 'stderr.log')
            self.assertEqual((out / 'stderr.log').read_bytes(), raw)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            self.api('strict_loads')('{"checks":{"A":false,"A":true}}')

    def test_atomic_writer_uses_observed_values_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'receipt.json'
            value = {'tests_succeeded': 2, 'tests_failed': 1, 'tests_not_evaluated': 9}
            LAUNCHER.write_new(target, value)
            self.assertEqual(json.loads(target.read_text(encoding='utf-8')), value)
            original = target.read_bytes()
            with self.assertRaises(FileExistsError):
                LAUNCHER.write_new(target, {'tests_succeeded': 12})
            self.assertEqual(target.read_bytes(), original)

    def synthetic_run(self, mode):
        """Exercise the actual launcher in a clean, entirely synthetic Git tree."""
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        repo = root / 'repo'
        native = repo / 'research/diagnostics/bg02_b0_20260905/native'
        native.mkdir(parents=True)
        shutil.copyfile(HERE / 'run_native.py', native / 'run_native.py')
        (native / 'calibrate.wls').write_text('(* SYNTHETIC TEST INPUT; NOT XACT *)\n', encoding='utf-8')
        helper = repo / 'wolfram/BASS/Kernel/Authority/Environment.wl'
        helper.parent.mkdir(parents=True)
        helper.write_text('(* SYNTHETIC TEST INPUT *)\n', encoding='utf-8')
        archive = root / 'synthetic-archive'
        archive.write_bytes(b'not a real xAct archive; process test only')
        contract = json.loads((HERE / 'CONTRACT.json').read_text(encoding='utf-8'))
        contract['xact_archive_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
        (native / 'CONTRACT.json').write_text(json.dumps(contract), encoding='utf-8')
        git_env = os.environ.copy()
        git_env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
        for args in [('init',), ('config', 'user.name', 'Synthetic Test'),
                     ('config', 'user.email', 'synthetic@example.invalid'),
                     ('add', '.'), ('-c', 'commit.gpgsign=false', 'commit', '-m', 'synthetic test fixture')]:
            subprocess.run(['git', '-C', str(repo), *args], env=git_env,
                           check=True, capture_output=True, timeout=15)
        executable = root / 'synthetic-kernel'
        checks = {IDS[0]: True, IDS[1]: False} if mode == 'partial' else dict.fromkeys(IDS, True)
        payload = {'schema_version': '1.0.0', 'stage_id': contract['stage_id'],
                   'status': 'FAIL_NATIVE_TYPED_VIEW_CALIBRATION' if mode == 'partial' else contract['native_success_status'],
                   'native_xact_evaluated': True, 'activation': {'archive_sha256': contract['xact_archive_sha256']},
                   'required_ids': IDS, 'observed_ids': list(checks), 'checks': checks,
                   'failed_ids': [key for key, value in checks.items() if value is False], 'messages': [],
                   'synthetic_test_only': True}
        body = '#!' + sys.executable + '\nimport json, os\nfrom pathlib import Path\n'
        body += 'payload = json.loads(' + repr(json.dumps(payload)) + ')\n'
        body += 'Path(os.environ["BASS_NATIVE_OUTPUT"], "native.json").write_text(json.dumps(payload), encoding="utf-8")\n'
        if mode == 'warning':
            body += 'print("Verbose::shdw: SYNTHETIC initialization warning.")\n'
        body += 'raise SystemExit(' + ('1' if mode == 'partial' else '0') + ')\n'
        executable.write_text(body, encoding='utf-8')
        executable.chmod(0o700)
        out = root / 'output'
        command = [sys.executable, '-B', str(native / 'run_native.py'), '--repo', str(repo),
                   '--output', str(out), '--xact-source', str(archive), '--timeout', '10',
                   '--wolfram', str(root / 'absent-kernel') if mode == 'missing' else str(executable)]
        proc = subprocess.run(command, capture_output=True, text=True, timeout=25, env=git_env)
        receipt_path = out / 'PROCESS_RECEIPT.json'
        self.assertTrue(receipt_path.is_file(), proc.stdout + proc.stderr)
        return proc, json.loads(receipt_path.read_text(encoding='utf-8'))

    def test_launcher_missing_kernel_accounts_for_unevaluated_checks(self):
        proc, r = self.synthetic_run('missing')
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual((r.get('tests_succeeded'), r.get('tests_failed'), r.get('tests_not_evaluated')), (0, 0, 12))
        self.assertIn('WOLFRAM_EXECUTABLE_NOT_FOUND', r.get('error', ''))
        self.assertFalse(r['native_xact_evaluated'])

    def test_launcher_partial_failure_preserves_observed_results(self):
        proc, r = self.synthetic_run('partial')
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual((r.get('tests_succeeded'), r.get('tests_failed'), r.get('tests_not_evaluated')), (1, 1, 10))
        self.assertFalse(r['exact_test_ids'])
        self.assertTrue(r['input_bytes_unchanged'])

    def test_launcher_does_not_admit_unrecorded_setup_warning(self):
        proc, r = self.synthetic_run('warning')
        self.assertNotEqual(proc.returncode, 0, 'nativeBody messages=[] must not hide a rendered setup warning')
        self.assertEqual(r['tests_succeeded'], 12)
        self.assertEqual(r['tests_failed'], 0)
        self.assertEqual(r['tests_not_evaluated'], 0)
        self.assertTrue(r['rendered_messages'])
        self.assertNotEqual(r['status'], 'PASS_NATIVE_CALIBRATION_ONLY')


if __name__ == '__main__':
    unittest.main(verbosity=2)
