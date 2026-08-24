"""Static and optional-installed proofs for the RF-00 unified install contract.

These tests never create an environment, invoke an installer, build a wheel, or
contact an index.  The coordinator owns the separate fresh-install integration
lane; this file checks that its repository inputs fail closed and agree exactly.
"""
from __future__ import annotations

from importlib import machinery, metadata
from pathlib import Path
import re
import tomllib

import pytest


ROOT = Path(__file__).resolve().parents[1]
ROOT_PROJECT = "bianchi-solver"
NATIVE_PROJECT = "bianchi-rustcore"
RF00_R3_WHEEL_SHA256 = (
    "e050974a78e5e02dc5ce8b77aa1dff5bf2bd62d2f52cb2cdcccf8b49d57f3917"
)


def _toml(relative_path: str):
    with (ROOT / relative_path).open("rb") as stream:
        return tomllib.load(stream)


def _normalized_command_text(relative_path: str) -> str:
    text = (ROOT / relative_path).read_text(encoding="utf-8")
    without_continuations = re.sub(r"\\\s*\n\s*", " ", text)
    return re.sub(r"\s+", " ", without_continuations)


def test_root_requires_exact_matching_native_distribution():
    build_system = _toml("pyproject.toml")["build-system"]
    root = _toml("pyproject.toml")["project"]
    native = _toml("_rustcore/pyproject.toml")["project"]
    cargo = _toml("_rustcore/Cargo.toml")["package"]

    assert root["name"] == ROOT_PROJECT
    assert build_system == {
        "requires": ["setuptools==68.1.2", "wheel==0.42.0"],
        "build-backend": "setuptools.build_meta",
    }
    setuptools = _toml("pyproject.toml")["tool"]["setuptools"]
    assert setuptools["packages"]["find"]["include"] == ["bianchi*", "audit*"]
    assert setuptools["package-data"] == {
        "bianchi.matter": ["gaunt_tables.npz"],
        "bianchi.generated": ["riemann_frame.pkl"],
    }
    assert native["name"] == NATIVE_PROJECT
    assert root["version"] == native["version"] == cargo["version"]
    exact_native = f"{NATIVE_PROJECT}=={root['version']}"
    assert root["dependencies"].count(exact_native) == 1
    assert not any(
        dependency.startswith(NATIVE_PROJECT) and dependency != exact_native
        for dependency in root["dependencies"]
    )


def test_install_documentation_uses_one_root_resolver_and_verified_wheel():
    readme = _normalized_command_text("README.md")

    assert RF00_R3_WHEEL_SHA256 in readme
    assert "sha256sum --check --strict" in readme
    assert re.search(
        r"python -m pip install --constraint requirements\.lock "
        r'"\$BASS_NATIVE_WHEEL" \.',
        readme,
    )
    assert "Python-only" in readme
    assert "pip install -e ." not in readme


def test_bootstrap_builds_locked_wheel_then_resolves_native_and_root_together():
    bootstrap = _normalized_command_text("bootstrap.sh")

    assert "rustc 1.94.1" in bootstrap
    assert "maturin==1.14.1" in bootstrap
    assert "python -m maturin build --release --locked" in bootstrap
    assert re.search(
        r"python -m pip install --disable-pip-version-check "
        r"--constraint requirements\.lock "
        r'"\$\{NATIVE_WHEELS\[0\]\}" \.',
        bootstrap,
    )
    assert 'metadata.version("bianchi-rustcore")' in bootstrap
    assert "incompatible bianchi-rustcore distribution" in bootstrap


def test_rf00_workflow_exercises_portable_and_native_install_contracts():
    workflow = _normalized_command_text(".github/workflows/rf00-backend-policy.yml")

    for pinned in (
        'PYTHON_VERSION: "3.12"',
        'RUST_TOOLCHAIN: "1.94.1"',
        'MATURIN_VERSION: "1.14.1"',
    ):
        assert pinned in workflow
    assert "Portable policy (extension absent/injected)" in workflow
    assert "Native wheel and supported-route policy" in workflow
    assert "cargo fetch --manifest-path _rustcore/Cargo.toml --locked" in workflow
    assert "maturin build --release --locked --offline" in workflow
    assert re.search(
        r"python -m pip install --constraint requirements\.lock "
        r'"\$\{native_wheels\[0\]\}" \.',
        workflow,
    )
    assert "tests/test_backend_policy.py" in workflow
    assert "tests/test_backend_packaging.py" in workflow


def test_optional_active_install_matches_root_and_native_metadata():
    """A coordinator-installed environment is checked, but absence stays portable."""

    try:
        root_distribution = metadata.distribution(ROOT_PROJECT)
    except metadata.PackageNotFoundError:
        pytest.skip("root distribution is not installed; fresh-install lane owns this proof")

    root_project = _toml("pyproject.toml")["project"]
    assert root_distribution.version == root_project["version"]
    requirements = root_distribution.requires or []
    assert any(
        requirement.replace(" ", "").startswith(
            f"{NATIVE_PROJECT}=={root_project['version']}"
        )
        for requirement in requirements
    )

    native_distribution = metadata.distribution(NATIVE_PROJECT)
    assert native_distribution.version == root_project["version"]
    from bianchi import backend_policy

    load = backend_policy.load_native()
    assert load.available and load.module is not None
    native_origin = backend_policy._native_extension_origin(load.module)
    assert native_origin is not None
    assert any(native_origin.endswith(suffix) for suffix in machinery.EXTENSION_SUFFIXES)
