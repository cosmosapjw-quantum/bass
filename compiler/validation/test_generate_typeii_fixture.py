"""Behavioral tests for the self-contained Type-II fixture generator."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class SplitMix64ContractTests(unittest.TestCase):
    def test_splitmix64_matches_frozen_known_answer_vector(self) -> None:
        """Catches changes to wrapping, shifts, constants, or update order."""
        from compiler.validation.generate_typeii_fixture import SplitMix64

        rng = SplitMix64(0x4241_5353_5F48_4F53)
        self.assertEqual(
            [rng.next_u64() for _ in range(4)],
            [
                0x7BA3_CE34_ECDA_7D8B,
                0x1E0A_1447_1CBF_DCEB,
                0x8AC8_BB4A_32E8_F124,
                0xC500_A6AF_09C4_BD49,
            ],
        )


class FixtureGenerationContractTests(unittest.TestCase):
    def test_two_runs_are_identical_and_reconstruct_source_model(self) -> None:
        """Catches hidden randomness, timestamps, and non-source trajectory data."""
        from compiler.validation.generate_typeii_fixture import generate_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = generate_artifacts(REPO_ROOT, root / "a")
            second = generate_artifacts(REPO_ROOT, root / "b")

            self.assertEqual(set(first), set(second))
            for relative in first:
                self.assertEqual(first[relative], second[relative], relative)

            fixture = json.loads(
                first[Path("compiler/validation/typeii_fixture_canonical.json")]
            )
            samples = fixture["trajectory"]["samples"]
            self.assertEqual(len(samples), 401)
            self.assertEqual(samples[0]["state"], [0.2375, 0.0, -0.11295198246134101, 0.865, 0.05])
            self.assertEqual(
                samples[1]["state"],
                [
                    0.237483198522475,
                    1.2265009701608058e-05,
                    -0.11293368496280672,
                    0.8650058629844937,
                    0.049991577928173256,
                ],
            )
            self.assertAlmostEqual(samples[200]["state"][1], 0.0022546245729999554, delta=2e-18)
            self.assertAlmostEqual(samples[400]["state"][1], 0.004138743982585919, delta=2e-18)
            self.assertEqual(
                [samples[i]["opacity"] for i in (0, 200, 400)],
                [240.13336620482818, 100.08485094440381, 13.322173705416928],
            )
            self.assertEqual(
                fixture["rng_probe"]["u64_hex"][:4],
                [
                    "0x7ba3ce34ecda7d8b",
                    "0x1e0a14471cbfdceb",
                    "0x8ac8bb4a32e8f124",
                    "0xc500a6af09c4bd49",
                ],
            )

            receipt = json.loads(
                first[Path("compiler/validation/typeii_fixture_receipt.json")]
            )
            self.assertFalse(receipt["environment"]["third_party_numeric_used"])
            self.assertEqual(
                receipt["environment"]["scope"],
                "fixture generator execution only",
            )
            self.assertTrue(receipt["environment"]["libc"]["name"])
            self.assertTrue(receipt["environment"]["libc"]["version"])
            self.assertTrue(receipt["environment"]["python_compiler"])
            self.assertIn(
                "not claimed",
                receipt["environment"]["cross_platform_bitwise_identity"],
            )
            self.assertEqual(
                receipt["authority"]["formula_authority_label_sha256"],
                "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361",
            )
            self.assertEqual(
                receipt["authority"]["generated_typeii_background_actual_sha256"],
                "0f1f31dad4c106fa22ac1ea8e95651ede24a32d24400629e10f8271d99490d15",
            )
            self.assertNotEqual(
                receipt["authority"]["formula_authority_label_sha256"],
                receipt["authority"]["generated_typeii_background_actual_sha256"],
            )
            self.assertIn(
                "does not rerun SymPy/rustfmt lowering",
                receipt["authority"]["generated_typeii_background_hash_evidence"],
            )
            expected_executable_sources = {
                    "compiler/tests/test_rust_typeii_lowering.py",
                    "compiler/tests/test_rust_typeii_polarized_lowering.py",
                    "compiler/validation/test_generate_typeii_fixture.py",
                    "compiler/validation/test_typeii_conservation_quad.py",
                    "compiler/validation/test_typeii_polarized_runtime.py",
                    "runtime/rust/typeii/tests/typeii_fixture_reconstruction.rs",
                    "runtime/rust/typeii/tests/typeii_krylov_adapt_hostile.rs",
                    "runtime/rust/typeii/tests/typeii_krylov_adapt_unit.rs",
                    "runtime/rust/typeii/tests/typeii_polarized_runtime_unit.rs",
                    "runtime/rust/typeii/tests/typeii_runtime_unit.rs",
            }
            pre_test = "runtime/rust/typeii/tests/typeii_pre_liouville_safety.rs"
            if (REPO_ROOT / pre_test).is_file():
                expected_executable_sources.add(pre_test)
            self.assertEqual(
                set(receipt["executable_test_sources"]),
                expected_executable_sources,
            )
            self.assertEqual(
                receipt["authority"]["generated_typeii_background_actual_sha256"],
                receipt["input_hashes"]["generated/rust/typeii/typeii_background.rs"],
            )
            ap_status = receipt["source_dependency_status"][
                "pre_liouville_ap_implementation"
            ]
            ap_paths = {
                "runtime/rust/typeii/typeii_collision_ap.rs",
                "runtime/rust/typeii/typeii_physical_guard.rs",
                "runtime/rust/typeii/typeii_polarized_runtime_physical.rs",
                "runtime/rust/typeii/tests/typeii_pre_liouville_safety.rs",
            }
            present = {path for path in ap_paths if (REPO_ROOT / path).is_file()}
            if present:
                self.assertEqual(present, ap_paths)
                self.assertEqual(ap_status["status"], "integrated_and_hashed")
                self.assertTrue(ap_paths.issubset(receipt["input_hashes"]))
                self.assertTrue(ap_status["fixture_source_binding_complete"])
                self.assertTrue(ap_status["final_approval_allowed"])
                self.assertTrue(
                    ap_status["fixture_source_binding_allows_final_approval"]
                )
                self.assertIn("does not certify", ap_status["final_approval_allowed_meaning"])
            else:
                self.assertEqual(ap_status["status"], "not_integrated")
                self.assertEqual(set(ap_status["missing_paths"]), ap_paths)
                self.assertFalse(ap_status["fixture_source_binding_complete"])
                self.assertFalse(ap_status["final_approval_allowed"])
                self.assertFalse(
                    ap_status["fixture_source_binding_allows_final_approval"]
                )
                self.assertIn("never certifies", ap_status["final_approval_allowed_meaning"])
            self.assertTrue(ap_status["final_approval_requires_independent_audits"])

    def test_provenance_preserves_known_historical_discrepancies(self) -> None:
        """Catches silent normalization or relabeling of compatibility bytes."""
        from compiler.validation.generate_typeii_fixture import generate_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            generated = generate_artifacts(REPO_ROOT, Path(tmp))
            provenance = json.loads(
                generated[Path("runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json")]
            )
        schedule = provenance["historical_preserved"]["rust_v_schedule"]
        self.assertEqual(
            schedule["compatibility_discrepancies"],
            [
                {
                    "absolute_difference": 9.000439282758066e-14,
                    "index": 63,
                    "json_value": 0.04836688450001,
                    "rust_array": "V2",
                    "rust_value": 0.0483668845001,
                },
                {
                    "absolute_difference": 3.084338340286763e-15,
                    "index": 98,
                    "json_value": -0.016058987543451454,
                    "rust_array": "V2DOT",
                    "rust_value": -0.01605898754345454,
                },
            ],
        )
        public = provenance["historical_preserved"]["public_kato_one_step_sigma_m"]
        self.assertEqual(
            [item["absolute_difference_from_source_rk4"] for item in public],
            [1.3605942747788556e-14, 8.957157593219266e-14],
        )
        self.assertTrue(all("not exact source anchor" in item["role"] for item in public))

    def test_provenance_preserves_complete_legacy_receipt_without_reverification_claim(self) -> None:
        """Catches loss or inflation of the pre-generator provenance receipt."""
        from compiler.validation.generate_typeii_fixture import generate_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            generated = generate_artifacts(REPO_ROOT, Path(tmp))
            provenance = json.loads(
                generated[Path("runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json")]
            )

        legacy = provenance["historical_preserved"]["legacy_fixture_provenance_v1"]
        self.assertEqual(
            legacy["receipt"],
            {
                "stage": "G-RUNTIME-KATO-II",
                "fixture": "source-derived tilted Type-II 5-state trajectory + actual prior SahaHistory/RateSchedule opacity, 401 samples on tau=[0,0.2] with dt=0.0005",
                "fixture_sha256": "5737dead724b86ead64cc25f9e00802973df1eb2abbdc92a5e7c095df1378ef1",
                "full_runtime_test_sha256": "599aa392adffd59d85e54136296a596ff8ea0324df4c1efeccca751f7a98abf1",
                "research_bundle": "BASS_GRUNTIME_KATO_II_20260818.zip",
                "research_bundle_sha256": "0b0cf2637a65c96c3024820ffb2a3feecfa43d94b659a4649b9cbf141c22364f",
                "gold_cases": {
                    "alpha_1": {
                        "errors": [
                            0.002354394711231387,
                            0.0005903517637918307,
                            0.0001485149908708786,
                        ],
                        "orders": [1.995709454, 1.990966285],
                    },
                    "alpha_1e3": {
                        "errors": [
                            0.0014570001950704812,
                            0.0003553667196898122,
                            0.00008949139541933213,
                        ],
                        "orders": [2.035620587, 1.989487699],
                    },
                    "alpha_1e5": {
                        "errors": [
                            0.0014404979386051036,
                            0.0003467025177451369,
                            0.0000850760320976562,
                        ],
                        "orders": [2.054797377, 2.02687366],
                    },
                },
                "note": "The 80 kB generated Rust fixture is kept in the deterministic research bundle rather than duplicated in Git history. The public PR keeps the fixture hash, gold/order receipt, runtime source, and unit/fail-closed tests.",
            },
        )
        self.assertFalse(legacy["verification"]["referenced_bytes_available"])
        self.assertFalse(legacy["verification"]["hashes_freshly_verified"])
        self.assertIn("historical", legacy["verification"]["status"])


class FixtureMutationDetectionTests(unittest.TestCase):
    PRE_LIOUVILLE_PATHS = (
        "runtime/rust/typeii/typeii_collision_ap.rs",
        "runtime/rust/typeii/typeii_physical_guard.rs",
        "runtime/rust/typeii/typeii_polarized_runtime_physical.rs",
        "runtime/rust/typeii/tests/typeii_pre_liouville_safety.rs",
    )

    def _copy_repo(self, destination: Path) -> Path:
        root = destination / "repo"
        shutil.copytree(REPO_ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return root

    def _ensure_synthetic_pre_liouville_bundle(self, root: Path) -> None:
        present = [
            (root / relative).is_file() for relative in self.PRE_LIOUVILLE_PATHS
        ]
        self.assertTrue(all(present) or not any(present))
        if all(present):
            return
        for relative in self.PRE_LIOUVILLE_PATHS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                f"// deterministic synthetic dependency for {relative}\n",
                encoding="utf-8",
            )

    def test_seed_mutation_is_rejected(self) -> None:
        """Catches an unreviewed deterministic-seed change."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            authority_path = root / "compiler/validation/typeii_fixture_authority.json"
            authority = json.loads(authority_path.read_text(encoding="utf-8"))
            authority["rng"]["seed_hex"] = "0x424153535f484f52"
            authority_path.write_text(json.dumps(authority), encoding="utf-8")
            with self.assertRaisesRegex(FixtureContractError, "seed mismatch"):
                generate_artifacts(root, Path(tmp) / "out")

    def test_formula_authority_hash_mutation_is_rejected(self) -> None:
        """Catches substitution of the formula authority label."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            authority_path = root / "compiler/validation/typeii_fixture_authority.json"
            authority = json.loads(authority_path.read_text(encoding="utf-8"))
            authority["formula_authority_label_sha256"] = "0" * 64
            authority_path.write_text(json.dumps(authority), encoding="utf-8")
            with self.assertRaisesRegex(FixtureContractError, "authority label hash mismatch"):
                generate_artifacts(root, Path(tmp) / "out")

    def test_receipt_output_hash_mutation_is_detected(self) -> None:
        """Catches a receipt that no longer authenticates its canonical output."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
            verify_generated_outputs,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            generate_artifacts(root, root)
            receipt_path = root / "compiler/validation/typeii_fixture_receipt.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["canonical_outputs"][
                "compiler/validation/typeii_fixture_canonical.json"
            ] = "0" * 64
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(FixtureContractError, "output hash mismatch"):
                verify_generated_outputs(root)

    def test_non_hash_receipt_mutation_is_detected_by_provenance_link(self) -> None:
        """Catches receipt edits outside the canonical-output hash fields."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
            verify_generated_outputs,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            generate_artifacts(root, root)
            receipt_path = root / "compiler/validation/typeii_fixture_receipt.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["environment"]["machine"] = "mutated-machine"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(FixtureContractError, "receipt hash mismatch"):
                verify_generated_outputs(root)

    def test_one_byte_fixture_mutation_is_detected_and_check_is_nonmutating(self) -> None:
        """Catches fixture corruption and accidental writes from check mode."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            check_generated_outputs,
            generate_artifacts,
            verify_generated_outputs,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            generate_artifacts(root, root)
            tracked = [
                root / "compiler/validation/typeii_fixture_canonical.json",
                root / "compiler/validation/typeii_fixture_receipt.json",
                root / "runtime/rust/typeii/tests/support/typeii_fixture_generated.rs",
                root / "runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json",
            ]
            before = {path: path.read_bytes() for path in tracked}
            check_generated_outputs(root)
            self.assertEqual(before, {path: path.read_bytes() for path in tracked})

            fixture_path = tracked[0]
            mutated = bytearray(fixture_path.read_bytes())
            mutated[len(mutated) // 2] ^= 1
            fixture_path.write_bytes(mutated)
            with self.assertRaisesRegex(FixtureContractError, "output hash mismatch"):
                verify_generated_outputs(root)

    def test_authority_input_file_mutation_is_detected(self) -> None:
        """Catches drift in a hashed schedule input after receipt generation."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
            verify_generated_outputs,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            generate_artifacts(root, root)
            schedule_path = root / "compiler/validation/typeII_v_schedule.json"
            schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
            schedule["v2"][10] += 1e-12
            schedule_path.write_text(json.dumps(schedule), encoding="utf-8")
            with self.assertRaisesRegex(FixtureContractError, "input hash mismatch"):
                verify_generated_outputs(root)

    def test_hostile_test_source_mutation_is_detected(self) -> None:
        """Catches counted hostile/nonnormal/oscillatory source drift."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
            verify_generated_outputs,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            generate_artifacts(root, root)
            hostile_path = root / "runtime/rust/typeii/tests/typeii_krylov_adapt_hostile.rs"
            hostile_path.write_bytes(hostile_path.read_bytes() + b"\n// mutation\n")
            with self.assertRaisesRegex(FixtureContractError, "input hash mismatch"):
                verify_generated_outputs(root)

    def test_generated_background_actual_hash_is_measured_and_mutation_is_detected(self) -> None:
        """Catches relabeling a declaration as the measured generated-file hash."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
            verify_generated_outputs,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            generate_artifacts(root, root)
            background_path = root / "generated/rust/typeii/typeii_background.rs"
            background_path.write_bytes(background_path.read_bytes() + b"\n// mutation\n")
            with self.assertRaisesRegex(
                FixtureContractError, "generated background actual hash mismatch"
            ):
                verify_generated_outputs(root)

    def test_ap_implementation_source_mutation_is_detected(self) -> None:
        """Catches drift in the canonical AP/physical implementation bytes."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
            verify_generated_outputs,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            self._ensure_synthetic_pre_liouville_bundle(root)
            generate_artifacts(root, root)
            ap_path = root / "runtime/rust/typeii/typeii_collision_ap.rs"
            ap_path.write_bytes(ap_path.read_bytes() + b"\n// mutation\n")
            with self.assertRaisesRegex(FixtureContractError, "input hash mismatch"):
                verify_generated_outputs(root)

    def test_partial_ap_implementation_source_set_fails_closed(self) -> None:
        """Catches receipts generated from a partially copied AP source set."""
        from compiler.validation.generate_typeii_fixture import (
            FixtureContractError,
            generate_artifacts,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            self._ensure_synthetic_pre_liouville_bundle(root)
            (root / "runtime/rust/typeii/typeii_physical_guard.rs").unlink()
            with self.assertRaisesRegex(
                FixtureContractError, "partial AP implementation source integration"
            ):
                generate_artifacts(root, Path(tmp) / "out")

    def test_all_absent_pre_liouville_bundle_generates_honest_pr9_receipt(self) -> None:
        """Catches an accidental future-PRE dependency in the amended PR9 tree."""
        from compiler.validation.generate_typeii_fixture import (
            check_generated_outputs,
            generate_artifacts,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = self._copy_repo(Path(tmp))
            for relative in self.PRE_LIOUVILLE_PATHS:
                path = root / relative
                if path.is_file():
                    path.unlink()

            generated = generate_artifacts(root, root)
            receipt = json.loads(
                generated[Path("compiler/validation/typeii_fixture_receipt.json")]
            )
            status = receipt["source_dependency_status"][
                "pre_liouville_ap_implementation"
            ]
            self.assertEqual(status["status"], "not_integrated")
            self.assertFalse(status["fixture_source_binding_complete"])
            self.assertFalse(status["final_approval_allowed"])
            self.assertFalse(status["fixture_source_binding_allows_final_approval"])
            self.assertEqual(
                set(status["missing_paths"]), set(self.PRE_LIOUVILLE_PATHS)
            )
            self.assertNotIn(
                "runtime/rust/typeii/tests/typeii_pre_liouville_safety.rs",
                receipt["executable_test_sources"],
            )
            self.assertEqual(len(receipt["executable_test_sources"]), 10)
            check_generated_outputs(root)


if __name__ == "__main__":
    unittest.main()
