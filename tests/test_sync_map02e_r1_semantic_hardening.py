from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
PARENT = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02E"
    / "BASS_SHARED_FRAME_PHOTON_EXPORT.json"
)
GENERATOR = ROOT / "scripts" / "build_sync_map02e_r1_hardening.py"
VERIFIER = ROOT / "scripts" / "verify_sync_map02e_r1_hardening.py"
WOLFRAM_MODULE = (
    ROOT
    / "wolfram"
    / "BASS"
    / "Kernel"
    / "IR"
    / "SharedFramePhotonExportHardeningR1.wl"
)
WOLFRAM_FIX = (
    ROOT
    / "wolfram"
    / "BASS"
    / "Kernel"
    / "IR"
    / "SharedFramePhotonExportHardeningR1Fix1.wl"
)
WOLFRAM_TEST = (
    ROOT
    / "wolfram"
    / "BASS"
    / "Tests"
    / "SYNCMAP02ER1SharedFramePhotonHardening.wlt"
)
LOCAL_RUNNER = (
    ROOT
    / "wolfram"
    / "scripts"
    / "run_sync_map02e_r1_local_replay.wls"
)
SHELL_RUNNER = ROOT / "scripts" / "run_sync_map02e_r1_local_validation.sh"
PATCH_CONTRACT = (
    ROOT
    / "docs"
    / "bass_master_ssot_v2"
    / "SYNC_MAP_02E_R1"
    / "SEMANTIC_HARDENING_PATCH_CONTRACT.json"
)

FORMULA_IDS = {
    "BASS.FRAME.ABERRATED_DIRECTION.001",
    "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "BASS.FRAME.DOPPLER_FACTOR.001",
    "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "BASS.PHOTON.DIRECTION_FLOW.001",
    "BASS.PHOTON.ENERGY_DRIFT.001",
}


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_verifier_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "bass_sync_map02e_r1_verifier",
        VERIFIER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier module: {VERIFIER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _generate(tmp_path: Path) -> tuple[Path, Path, dict]:
    output = tmp_path / "BASS_SHARED_FRAME_PHOTON_EXPORT_R1.json"
    receipt = tmp_path / "SYNC_MAP_02E_R1_LOCAL_BUILD_RECEIPT.json"
    subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--input",
            str(PARENT),
            "--output",
            str(output),
            "--receipt",
            str(receipt),
        ],
        cwd=ROOT,
        check=True,
    )
    return output, receipt, json.loads(output.read_text(encoding="utf-8"))


def _build(tmp_path: Path) -> dict:
    output, receipt, data = _generate(tmp_path)
    subprocess.run(
        [
            sys.executable,
            str(VERIFIER),
            "--input",
            str(output),
            "--receipt",
            str(receipt),
        ],
        cwd=ROOT,
        check=True,
    )
    return data


class SyncMap02ER1SemanticHardeningTests(unittest.TestCase):
    def build(self) -> dict:
        with tempfile.TemporaryDirectory(prefix="bass-sync-map02e-r1-") as raw:
            return _build(Path(raw))

    def generate(self) -> dict:
        with tempfile.TemporaryDirectory(prefix="bass-sync-map02e-r1-generate-") as raw:
            _, _, data = _generate(Path(raw))
            return data

    def test_required_surfaces_exist(self) -> None:
        for path in (
            GENERATOR,
            VERIFIER,
            WOLFRAM_MODULE,
            WOLFRAM_FIX,
            WOLFRAM_TEST,
            LOCAL_RUNNER,
            SHELL_RUNNER,
            PATCH_CONTRACT,
        ):
            self.assertTrue(path.is_file(), path)

    def test_hardened_registry_structure(self) -> None:
        data = self.build()
        self.assertEqual(data["repository_scope"], "BASS_ONLY")
        self.assertEqual(data["owner"], "bass")
        self.assertEqual(data["formula_count"], 6)
        self.assertEqual(
            {row["formula_id"] for row in data["formulas"]}, FORMULA_IDS
        )
        self.assertNotIn("consumer_bindings", data)
        self.assertEqual(set(data["declared_consumer_targets"]), FORMULA_IDS)

    def test_regular_aberration_and_weighted_pullback(self) -> None:
        data = self.generate()
        by_id = {row["formula_id"]: row for row in data["formulas"]}

        aberration = by_id["BASS.FRAME.ABERRATED_DIRECTION.001"]
        aberration_ir = aberration["equation_ir"]
        executable_text = json.dumps(
            {
                "target": aberration_ir["target"],
                "terms": aberration_ir["terms"],
            },
            sort_keys=True,
        )
        history_text = json.dumps(
            {"known_limits": aberration_ir["known_limits"]},
            sort_keys=True,
        )
        self.assertIn("gamma^2/(gamma+1)", executable_text)
        self.assertNotIn("(gamma-1)/beta_squared", executable_text)
        self.assertIn("(gamma-1)/beta_squared", history_text)
        self.assertIn("gamma^2/(gamma+1)", history_text)
        self.assertEqual(
            aberration_ir["domain"]["zero_boost"],
            "direct evaluation without 0/0",
        )

        verifier = _load_verifier_module()
        verifier.check_aberration(aberration)

        singular_mutant = copy.deepcopy(aberration)
        singular_mutant["equation_ir"]["terms"][0]["input"] = (
            "[n_sky^a+(gamma+((gamma-1)/beta_squared)*beta_dot_n_sky)*"
            "beta^a]/doppler_factor_source(n_sky)"
        )
        with self.assertRaisesRegex(ValueError, "singular coefficient"):
            verifier.check_aberration(singular_mutant)

        blackbody = by_id["BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001"]
        self.assertEqual(
            blackbody["dependencies"],
            [
                "BASS.FRAME.ABERRATED_DIRECTION.001",
                "BASS.FRAME.DOPPLER_FACTOR.001",
            ],
        )
        roles = {
            row["formula_id"]: row["role"]
            for row in blackbody["dependency_roles"]
        }
        self.assertEqual(
            roles,
            {
                "BASS.FRAME.ABERRATED_DIRECTION.001": "BASE_MAP_REQUIRED",
                "BASS.FRAME.DOPPLER_FACTOR.001": "FIBER_WEIGHT_REQUIRED",
            },
        )
        operator_ir = blackbody["equation_ir"]["operator_ir"]
        self.assertEqual(
            operator_ir["base_map"]["target_evaluation_uses"], "INVERSE_MAP"
        )
        self.assertEqual(operator_ir["fiber_weight"]["exponent"], 1)
        self.assertEqual(
            operator_ir["defining_equation"],
            {
                "lhs": "Pullback[A_beta,temperature_tilde]",
                "rhs": "doppler_factor_source*temperature_source",
            },
        )

    def test_photon_parameter_and_geodesic_normal_specialization(self) -> None:
        data = self.build()
        by_id = {row["formula_id"]: row for row in data["formulas"]}
        for formula_id in (
            "BASS.PHOTON.DIRECTION_FLOW.001",
            "BASS.PHOTON.ENERGY_DRIFT.001",
        ):
            row = by_id[formula_id]
            target = row["equation_ir"]["target"]
            self.assertIn("/ds", target)
            self.assertNotIn("/d ell", target)
            assumptions = "\n".join(row["equation_ir"]["assumptions"])
            self.assertIn("ray_parameter s = c*t", assumptions)
            self.assertIn(
                "normal_congruence_acceleration A_normal^a = 0", assumptions
            )
            self.assertEqual(
                row["structural_specializations"],
                [
                    {
                        "formula_id": "BASS.GEO.NORMAL_ACCELERATION.001",
                        "role": "SPECIALIZES_UNDER_ZERO",
                        "value": "A_normal^a=0",
                    }
                ],
            )

        direction = by_id["BASS.PHOTON.DIRECTION_FLOW.001"]
        self.assertEqual(
            direction["equation_ir"]["screen_basis_transport_status"],
            "EXCLUDED_NEXT_BASS_NODE",
        )

    def test_semantic_hashes_are_reproducible(self) -> None:
        data = self.build()
        for row in data["formulas"]:
            self.assertEqual(
                row["semantic_hash"], _sha256(row["semantic_projection"])
            )
        self.assertEqual(
            data["registry_semantic_hash"],
            _sha256(data["registry_semantic_projection"]),
        )

    def test_no_cross_repository_source_mutation_is_declared(self) -> None:
        data = self.build()
        self.assertEqual(data["repository_scope"], "BASS_ONLY")
        excluded = set(data["coverage"]["excluded"])
        self.assertIn("REC, REI, or HTT source modification", excluded)
        self.assertEqual(
            data["claim_boundary"],
            [
                "BASS_OWNER_FORMULA_HARDENING_ONLY",
                "NO_CROSS_REPOSITORY_SOURCE_MUTATION",
                "NO_CONSUMER_PARITY",
                "NO_BACKGROUND_PROVIDER",
                "NO_GLOBAL_TILT",
                "NO_SCREEN_TRANSPORT",
                "NO_NUMERICAL_OR_SCIENCE_PROMOTION",
            ],
        )


if __name__ == "__main__":
    unittest.main()
