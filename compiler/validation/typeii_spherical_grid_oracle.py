#!/usr/bin/env python3
"""Independent SciPy/Qhull oracle for G-POL-LIOUVILLE-II-B2B.

The runtime Rust mesh is not imported.  Vertex refinement is reconstructed in
NumPy and the spherical triangulation is independently recovered as the 3-D
convex hull using SciPy/Qhull.  Radial barycentric coordinates and a solid-body
rotation semi-Lagrangian witness are then evaluated from that hull.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.spatial import ConvexHull

HERE = Path(__file__).resolve().parent
JSON_OUT = HERE / "typeii_spherical_grid_oracle.json"
RUST_OUT = (
    HERE.parent.parent
    / "runtime"
    / "rust"
    / "typeii"
    / "tests"
    / "support"
    / "typeii_spherical_grid_fixture.rs"
)


def unit(v: Iterable[float]) -> np.ndarray:
    a = np.asarray(v, dtype=np.float64)
    n = np.linalg.norm(a)
    if not np.isfinite(n) or n <= 0:
        raise ValueError("invalid vector")
    return a / n


def base_vertices_faces() -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    vertices = np.array(
        [
            [-1, phi, 0],
            [1, phi, 0],
            [-1, -phi, 0],
            [1, -phi, 0],
            [0, -1, phi],
            [0, 1, phi],
            [0, -1, -phi],
            [0, 1, -phi],
            [phi, 0, -1],
            [phi, 0, 1],
            [-phi, 0, -1],
            [-phi, 0, 1],
        ],
        dtype=np.float64,
    )
    vertices /= np.linalg.norm(vertices, axis=1)[:, None]
    faces = [
        (0, 11, 5),
        (0, 5, 1),
        (0, 1, 7),
        (0, 7, 10),
        (0, 10, 11),
        (1, 5, 9),
        (5, 11, 4),
        (11, 10, 2),
        (10, 7, 6),
        (7, 1, 8),
        (3, 9, 4),
        (3, 4, 2),
        (3, 2, 6),
        (3, 6, 8),
        (3, 8, 9),
        (4, 9, 5),
        (2, 4, 11),
        (6, 2, 10),
        (8, 6, 7),
        (9, 8, 1),
    ]
    return vertices, faces


def refine_vertices(level: int) -> np.ndarray:
    vertices, faces = base_vertices_faces()
    verts = [v.copy() for v in vertices]
    for _ in range(level):
        cache: dict[tuple[int, int], int] = {}
        new_faces: list[tuple[int, int, int]] = []

        def midpoint(a: int, b: int) -> int:
            edge = tuple(sorted((a, b)))
            if edge not in cache:
                cache[edge] = len(verts)
                verts.append(unit(verts[a] + verts[b]))
            return cache[edge]

        for a, b, c in faces:
            ab, bc, ca = midpoint(a, b), midpoint(b, c), midpoint(c, a)
            new_faces.extend(((a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)))
        faces = new_faces
    return np.asarray(verts, dtype=np.float64)


def hull_face_keys(vertices: np.ndarray) -> list[tuple[int, int, int]]:
    hull = ConvexHull(vertices, qhull_options="Qt")
    return sorted(tuple(sorted(map(int, face))) for face in hull.simplices)


def radial_barycentric(
    vertices: np.ndarray, face_key: tuple[int, int, int], direction: np.ndarray
) -> tuple[np.ndarray, float, float]:
    ids = np.asarray(face_key, dtype=int)
    columns = vertices[ids].T
    y = np.linalg.solve(columns, direction)
    s = float(y.sum())
    if not np.isfinite(s) or s <= 0:
        raise ValueError("back-facing face")
    weights = y / s
    lam = 1.0 / s
    defect = float(np.max(np.abs(columns @ weights - lam * direction)))
    return weights, lam, defect


def locate(
    vertices: np.ndarray,
    faces: list[tuple[int, int, int]],
    direction: np.ndarray,
    tol: float = 2e-12,
) -> tuple[tuple[int, int, int], np.ndarray, float, int]:
    direction = unit(direction)
    candidates = []
    for key in faces:
        try:
            weights, lam, defect = radial_barycentric(vertices, key, direction)
        except (ValueError, np.linalg.LinAlgError):
            continue
        if lam > 0 and lam <= 1 + tol and np.min(weights) >= -tol and np.max(weights) <= 1 + tol:
            clipped = np.maximum(weights, 0.0)
            clipped /= clipped.sum()
            candidates.append((key, clipped, lam, defect))
    if not candidates:
        raise ValueError("direction not covered")
    candidates.sort(key=lambda item: item[0])
    key, weights, lam, _ = candidates[0]
    return key, weights, lam, len(candidates)


def rz(angle: float, direction: np.ndarray) -> np.ndarray:
    s, c = math.sin(angle), math.cos(angle)
    x, y, z = direction
    return np.array([c * x - s * y, s * x + c * y, z])


def intensity(e: np.ndarray) -> float:
    return float(1.2 + 0.25 * e[0] - 0.17 * e[1] + 0.11 * e[2])


def unpolarized_packed(e: np.ndarray, value: float) -> np.ndarray:
    p = np.eye(3) - np.outer(e, e)
    m = 0.5 * value * p
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


def sample_directions() -> list[np.ndarray]:
    return [
        unit([0.31, -0.27, 0.91]),
        unit([-0.62, 0.18, 0.76]),
        unit([0.12, 0.82, -0.56]),
        unit([-0.44, -0.71, -0.55]),
        unit([0.73, 0.52, 0.44]),
        unit([-0.21, 0.37, -0.905]),
    ]


def build_receipt() -> dict:
    levels = {}
    for level in (0, 1, 2):
        vertices = refine_vertices(level)
        faces = hull_face_keys(vertices)
        levels[str(level)] = {
            "vertices": int(len(vertices)),
            "faces": int(len(faces)),
            "expected_vertices": 10 * 4**level + 2,
            "expected_faces": 20 * 4**level,
        }

    vertices1 = refine_vertices(1)
    faces1 = hull_face_keys(vertices1)
    samples = []
    for direction in sample_directions():
        key, weights, lam, candidates = locate(vertices1, faces1, direction)
        samples.append(
            {
                "direction": direction.tolist(),
                "face_key": list(key),
                "weights": weights.tolist(),
                "radial_scale": lam,
                "candidate_faces": candidates,
            }
        )

    level = 2
    omega, dt = 0.61, 0.27
    target = unit([0.33, -0.24, 0.913])
    departure = rz(-omega * dt, target)
    vertices = refine_vertices(level)
    faces = hull_face_keys(vertices)
    key, weights, lam, candidates = locate(vertices, faces, departure)
    interpolated_intensity = float(
        sum(weight * intensity(vertices[index]) for weight, index in zip(weights, key))
    )
    expected = unpolarized_packed(target, interpolated_intensity)
    exact = unpolarized_packed(target, intensity(departure))

    return {
        "schema": "bass-g-pol-liouville-iib2b-oracle-v1",
        "scipy": __import__("scipy").__version__,
        "numpy": np.__version__,
        "levels": levels,
        "level1_face_keys": [list(key) for key in faces1],
        "samples": samples,
        "solid_rotation": {
            "level": level,
            "omega": omega,
            "dt": dt,
            "target": target.tolist(),
            "departure": departure.tolist(),
            "face_key": list(key),
            "weights": weights.tolist(),
            "radial_scale": lam,
            "candidate_faces": candidates,
            "interpolated_intensity": interpolated_intensity,
            "expected_packed": expected.tolist(),
            "exact_packed": exact.tolist(),
            "spatial_error": float(np.max(np.abs(expected - exact))),
        },
    }


def f64(x: float) -> str:
    return format(float(x), ".17e")


def _canonicalize_rust(source: str) -> str:
    rustfmt = os.environ.get("RUSTFMT") or shutil.which("rustfmt")
    if rustfmt is None:
        raise RuntimeError("pinned rustfmt must be available to canonicalize the Rust fixture")
    with tempfile.TemporaryDirectory(prefix="bass-b2b-rustfmt-") as tmp:
        path = Path(tmp) / "fixture.rs"
        path.write_text(source)
        subprocess.run([rustfmt, "--edition", "2021", str(path)], check=True)
        return path.read_text()


def rust_fixture(receipt: dict) -> str:
    lines = [
        "// @generated by compiler/validation/typeii_spherical_grid_oracle.py",
        "pub const LEVEL1_FACE_KEYS: [[usize; 3]; 80] = [",
    ]
    for key in receipt["level1_face_keys"]:
        lines.append(f"    [{key[0]}, {key[1]}, {key[2]}],")
    lines.append("];")
    lines.extend([
        "",
        "pub struct LocatorCase {",
        "    pub direction: [f64; 3],",
        "    pub face_key: [usize; 3],",
        "    pub weights: [f64; 3],",
        "    pub radial_scale: f64,",
        "    pub candidate_faces: usize,",
        "}",
        "pub const LOCATOR_CASES: [LocatorCase; 6] = [",
    ])
    for case in receipt["samples"]:
        d, k, w = case["direction"], case["face_key"], case["weights"]
        lines.extend(
            [
                "    LocatorCase {",
                f"        direction: [{f64(d[0])}, {f64(d[1])}, {f64(d[2])}],",
                f"        face_key: [{k[0]}, {k[1]}, {k[2]}],",
                f"        weights: [{f64(w[0])}, {f64(w[1])}, {f64(w[2])}],",
                f"        radial_scale: {f64(case['radial_scale'])},",
                f"        candidate_faces: {case['candidate_faces']},",
                "    },",
            ]
        )
    sr = receipt["solid_rotation"]
    lines.append("];")
    lines.append("")
    lines.append(f"pub const SOLID_OMEGA: f64 = {f64(sr['omega'])};")
    lines.append(f"pub const SOLID_DT: f64 = {f64(sr['dt'])};")
    lines.append(
        "pub const SOLID_TARGET: [f64; 3] = ["
        + ", ".join(f64(x) for x in sr["target"])
        + "];"
    )
    lines.append(
        "pub const SOLID_DEPARTURE: [f64; 3] = ["
        + ", ".join(f64(x) for x in sr["departure"])
        + "];"
    )
    lines.append(
        "pub const SOLID_EXPECTED_PACKED: [f64; 9] = ["
        + ", ".join(f64(x) for x in sr["expected_packed"])
        + "];"
    )
    lines.append(f"pub const SOLID_SPATIAL_ERROR: f64 = {f64(sr['spatial_error'])};")
    return _canonicalize_rust("\n".join(lines) + "\n")


def write_outputs() -> None:
    receipt = build_receipt()
    JSON_OUT.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    RUST_OUT.parent.mkdir(parents=True, exist_ok=True)
    RUST_OUT.write_text(rust_fixture(receipt))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    if args.write:
        write_outputs()
    else:
        print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
