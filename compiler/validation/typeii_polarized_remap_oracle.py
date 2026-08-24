#!/usr/bin/env python3
"""Independent SciPy oracle and deterministic fixture generator for B2 remap."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
JSON_OUT = ROOT / "compiler/validation/typeii_polarized_remap_oracle.json"
RUST_OUT = ROOT / "runtime/rust/typeii/tests/support/typeii_polarized_remap_fixture.rs"


def unit(x: np.ndarray) -> np.ndarray:
    """Normalize a 3-vector with a fixed binary64 reduction order.

    ``np.linalg.norm`` delegates the three-term reduction to the active NumPy/
    BLAS build.  Different conforming builds changed the last bit of the B2A
    fixture.  Keep the original right-associated scalar evaluation explicit so
    the committed JSON and Rust fixture remain byte-reproducible.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.shape != (3,):
        raise ValueError(f"expected a 3-vector, got shape {x.shape}")
    x0, x1, x2 = map(float, x)
    norm = math.sqrt(x0 * x0 + (x1 * x1 + x2 * x2))
    if norm == 0.0:
        raise ValueError("cannot normalize the zero vector")
    return x / norm


def pack(m: np.ndarray) -> np.ndarray:
    return np.array(
        [
            m[0, 0],
            m[1, 1],
            m[2, 2],
            0.5 * (m[0, 1] + m[1, 0]),
            0.5 * (m[0, 2] + m[2, 0]),
            0.5 * (m[1, 2] + m[2, 1]),
            0.5 * (m[1, 2] - m[2, 1]),
            0.5 * (m[2, 0] - m[0, 2]),
            0.5 * (m[0, 1] - m[1, 0]),
        ],
        dtype=np.float64,
    )


def unpack(p: np.ndarray) -> np.ndarray:
    return np.array(
        [
            [p[0], p[3] + p[8], p[4] - p[7]],
            [p[3] - p[8], p[1], p[5] + p[6]],
            [p[4] + p[7], p[5] - p[6], p[2]],
        ],
        dtype=np.float64,
    )


def canonical_dyad(e: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    refs = np.eye(3)
    ref = refs[np.argmin(np.abs(refs @ e))]
    s1 = unit(ref - np.dot(ref, e) * e)
    s2 = unit(np.cross(e, s1))
    return s1, s2


def stokes_tensor(e: np.ndarray, psi: float, stokes: np.ndarray) -> np.ndarray:
    s1, s2 = canonical_dyad(e)
    c, s = np.cos(psi), np.sin(psi)
    t1 = c * s1 + s * s2
    t2 = -s * s1 + c * s2
    i, q, u, v = stokes
    h11, h22 = 0.5 * (i + q), 0.5 * (i - q)
    # Remote PR #13 authority: p8=-V/2.
    h12, h21 = 0.5 * (u - v), 0.5 * (u + v)
    return (
        h11 * np.outer(t1, t1)
        + h22 * np.outer(t2, t2)
        + h12 * np.outer(t1, t2)
        + h21 * np.outer(t2, t1)
    )


def shortest_rotation(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    c = float(np.clip(np.dot(a, b), -1.0, 1.0))
    axis = np.cross(a, b)
    s = float(np.linalg.norm(axis))
    if c < -1.0 + 1.0e-12:
        raise ValueError("antipodal")
    if s < 1.0e-15:
        return np.eye(3)
    axis /= s
    angle = np.arctan2(s, c)
    return Rotation.from_rotvec(axis * angle).as_matrix()


def project(m: np.ndarray, e: np.ndarray) -> np.ndarray:
    p = np.eye(3) - np.outer(e, e)
    return p @ m @ p


def build_fixture() -> dict[str, object]:
    target = unit(np.array([0.23, -0.31, 0.922], dtype=np.float64))
    dirs = np.array(
        [
            unit(np.array([0.41, -0.18, 0.894])),
            unit(np.array([-0.08, -0.48, 0.874])),
            unit(np.array([0.12, -0.04, 0.992])),
        ]
    )
    weights = np.array([0.17, 0.29, 0.54], dtype=np.float64)

    # Deliberately non-constant source states exercise transport plus interpolation.
    source_stokes = [
        np.array([2.0, 0.52, -0.21, 0.14]),
        np.array([1.5, -0.18, 0.43, -0.09]),
        np.array([2.3, 0.31, 0.17, 0.07]),
    ]
    gauges = [0.21, -0.37, 0.49]
    states = [stokes_tensor(d, g, s) for d, g, s in zip(dirs, gauges, source_stokes)]

    transported = []
    dots = []
    for d, m in zip(dirs, states):
        r = shortest_rotation(d, target)
        transported.append(project(r @ m @ r.T, target))
        dots.append(float(np.dot(d, target)))
    expected = project(sum(w * m for w, m in zip(weights, transported)), target)

    # An independent round-trip witness.
    a = unit(np.array([0.3, -0.4, 0.8]))
    b = unit(np.array([-0.2, 0.7, 0.5]))
    state_a = stokes_tensor(a, 0.31, np.array([2.0, 0.5, -0.3, 0.2]))
    rab = shortest_rotation(a, b)
    rba = shortest_rotation(b, a)
    roundtrip = rba @ (rab @ state_a @ rab.T) @ rba.T

    return {
        "schema": "bass-g-pol-liouville-iib2-oracle-v1",
        "target": target.tolist(),
        "source_directions": dirs.tolist(),
        "weights": weights.tolist(),
        "source_states": [pack(m).tolist() for m in states],
        "expected_output": pack(expected).tolist(),
        "expected_minimum_transport_dot": min(dots),
        "roundtrip_max_error": float(np.max(np.abs(roundtrip - state_a))),
        "authority": {
            "rotation": "scipy.spatial.transform.Rotation.from_rotvec",
            "path": "unique shortest great-circle; antipodes excluded",
            "packed_v_sign": "PR13 p8=-V/2",
        },
    }


def rust_array(xs: list[float]) -> str:
    return "[" + ", ".join(format(float(x), ".17g") for x in xs) + "]"


def write_outputs(data: dict[str, object]) -> None:
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    RUST_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    dirs = data["source_directions"]
    states = data["source_states"]
    lines = [
        "// Generated by compiler/validation/typeii_polarized_remap_oracle.py",
        "// Independent SciPy shortest-geodesic rotation fixture.",
        f"pub const TARGET: [f64; 3] = {rust_array(data['target'])};",
        "pub const SOURCE_DIRECTIONS: [[f64; 3]; 3] = [",
    ]
    lines.extend(f"    {rust_array(row)}," for row in dirs)
    lines.append("];")
    lines.append(f"pub const WEIGHTS: [f64; 3] = {rust_array(data['weights'])};")
    lines.append("pub const SOURCE_STATES: [[f64; 9]; 3] = [")
    lines.extend(f"    {rust_array(row)}," for row in states)
    lines.append("];")
    lines.append(f"pub const EXPECTED_OUTPUT: [f64; 9] = {rust_array(data['expected_output'])};")
    lines.append(
        "pub const EXPECTED_MINIMUM_TRANSPORT_DOT: f64 = "
        + format(float(data["expected_minimum_transport_dot"]), ".17g")
        + ";"
    )
    RUST_OUT.write_text("\n".join(lines) + "\n")
    rustfmt = os.environ.get("RUSTFMT") or shutil.which("rustfmt")
    if rustfmt is None:
        raise RuntimeError("pinned rustfmt must be available to canonicalize the Rust fixture")
    subprocess.run([rustfmt, "--edition", "2021", str(RUST_OUT)], check=True)


def main() -> int:
    data = build_fixture()
    write_outputs(data)
    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
