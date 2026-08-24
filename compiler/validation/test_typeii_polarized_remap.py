from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "remap_oracle", HERE / "typeii_polarized_remap_oracle.py"
)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_fixture_roundtrip_is_machine_precision():
    data = MOD.build_fixture()
    assert data["roundtrip_max_error"] < 2.0e-15


def test_shortest_rotation_maps_directions_and_is_proper():
    data = MOD.build_fixture()
    target = np.array(data["target"])
    for source in data["source_directions"]:
        source = np.array(source)
        r = MOD.shortest_rotation(source, target)
        np.testing.assert_allclose(r @ source, target, atol=8e-16, rtol=0)
        np.testing.assert_allclose(r.T @ r, np.eye(3), atol=8e-16, rtol=0)
        assert abs(np.linalg.det(r) - 1.0) < 1e-15


def test_expected_output_is_physical_on_target_screen():
    data = MOD.build_fixture()
    target = np.array(data["target"])
    m = MOD.unpack(np.array(data["expected_output"]))
    p = np.eye(3) - np.outer(target, target)
    np.testing.assert_allclose(m, p @ m @ p, atol=8e-16, rtol=0)


def test_unpolarized_monopole_is_exact_under_independent_transport():
    target = MOD.unit(np.array([0.2, -0.3, 0.93]))
    sources = [MOD.unit(np.array(x)) for x in ([0.4, 0.1, 0.9], [-0.2, 0.5, 0.84])]
    intensity = 2.4
    expected = 0.5 * intensity * (np.eye(3) - np.outer(target, target))
    for source in sources:
        m = 0.5 * intensity * (np.eye(3) - np.outer(source, source))
        r = MOD.shortest_rotation(source, target)
        np.testing.assert_allclose(r @ m @ r.T, expected, atol=2e-15, rtol=0)


def test_symmetric_l1_stencil_is_second_order():
    target = np.array([0.0, 0.0, 1.0])
    errors = []
    for h in (0.2, 0.1, 0.05, 0.025):
        rp = MOD.Rotation.from_rotvec(np.array([0.0, h, 0.0])).as_matrix()
        rm = MOD.Rotation.from_rotvec(np.array([0.0, -h, 0.0])).as_matrix()
        dirs = (rp @ target, rm @ target)
        avg = 0.5 * sum(1.0 + 0.3 * d[2] for d in dirs)
        errors.append(abs(avg - 1.3))
    ratios = np.array(errors[:-1]) / np.array(errors[1:])
    assert np.all((ratios > 3.85) & (ratios < 4.15))


def test_componentwise_qu_interpolation_is_gauge_dependent_negative_control():
    e = np.array([0.0, 0.0, 1.0])
    tensor = MOD.stokes_tensor(e, 0.0, np.array([2.0, 0.8, 0.35, 0.0]))
    # Same tensor, two unrelated basis gauges. Q+iU acquires opposite phase shifts.
    def local_qu(psi: float) -> complex:
        s1, s2 = MOD.canonical_dyad(e)
        c, s = np.cos(psi), np.sin(psi)
        a = c * s1 + s * s2
        b = -s * s1 + c * s2
        h11, h22 = a @ tensor @ a, b @ tensor @ b
        h12, h21 = a @ tensor @ b, b @ tensor @ a
        return complex(h11 - h22, h12 + h21)

    naive = 0.5 * (local_qu(0.63) + local_qu(-0.48))
    correct = complex(0.8, 0.35)
    assert abs(naive - correct) > 0.2


def test_shortest_rotation_matches_embedded_sphere_parallel_transport_ode():
    from scipy.integrate import solve_ivp

    a = MOD.unit(np.array([0.31, -0.27, 0.91]))
    b = MOD.unit(np.array([-0.22, 0.51, 0.83]))
    r = MOD.shortest_rotation(a, b)
    axis = MOD.unit(np.cross(a, b))
    theta = np.arctan2(np.linalg.norm(np.cross(a, b)), np.dot(a, b))
    v0 = MOD.unit(np.cross(a, np.array([0.4, 0.7, -0.2])))

    def rhs(tau: float, v: np.ndarray) -> np.ndarray:
        rt = MOD.Rotation.from_rotvec(axis * (theta * tau)).as_matrix()
        e = rt @ a
        e_dot = theta * np.cross(axis, e)
        # Embedded unit-sphere Levi-Civita equation: P(e) v_dot = 0.
        return -np.dot(v, e_dot) * e

    sol = solve_ivp(rhs, (0.0, 1.0), v0, rtol=2e-12, atol=2e-14, method="DOP853")
    assert sol.success
    np.testing.assert_allclose(sol.y[:, -1], r @ v0, atol=3e-12, rtol=0)
    assert abs(np.dot(sol.y[:, -1], b)) < 3e-12


def test_generator_reproduces_committed_outputs_byte_identically(tmp_path):
    import os
    import shutil
    import subprocess
    import sys

    json_path = HERE / "typeii_polarized_remap_oracle.json"
    rust_path = HERE.parents[1] / "runtime/rust/typeii/tests/support/typeii_polarized_remap_fixture.rs"
    before_json = json_path.read_bytes()
    before_rust = rust_path.read_bytes()
    env = os.environ.copy()
    rustfmt = shutil.which("rustfmt")
    assert rustfmt is not None, "pinned rustfmt must be on PATH"
    env["RUSTFMT"] = rustfmt
    try:
        subprocess.run(
            [sys.executable, str(HERE / "typeii_polarized_remap_oracle.py")],
            check=True,
            stdout=subprocess.DEVNULL,
            env=env,
        )
        assert json_path.read_bytes() == before_json
        assert rust_path.read_bytes() == before_rust
    finally:
        json_path.write_bytes(before_json)
        rust_path.write_bytes(before_rust)
