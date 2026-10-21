"""Small execution controls only; no science solve or benchmark."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import shared_executor as se


def snapshot(**changes):
    result = {"affinity_cpus": list(range(64)), "cpu_quota_cores": 64.,
              "sampled_idle_cores": 64., "quota_remaining_cores": 64.,
              "sampled_seconds": .5, "mem_available_bytes": 120 * se.GIB,
              "cgroup_remaining_bytes": 120 * se.GIB}
    result.update(changes)
    return result


def manifest_for(source):
    return {"schema": se.SCHEMA,
            "science_binding": {"source": {"sha256": se.file_sha256(source)},
                                "input": {"fixture": "executor_control"},
                                "toolchain": {"python": sys.version}},
            "bound_files": [{"path": str(source), "sha256": se.file_sha256(source)}],
            "jobs": [{"id": "control", "argv": [sys.executable, str(source), "{attempt_dir}/result.json"],
                      "outputs": ["result.json"], "memory_mb": 128, "timeout_s": 5}]}


class ExecutorControls(unittest.TestCase):
    def test_synthetic_disk_admission_cap_and_free_reserve(self):
        cap = 4 * se.GIB
        observation = {"scope_bytes": cap - 1,
                       "filesystem_free_bytes": se.FILESYSTEM_FREE_RESERVE + 1}
        self.assertIsNone(se.disk_admission_reason(observation, cap))
        observation["scope_bytes"] = cap
        self.assertEqual(se.disk_admission_reason(observation, cap),
                         "SCOPE_DISK_ADMISSION_CAP")
        observation["scope_bytes"] = 0
        observation["filesystem_free_bytes"] = se.FILESYSTEM_FREE_RESERVE
        self.assertEqual(se.disk_admission_reason(observation, cap),
                         "FILESYSTEM_FREE_SPACE_RESERVE")

    def test_synthetic_resource_caps_and_existing_load(self):
        full = snapshot()
        self.assertEqual(se.admission_budget(full, [], profile="sandbox", max_workers=64,
                                             reserve_bytes=0), (8, 8 * se.GIB))
        self.assertEqual(se.admission_budget(full, [], profile="ncp", max_workers=64,
                                             reserve_bytes=0), (64, 120 * se.GIB))
        loaded = snapshot(cpu_quota_cores=3.5, sampled_idle_cores=4.,
                          quota_remaining_cores=1.75, cgroup_remaining_bytes=640 * se.MIB)
        self.assertEqual(se.admission_budget(loaded, [], profile="ncp", max_workers=64,
                                             reserve_bytes=256 * se.MIB), (1, 384 * se.MIB))
        occupied = [{"memory_bytes": se.GIB, "rss_bytes": 512 * se.MIB}] * 2
        self.assertEqual(se.admission_budget(full, occupied, profile="sandbox", max_workers=8,
                                             reserve_bytes=0), (6, 6 * se.GIB))

    def test_identity_excludes_admission_but_includes_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.py"
            source.write_text("pass\n")
            manifest = manifest_for(source)
            identity = se.job_identity(manifest, manifest["jobs"][0])
            altered = copy.deepcopy(manifest)
            altered["jobs"][0].update(memory_mb=512, timeout_s=20)
            self.assertEqual(identity, se.job_identity(altered, altered["jobs"][0]))
            altered["science_binding"]["source"]["sha256"] = "a" * 64
            self.assertNotEqual(identity, se.job_identity(altered, altered["jobs"][0]))
            source.write_text("raise RuntimeError('changed source')\n")
            with self.assertRaisesRegex(ValueError, "SOURCE_INPUT_BINDING_MISMATCH"):
                se.verify_bound_files(manifest, directory)

    def test_stale_output_never_reuses_or_changes_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            attempt = Path(directory)
            result = attempt / "result.json"
            result.write_text('{"control":1}\n')
            identity = "a" * 64
            receipt = {"job_identity": identity, "status": "PASS",
                       "outputs": {"result.json": {"bytes": result.stat().st_size,
                                                   "sha256": se.file_sha256(result)}}}
            se.write_json_new(attempt / "receipt.json", receipt)
            before = (attempt / "receipt.json").read_bytes()
            self.assertTrue(se.verify_completed(attempt, identity, ["result.json"])[0])
            result.write_text('{"control":2}\n')  # same size, different bytes
            self.assertEqual(se.verify_completed(attempt, identity, ["result.json"])[1], "STALE_OUTPUT")
            result.unlink()
            self.assertEqual(se.verify_completed(attempt, identity, ["result.json"])[1], "STALE_OUTPUT")
            self.assertEqual(before, (attempt / "receipt.json").read_bytes())

    def test_duplicate_job_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.py"
            source.write_text("pass\n")
            manifest = manifest_for(source)
            manifest["jobs"].append(copy.deepcopy(manifest["jobs"][0]))
            with self.assertRaisesRegex(ValueError, "DUPLICATE_JOB_ID"):
                se.validate_manifest(manifest)

    def test_active_scope_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            with se.execution_lock(directory):
                with self.assertRaisesRegex(RuntimeError, "ACTIVE_RUN_LOCK"):
                    with se.execution_lock(directory):
                        self.fail("second coordinator acquired active scope")
            with se.execution_lock(directory):
                pass

    def test_one_child_control_then_resume_with_new_width(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "control.py"
            source.write_text("from pathlib import Path\nimport sys\n"
                "Path(sys.argv[1]).write_text('{\"control\":true}\\n')\n"
                "with Path(__file__).with_suffix('.starts').open('a') as h: h.write('start\\n')\n")
            manifest_path = root / "manifest.json"
            se.write_json_new(manifest_path, manifest_for(source))
            with mock.patch.object(se.ResourceObserver, "sample", return_value=snapshot()):
                first = se.run(manifest_path, root / "scope", max_workers=1, poll_s=.05)
                second = se.run(manifest_path, root / "scope", max_workers=7, poll_s=.05)
            self.assertEqual(first["status"], "COMPLETE")
            self.assertEqual(first["jobs"][0]["status"], "PASS")
            self.assertEqual(second["jobs"][0]["status"], "SKIPPED_PASS")
            self.assertEqual(source.with_suffix(".starts").read_text(), "start\n")
            self.assertEqual(len(list((root / "scope" / "jobs").rglob("receipt.json"))), 1)


if __name__ == "__main__":
    unittest.main()
