"""Small infrastructure controls, not BASS physics or an NCP64 campaign.

Run only after the parent freezes the source and authorizes this verification.
All helper processes and files belong to this test's temporary directory.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zipfile

import bundle
import resources
import runner

HELPER = '''import json,pathlib,subprocess,sys,time
mode,output,input_path=sys.argv[1:4]
data=json.loads(pathlib.Path(input_path).read_text())
if mode=='fail': sys.exit(7)
if mode=='output_budget':
    for index in range(8):
        (pathlib.Path(output).parent/f'chunk-{index}').write_bytes(b'x'*32768)
if mode=='sleep':
    child="import pathlib,sys,time; time.sleep(2); pathlib.Path(sys.argv[1]).write_text('late')"
    subprocess.Popen([sys.executable,'-c',child,str(pathlib.Path(output).parent/'late-marker')])
    time.sleep(10)
if len(sys.argv)>4: assert pathlib.Path(sys.argv[4]).is_file()
pathlib.Path(output).write_text(json.dumps({'status':'FAIL' if mode=='reject' else 'PASS_SCOPED','value':data['value']}))
'''

# Imports the actual production helper copied byte-for-byte into the test repo.
# The deliberately stubborn descendant requires the helper's TERM/KILL path.
PRODUCTION_WRAPPER = r'''import importlib.util,json,pathlib,sys
module_path,output_path=sys.argv[1:3]
mode=sys.argv[3] if len(sys.argv)>3 else 'interrupt'
spec=importlib.util.spec_from_file_location('s12_actual_process_control',module_path)
production=importlib.util.module_from_spec(spec);spec.loader.exec_module(production)
output=pathlib.Path(output_path)
grandchild="import os,pathlib,signal,sys,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(3); pathlib.Path(sys.argv[2]).write_text('late')"
child="import signal,subprocess,sys,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2],sys.argv[3]]); time.sleep(10)"
if mode=='normal_exit':
    child="""import pathlib,subprocess,sys,time
subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2],sys.argv[3]])
deadline=time.monotonic()+1
while not pathlib.Path(sys.argv[2]).exists() and time.monotonic()<deadline: time.sleep(.01)
assert pathlib.Path(sys.argv[2]).exists()
"""
record=production.run_owned([sys.executable,'-c',child,grandchild,str(output.parent/'nested-ready'),str(output.parent/'nested-late')],
    stdout_path=output.parent/'nested.stdout',stderr_path=output.parent/'nested.stderr',
    receipt_path=output.parent/'nested-receipt.json',timeout_s=5)
output.write_text(json.dumps({'status':record['status']}))
sys.exit(record['exit_code'])
'''


class InfrastructureControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="bass_s12_infra_")
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"; self.repo.mkdir()
        self.runs = self.root / "runs"
        (self.repo / "helper.py").write_text(HELPER)
        (self.repo / "input.json").write_text('{"value": 23}\n')
        self.manifest_path = self.root / "jobs.json"
        self.data = {"schema": runner.SCHEMA, "scope": "new_s12_birth_memory",
                     "allow_completed_campaign_replay": False,
                     "source_files": {"helper.py": runner.digest_file(self.repo / "helper.py")},
                     "reserve_cpus": 0, "reserve_ram_bytes": 0, "max_workers": 2,
                     "jobs": [self.job("case") ]}

    def tearDown(self):
        self.temporary.cleanup()

    def job(self, ident, mode="pass", needs=None):
        return {"id": ident, "kind": "new_rust_history", "needs": needs or [],
                "argv": [sys.executable, "{repo}/helper.py", mode, "{run}/result.json", "{repo}/input.json"],
                "input_files": {"input.json": runner.digest_file(self.repo / "input.json")},
                "cpus": 1, "ram_bytes": 128 << 20, "timeout_s": 5,
                "output_budget_bytes": 1 << 20, "artifacts": ["result.json"],
                "accept": [{"artifact": "result.json", "pointer": "/status", "equals": "PASS_SCOPED"}]}

    def observation(self, profile, disk_root, own_group_ids=()):
        affinity = sorted(os.sched_getaffinity(0))[:2]
        return {"profile": profile, "configured": {"workers": 2}, "affinity": affinity,
                "cpu_cap": len(affinity), "ram_cap_bytes": 512 << 20,
                "ram_available_bytes": 512 << 20, "busy_cpus_estimate": 0,
                "own_busy_cpus_estimate": 0, "own_process_groups": resources.process_groups(own_group_ids),
                "procfs_namespace_proof": resources.procfs_identity(),
                "disk_allocated_bytes": resources.allocated_bytes(disk_root), "disk_free_bytes": 1 << 32}

    def run_once(self, observation=None):
        self.manifest_path.write_text(json.dumps(self.data))
        manifest, sha = runner.load_manifest(self.manifest_path, self.repo)
        with patch.object(resources, "snapshot", side_effect=observation or self.observation):
            return runner.execute(manifest, sha, self.repo, self.runs, self.root, "sandbox")

    def receipts(self, ident):
        return list((self.runs / ident).glob("*/receipt.json"))

    def test_exact_pass_resume_and_changed_artifact(self):
        first = self.run_once(); self.assertEqual(first["status"], "PASS")
        original = self.receipts("case")[0]
        original_bytes = original.read_bytes()
        second = self.run_once()
        self.assertEqual(second["jobs"]["case"]["status"], "SKIPPED_EXACT_PASS")
        self.assertEqual(len(self.receipts("case")), 1)
        (original.parent / "result.json").write_text("tampered")
        third = self.run_once()
        self.assertEqual(third["jobs"]["case"]["status"], "PASS")
        self.assertEqual(len(self.receipts("case")), 2)
        self.assertEqual(original.read_bytes(), original_bytes)
        self.assertEqual((original.parent / "result.json").read_text(), "tampered")

    def test_failed_attempt_is_preserved_and_never_skipped(self):
        self.data["jobs"][0] = self.job("case", "fail")
        self.assertEqual(self.run_once()["jobs"]["case"]["status"], "FAIL")
        old = self.receipts("case")[0].read_bytes()
        self.assertEqual(self.run_once()["jobs"]["case"]["status"], "FAIL")
        self.assertEqual(len(self.receipts("case")), 2)
        self.assertIn(old, [p.read_bytes() for p in self.receipts("case")])

    def test_zero_exit_does_not_bypass_scientific_json_gate(self):
        self.data["jobs"][0] = self.job("case", "reject")
        self.assertEqual(self.run_once()["status"], "INCOMPLETE_OR_FAIL")
        rec = json.loads(self.receipts("case")[0].read_bytes())
        self.assertEqual(rec["exit_code"], 0)
        self.assertEqual(rec["status"], "FAIL")
        self.assertTrue(any(x.startswith("JSON_ACCEPTANCE") for x in rec["failures"]))

    def test_build_dependency_then_exact_resume(self):
        build = self.job("build"); build["kind"] = "build"; build["accept"] = []
        case = self.job("case", needs=["build"])
        case["argv"].append("{dep:build}/result.json")
        self.data["jobs"] = [build, case]
        self.assertEqual(self.run_once()["status"], "PASS")
        second = self.run_once()
        self.assertTrue(all(x["status"] == "SKIPPED_EXACT_PASS" for x in second["jobs"].values()))

    def test_failed_dependency_blocks_only_its_descendant(self):
        self.data["jobs"] = [self.job("bad", "fail"), self.job("child", needs=["bad"]), self.job("independent")]
        result = self.run_once()
        self.assertEqual(result["jobs"]["bad"]["status"], "FAIL")
        self.assertEqual(result["jobs"]["child"]["status"], "BLOCKED_DEPENDENCY")
        self.assertEqual(result["jobs"]["independent"]["status"], "PASS")
        self.assertFalse((self.runs / "child").exists())

    def test_hash_mismatch_is_rejected_before_execution(self):
        (self.repo / "input.json").write_text('{"value": 24}\n')
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            self.run_once()
        self.assertFalse(self.runs.exists())

    def test_reserved_load_refuses_new_process(self):
        def saturated(profile, disk_root, own_group_ids=()):
            obs = self.observation(profile, disk_root, own_group_ids)
            obs["busy_cpus_estimate"] = obs["cpu_cap"]
            return obs
        result = self.run_once(saturated)
        self.assertEqual(result["jobs"]["case"]["status"], "NOT_STARTED_RESOURCE_UNAVAILABLE")
        self.assertFalse((self.runs / "case").exists())

    def test_aggregate_output_budget_is_enforced_even_on_zero_exit(self):
        self.data["jobs"][0] = self.job("case", "output_budget")
        self.data["jobs"][0]["output_budget_bytes"] = 128 << 10
        result = self.run_once()
        self.assertEqual(result["jobs"]["case"]["status"], "FAIL")
        rec = json.loads(self.receipts("case")[0].read_bytes())
        self.assertIn("OUTPUT_BUDGET_EXCEEDED", rec["failures"])
        self.assertGreater(resources.allocated_bytes(self.receipts("case")[0].parent), 128 << 10)

    def test_task_disk_cap_and_system_free_space_refuse_admission(self):
        for field, value in (("disk_allocated_bytes", resources.DISK_CAP_BYTES - 512),
                             ("disk_free_bytes", 512)):
            with self.subTest(field=field):
                def insufficient(profile, disk_root, own_group_ids=()):
                    obs = self.observation(profile, disk_root, own_group_ids)
                    obs[field] = value
                    return obs
                result = self.run_once(insufficient)
                self.assertEqual(result["jobs"]["case"]["status"], "NOT_STARTED_RESOURCE_UNAVAILABLE")
                self.assertFalse((self.runs / "case").exists())

    def test_global_disk_cap_breach_marks_active_job_failed(self):
        self.data["jobs"][0] = self.job("case", "sleep")
        def breached(profile, disk_root, own_group_ids=()):
            obs = self.observation(profile, disk_root, own_group_ids)
            if own_group_ids:
                obs["disk_allocated_bytes"] = resources.DISK_CAP_BYTES + 4096
            return obs
        result = self.run_once(breached)
        self.assertEqual(result["jobs"]["case"]["status"], "FAIL")
        rec = json.loads(self.receipts("case")[0].read_bytes())
        self.assertIn("DISK_CAP_EXCEEDED", rec["failures"])
        self.assertEqual(rec["other_owner_processes_signaled"], 0)

    def test_timeout_kills_own_descendants_not_other_job(self):
        self.data["jobs"][0] = self.job("case", "sleep")
        self.data["jobs"][0]["timeout_s"] = 0.25
        other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(8)"], start_new_session=True)
        try:
            result = self.run_once()
            self.assertEqual(result["jobs"]["case"]["status"], "FAIL")
            recpath = self.receipts("case")[0]; rec = json.loads(recpath.read_bytes())
            self.assertIn("TIMEOUT", rec["failures"])
            time.sleep(2.15)
            self.assertFalse((recpath.parent / "late-marker").exists())
            self.assertIsNone(other.poll())
        finally:
            other.terminate(); other.wait(timeout=3)

    def test_production_helper_cleans_nested_session_and_preserves_other_job(self):
        namespace_proof = resources.procfs_identity()
        self.assertEqual(namespace_proof["local_pid"], os.getpid())
        self.assertEqual(namespace_proof["local_pgid"], os.getpgrp())
        self.assertEqual(namespace_proof["pid_namespace"], os.readlink("/proc/self/ns/pid"))
        self.assertEqual(namespace_proof["procfs_self_pid"], int(Path("/proc/self/stat").read_text().split(" ", 1)[0]))
        production = Path(__file__).resolve().parent.parent / "process_control.py"
        shutil.copyfile(production, self.repo / "process_control.py")
        (self.repo / "production_wrapper.py").write_text(PRODUCTION_WRAPPER)
        for name in ("process_control.py", "production_wrapper.py"):
            self.data["source_files"][name] = runner.digest_file(self.repo / name)
        other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(15)"], start_new_session=True)
        nested_groups = []
        try:
            for mode, timeout in (("interrupt", 1.0), ("normal_exit", 5.0)):
                with self.subTest(mode=mode):
                    ident = "case_" + mode
                    job = self.job(ident)
                    job["argv"] = [sys.executable, "{repo}/production_wrapper.py", "{repo}/process_control.py", "{run}/result.json", mode]
                    job["timeout_s"] = timeout
                    self.data["jobs"] = [job]
                    nested_observations = []
                    def observed(profile, disk_root, own_group_ids=()):
                        value = self.observation(profile, disk_root, own_group_ids)
                        nested_observations.extend(value["own_process_groups"].values())
                        return value
                    result = self.run_once(observed)
                    self.assertEqual(result["jobs"][ident]["status"], "FAIL")
                    recpath = self.receipts(ident)[0]
                    outer = json.loads(recpath.read_bytes())
                    nested = json.loads((recpath.parent / "nested-receipt.json").read_bytes())
                    nested_group = nested["owned_process_group"]
                    nested_groups.append(nested_group)
                    (self.root / (mode + "_observed_resources.json")).write_text(json.dumps(nested_observations, indent=2))
                    if mode == "interrupt":
                        self.assertIn("TIMEOUT", outer["failures"])
                        self.assertEqual(nested["status"], "INTERRUPTED")
                        self.assertEqual(nested["signal"], signal.SIGTERM)
                        self.assertTrue(any(nested_group in value["process_ids"]
                            and value["namespace_proof"]["pid_namespace"] == namespace_proof["pid_namespace"]
                            and len(value["procfs_pids"]) == len(value["process_ids"])
                            and value["nested_session_processes"] >= 2
                            and value["live_processes"] >= 3
                            and value["nested_session_rss_bytes"] > 0
                            and value["rss_bytes"] >= value["nested_session_rss_bytes"]
                            for value in nested_observations), "outer owner accounting missed the real nested child tree")
                    else:
                        self.assertNotIn("TIMEOUT", outer["failures"])
                        self.assertEqual(nested["status"], "LEFTOVER_OWNED_CHILDREN")
                        self.assertEqual(nested["parent_returncode"], 0)
                        self.assertEqual(nested["exit_code"], 125)
                    self.assertIn("SIGTERM", nested["cleanup_actions"])
                    self.assertIn("SIGKILL", nested["cleanup_actions"])
                    self.assertTrue((recpath.parent / "nested-ready").is_file())
                    time.sleep(3.1 if mode == "normal_exit" else 2.1)
                    self.assertEqual(resources.process_groups([nested_group])[nested_group]["live_processes"], 0)
                    self.assertFalse((recpath.parent / "nested-late").exists())
                    self.assertIsNone(other.poll())
        finally:
            # Cleanup only this test's separately created sentinel and the exact
            # child group named by this test-owned production receipt.
            for nested_group in nested_groups:
                try: os.killpg(nested_group, signal.SIGKILL)
                except ProcessLookupError: pass
            other.terminate(); other.wait(timeout=3)

    def test_atomic_receipt_cannot_overwrite_history(self):
        p = self.root / "record.json"
        runner.atomic_json(p, {"old": True}); original = p.read_bytes()
        with self.assertRaises(FileExistsError):
            runner.atomic_json(p, {"old": False})
        self.assertEqual(p.read_bytes(), original)

    def test_bundle_rejects_changed_payload_even_with_new_archive_sha(self):
        self.assertEqual(self.run_once()["status"], "PASS")
        archive = self.root / "return.zip"
        receipt = bundle.create(self.manifest_path, self.repo, self.runs, archive, self.root)
        self.assertEqual(bundle.verify(archive, receipt["sha256"], receipt["bytes"])["status"], "PASS_EXACT_ARCHIVE_BYTES_CRC_MANIFEST")
        changed = self.root / "changed.zip"
        with zipfile.ZipFile(archive) as source, zipfile.ZipFile(changed, "x") as target:
            for info in source.infolist():
                value = source.read(info.filename)
                if info.filename.endswith("/result.json"):
                    value = b"x" * len(value)
                target.writestr(info, value)
        with self.assertRaisesRegex(ValueError, "payload SHA256 mismatch"):
            bundle.verify(changed, runner.digest_file(changed), changed.stat().st_size)


if __name__ == "__main__":
    unittest.main(verbosity=2)
