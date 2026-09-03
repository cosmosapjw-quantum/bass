from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

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


def _build(tmp_path: Path) -> dict:
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
    return json.loads(output.read_text(encoding="utf-8"))


def test_required_surfaces_exist() -> None:
    for path in (
        GENERATOR,
        VERIFIER,
        WOLFRAM_MODULE,
        WOLFRAM_TEST,
        LOCAL_RUNNER,
        PATCH_CONTRACT,
    ):
        assert path.is_file(), path


def test_hardened_registry_structure(tmp_path: Path) -> None:
    data = _build(tmp_path)
    assert data["repository_scope"] == "BASS_ONLY"
    assert data["owner"] == "bass"
    assert data["formula_count"] == 6
    assert {row["formula_id"] for row in data["formulas"]} == FORMULA_IDS
    assert "consumer_bindings" not in data
    assert set(data["declared_consumer_targets"]) == FORMULA_IDS


def test_regular_aberration_and_weighted_pullback(tmp_path: Path) -> None:
    data = _build(tmp_path)
    by_id = {row["formula_id"]: row for row in data["formulas"]}

    aberration = by_id["BASS.FRAME.ABERRATED_DIRECTION.001"]
    aberration_text = json.dumps(aberration, sort_keys=True)
    assert "gamma^2/(gamma+1)" in aberration_text
    assert "(gamma-1)/beta_squared" not in aberration_text
    assert aberration["equation_ir"]["domain"]["zero_boost"] == (
        "direct evaluation without 0/0"
    )

    blackbody = by_id["BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001"]
    assert blackbody["dependencies"] == [
        "BASS.FRAME.ABERRATED_DIRECTION.001",
        "BASS.FRAME.DOPPLER_FACTOR.001",
    ]
    roles = {
        row["formula_id"]: row["role"]
        for row in blackbody["dependency_roles"]
    }
    assert roles == {
        "BASS.FRAME.ABERRATED_DIRECTION.001": "BASE_MAP_REQUIRED",
        "BASS.FRAME.DOPPLER_FACTOR.001": "FIBER_WEIGHT_REQUIRED",
    }
    operator_ir = blackbody["equation_ir"]["operator_ir"]
    assert operator_ir["base_map"]["target_evaluation_uses"] == "INVERSE_MAP"
    assert operator_ir["fiber_weight"]["exponent"] == 1
    assert operator_ir["defining_equation"] == {
        "lhs": "Pullback[A_beta,temperature_tilde]",
        "rhs": "doppler_factor_source*temperature_source",
    }


def test_photon_parameter_and_geodesic_normal_specialization(tmp_path: Path) -> None:
    data = _build(tmp_path)
    by_id = {row["formula_id"]: row for row in data["formulas"]}
    for formula_id in (
        "BASS.PHOTON.DIRECTION_FLOW.001",
        "BASS.PHOTON.ENERGY_DRIFT.001",
    ):
        row = by_id[formula_id]
        target = row["equation_ir"]["target"]
        assert "/ds" in target
        assert "/d ell" not in target
        assumptions = "\n".join(row["equation_ir"]["assumptions"])
        assert "ray_parameter s = c*t" in assumptions
        assert "normal_congruence_acceleration A_normal^a = 0" in assumptions
        specializations = row["structural_specializations"]
        assert specializations == [
            {
                "formula_id": "BASS.GEO.NORMAL_ACCELERATION.001",
                "role": "SPECIALIZES_UNDER_ZERO",
                "value": "A_normal^a=0",
            }
        ]

    direction = by_id["BASS.PHOTON.DIRECTION_FLOW.001"]
    assert direction["equation_ir"]["screen_basis_transport_status"] == (
        "EXCLUDED_NEXT_BASS_NODE"
    )


def test_semantic_hashes_are_reproducible(tmp_path: Path) -> None:
    data = _build(tmp_path)
    for row in data["formulas"]:
        assert row["semantic_hash"] == _sha256(row["semantic_projection"])
    assert data["registry_semantic_hash"] == _sha256(
        data["registry_semantic_projection"]
    )


def test_no_cross_repository_source_mutation_is_declared(tmp_path: Path) -> None:
    data = _build(tmp_path)
    assert data["repository_scope"] == "BASS_ONLY"
    excluded = set(data["coverage"]["excluded"])
    assert "REC, REI, or HTT source modification" in excluded
    assert data["claim_boundary"] == [
        "BASS_OWNER_FORMULA_HARDENING_ONLY",
        "NO_CROSS_REPOSITORY_SOURCE_MUTATION",
        "NO_CONSUMER_PARITY",
        "NO_BACKGROUND_PROVIDER",
        "NO_GLOBAL_TILT",
        "NO_SCREEN_TRANSPORT",
        "NO_NUMERICAL_OR_SCIENCE_PROMOTION",
    ]
