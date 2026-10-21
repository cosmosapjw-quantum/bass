"""Checkpoint/identity I/O tests with an injected toy runner, not science results."""
import copy
from dataclasses import asdict
import json
import multiprocessing
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import batch_worker as worker
import work_plan as wp


def toy_runner(case, context, nsteps):
    split, _ = wp.modules()
    initial = {"a": .1999, "H": 1., "Tgas_K": 12000., "x_HII": .4, "x_HeII": .5,
               "nerr": 0., "eerr": 0., "gamma_number_N0": 1., "nu_number_N0": 1.,
               "Sigma_half": case["Sigma_half_requested"], "Pi_m_half": case["Pi_m_half_requested"],
               "Pi_r_half": case["Pi_r_half_requested"], "signed_Sigma": case["signed_Sigma_requested"],
               "signed_Pi_m": case["signed_Pi_m_requested"], "signed_Pi_r": case["signed_Pi_r_requested"],
               "signed_Pi_total": case["signed_Pi_total_requested"]}
    history = [{**initial, "a": .1999 + .0001 * (i + 1) / nsteps} for i in range(nsteps)]
    history[-1]["a"] = .2
    seed = split.seed_for(case, context)
    parameters = asdict(split.parameters(case[wp.MAGNITUDES[0]], case[wp.SIGNS[0]], seed["alpha_m"], seed["alpha_r"]))
    return {"case": copy.deepcopy(case), "seed": seed, "calibration": context.calibration,
            "initial": initial, "numeric_checks": split.initial_checks(case, initial), "gates": dict.fromkeys(worker.GATES, True),
            "owner_result": {"schema": "rei.c15.active_source_shear_stress_coupling.v1", "config": parameters,
                             "source_identity": split.prior.load_owner().source_identity(),
                             "nsteps": nsteps, "history": history, "final": copy.deepcopy(history[-1]),
                             "errors": dict.fromkeys(("photochemical_number_abs_max", "photochemical_energy_eV_H_abs_max",
                                                      "gamma_number_monopole_abs_max", "nu_number_monopole_abs_max"), 0.)}}


def concurrent_run(input_path, output, counter, start, replies):
    def counted(case, context, nsteps):
        with Path(counter).open("a") as stream:
            stream.write(case["case_id"] + "\n")
        return toy_runner(case, context, nsteps)
    try:
        start.wait(10)
        result = worker.run_group(input_path, output, runner=counted)
        replies.put((result["status"], result["case_cache"][0]["reused"]))
    except Exception as error:
        replies.put(("ERROR", repr(error)))


class BatchWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        registry = wp.load_completed_registry()
        contract = copy.deepcopy(registry["context"]["baseline_contract"])
        contract["grid"].update(Sigma_half=[.00025], Pi_m_half=[1e-5], Pi_r_half=[2e-5])
        cls.cases = wp.modules()[0].signed_grid(contract)[:2]
        observed = {"affinity_cpus": [0, 1], "cpu_quota_cores": 2., "sampled_idle_cores": 2.,
                    "quota_remaining_cores": 2., "sampled_seconds": .1, "mem_available_bytes": 4 * 1024**3,
                    "cgroup_remaining_bytes": 4 * 1024**3}
        cls.plan = wp.build_plan(cases=cls.cases, nsteps=2, snapshot=observed)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = self.root / "store"

    def prepared(self, plan=None, label="first", group_size=2, store=None):
        plan_path = self.root / (label + "-plan.json")
        worker.write_json(plan_path, self.plan if plan is None else plan)
        out = self.root / label
        receipt = worker.prepare(plan_path, out, store or self.store, group_size)
        inputs = sorted((out / "inputs").glob("*.json"))
        return out, inputs, receipt

    def test_no_work_creates_receipt_without_manifest_store_or_resource_call(self):
        plan = wp.build_plan()
        with patch.object(wp.modules()[1], "ResourceObserver", side_effect=AssertionError("resources")):
            out, inputs, receipt = self.prepared(plan)
        self.assertEqual((receipt["completed_count"], receipt["pending_count"], receipt["jobs"], receipt["launched_jobs"]), (729, 0, 0, 0))
        self.assertEqual(inputs, [])
        self.assertTrue((out / "no_work.json").is_file())
        self.assertFalse((out / "manifest.json").exists())
        self.assertFalse(self.store.exists())

    def test_standard_manifest_and_full_completion(self):
        out, inputs, receipt = self.prepared(group_size="auto")
        manifest = json.loads((out / "manifest.json").read_text())
        _, executor = wp.modules()
        executor.validate_manifest(manifest)
        executor.verify_bound_files(manifest, out)
        self.assertEqual(receipt["launched_jobs"], 0)
        self.assertTrue(all(job["outputs"] == ["result.json"] for job in manifest["jobs"]))
        for index, path in enumerate(inputs):
            result = worker.run_group(path, self.root / f"done-{index}.json", runner=toy_runner)
            self.assertEqual(result["status"], "SUCCEEDED")
            self.assertEqual(result["schema"], "rei.sigma_pi_split.group_result.v1")
            self.assertEqual(len(result["cases"]), receipt["group_size"])
            self.assertFalse(any(item["reused"] for item in result["case_cache"]))

    def test_partial_failure_keeps_successful_case_and_resumes(self):
        _, inputs, _ = self.prepared()
        calls = []
        def fail_second(case, context, nsteps):
            calls.append(case["case_id"])
            if len(calls) == 2:
                raise RuntimeError("injected failure")
            return toy_runner(case, context, nsteps)
        failed = self.root / "failed.json"
        with self.assertRaisesRegex(RuntimeError, "injected failure"):
            worker.run_group(inputs[0], failed, runner=fail_second)
        self.assertFalse(failed.exists())
        checkpoint = json.loads((self.root / "failed.checkpoint.json").read_text())
        self.assertEqual(len(checkpoint["cases"]), 1)
        self.assertEqual(len(list(self.store.rglob("receipt.json"))), 1)
        self.assertTrue(list(self.root.glob("failed.failure-*.json")))
        self.assertTrue(list(self.store.rglob("failures/*.json")))
        new_calls = []
        def resumed(case, context, nsteps):
            new_calls.append(case["case_id"])
            return toy_runner(case, context, nsteps)
        result = worker.run_group(inputs[0], self.root / "resumed.json", runner=resumed)
        self.assertEqual(result["status"], "SUCCEEDED")
        self.assertEqual(len(new_calls), 1)
        self.assertEqual([entry["reused"] for entry in result["case_cache"]], [True, False])

    def test_relabel_regroup_and_relocated_store_reuse_original_provenance(self):
        _, inputs, _ = self.prepared()
        first = worker.run_group(inputs[0], self.root / "first-result.json", runner=toy_runner)
        old_receipts = {p.parent.name: p.read_bytes() for p in self.store.rglob("receipt.json")}
        moved = self.root / "another-host-store"
        shutil.copytree(self.store, moved)
        altered = copy.deepcopy(self.plan)
        for item in altered["pending"]:
            item["case"]["case_id"] = "renamed_" + item["case"]["case_id"]
        _, inputs, _ = self.prepared(altered, "relocated", 1, moved)
        for index, path in enumerate(inputs):
            def forbidden(*args):
                raise AssertionError("already stored case reran")
            result = worker.run_group(path, self.root / f"relocated-{index}.json", runner=forbidden)
            self.assertTrue(result["case_cache"][0]["reused"])
            self.assertTrue(result["cases"][0]["case"]["case_id"].startswith("renamed_"))
            self.assertFalse(result["case_cache"][0]["original_case_id"].startswith("renamed_"))
        self.assertEqual(old_receipts, {p.parent.name: p.read_bytes() for p in moved.rglob("receipt.json")})
        self.assertEqual(len(first["cases"]), 2)

    def test_corrupted_store_fails_without_recompute_or_overwrite(self):
        _, inputs, _ = self.prepared()
        worker.run_group(inputs[0], self.root / "before.json", runner=toy_runner)
        data = json.loads(inputs[0].read_text())
        entry = self.store / data["source_id"] / data["pending"][0]["science_id"]
        damaged = (entry / "case.json").read_bytes() + b"\n"
        (entry / "case.json").write_bytes(damaged)
        with self.assertRaisesRegex(ValueError, "CORRUPT_CASE_STORE"):
            worker.run_group(inputs[0], self.root / "after.json", runner=lambda *args: self.fail("corruption reran"))
        self.assertEqual((entry / "case.json").read_bytes(), damaged)
        self.assertFalse((self.root / "after.json").exists())

    def test_mutated_bound_plan_and_backend_identity_fail(self):
        _, inputs, _ = self.prepared()
        plan_path = self.root / "first-plan.json"
        plan_path.write_bytes(plan_path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "BOUND_SOURCE_OR_PLAN_CHANGED"):
            worker.run_group(inputs[0], self.root / "mutated.json", runner=toy_runner)
        _, inputs, _ = self.prepared(label="clean")
        original = worker.backend_binding
        def changed(registry):
            _, bound = original(registry)
            return "0" * 64, bound
        with patch.object(worker, "backend_binding", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "BACKEND_CONTEXT_OR_TOOLCHAIN_CHANGED"):
                worker.run_group(inputs[0], self.root / "source-changed.json", runner=toy_runner)

    def test_forged_payload_and_completed729_requeue_are_rejected(self):
        altered = copy.deepcopy(self.plan)
        altered["pending"][0]["science"]["parameters"]["massive_fraction"] = .2
        altered["pending"][0]["science_id"] = wp.identity(altered["pending"][0]["science"])
        with self.assertRaisesRegex(ValueError, "PENDING_SCIENCE"):
            self.prepared(altered, "forged")
        record = next(iter(wp.load_completed_registry()["records"].values()))
        altered = copy.deepcopy(self.plan)
        altered.update(candidate_count=1, pending_count=1, pending=[{k: record[k] for k in ("case", "seed", "science", "science_id")}])
        with self.assertRaisesRegex(ValueError, "COMPLETED729_MUST_NOT_BE_PENDING"):
            self.prepared(altered, "requeued")

    def test_bad_gates_or_incomplete_history_never_create_completion(self):
        for mode in ("gate", "history", "config", "source", "final", "errors"):
            with self.subTest(mode=mode):
                _, inputs, _ = self.prepared(label=mode, store=self.root / (mode + "-store"))
                def bad(case, context, nsteps):
                    result = toy_runner(case, context, nsteps)
                    if mode == "gate":
                        result["gates"]["number_5e-12"] = False
                    elif mode == "history":
                        result["owner_result"]["history"].pop()
                    elif mode == "config":
                        result["owner_result"]["config"]["massive_fraction"] = .2
                    elif mode == "source":
                        result["owner_result"]["source_identity"] = {"fabricated": "source"}
                    elif mode == "final":
                        result["owner_result"]["final"]["H"] *= 1.1
                    elif mode == "errors":
                        result["owner_result"]["history"][0]["nerr"] = .01
                    return result
                output = self.root / (mode + "-result.json")
                with self.assertRaisesRegex(ValueError, "CASE_RESULT_CONTRACT|CASE_HISTORY_ERROR_REDUCTION"):
                    worker.run_group(inputs[0], output, runner=bad)
                self.assertFalse(output.exists())
                self.assertFalse(list((self.root / (mode + "-store")).rglob("receipt.json")))

    def test_two_processes_share_one_case_lock(self):
        _, inputs, _ = self.prepared(group_size=1)
        processes = multiprocessing.get_context("fork")
        start, replies = processes.Event(), processes.Queue()
        counter = self.root / "runner-calls.txt"
        children = [processes.Process(target=concurrent_run, args=(inputs[0], self.root / f"parallel-{i}.json", counter, start, replies)) for i in range(2)]
        for child in children:
            child.start()
        start.set()
        try:
            responses = [replies.get(timeout=15) for _ in children]
            self.assertEqual(sorted(responses), [("SUCCEEDED", False), ("SUCCEEDED", True)])
        finally:
            for child in children:
                child.join(timeout=15)
                if child.is_alive():
                    child.terminate()
                    child.join()
        self.assertEqual(len(counter.read_text().splitlines()), 1)
        self.assertTrue(all(child.exitcode == 0 for child in children))


if __name__ == "__main__":
    unittest.main()
