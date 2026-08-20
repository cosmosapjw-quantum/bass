#!/usr/bin/env python3
"""Deterministic, stdlib-only Type-II fixture reconstruction.

The complete generator and CLI are deliberately kept in one executable source
file so the numerical and provenance contracts travel with the fixture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import sys
import tempfile
from typing import Any, Mapping


U64_MASK = (1 << 64) - 1
SPLITMIX64_GAMMA = 0x9E37_79B9_7F4A_7C15
SPLITMIX64_MUL1 = 0xBF58_476D_1CE4_E5B9
SPLITMIX64_MUL2 = 0x94D0_49BB_1331_11EB
CANONICAL_SEED = 0x4241_5353_5F48_4F53
FORMULA_AUTHORITY_LABEL_SHA256 = (
    "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361"
)
GENERATED_BACKGROUND_ACTUAL_SHA256 = (
    "0f1f31dad4c106fa22ac1ea8e95651ede24a32d24400629e10f8271d99490d15"
)
OUTPUT_PATHS = (
    Path("compiler/validation/typeii_fixture_canonical.json"),
    Path("compiler/validation/typeii_fixture_receipt.json"),
    Path("runtime/rust/typeii/tests/support/typeii_fixture_generated.rs"),
    Path("runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json"),
)
BASE_EXECUTABLE_TEST_SOURCE_PATHS = (
    Path("compiler/tests/test_rust_typeii_lowering.py"),
    Path("compiler/tests/test_rust_typeii_polarized_lowering.py"),
    Path("compiler/validation/test_generate_typeii_fixture.py"),
    Path("compiler/validation/test_typeii_conservation_quad.py"),
    Path("compiler/validation/test_typeii_polarized_runtime.py"),
    Path("runtime/rust/typeii/tests/typeii_fixture_reconstruction.rs"),
    Path("runtime/rust/typeii/tests/typeii_krylov_adapt_hostile.rs"),
    Path("runtime/rust/typeii/tests/typeii_krylov_adapt_unit.rs"),
    Path("runtime/rust/typeii/tests/typeii_polarized_runtime_unit.rs"),
    Path("runtime/rust/typeii/tests/typeii_runtime_unit.rs"),
)
SOURCE_DEPENDENCY_PATHS = (
    Path("compiler/examples/typeII-minimal.symir.json"),
    Path("compiler/lowering/rust_typeii.py"),
    Path("compiler/lowering/rust_typeii_polarized.py"),
    Path("compiler/lowering/templates/typeii_polarized.rs.in"),
    Path("compiler/validation/typeII_v_schedule.json"),
    Path("compiler/validation/typeii_conservation_quad.py"),
    Path("compiler/validation/typeii_fixture_authority.json"),
    Path("compiler/validation/typeii_polarized_runtime.py"),
    Path("generated/rust/typeii/typeii_background.rs"),
    Path("generated/rust/typeii/typeii_collision.rs"),
    Path("generated/rust/typeii/typeii_kato.rs"),
    Path("generated/rust/typeii/typeii_polarized.rs"),
    Path("generated/rust/typeii/manifest.json"),
    Path("generated/rust/typeii/polarized_manifest.json"),
    Path("runtime/rust/typeii/tests/support/typeii_polarized_tail.rs"),
    Path("runtime/rust/typeii/tests/support/typeii_v_schedule.rs"),
    Path("runtime/rust/typeii/typeii_krylov_adapt.rs"),
    Path("runtime/rust/typeii/typeii_polarized_runtime.rs"),
    Path("runtime/rust/typeii/typeii_runtime.rs"),
)
BACKGROUND_SOURCE_PATH = Path("generated/rust/typeii/typeii_background.rs")
AP_IMPLEMENTATION_PATHS = (
    Path("runtime/rust/typeii/typeii_collision_ap.rs"),
    Path("runtime/rust/typeii/typeii_physical_guard.rs"),
    Path("runtime/rust/typeii/typeii_polarized_runtime_physical.rs"),
)
PRE_LIOUVILLE_TEST_PATH = Path(
    "runtime/rust/typeii/tests/typeii_pre_liouville_safety.rs"
)
PRE_LIOUVILLE_DEPENDENCY_PATHS = AP_IMPLEMENTATION_PATHS + (
    PRE_LIOUVILLE_TEST_PATH,
)
LEGACY_FIXTURE_PROVENANCE_V1 = {
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
}


class FixtureContractError(ValueError):
    """Raised when an authority or tracked output violates the fixture contract."""


class SplitMix64:
    """Unsigned-64 SplitMix64 with explicit wrapping after each operation."""

    def __init__(self, seed: int) -> None:
        if not 0 <= seed <= U64_MASK:
            raise ValueError("SplitMix64 seed must fit in unsigned 64 bits")
        self.state = seed

    def next_u64(self) -> int:
        self.state = (self.state + SPLITMIX64_GAMMA) & U64_MASK
        z = self.state
        z = ((z ^ (z >> 30)) * SPLITMIX64_MUL1) & U64_MASK
        z = ((z ^ (z >> 27)) * SPLITMIX64_MUL2) & U64_MASK
        return (z ^ (z >> 31)) & U64_MASK

    def next_signed_unit_f64(self) -> float:
        """Return a binary64 in [-1,1) from the high 53 output bits."""
        return 2.0 * ((self.next_u64() >> 11) * (2.0**-53)) - 1.0


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value: Any) -> bytes:
    """UTF-8, sorted-key, compact JSON plus one LF; floats use Python repr."""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FixtureContractError(f"cannot load {path}: {exc}") from exc


def _validate_authority(authority: Mapping[str, Any]) -> None:
    if authority.get("schema") != "bass-typeii-fixture-authority-v1":
        raise FixtureContractError("unexpected authority schema")
    if authority.get("formula_authority_label_sha256") != FORMULA_AUTHORITY_LABEL_SHA256:
        raise FixtureContractError("formula authority label hash mismatch")
    if authority.get("generated_typeii_background_actual_sha256") != GENERATED_BACKGROUND_ACTUAL_SHA256:
        raise FixtureContractError("generated background output hash mismatch")
    rng = authority.get("rng", {})
    if rng.get("algorithm") != "SplitMix64" or rng.get("seed_hex") != f"0x{CANONICAL_SEED:016x}":
        raise FixtureContractError("SplitMix64 algorithm or seed mismatch")
    trajectory = authority.get("trajectory", {})
    if trajectory.get("integrator") != "fixed-step-classical-rk4-binary64":
        raise FixtureContractError("trajectory integrator mismatch")
    if trajectory.get("sample_count") != 401:
        raise FixtureContractError("trajectory sample count mismatch")
    if trajectory.get("dt") != 0.0005 or trajectory.get("tau_end") != 0.2:
        raise FixtureContractError("trajectory interval mismatch")
    anchors = authority.get("opacity_model", {}).get("anchors", [])
    expected = [
        [0.0, 240.13336620482818],
        [0.1, 100.08485094440381],
        [0.2, 13.322173705416928],
    ]
    if anchors != expected:
        raise FixtureContractError("opacity receipt anchors mismatch")


def typeii_rhs(state: list[float], gamma: float) -> list[float]:
    """Tilted Type-II aligned five-state RHS from the symbolic source model."""
    sigma_p, sigma_m, sigma_13, n1, v2 = state
    sqrt3 = math.sqrt(3.0)
    sigma2 = sigma_p * sigma_p + sigma_m * sigma_m + sigma_13 * sigma_13
    omega = 1.0 - sigma2 - n1 * n1 / 12.0
    gp = 1.0 + (gamma - 1.0) * v2 * v2
    gm = 1.0 - (gamma - 1.0) * v2 * v2
    sig2 = sigma_p + sqrt3 * sigma_m
    q = (
        2.0 * sigma2
        + 0.5
        * ((3.0 * gamma - 2.0) + (2.0 - gamma) * v2 * v2)
        * omega
        / gp
    )
    ttil = (
        (3.0 * gamma - 4.0) * (1.0 - v2 * v2)
        + (2.0 - gamma) * sig2 * v2 * v2
    ) / gm
    return [
        -(2.0 - q) * sigma_p
        + n1 * n1 / 3.0
        + gamma * omega * v2 * v2 / (2.0 * gp)
        - 3.0 * sigma_13 * sigma_13,
        -(2.0 - q) * sigma_m
        + sqrt3 * gamma * omega * v2 * v2 / (2.0 * gp)
        + sqrt3 * sigma_13 * sigma_13,
        sigma_13 * (-(2.0 - q) + 3.0 * sigma_p - sqrt3 * sigma_m),
        (q - 4.0 * sigma_p) * n1,
        v2 * (ttil - sig2),
    ]


def _rk4_step(state: list[float], dt: float, gamma: float) -> list[float]:
    k1 = typeii_rhs(state, gamma)
    k2 = typeii_rhs([x + 0.5 * dt * k for x, k in zip(state, k1)], gamma)
    k3 = typeii_rhs([x + 0.5 * dt * k for x, k in zip(state, k2)], gamma)
    k4 = typeii_rhs([x + dt * k for x, k in zip(state, k3)], gamma)
    return [
        x + dt * (a + 2.0 * b + 2.0 * c + d) / 6.0
        for x, a, b, c, d in zip(state, k1, k2, k3, k4)
    ]


def _opacity(index: int, tau: float, anchors: list[list[float]]) -> float:
    """Positive log-quadratic schedule constrained by the three old receipts."""
    anchor_by_index = {0: anchors[0][1], 200: anchors[1][1], 400: anchors[2][1]}
    if index in anchor_by_index:
        return float(anchor_by_index[index])
    x = tau / 0.1
    logs = [math.log(float(pair[1])) for pair in anchors]
    lagrange = [0.5 * (x - 1.0) * (x - 2.0), -x * (x - 2.0), 0.5 * x * (x - 1.0)]
    return math.exp(sum(weight * value for weight, value in zip(lagrange, logs)))


def _trajectory(authority: Mapping[str, Any]) -> list[dict[str, Any]]:
    contract = authority["trajectory"]
    state = [float(x) for x in contract["initial_state"]]
    gamma = float(contract["gamma"])
    dt = float(contract["dt"])
    anchors = authority["opacity_model"]["anchors"]
    opacity0 = float(anchors[0][1])
    samples = []
    for index in range(int(contract["sample_count"])):
        tau = index * dt
        opacity = _opacity(index, tau, anchors)
        samples.append(
            {
                "index": index,
                "opacity": opacity,
                "rhs": typeii_rhs(state, gamma),
                "saha_xe_proxy": opacity / opacity0,
                "state": list(state),
                "tau": tau,
            }
        )
        if index + 1 < int(contract["sample_count"]):
            state = _rk4_step(state, dt, gamma)
    return samples


def _fmt_rust_float(value: float) -> str:
    if not math.isfinite(value):
        raise FixtureContractError("non-finite value cannot enter Rust fixture")
    text = repr(float(value))
    if "e" not in text and "." not in text:
        text += ".0"
    return text


def _render_rust(samples: list[dict[str, Any]], rng_words: list[int]) -> bytes:
    def field_array(name: str, values: list[float]) -> list[str]:
        rendered = [_fmt_rust_float(x) for x in values]
        single = f"        {name}: [{', '.join(rendered)}],"
        if len(single) <= 100:
            return [single]
        return [
            f"        {name}: [",
            *(f"            {value}," for value in rendered),
            "        ],",
        ]

    rows = []
    for sample in samples:
        rows.extend(
            [
                "    TypeIIFixtureSample {",
                f"        tau: {_fmt_rust_float(sample['tau'])},",
                *field_array("state", sample["state"]),
                *field_array("rhs", sample["rhs"]),
                f"        opacity: {_fmt_rust_float(sample['opacity'])},",
                "    },",
            ]
        )
    words = "\n".join(f"    0x{x:016x}_u64," for x in rng_words)
    text = f'''//! AUTO-GENERATED by compiler/validation/generate_typeii_fixture.py.
//! Canonical source-derived Type-II RK4 fixture; do not edit by hand.

pub const FORMULA_AUTHORITY_LABEL_SHA256: &str =
    "{FORMULA_AUTHORITY_LABEL_SHA256}";
pub const GENERATED_BACKGROUND_ACTUAL_SHA256: &str =
    "{GENERATED_BACKGROUND_ACTUAL_SHA256}";
pub const SPLITMIX64_SEED: u64 = 0x{CANONICAL_SEED:016x}_u64;

#[derive(Clone, Copy, Debug)]
pub struct SplitMix64 {{
    state: u64,
}}

impl SplitMix64 {{
    pub const fn new(seed: u64) -> Self {{
        Self {{ state: seed }}
    }}

    pub fn next_u64(&mut self) -> u64 {{
        self.state = self.state.wrapping_add(0x{SPLITMIX64_GAMMA:016x});
        let mut z = self.state;
        z = (z ^ (z >> 30)).wrapping_mul(0x{SPLITMIX64_MUL1:016x});
        z = (z ^ (z >> 27)).wrapping_mul(0x{SPLITMIX64_MUL2:016x});
        z ^ (z >> 31)
    }}
}}

pub const RNG_U64_KNOWN_ANSWER: [u64; {len(rng_words)}] = [
{words}
];

#[derive(Clone, Copy, Debug)]
pub struct TypeIIFixtureSample {{
    pub tau: f64,
    pub state: [f64; 5],
    pub rhs: [f64; 5],
    pub opacity: f64,
}}

pub const TYPEII_SAMPLES: [TypeIIFixtureSample; {len(samples)}] = [
{chr(10).join(rows)}
];
'''
    return text.encode("utf-8")


def _parse_rust_array(text: str, name: str) -> list[float]:
    match = re.search(
        rf"pub const {re.escape(name)}: \[f64; \d+\] = \[(.*?)\];",
        text,
        flags=re.DOTALL,
    )
    if match is None:
        raise FixtureContractError(f"cannot find Rust array {name}")
    try:
        return [float(token.strip()) for token in match.group(1).split(",") if token.strip()]
    except ValueError as exc:
        raise FixtureContractError(f"cannot parse Rust array {name}") from exc


def _schedule_discrepancies(repo_root: Path) -> list[dict[str, Any]]:
    canonical = _load_json(repo_root / "compiler/validation/typeII_v_schedule.json")
    rust_text = (
        repo_root / "runtime/rust/typeii/tests/support/typeii_v_schedule.rs"
    ).read_text(encoding="utf-8")
    discrepancies = []
    for rust_name, json_name in (("V2", "v2"), ("V2DOT", "v2dot")):
        rust_values = _parse_rust_array(rust_text, rust_name)
        json_values = canonical[json_name]
        if len(rust_values) != len(json_values):
            raise FixtureContractError(f"{rust_name} length mismatch")
        for index, (rust_value, json_value) in enumerate(zip(rust_values, json_values)):
            if rust_value != json_value:
                discrepancies.append(
                    {
                        "absolute_difference": abs(rust_value - json_value),
                        "index": index,
                        "json_value": json_value,
                        "rust_array": rust_name,
                        "rust_value": rust_value,
                    }
                )
    return discrepancies


def _observed_environment() -> dict[str, Any]:
    libc_name, libc_version = platform.libc_ver()
    python_build_name, python_build_date = platform.python_build()
    return {
        "blas": "not used",
        "byteorder": sys.byteorder,
        "cross_platform_bitwise_identity": "not claimed; canonical float bytes are established only for the recorded CPython/compiler/libc-libm environment",
        "float_mant_dig": sys.float_info.mant_dig,
        "float_radix": sys.float_info.radix,
        "libc": {"name": libc_name, "version": libc_version},
        "libm_usage": "CPython math.sqrt/log/exp; implementation supplied by the recorded platform libc/libm toolchain",
        "machine": platform.machine(),
        "numpy": "not imported",
        "python_build": {"date": python_build_date, "name": python_build_name},
        "python_compiler": platform.python_compiler(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "scope": "fixture generator execution only",
        "scipy": "not imported",
        "system": platform.system(),
        "third_party_numeric_used": False,
        "thread_controls": "not applicable; stdlib scalar arithmetic only",
    }


def _input_hashes(repo_root: Path) -> dict[str, str]:
    paths = tuple(
        dict.fromkeys(
            _executable_test_source_paths(repo_root)
            + SOURCE_DEPENDENCY_PATHS
            + _integrated_ap_source_paths(repo_root)
        )
    )
    return {path.as_posix(): _sha256((repo_root / path).read_bytes()) for path in paths}


def _integrated_pre_liouville_dependency_paths(repo_root: Path) -> tuple[Path, ...]:
    present = tuple(
        (repo_root / path).is_file() for path in PRE_LIOUVILLE_DEPENDENCY_PATHS
    )
    if any(present) and not all(present):
        missing = [
            path.as_posix()
            for path, exists in zip(PRE_LIOUVILLE_DEPENDENCY_PATHS, present)
            if not exists
        ]
        raise FixtureContractError(
            f"partial AP implementation source integration; missing: {', '.join(missing)}"
        )
    if all(present):
        return PRE_LIOUVILLE_DEPENDENCY_PATHS
    return ()


def _integrated_ap_source_paths(repo_root: Path) -> tuple[Path, ...]:
    if _integrated_pre_liouville_dependency_paths(repo_root):
        return AP_IMPLEMENTATION_PATHS
    return ()


def _executable_test_source_paths(repo_root: Path) -> tuple[Path, ...]:
    if _integrated_pre_liouville_dependency_paths(repo_root):
        return BASE_EXECUTABLE_TEST_SOURCE_PATHS + (PRE_LIOUVILLE_TEST_PATH,)
    return BASE_EXECUTABLE_TEST_SOURCE_PATHS


def _ap_source_dependency_status(
    repo_root: Path, input_hashes: Mapping[str, str]
) -> dict[str, Any]:
    integrated = _integrated_pre_liouville_dependency_paths(repo_root)
    required = [path.as_posix() for path in PRE_LIOUVILLE_DEPENDENCY_PATHS]
    if not integrated:
        return {
            "claim_boundary": "the future PRE Liouville AP/physical source-and-test bundle is absent; this PR9 receipt makes no claim that those bytes are integrated",
            "final_approval_allowed": False,
            "final_approval_allowed_meaning": "false because the fixture source-binding prerequisite is unsatisfied; this field never certifies independent audit results",
            "final_approval_requires_independent_audits": True,
            "fixture_source_binding_complete": False,
            "fixture_source_binding_allows_final_approval": False,
            "missing_paths": required,
            "required_final_paths": required,
            "status": "not_integrated",
        }
    hashed_paths = {}
    for path in integrated:
        name = path.as_posix()
        if name not in input_hashes:
            raise FixtureContractError(f"missing AP implementation input hash: {name}")
        hashed_paths[name] = input_hashes[name]
    return {
        "claim_boundary": "candidate PRE Liouville AP/physical source-and-test bytes are present and hashed at canonical runtime/rust paths; independent physical/AP approval remains separate",
        "final_approval_allowed": True,
        "final_approval_allowed_meaning": "true only for the fixture source-binding prerequisite; this field does not certify the separately required independent audits",
        "final_approval_requires_independent_audits": True,
        "fixture_source_binding_complete": True,
        "fixture_source_binding_allows_final_approval": True,
        "hashed_paths": hashed_paths,
        "required_final_paths": required,
        "status": "integrated_and_hashed",
    }


def generate_artifacts(
    repo_root: Path,
    output_root: Path,
    *,
    authority_path: Path | None = None,
) -> dict[Path, bytes]:
    """Generate all canonical outputs and write them below ``output_root``."""
    repo_root = repo_root.resolve()
    output_root = output_root.resolve()
    authority_path = authority_path or (
        repo_root / "compiler/validation/typeii_fixture_authority.json"
    )
    authority = _load_json(authority_path)
    _validate_authority(authority)
    samples = _trajectory(authority)
    rng = SplitMix64(CANONICAL_SEED)
    rng_words = [rng.next_u64() for _ in range(16)]
    rng_float_source = SplitMix64(CANONICAL_SEED)
    rng_floats = [rng_float_source.next_signed_unit_f64() for _ in range(16)]

    fixture = {
        "claim_boundary": authority["claim_boundary"],
        "float_representation": "JSON numbers emitted by CPython shortest round-trip repr for IEEE-754 binary64",
        "json_serialization": "UTF-8; sorted keys; compact separators; ensure_ascii=true; one terminal LF",
        "opacity_model": authority["opacity_model"],
        "rng_probe": {
            "algorithm": "SplitMix64",
            "seed_hex": f"0x{CANONICAL_SEED:016x}",
            "signed_unit_f64": rng_floats,
            "u64_hex": [f"0x{x:016x}" for x in rng_words],
        },
        "schema": "bass-typeii-canonical-fixture-v1",
        "trajectory": {
            "contract": authority["trajectory"],
            "samples": samples,
        },
    }
    fixture_bytes = _canonical_json(fixture)
    rust_bytes = _render_rust(samples, rng_words)
    generator_path = Path(__file__).resolve()
    input_hashes = _input_hashes(repo_root)
    input_hashes["compiler/validation/typeii_fixture_authority.json"] = _sha256(
        authority_path.read_bytes()
    )
    background_actual_sha256 = input_hashes[BACKGROUND_SOURCE_PATH.as_posix()]
    if background_actual_sha256 != GENERATED_BACKGROUND_ACTUAL_SHA256:
        raise FixtureContractError("generated background actual hash mismatch")
    source_dependency_status = {
        "pre_liouville_ap_implementation": _ap_source_dependency_status(
            repo_root, input_hashes
        )
    }
    receipt = {
        "authority": {
            "authority_input_sha256": input_hashes[
                "compiler/validation/typeii_fixture_authority.json"
            ],
            "formula_authority_label_sha256": FORMULA_AUTHORITY_LABEL_SHA256,
            "generated_typeii_background_actual_sha256": background_actual_sha256,
            "generated_typeii_background_hash_evidence": authority[
                "generated_typeii_background_hash_evidence"
            ],
            "hash_roles_are_distinct": True,
            "opacity_authority_boundary": authority["opacity_model"]["authority_boundary"],
        },
        "canonical_outputs": {
            "compiler/validation/typeii_fixture_canonical.json": _sha256(fixture_bytes),
            "runtime/rust/typeii/tests/support/typeii_fixture_generated.rs": _sha256(rust_bytes),
        },
        "environment": _observed_environment(),
        "executable_test_sources": {
            path.as_posix(): input_hashes[path.as_posix()]
            for path in _executable_test_source_paths(repo_root)
        },
        "generator": {
            "path": "compiler/validation/generate_typeii_fixture.py",
            "sha256": _sha256(generator_path.read_bytes()),
            "stdlib_only": True,
        },
        "input_hashes": dict(sorted(input_hashes.items())),
        "schema": "bass-typeii-fixture-receipt-v1",
        "serialization": {
            "encoding": "UTF-8",
            "float": "shortest round-trip binary64 repr",
            "json": "sorted keys, compact separators, one terminal LF",
        },
        "source_dependency_status": source_dependency_status,
    }
    receipt_bytes = _canonical_json(receipt)
    discrepancies = _schedule_discrepancies(repo_root)
    source_mid_sigma_m = samples[1]["state"][1]
    source_end_sigma_m = samples[2]["state"][1]
    historical_mid_sigma_m = 0.000012265009715214
    historical_end_sigma_m = 0.000024519691346677
    provenance = {
        "claim_boundary": {
            "establishes": "deterministic reconstruction under the stated discrete RK4 and receipt-constrained opacity model",
            "not_established": [
                "bitwise identity with the unavailable historical 80 kB fixture",
                "original SahaHistory thermodynamic authority",
                "cross-family generality",
            ],
        },
        "generated": {
            "canonical_fixture": {
                "path": "compiler/validation/typeii_fixture_canonical.json",
                "sha256": _sha256(fixture_bytes),
                "status": "regenerated from executable source",
            },
            "receipt": {
                "path": "compiler/validation/typeii_fixture_receipt.json",
                "sha256": _sha256(receipt_bytes),
            },
            "rust_support": {
                "path": "runtime/rust/typeii/tests/support/typeii_fixture_generated.rs",
                "sha256": _sha256(rust_bytes),
                "status": "regenerated from the same in-memory canonical samples",
            },
        },
        "historical_preserved": {
            "legacy_fixture_provenance_v1": {
                "receipt": LEGACY_FIXTURE_PROVENANCE_V1,
                "verification": {
                    "hashes_freshly_verified": False,
                    "referenced_bytes_available": False,
                    "status": "historical receipt preserved exactly as structured fields; referenced fixture and research-bundle bytes are unavailable and not freshly verified",
                },
            },
            "legacy_80kb_fixture_receipt": {
                "bytes_available": False,
                "claimed_sha256": "5737dead724b86ead64cc25f9e00802973df1eb2abbdc92a5e7c095df1378ef1",
                "status": "hash claim retained for history; bytes absent and not freshly verified",
            },
            "public_kato_one_step_sigma_m": [
                {
                    "absolute_difference_from_source_rk4": abs(
                        historical_mid_sigma_m - source_mid_sigma_m
                    ),
                    "historical_literal": historical_mid_sigma_m,
                    "role": "compatibility regression anchor, not exact source anchor",
                    "source_rk4": source_mid_sigma_m,
                    "stage": "midpoint",
                },
                {
                    "absolute_difference_from_source_rk4": abs(
                        historical_end_sigma_m - source_end_sigma_m
                    ),
                    "historical_literal": historical_end_sigma_m,
                    "role": "compatibility regression anchor, not exact source anchor",
                    "source_rk4": source_end_sigma_m,
                    "stage": "endpoint",
                },
            ],
            "rust_v_schedule": {
                "compatibility_discrepancies": discrepancies,
                "json_path": "compiler/validation/typeII_v_schedule.json",
                "json_sha256": input_hashes["compiler/validation/typeII_v_schedule.json"],
                "rust_path": "runtime/rust/typeii/tests/support/typeii_v_schedule.rs",
                "rust_sha256": input_hashes[
                    "runtime/rust/typeii/tests/support/typeii_v_schedule.rs"
                ],
                "status": "both historical byte sequences retained without normalization",
            },
        },
        "provenance_hash_roles": {
            "formula_authority_label_sha256": FORMULA_AUTHORITY_LABEL_SHA256,
            "generated_typeii_background_actual_sha256": GENERATED_BACKGROUND_ACTUAL_SHA256,
            "note": "the authority label is not represented as the generated Rust file hash",
        },
        "schema": "bass-fixture-provenance-v2",
        "source_dependency_status": source_dependency_status,
    }
    provenance_bytes = _canonical_json(provenance)
    outputs = {
        OUTPUT_PATHS[0]: fixture_bytes,
        OUTPUT_PATHS[1]: receipt_bytes,
        OUTPUT_PATHS[2]: rust_bytes,
        OUTPUT_PATHS[3]: provenance_bytes,
    }
    for relative, data in outputs.items():
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return outputs


def verify_generated_outputs(repo_root: Path) -> None:
    """Validate tracked hashes without generating or mutating any output."""
    receipt_path = repo_root / OUTPUT_PATHS[1]
    receipt = _load_json(receipt_path)
    if receipt.get("schema") != "bass-typeii-fixture-receipt-v1":
        raise FixtureContractError("unexpected fixture receipt schema")
    expected = receipt.get("canonical_outputs", {})
    for relative in (OUTPUT_PATHS[0], OUTPUT_PATHS[2]):
        actual_hash = _sha256((repo_root / relative).read_bytes())
        if expected.get(relative.as_posix()) != actual_hash:
            raise FixtureContractError(f"output hash mismatch: {relative}")
    generator = repo_root / "compiler/validation/generate_typeii_fixture.py"
    if receipt.get("generator", {}).get("sha256") != _sha256(generator.read_bytes()):
        raise FixtureContractError("generator source hash mismatch")
    input_hashes = receipt.get("input_hashes")
    if not isinstance(input_hashes, dict) or not input_hashes:
        raise FixtureContractError("missing input hash inventory")
    integrated_ap_inputs = _integrated_ap_source_paths(repo_root)
    executable_test_sources = _executable_test_source_paths(repo_root)
    required_inputs = {
        path.as_posix()
        for path in (
            executable_test_sources
            + SOURCE_DEPENDENCY_PATHS
            + integrated_ap_inputs
        )
    }
    missing_inputs = sorted(required_inputs.difference(input_hashes))
    if missing_inputs:
        raise FixtureContractError(
            f"missing required input hashes: {', '.join(missing_inputs)}"
        )
    executable_sources = receipt.get("executable_test_sources")
    expected_executable_sources = {
        path.as_posix(): input_hashes[path.as_posix()]
        for path in executable_test_sources
    }
    if executable_sources != expected_executable_sources:
        raise FixtureContractError("executable test source inventory mismatch")
    expected_dependency_status = {
        "pre_liouville_ap_implementation": _ap_source_dependency_status(
            repo_root, input_hashes
        )
    }
    if receipt.get("source_dependency_status") != expected_dependency_status:
        raise FixtureContractError("source dependency status mismatch")
    background_name = BACKGROUND_SOURCE_PATH.as_posix()
    declared_background_hash = receipt.get("authority", {}).get(
        "generated_typeii_background_actual_sha256"
    )
    if declared_background_hash != input_hashes.get(background_name):
        raise FixtureContractError("generated background hash role mismatch")
    if _sha256((repo_root / BACKGROUND_SOURCE_PATH).read_bytes()) != declared_background_hash:
        raise FixtureContractError("generated background actual hash mismatch")
    for name, expected_hash in input_hashes.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise FixtureContractError(f"unsafe input hash path: {name}")
        actual_hash = _sha256((repo_root / relative).read_bytes())
        if actual_hash != expected_hash:
            raise FixtureContractError(f"input hash mismatch: {name}")
    authority_name = "compiler/validation/typeii_fixture_authority.json"
    if receipt.get("authority", {}).get("authority_input_sha256") != input_hashes.get(
        authority_name
    ):
        raise FixtureContractError("authority input hash role mismatch")
    provenance = _load_json(repo_root / OUTPUT_PATHS[3])
    generated = provenance.get("generated", {})
    if generated.get("canonical_fixture", {}).get("sha256") != expected.get(
        OUTPUT_PATHS[0].as_posix()
    ):
        raise FixtureContractError("provenance canonical fixture hash role mismatch")
    if generated.get("rust_support", {}).get("sha256") != expected.get(
        OUTPUT_PATHS[2].as_posix()
    ):
        raise FixtureContractError("provenance Rust support hash role mismatch")
    if generated.get("receipt", {}).get("sha256") != _sha256(receipt_path.read_bytes()):
        raise FixtureContractError("receipt hash mismatch against provenance")


def check_generated_outputs(repo_root: Path) -> None:
    """Regenerate in a temporary directory and byte-compare tracked outputs."""
    verify_generated_outputs(repo_root)
    with tempfile.TemporaryDirectory(prefix="bass-typeii-fixture-check-") as tmp:
        regenerated = generate_artifacts(repo_root, Path(tmp))
        for relative, expected in regenerated.items():
            actual = (repo_root / relative).read_bytes()
            if actual != expected:
                raise FixtureContractError(f"byte mismatch: {relative}")


def _write_generated(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="bass-typeii-fixture-write-") as tmp:
        generated = generate_artifacts(repo_root, Path(tmp))
        for relative, data in generated.items():
            destination = repo_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            staging = destination.with_name(destination.name + ".tmp")
            staging.write_bytes(data)
            staging.replace(destination)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="atomically update tracked outputs")
    mode.add_argument(
        "--check",
        action="store_true",
        help="regenerate in a temporary directory and byte-compare without mutation",
    )
    mode.add_argument(
        "--verify", action="store_true", help="verify tracked hashes without regeneration"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    try:
        if args.write:
            _write_generated(repo_root)
        elif args.check:
            check_generated_outputs(repo_root)
        else:
            verify_generated_outputs(repo_root)
    except (FixtureContractError, OSError) as exc:
        print(f"fixture verification failed: {exc}", file=sys.stderr)
        return 1
    print("Type-II fixture verification PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
