"""Load the frozen E2 electron/rate authority without the legacy JAX package root.

This is a verification-only import seam.  It executes the exact frozen E2 owner
files while replacing only optional, out-of-scope package dependencies with the
same narrow stubs used by the E2 authority's own focused regression test.

The loader deliberately does not execute ``bianchi/__init__.py`` or
``bianchi/q/__init__.py``.  Those legacy initializers force JAX globally, which
is outside the current BASS target architecture (pure-Python frontend + Rust
backend) and is irrelevant to the bounded E2 collision-rate authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.abc
import importlib.util
from pathlib import Path
import sys
import types
from typing import Iterable

import numpy as np

_OPTIONAL_STACK = frozenset({"jax", "jaxlib", "equinox", "diffrax"})


class _RejectOptionalStack(importlib.abc.MetaPathFinder):
    """Fail if the bounded pure-Python owner slice attempts optional imports."""

    def find_spec(self, fullname: str, path=None, target=None):  # noqa: D401
        root = fullname.partition(".")[0]
        if root in _OPTIONAL_STACK:
            raise ModuleNotFoundError(
                f"optional stack import forbidden in pure-Python E2 parity: {fullname}",
                name=root,
            )
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _package(name: str, path: Path) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__package__ = name
    module.__path__ = [str(path)]
    spec = importlib.util.spec_from_loader(name, loader=None, is_package=True)
    if spec is not None:
        spec.submodule_search_locations = [str(path)]
    module.__spec__ = spec
    module.__bass_pure_python_namespace__ = True
    return module


def _load(name: str, path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot create import spec for {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _require_files(module_root: Path, relatives: Iterable[str]) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for relative in relatives:
        path = module_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"required frozen E2 owner file missing: {path}")
        found[relative] = path
    return found


def _purge_bianchi_modules() -> None:
    for key in list(sys.modules):
        if key == "bianchi" or key.startswith("bianchi."):
            sys.modules.pop(key, None)


def load_exact_e2_owner(module_root: str | Path):
    """Return exact frozen ``electron`` and ``electron_rate`` modules.

    Parameters
    ----------
    module_root:
        Repository root whose package lives at ``module_root/bianchi``.

    Returns
    -------
    ``(electron_module, electron_rate_module, receipt)``.

    The process must not already contain a ``bianchi`` import.  This fail-closed
    rule prevents a JAX-backed or otherwise contaminated package instance from
    being mistaken for the isolated pure-Python authority slice.
    """

    root = Path(module_root).resolve()
    package_root = root / "bianchi"
    q_root = package_root / "q"
    thermo_root = package_root / "thermo"

    required = _require_files(
        root,
        (
            "bianchi/q/polarization.py",
            "bianchi/q/polstate.py",
            "bianchi/q/boost.py",
            "bianchi/q/electron.py",
            "bianchi/q/electron_rate.py",
        ),
    )

    contaminated = [
        key for key in sys.modules if key == "bianchi" or key.startswith("bianchi.")
    ]
    if contaminated:
        raise RuntimeError(
            "bianchi is already imported; start a fresh parity process before "
            "loading the isolated pure-Python E2 owner"
        )

    before_optional = {name for name in sys.modules if name.partition(".")[0] in _OPTIONAL_STACK}
    blocker = _RejectOptionalStack()
    sys.meta_path.insert(0, blocker)
    try:
        bianchi_pkg = _package("bianchi", package_root)
        q_pkg = _package("bianchi.q", q_root)
        thermo_pkg = _package("bianchi.thermo", thermo_root)
        sys.modules.update(
            {
                "bianchi": bianchi_pkg,
                "bianchi.q": q_pkg,
                "bianchi.thermo": thermo_pkg,
            }
        )

        # Exact constants consumed by electron_rate.py.  This matches the
        # frozen E2 test's own focused no-optional-stack loader and avoids
        # importing unrelated recombination/background modules.
        history = types.ModuleType("bianchi.thermo.history_api")
        history.SIGMA_T_CM2 = 6.6524587e-25
        history.C_CM_S = 2.99792458e10
        sys.modules["bianchi.thermo.history_api"] = history
        thermo_pkg.history_api = history

        # electron.py imports boost/polstate, whose unrelated full collision
        # paths reach broader package modules.  The exact E2 rate slice only
        # needs the declared symbols below; any attempted use fails loudly.
        comoving = types.ModuleType("bianchi.q.comoving")

        def _collision_out_of_scope(*args, **kwargs):
            raise RuntimeError("collision kernel is outside the bounded E2 rate parity gate")

        comoving.collide_log = _collision_out_of_scope
        coupled = types.ModuleType("bianchi.q.coupled")
        coupled.mat3 = lambda value: np.asarray(value, float).reshape(3, 3)
        sys.modules["bianchi.q.comoving"] = comoving
        sys.modules["bianchi.q.coupled"] = coupled
        q_pkg.comoving = comoving
        q_pkg.coupled = coupled

        q_pkg.polarization = _load(
            "bianchi.q.polarization", required["bianchi/q/polarization.py"]
        )
        q_pkg.polstate = _load("bianchi.q.polstate", required["bianchi/q/polstate.py"])
        q_pkg.boost = _load("bianchi.q.boost", required["bianchi/q/boost.py"])
        q_pkg.electron = _load("bianchi.q.electron", required["bianchi/q/electron.py"])
        q_pkg.electron_rate = _load(
            "bianchi.q.electron_rate", required["bianchi/q/electron_rate.py"]
        )
    except Exception:
        _purge_bianchi_modules()
        raise
    finally:
        try:
            sys.meta_path.remove(blocker)
        except ValueError:  # pragma: no cover - defensive only
            pass

    after_optional = {name for name in sys.modules if name.partition(".")[0] in _OPTIONAL_STACK}
    newly_imported_optional = sorted(after_optional - before_optional)
    if newly_imported_optional:
        _purge_bianchi_modules()
        raise RuntimeError(
            "optional stack entered isolated E2 parity: " + ", ".join(newly_imported_optional)
        )

    receipt = {
        "loader": "pure-python-isolated-e2-owner/v1",
        "module_root": str(root),
        "package_initializers_executed": False,
        "optional_stack_imported": False,
        "optional_stack_policy": "forbid-jax-jaxlib-equinox-diffrax",
        "owner_sha256": {
            "electron.py": _sha256(required["bianchi/q/electron.py"]),
            "electron_rate.py": _sha256(required["bianchi/q/electron_rate.py"]),
        },
        "stub_scope": [
            "bianchi.thermo.history_api constants only",
            "bianchi.q.comoving.collide_log fail-closed",
            "bianchi.q.coupled.mat3 exact reshape helper",
        ],
    }
    return q_pkg.electron, q_pkg.electron_rate, receipt
