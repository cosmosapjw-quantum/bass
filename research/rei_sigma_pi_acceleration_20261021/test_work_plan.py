"""Small correctness checks; no ODE integrations or performance benchmarks."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import work_plan as plan


def snapshot(cpus=64, idle=64, memory_gib=128):
    return {"affinity_cpus": list(range(cpus)), "cpu_quota_cores": cpus,
            "sampled_idle_cores": idle, "quota_remaining_cores": idle,
            "sampled_seconds": .1, "mem_available_bytes": memory_gib * 1024**3,
            "cgroup_remaining_bytes": memory_gib * 1024**3}


class WorkPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = plan.load_completed_registry()
        cls.cases = [record["case"] for record in cls.registry["records"].values()]
        cls.split, cls.executor = plan.modules()

    def copied_baseline(self, root):
        target = Path(root) / "another-host-renamed-directory"
        shutil.copytree(plan.BASELINE / "vendor", target / "vendor")
        for relative in plan.PINS:
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(plan.BASELINE / relative, destination)
        return target

    def test_completed729_never_observes_resources_or_prepares_new_models(self):
        with patch.object(self.executor, "ResourceObserver", side_effect=AssertionError("resource call")), \
             patch.object(self.split, "PreparedContext", side_effect=AssertionError("new context")):
            result = plan.build_plan()
        self.assertEqual((result["completed_count"], result["pending_count"], result["job_count"], result["launched_jobs"]), (729, 0, 0, 0))
        self.assertIsNone(result["resource_budget"])
        self.assertEqual(result["batches"], [])
        self.assertTrue(all(c["evidence"]["kind"] == "external_pinned_completion" for c in result["completed"]))
        self.assertNotIn("raw_history", json.dumps(result))

    def test_regroup_backend_profile_and_case_label_preserve_science(self):
        cases = copy.deepcopy(self.cases[:4])
        a = plan.build_plan(cases=cases, group_size=1, profile="sandbox", backend="owner")
        for case in cases:
            case["case_id"] = "renamed_" + case["case_id"]
        b = plan.build_plan(cases=list(reversed(cases)), group_size=8, profile="ncp", backend="exact-cache")
        self.assertEqual({c["science_id"] for c in a["completed"]}, {c["science_id"] for c in b["completed"]})
        self.assertNotEqual(a["execution_id"], b["execution_id"])

    def test_relocation_keeps_scientific_identity_and_external_urls(self):
        with tempfile.TemporaryDirectory() as root:
            restored = plan.load_completed_registry(self.copied_baseline(root))
        self.assertEqual(self.registry["context_id"], restored["context_id"])
        self.assertEqual(self.registry["records"], restored["records"])
        self.assertEqual(self.registry["evidence_sources"], restored["evidence_sources"])
        self.assertTrue(all(not Path(item["path"]).is_absolute() for item in restored["context"]["source_binding"]["files"]))

    def test_step_change_invalidates_completed_and_uses_actual_seed(self):
        result = plan.build_plan(cases=self.cases[:1], nsteps=128, snapshot=snapshot())
        self.assertEqual((result["completed_count"], result["pending_count"], result["job_count"]), (0, 1, 1))
        pending = result["pending"][0]
        archived = self.registry["records"][plan.coordinate_key(self.cases[0])]
        self.assertNotEqual(pending["science_id"], archived["science_id"])
        self.assertEqual(pending["science"]["nsteps"], 128)
        self.assertEqual(pending["science"]["parameters"]["massive_quadrupole"], pending["seed"]["alpha_m"])
        self.assertEqual(pending["science"]["parameters"]["gamma_quadrupole"], pending["seed"]["alpha_r"])

    def test_physics_and_toolchain_participate_in_identity(self):
        record = self.registry["records"][plan.coordinate_key(self.cases[0])]
        context = copy.deepcopy(self.registry["context"])
        context["baseline_contract"]["physics"]["massive_fraction"] = .2
        altered = copy.deepcopy(record["science"])
        altered["context_id"] = plan.identity(context)
        self.assertNotEqual(plan.identity(altered), record["science_id"])
        altered = copy.deepcopy(record["science"])
        altered["toolchain"]["numpy"] = "another-version"
        self.assertNotEqual(plan.identity(altered), record["science_id"])
        unsupported = {**self.cases[0], "massive_fraction": .2}
        with self.assertRaisesRegex(ValueError, "EXACT_CASE_SCHEMA"):
            plan.build_plan(cases=[unsupported])

    def test_duplicate_missing_and_inconsistent_cases_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            plan.validate_cases([self.cases[0], {**self.cases[0], "case_id": "alias"}])
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            plan.validate_cases([self.cases[0], {**self.cases[1], "case_id": self.cases[0]["case_id"]}])
        with self.assertRaisesRegex(ValueError, "MISMATCHING_SIGNED"):
            plan.normalize_case({**self.cases[0], "signed_Pi_m_requested": 1.})
        with self.assertRaisesRegex(ValueError, "EXACT_CASE_SCHEMA"):
            plan.normalize_case({k: v for k, v in self.cases[0].items() if k != "Pi_r_half_requested"})
        with tempfile.TemporaryDirectory() as root:
            target = self.copied_baseline(root)
            (target / plan.CASES).unlink()
            with self.assertRaises(FileNotFoundError):
                plan.load_completed_registry(target)

    def test_mutated_completion_and_source_are_rejected(self):
        for relative in (plan.CASES, plan.SUMMARY, plan.REVIEW, "vendor/rei_c15/research/rei_c15_sigma_pi_feedback_20261015/coupled.py"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as root:
                target = self.copied_baseline(root)
                path = target / relative
                path.write_bytes(path.read_bytes() + b"\n")
                with self.assertRaisesRegex(ValueError, "PIN_MISMATCH|SOURCE_BINDING_MISMATCH"):
                    plan.load_completed_registry(target)

    def test_custom_cases_file_validates_seed_without_integrating(self):
        contract = copy.deepcopy(self.registry["context"]["baseline_contract"])
        contract["grid"].update(Sigma_half=[.00025], Pi_m_half=[1e-5], Pi_r_half=[2e-5])
        case = self.split.signed_grid(contract)[0]
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "cases.json"
            path.write_text(json.dumps([case]))
            result = plan.build_plan(cases=path, snapshot=snapshot())
        self.assertEqual((result["completed_count"], result["pending_count"], result["launched_jobs"]), (0, 1, 0))
        seed = result["pending"][0]["seed"]
        self.assertTrue(-1 <= seed["alpha_m"] <= 2 and -1 <= seed["alpha_r"] <= 2)
        contract["grid"]["Pi_m_half"] = [1e6]
        with self.assertRaisesRegex(ValueError, "outside positive"):
            plan.build_plan(cases=[self.split.signed_grid(contract)[0]], snapshot=snapshot())

    def test_pending_batches_obey_caps_and_spare_capacity(self):
        for profile, cap in (("ncp", 64), ("sandbox", 8)):
            with self.subTest(profile=profile):
                result = plan.build_plan(cases=self.cases[:70], nsteps=128, group_size=1, profile=profile, snapshot=snapshot())
                self.assertEqual(result["resource_budget"]["width"], cap)
                self.assertEqual(result["job_count"], 70)
                self.assertTrue(all(len(batch) <= cap for batch in result["batches"]))
                self.assertEqual(result["execution"]["numeric_threads"], 1)
        busy = plan.build_plan(cases=self.cases[:10], nsteps=128, group_size=1, snapshot=snapshot(idle=3.7))
        self.assertEqual(busy["resource_budget"]["width"], 3)
        blocked = plan.build_plan(cases=self.cases[:1], nsteps=128, snapshot=snapshot(memory_gib=1))
        self.assertEqual((blocked["pending_count"], blocked["job_count"]), (1, 0))

    def test_empty_candidates_need_no_resources(self):
        with patch.object(self.executor, "ResourceObserver", side_effect=AssertionError("resource call")):
            result = plan.build_plan(cases=[])
        self.assertEqual((result["pending_count"], result["job_count"], result["launched_jobs"]), (0, 0, 0))

    def test_returned_plan_does_not_alias_executor_thread_policy(self):
        expected = dict(self.executor.THREAD_ENV)
        first = plan.build_plan(cases=[])
        first['execution']['thread_env']['OMP_NUM_THREADS'] = '64'
        second = plan.build_plan(cases=[])
        self.assertEqual(self.executor.THREAD_ENV, expected)
        self.assertEqual(second['execution']['thread_env'], expected)
        self.assertEqual(second['execution']['numeric_threads'], 1)


if __name__ == "__main__":
    unittest.main()
