#!/usr/bin/env python3
"""Self-contained verifier for the BASS-8B.2B.1 candidate package."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_manifest() -> int:
    manifest = ROOT / "MANIFEST.sha256"
    if not manifest.is_file():
        raise RuntimeError("missing MANIFEST.sha256")
    count = 0
    for raw in manifest.read_text().splitlines():
        if not raw.strip():
            continue
        expected, rel = raw.split("  ", 1)
        path = ROOT / rel
        if not path.is_file():
            raise RuntimeError(f"manifest path missing: {rel}")
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"manifest mismatch: {rel}: {actual}")
        count += 1
    return count


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def load_audit_module():
    path = ROOT / "audit" / "run_rate_dual_numerical_audit.py"
    spec = importlib.util.spec_from_file_location("rate_dual_numerical_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load numerical audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    manifest_count = check_manifest()
    print(f"MANIFEST_PASS count={manifest_count}")

    run(["sha256sum", "-c", "audit/input_hashes.sha256"])

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(ROOT / "host_replay"),
            str(ROOT / "source"),
            str(ROOT / "inputs" / "bass8b2a"),
            str(ROOT / "inputs" / "bass8b2b0"),
            env.get("PYTHONPATH", ""),
        ]
    ).rstrip(os.pathsep)
    env.setdefault("TERM", "xterm")

    run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "source/direction_dependent_rate_dual.py",
            "source/exact_rate_dual_witness.py",
            "audit/run_rate_dual_numerical_audit.py",
            "tests/test_direction_dependent_rate_dual.py",
            "host_replay/pure_python_e2_loader.py",
            "host_replay/test_exact_e2_rate_parity.py",
            "tests/test_pure_python_e2_loader.py",
        ],
        env=env,
    )
    run([sys.executable, "-m", "pytest", "tests", "-q"], env=env)

    optional = {"jax", "jaxlib", "equinox", "diffrax"}
    for relative in (
        "source/direction_dependent_rate_dual.py",
        "host_replay/pure_python_e2_loader.py",
        "host_replay/test_exact_e2_rate_parity.py",
        "tests/test_direction_dependent_rate_dual.py",
        "tests/test_pure_python_e2_loader.py",
    ):
        tree = ast.parse((ROOT / relative).read_text(), filename=relative)
        for node in ast.walk(tree):
            roots = []
            if isinstance(node, ast.Import):
                roots = [alias.name.partition(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots = [node.module.partition(".")[0]]
            if optional.intersection(roots):
                raise RuntimeError(f"optional JAX stack import in pure-Python target: {relative}")
    shell = (ROOT / "host_replay" / "run_exact_e2_host_parity.sh").read_text()
    if "pip install jax" in shell or "'jax'," in shell or '"jax",' in shell:
        raise RuntimeError("host parity shell still treats JAX as a dependency")
    print("PURE_PYTHON_FRONTEND_POLICY_PASS")

    sys.path[:0] = [
        str(ROOT / "source"),
        str(ROOT / "inputs" / "bass8b2a"),
        str(ROOT / "inputs" / "bass8b2b0"),
    ]
    from exact_rate_dual_witness import exact_witness

    exact = exact_witness()
    if exact.get("status") != "PASS_EXACT_RATE_DUAL_WITNESS":
        raise RuntimeError("exact SymPy witness did not pass")
    print("EXACT_SYMPY_PASS")

    wolfram = json.loads(
        (ROOT / "audit" / "exact_rate_dual_wolfram_receipt.json").read_text()
    )
    wl_source = ROOT / "source" / "exact_rate_dual_witness.wl"
    if wolfram.get("source_sha256") != sha256(wl_source):
        raise RuntimeError("Wolfram receipt/source mismatch")
    if wolfram.get("status") != "PASS_EXACT_RATE_DUAL_WOLFRAM_WITNESS":
        raise RuntimeError("Wolfram receipt not PASS")
    print("EXACT_WOLFRAM_RECEIPT_PASS")

    module = load_audit_module()
    randomized = module.randomized_sweep()
    if randomized["random_cases"] != 500:
        raise RuntimeError("randomized audit case count changed")
    thresholds = {
        "node_unit_residual": 1.0e-12,
        "doppler_rest_formula_residual": 1.0e-12,
        "rate_formula_residual": 1.0e-12,
        "rate_log_derivative_residual": 1.0e-12,
        "left_null_relative_residual": 1.0e-12,
        "projector_global_scalar_residual": 1.0e-15,
        "so3_generator_residual": 1.0e-11,
        "so3_rate_jet_residual": 1.0e-11,
    }
    for key, limit in thresholds.items():
        if float(randomized[key]) > limit:
            raise RuntimeError(f"randomized audit threshold failed: {key}")
    if randomized["mutation_detected_omit_gamma"] != randomized["mutation_eligible_omit_gamma"]:
        raise RuntimeError("omit-gamma mutation escaped an eligible case")
    for key in (
        "mutation_detected_omit_direction_factor",
        "mutation_detected_double_doppler",
        "mutation_detected_unchanged_left",
    ):
        if randomized[key] != 500:
            raise RuntimeError(f"mutation audit incomplete: {key}")
    print("RANDOMIZED_AUDIT_PASS cases=500")

    frozen_audit = json.loads((ROOT / "audit" / "rate_dual_numerical_audit.json").read_text())
    if frozen_audit.get("status") != "PASS_RATE_DUAL_NUMERICAL_AUDIT":
        raise RuntimeError("frozen numerical audit receipt not PASS")
    for name in (
        "rate_dual_fd_convergence.png",
        "rate_dual_mutation_defects.png",
        "global_scalar_projector_cancellation.png",
        "rate_dual_so3_covariance.png",
    ):
        if not (ROOT / "figures" / name).is_file():
            raise RuntimeError(f"missing figure: {name}")
    print("PLOT_EVIDENCE_PRESENT count=4")

    decision = json.loads((ROOT / "DECISION.json").read_text())
    status = decision["status"]
    if status["BASS-8B.2B.1"] != "CANDIDATE_GREEN__PURE_PYTHON_EXACT_E2_HOST_PARITY_REQUIRED":
        raise RuntimeError("claim boundary changed")
    if status["row7"].startswith("PASS") or status["row8"].startswith("PASS"):
        raise RuntimeError("authority row was improperly promoted")
    architecture = decision.get("architecture", {})
    if architecture.get("frontend") != "pure-python-numpy-scipy-sympy-pytest":
        raise RuntimeError("pure-Python frontend architecture not sealed")
    if architecture.get("jax_stack") != "EXCLUDED_FROM_CURRENT_TARGET":
        raise RuntimeError("JAX exclusion policy not sealed")
    print("CLAIM_BOUNDARY_PASS")
    print("BASS8B2B1_PACKAGE_VERIFY_PASS__PURE_PYTHON_EXACT_E2_HOST_PARITY_STILL_REQUIRED")


if __name__ == "__main__":
    main()
