#!/usr/bin/env python3
"""Verify the source-bound RF-03 matter and thermodynamics authority contract."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import NoReturn


BASE_HEAD = "dfa17457d402bd441d3fdf786c2d79c529512ee5"
BASE_TREE = "9fc67fb0ba10e091e25a14d7e1fac88b77a0241e"
AUTHORITY_HEAD = "55335d3817a82da7e0f9bf24ef7632a2533645d3"
AUTHORITY_TREE = "7c02689430d01abdf998c5b7ab1c5a6eb48859f4"
MODEL_ID = "explicit_gamma_law_tilted_perfect_fluid_v1"
STATE_ORDER = ["Omega", "v1", "v2", "v3"]
SOURCE_BLOBS = {
    "bianchi/matter/fluid.py": "41905ff26914b2a7931ce2281d67b25fbde273b5",
    "bianchi/matter/species.py": "60a683fcdc639ae790cf6f3c723182d26940d21f",
    "bianchi/matter/tilt_admissibility.py": "c384a87c1722bd3c6b9b7e02ea71efe7ec88b676",
    "bianchi/thermo/temperature.py": "4b792b04df072446a5d046524ea5323e4237d7e4",
    "compiler/validation/typeii_fixture_authority.json": (
        "b71372faa7dde85e928802c08c831299ebe99bcd"
    ),
    "runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json": (
        "dfee51903025b4c9d3f62f63581271bd3b6a98cb"
    ),
}
DEFAULT_PRIOR_FREEZE = Path(
    "/tmp/bass-rf03-20260828.4M5fCz/worktree/artifacts/"
    "rust_first_runtime/rf03/SCHEMA_AND_ROUTE_FREEZE.json"
)


class VerificationError(RuntimeError):
    pass


def fail(code: str, detail: str) -> NoReturn:
    raise VerificationError(f"{code}: {detail}")


def load_json(path: Path) -> object:
    def no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                fail("DUPLICATE_JSON_KEY", f"{path}: {key}")
            result[key] = value
        return result

    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("INVALID_JSON", f"{path}: {exc}")


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        fail("GIT_FAILURE", f"git {' '.join(args)}: {result.stderr.strip()}")
    return result


def git_line(repo: Path, *args: str) -> str:
    return git(repo, *args).stdout.removesuffix("\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        fail("AUTHORITY_SEMANTICS_MISMATCH", f"{label} must be an object")
    return value


def require_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        fail(
            "AUTHORITY_SEMANTICS_MISMATCH",
            f"{label} expected={expected!r} actual={actual!r}",
        )


def verify_git_identity(repo: Path, authority: dict[str, object]) -> None:
    if git_line(repo, "rev-parse", f"{BASE_HEAD}^{{tree}}") != BASE_TREE:
        fail("BASE_IDENTITY_MISMATCH", "RF-02C base tree differs")
    ancestor = git(repo, "merge-base", "--is-ancestor", BASE_HEAD, "HEAD", check=False)
    if ancestor.returncode:
        fail("BASE_IDENTITY_MISMATCH", "RF-02C base is not an ancestor of HEAD")
    if git_line(repo, "rev-parse", f"{AUTHORITY_HEAD}^{{tree}}") != AUTHORITY_TREE:
        fail("AUTHORITY_PACKAGE_IDENTITY_MISMATCH", "R2 authority tree differs")

    declared = mapping(authority.get("source_blobs"), "source_blobs")
    if declared != SOURCE_BLOBS:
        fail(
            "SOURCE_BLOB_IDENTITY_MISMATCH",
            f"declared source map expected={SOURCE_BLOBS!r} actual={declared!r}",
        )
    for path, expected in SOURCE_BLOBS.items():
        actual = git_line(repo, "rev-parse", f"HEAD:{path}")
        if actual != expected:
            fail(
                "SOURCE_BLOB_IDENTITY_MISMATCH",
                f"{path} expected={expected} actual={actual}",
            )


def class_node(tree: ast.Module, name: str, path: Path) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    fail("SOURCE_SEMANTICS_MISMATCH", f"{path}: missing class {name}")


def method_node(owner: ast.ClassDef, name: str, path: Path) -> ast.FunctionDef:
    for node in owner.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    fail("SOURCE_SEMANTICS_MISMATCH", f"{path}: missing {owner.name}.{name}")


def module_function(tree: ast.Module, name: str, path: Path) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    fail("SOURCE_SEMANTICS_MISMATCH", f"{path}: missing function {name}")


def positional_names(function: ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in [*function.args.posonlyargs, *function.args.args]]


def verify_source_semantics(repo: Path) -> None:
    fluid_path = repo / "bianchi/matter/fluid.py"
    species_path = repo / "bianchi/matter/species.py"
    fluid_tree = ast.parse(fluid_path.read_text(encoding="utf-8"), filename=str(fluid_path))
    species_tree = ast.parse(
        species_path.read_text(encoding="utf-8"), filename=str(species_path)
    )

    tilted = class_node(fluid_tree, "TiltedFluid", fluid_path)
    fields = [
        node.target.id
        for node in tilted.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    ]
    require_equal(fields, ["gamma", "Omega", "v"], "TiltedFluid field order")
    tilted_of = method_node(tilted, "of", fluid_path)
    require_equal(positional_names(tilted_of), ["gamma", "Omega", "v"], "TiltedFluid.of")
    require_equal(len(tilted_of.args.defaults), 0, "TiltedFluid.of defaults")

    expected_functions = {
        "sources": ["f", "Sigma", "A"],
        "dOmega": ["f", "s", "q"],
        "dv_general": ["f", "s", "Sigma", "N", "A", "R"],
    }
    for name, expected_args in expected_functions.items():
        require_equal(
            positional_names(module_function(fluid_tree, name, fluid_path)),
            expected_args,
            f"{name} arguments",
        )

    species = class_node(species_tree, "FluidSpecies", species_path)
    species_of = method_node(species, "of", species_path)
    require_equal(
        positional_names(species_of)[:3],
        ["gamma", "Omega", "v"],
        "FluidSpecies.of required prefix",
    )
    if len(positional_names(species_of)) - len(species_of.args.defaults) != 3:
        fail("SOURCE_SEMANTICS_MISMATCH", "FluidSpecies.of gamma/Omega/v must be required")

    direct_tilted_constructor = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "of"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "TiltedFluid"
        for node in ast.walk(species_of)
    )
    if not direct_tilted_constructor:
        fail("SOURCE_SEMANTICS_MISMATCH", "FluidSpecies.of must directly select TiltedFluid")

    force_methods = [
        method_node(species, name, species_path)
        for name in ("_src", "q_source", "pi", "q_flux", "rhs")
    ]
    for method in force_methods:
        for node in ast.walk(method):
            if (isinstance(node, ast.Name) and node.id == "T_gamma") or (
                isinstance(node, ast.Attribute) and node.attr == "T_gamma"
            ):
                fail(
                    "T_GAMMA_FEEDBACK_DETECTED",
                    f"FluidSpecies.{method.name} reads T_gamma",
                )


def verify_authority_semantics(authority: dict[str, object]) -> None:
    require_equal(authority.get("schema"), "bass-rf03-production-authority/v1", "schema")
    source_base = mapping(authority.get("source_base"), "source_base")
    require_equal(source_base.get("head"), BASE_HEAD, "source_base.head")
    require_equal(source_base.get("tree"), BASE_TREE, "source_base.tree")
    package = mapping(authority.get("authority_package"), "authority_package")
    require_equal(package.get("head"), AUTHORITY_HEAD, "authority_package.head")
    require_equal(package.get("tree"), AUTHORITY_TREE, "authority_package.tree")

    matter = mapping(authority.get("production_matter_authority"), "matter authority")
    require_equal(matter.get("model_id"), MODEL_ID, "model_id")
    require_equal(matter.get("state_order"), STATE_ORDER, "matter state_order")
    require_equal(
        matter.get("caller_must_supply"),
        ["model_id", "gamma", "Omega", "v"],
        "caller_must_supply",
    )
    require_equal(matter.get("equation_of_state"), "p = (gamma - 1) rho", "EOS")
    force = mapping(matter.get("force"), "force")
    jvp = mapping(matter.get("jvp"), "jvp")
    require_equal(force.get("state_order"), STATE_ORDER, "force.state_order")
    require_equal(jvp.get("state_order"), STATE_ORDER, "jvp.state_order")
    selection = mapping(matter.get("selection"), "selection")
    require_equal(selection.get("missing_model_id"), "TYPED_FAILURE", "missing model")
    require_equal(selection.get("unknown_model_id"), "TYPED_FAILURE", "unknown model")
    for key in (
        "hidden_default_gamma",
        "python_fallback",
        "silent_constant_w_fallback",
        "surrogate_eos_substitution",
    ):
        require_equal(selection.get(key), "FORBIDDEN", f"selection.{key}")

    thermo = mapping(authority.get("thermodynamics_boundary"), "thermodynamics")
    require_equal(thermo.get("T_gamma_force_role"), "EXOGENOUS_NO_FEEDBACK", "T_gamma force")
    require_equal(thermo.get("T_gamma_jvp_role"), "EXOGENOUS_NO_FEEDBACK", "T_gamma JVP")
    require_equal(
        thermo.get("tilted_temperature_formula"),
        "UNDEFINED_AND_NOT_AUTHORIZED",
        "tilted temperature",
    )
    historical = mapping(thermo.get("historical_typeii"), "historical_typeii")
    require_equal(historical.get("classification"), "SURROGATE_REFERENCE_ONLY", "Type-II")
    require_equal(historical.get("production_promotion"), "FORBIDDEN", "Type-II promotion")


def verify_historical_typeii(repo: Path) -> None:
    authority = mapping(
        load_json(repo / "compiler/validation/typeii_fixture_authority.json"),
        "typeii fixture authority",
    )
    opacity = mapping(authority.get("opacity_model"), "opacity_model")
    boundary = opacity.get("authority_boundary")
    if not isinstance(boundary, str) or "not the original thermodynamics authority" not in boundary:
        fail("TYPEII_AUTHORITY_DRIFT", "fixture no longer declares surrogate boundary")
    provenance = mapping(
        load_json(repo / "runtime/rust/typeii/tests/FIXTURE_PROVENANCE.json"),
        "Type-II fixture provenance",
    )
    claim = mapping(provenance.get("claim_boundary"), "Type-II claim boundary")
    excluded = claim.get("not_established")
    if not isinstance(excluded, list) or "original SahaHistory thermodynamic authority" not in excluded:
        fail("TYPEII_AUTHORITY_DRIFT", "provenance promotes historical thermodynamics")


def prior_freeze_payload(path: Path | None) -> dict[str, object]:
    if path is None or not path.is_file():
        return {
            "availability": "ORIGINAL_LOCAL_BLOCKER_ARTIFACT_UNAVAILABLE",
            "content": None,
            "sha256": None,
        }
    content = load_json(path)
    if not isinstance(content, dict):
        fail("PRIOR_FREEZE_INVALID", "prior blocker freeze is not an object")
    return {
        "availability": "AVAILABLE",
        "content": content,
        "sha256": sha256(path),
    }


def verify(repo: Path, authority_path: Path, prior_freeze: Path | None) -> dict[str, object]:
    authority = load_json(authority_path)
    if not isinstance(authority, dict):
        fail("AUTHORITY_SEMANTICS_MISMATCH", "authority root must be an object")
    verify_authority_semantics(authority)
    verify_git_identity(repo, authority)
    verify_source_semantics(repo)
    verify_historical_typeii(repo)
    return {
        "schema": "bass-rf03-authority-verification/v1",
        "authority_package_head": AUTHORITY_HEAD,
        "authority_sha256": sha256(authority_path),
        "base_head": BASE_HEAD,
        "checks": {
            "authority_semantics": "PASS",
            "explicit_gamma_and_state": "PASS",
            "historical_typeii_surrogate_only": "PASS",
            "source_blob_identity": "PASS",
            "t_gamma_force_invariance": "PASS",
            "t_gamma_jvp_invariance": "PASS",
        },
        "claim": "NO_PASS_RF03",
        "prior_blocker_freeze": prior_freeze_payload(prior_freeze),
        "source_blobs": SOURCE_BLOBS,
        "terminal": "PASS_RF03_AUTHORITY",
    }


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=root)
    parser.add_argument(
        "--authority",
        type=Path,
        default=root / "provenance/authority/rf03/RF03_AUTHORITY.json",
    )
    parser.add_argument("--prior-freeze", type=Path, default=DEFAULT_PRIOR_FREEZE)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        payload = verify(args.repo.resolve(), args.authority.resolve(), args.prior_freeze)
        if args.receipt is not None:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(payload, sort_keys=True))
        return 0
    except VerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
