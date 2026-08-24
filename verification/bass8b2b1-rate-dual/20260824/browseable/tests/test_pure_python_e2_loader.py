from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest

from pure_python_e2_loader import load_exact_e2_owner


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _fake_owner_tree(tmp_path: Path) -> Path:
    root = tmp_path / "owner"
    _write(root / "bianchi" / "__init__.py", "raise RuntimeError('ROOT_INIT_EXECUTED')\n")
    _write(root / "bianchi" / "q" / "__init__.py", "raise RuntimeError('Q_INIT_EXECUTED')\n")
    _write(root / "bianchi" / "thermo" / "__init__.py", "raise RuntimeError('THERMO_INIT_EXECUTED')\n")
    _write(
        root / "bianchi" / "q" / "polarization.py",
        "import numpy as np\n"
        "def screen_proj(e):\n"
        "    e=np.asarray(e,float); return np.eye(3)[None]-np.einsum('ai,aj->aij',e,e)\n",
    )
    _write(
        root / "bianchi" / "q" / "polstate.py",
        "from bianchi.q.coupled import mat3\n"
        "def boost_shape(shape, beta, direction):\n"
        "    mat3([[1,0,0],[0,1,0],[0,0,1]])\n"
        "    return shape, direction, 1.0\n",
    )
    _write(
        root / "bianchi" / "q" / "boost.py",
        "import numpy as np\n"
        "from bianchi.q.comoving import collide_log\n"
        "def doppler(e, beta):\n"
        "    e=np.asarray(e,float); return np.ones(len(e)), e.copy()\n",
    )
    _write(
        root / "bianchi" / "q" / "electron.py",
        "from bianchi.q.boost import doppler\n"
        "from bianchi.q.polstate import boost_shape\n"
        "C_LIGHT_M_S=299792458.0\n"
        "class ColdElectronTestField:\n"
        "    pass\n",
    )
    _write(
        root / "bianchi" / "q" / "electron_rate.py",
        "from bianchi.thermo.history_api import SIGMA_T_CM2, C_CM_S\n"
        "from bianchi.q.electron import C_LIGHT_M_S\n"
        "SIGMA_T_M2=SIGMA_T_CM2*1e-4\n"
        "class ElectronCollisionContext:\n"
        "    pass\n",
    )
    return root


def _purge_bianchi() -> None:
    for key in list(sys.modules):
        if key == "bianchi" or key.startswith("bianchi."):
            sys.modules.pop(key, None)


def test_loader_bypasses_package_initializers_and_optional_stack(tmp_path):
    _purge_bianchi()
    root = _fake_owner_tree(tmp_path)
    before = set(sys.modules)
    electron, rate, receipt = load_exact_e2_owner(root)
    assert electron.C_LIGHT_M_S == 299_792_458.0
    assert rate.SIGMA_T_M2 == pytest.approx(6.6524587e-29, rel=0.0, abs=0.0)
    assert receipt["loader"] == "pure-python-isolated-e2-owner/v1"
    assert receipt["package_initializers_executed"] is False
    assert receipt["optional_stack_imported"] is False
    assert not any(
        name in set(sys.modules) - before
        for name in ("jax", "jaxlib", "equinox", "diffrax")
    )


def test_loader_fails_closed_when_required_owner_file_is_missing(tmp_path):
    _purge_bianchi()
    root = _fake_owner_tree(tmp_path)
    (root / "bianchi" / "q" / "electron_rate.py").unlink()
    with pytest.raises(FileNotFoundError, match="electron_rate.py"):
        load_exact_e2_owner(root)


def test_loader_rejects_contaminated_bianchi_import_state(tmp_path):
    _purge_bianchi()
    root = _fake_owner_tree(tmp_path)
    sys.modules["bianchi"] = object()  # type: ignore[assignment]
    try:
        with pytest.raises(RuntimeError, match="already imported"):
            load_exact_e2_owner(root)
    finally:
        _purge_bianchi()
