"""Independent coordinate Bianchi-II oracle for G-POL-LIOUVILLE-IIA.

The code integrates a coordinate null geodesic and two coordinate four-vectors
by the metric Christoffel symbols.  It does not import the Rust implementation
or the closed tetrad transport formula.  A second, separately written tetrad
ODE is compared only after the coordinate result has been constructed.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

EXPONENTS = np.array([0.4, 0.7, 0.25], dtype=float)
N1 = 1.0
T0 = 1.0
T1 = 1.25
E0 = np.array(
    [0.4514616300345193, -0.39320851648167815, 0.8009803113515666],
    dtype=float,
)

RUST_GOLDEN_TOLERANCES = {
    "direction_max_abs": 3.0e-10,
    "log_energy_abs": 5.0e-11,
    "spatial_transport_max_abs": 3.0e-10,
}


def observer_energy_factor(
    propagation_direction: np.ndarray, observer_velocity: np.ndarray
) -> float:
    """Return E_observer/E for future-directed p=E(1,e), signature (-,+,+,+).

    This fixes `e` as the photon propagation direction and `observer_velocity`
    as the observer's tetrad three-velocity.  It deliberately makes no sky-line-
    of-sight or Stokes Q/U convention.
    """
    e = np.asarray(propagation_direction, dtype=float)
    velocity = np.asarray(observer_velocity, dtype=float)
    if e.shape != (3,) or velocity.shape != (3,):
        raise ValueError("propagation direction and observer velocity must have shape (3,)")
    norm = float(np.linalg.norm(e))
    speed_squared = float(velocity @ velocity)
    if not np.isfinite(norm) or abs(norm - 1.0) > 2.0e-13:
        raise ValueError("propagation direction must be a finite unit vector")
    if not np.isfinite(speed_squared) or not 0.0 <= speed_squared < 1.0:
        raise ValueError("observer velocity must be finite and subluminal")
    gamma = 1.0 / np.sqrt(1.0 - speed_squared)
    return float(gamma * (1.0 - velocity @ e))


def scale_factors(t: float) -> np.ndarray:
    return t**EXPONENTS


def metric_and_derivatives(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Metric and `partial_mu g_ab` for omega1=dx-N1*y*dz."""
    t, y = float(x[0]), float(x[2])
    a = scale_factors(t)
    da = EXPONENTS * t ** (EXPONENTS - 1.0)
    g = np.zeros((4, 4), dtype=float)
    g[0, 0] = -1.0
    g[1, 1] = a[0] ** 2
    g[2, 2] = a[1] ** 2
    g[3, 3] = a[2] ** 2 + a[0] ** 2 * (N1 * y) ** 2
    g[1, 3] = g[3, 1] = -a[0] ** 2 * N1 * y

    dg = np.zeros((4, 4, 4), dtype=float)
    dg[0, 1, 1] = 2.0 * a[0] * da[0]
    dg[0, 2, 2] = 2.0 * a[1] * da[1]
    dg[0, 3, 3] = 2.0 * a[2] * da[2] + 2.0 * a[0] * da[0] * (N1 * y) ** 2
    dg[0, 1, 3] = dg[0, 3, 1] = -2.0 * a[0] * da[0] * N1 * y
    dg[2, 3, 3] = 2.0 * a[0] ** 2 * N1**2 * y
    dg[2, 1, 3] = dg[2, 3, 1] = -a[0] ** 2 * N1
    return g, dg


def christoffel(x: np.ndarray) -> np.ndarray:
    g, dg = metric_and_derivatives(x)
    ginv = np.linalg.inv(g)
    gamma = np.zeros((4, 4, 4), dtype=float)
    for k in range(4):
        for i in range(4):
            for j in range(4):
                gamma[k, i, j] = 0.5 * sum(
                    ginv[k, l] * (dg[i, l, j] + dg[j, l, i] - dg[l, i, j])
                    for l in range(4)
                )
    return gamma


def tetrad_to_coordinate(x: np.ndarray, vector: np.ndarray) -> np.ndarray:
    t, y = float(x[0]), float(x[2])
    a = scale_factors(t)
    out = np.zeros(4, dtype=float)
    out[0] = vector[0]
    out[3] = vector[3] / a[2]
    out[2] = vector[2] / a[1]
    out[1] = vector[1] / a[0] + N1 * y * out[3]
    return out


def coordinate_to_tetrad(x: np.ndarray, vector: np.ndarray) -> np.ndarray:
    t, y = float(x[0]), float(x[2])
    a = scale_factors(t)
    return np.array(
        [
            vector[0],
            a[0] * (vector[1] - N1 * y * vector[3]),
            a[1] * vector[2],
            a[2] * vector[3],
        ],
        dtype=float,
    )


def tangent_frame(e: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    seed = np.array([1.0, 0.0, 0.0]) if abs(e[0]) < 0.8 else np.array([0.0, 1.0, 0.0])
    u = seed - np.dot(seed, e) * e
    u /= np.linalg.norm(u)
    return u, np.cross(e, u)


def coordinate_rhs(_: float, state: np.ndarray) -> np.ndarray:
    x = state[:4]
    momentum = state[4:8]
    first = state[8:12]
    second = state[12:16]
    gamma = christoffel(x)
    energy = momentum[0]
    dx = momentum / energy
    dp = -np.einsum("mab,a,b->m", gamma, momentum, momentum) / energy
    dv1 = -np.einsum("mab,a,b->m", gamma, first, momentum) / energy
    dv2 = -np.einsum("mab,a,b->m", gamma, second, momentum) / energy
    return np.concatenate([dx, dp, dv1, dv2])


def coordinate_oracle() -> dict[str, object]:
    x0 = np.array([T0, 0.0, 0.0, 0.0], dtype=float)
    u0, v0 = tangent_frame(E0)
    p0 = tetrad_to_coordinate(x0, np.concatenate([[1.0], E0]))
    w10 = tetrad_to_coordinate(x0, np.concatenate([[0.0], u0]))
    w20 = tetrad_to_coordinate(x0, np.concatenate([[0.0], v0]))
    initial = np.concatenate([x0, p0, w10, w20])
    solution = solve_ivp(
        coordinate_rhs,
        (T0, T1),
        initial,
        method="DOP853",
        rtol=2.0e-13,
        atol=2.0e-15,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    final = solution.y[:, -1]
    x1 = final[:4]
    p1 = coordinate_to_tetrad(x1, final[4:8])
    first = coordinate_to_tetrad(x1, final[8:12])
    second = coordinate_to_tetrad(x1, final[12:16])
    energy = p1[0]
    e1 = p1[1:] / energy
    e1 /= np.linalg.norm(e1)

    w1 = first[1:] - first[0] * e1
    w2 = second[1:] - second[0] * e1
    w1 -= np.dot(w1, e1) * e1
    w1 /= np.linalg.norm(w1)
    w2 -= np.dot(w2, e1) * e1 + np.dot(w2, w1) * w1
    w2 /= np.linalg.norm(w2)
    screen_handedness = float(np.dot(np.cross(w1, w2), e1))
    if screen_handedness <= 0.0:
        raise RuntimeError(
            "coordinate parallel transport reversed the oriented photon screen"
        )
    initial_frame = np.column_stack([u0, v0, E0])
    final_frame = np.column_stack([w1, w2, e1])
    rotation = final_frame @ initial_frame.T

    g, _ = metric_and_derivatives(x1)
    null_residual = float(final[4:8] @ g @ final[4:8])
    return {
        "direction": e1.tolist(),
        "log_energy_shift": float(np.log(energy)),
        "spatial_transport": rotation.tolist(),
        "coordinate_final_time": float(x1[0]),
        "null_residual": null_residual,
        "orthogonality_defect": float(np.max(np.abs(rotation.T @ rotation - np.eye(3)))),
        "determinant_defect": float(abs(np.linalg.det(rotation) - 1.0)),
    }


def tetrad_formula_oracle() -> dict[str, object]:
    def rhs(t: float, state: np.ndarray) -> np.ndarray:
        e = state[:3]
        e /= np.linalg.norm(e)
        expansion = float(np.mean(EXPONENTS) / t)
        sigma = np.diag(EXPONENTS / t - expansion)
        n_tensor = np.diag([N1 * t ** (EXPONENTS[0] - EXPONENTS[1] - EXPONENTS[2]), 0.0, 0.0])
        sigma_e = sigma @ e
        sigma_ee = float(e @ sigma_e)
        shear_direction = -sigma_e + sigma_ee * e
        w = n_tensor @ e - 0.5 * np.trace(n_tensor) * e
        angular_velocity = w + np.cross(e, shear_direction)
        generator = np.array(
            [
                [0.0, -angular_velocity[2], angular_velocity[1]],
                [angular_velocity[2], 0.0, -angular_velocity[0]],
                [-angular_velocity[1], angular_velocity[0], 0.0],
            ]
        )
        rotation = state[4:].reshape(3, 3)
        return np.concatenate(
            [
                np.cross(angular_velocity, e),
                [-(expansion + sigma_ee)],
                (generator @ rotation).ravel(),
            ]
        )

    initial = np.concatenate([E0, [0.0], np.eye(3).ravel()])
    solution = solve_ivp(rhs, (T0, T1), initial, method="DOP853", rtol=2.0e-13, atol=2.0e-15)
    if not solution.success:
        raise RuntimeError(solution.message)
    final = solution.y[:, -1]
    direction = final[:3] / np.linalg.norm(final[:3])
    rotation = final[4:].reshape(3, 3)
    return {
        "direction": direction.tolist(),
        "log_energy_shift": float(final[3]),
        "spatial_transport": rotation.tolist(),
    }


def compute_receipt() -> dict[str, object]:
    coordinate = coordinate_oracle()
    tetrad = tetrad_formula_oracle()
    direction_error = float(
        np.max(np.abs(np.asarray(coordinate["direction"]) - np.asarray(tetrad["direction"])))
    )
    energy_error = abs(float(coordinate["log_energy_shift"]) - float(tetrad["log_energy_shift"]))
    rotation_error = float(
        np.max(
            np.abs(
                np.asarray(coordinate["spatial_transport"])
                - np.asarray(tetrad["spatial_transport"])
            )
        )
    )
    return {
        "schema": "bass-typeii-polarized-liouville-coordinate-oracle-v1",
        "metric": "ds2=-dt2+a1(t)^2(dx-N1*y*dz)^2+a2(t)^2dy2+a3(t)^2dz2",
        "exponents": EXPONENTS.tolist(),
        "n1": N1,
        "t0": T0,
        "t1": T1,
        "initial_direction": E0.tolist(),
        "coordinate": coordinate,
        "independent_tetrad_formula": tetrad,
        "cross_errors": {
            "direction_max_abs": direction_error,
            "log_energy_abs": energy_error,
            "spatial_transport_max_abs": rotation_error,
        },
    }


def _mask_rust_comments_and_strings(source: str) -> str:
    """Mask non-executable Rust text while preserving line structure.

    This is a deliberately small lexer for evidence extraction, not a Rust
    parser.  It handles nested block comments plus escaped and raw strings so a
    commented/string decoy cannot shadow the declaration compiled by rustc.
    """
    masked = list(source)
    length = len(source)

    def blank(start: int, end: int) -> None:
        for index in range(start, end):
            if masked[index] != "\n":
                masked[index] = " "

    index = 0
    while index < length:
        if source.startswith("//", index):
            end = source.find("\n", index + 2)
            end = length if end < 0 else end
            blank(index, end)
            index = end
            continue
        if source.startswith("/*", index):
            start = index
            depth = 1
            index += 2
            while index < length and depth:
                if source.startswith("/*", index):
                    depth += 1
                    index += 2
                elif source.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            if depth:
                raise ValueError("unterminated Rust block comment")
            blank(start, index)
            continue

        raw_start = index
        if source.startswith("br", index):
            raw_marker = index + 2
        elif source.startswith("r", index):
            raw_marker = index + 1
        else:
            raw_marker = -1
        if raw_marker >= 0:
            marker = raw_marker
            while marker < length and source[marker] == "#":
                marker += 1
            if marker < length and source[marker] == '"':
                hashes = marker - raw_marker
                terminator = '"' + "#" * hashes
                end = source.find(terminator, marker + 1)
                if end < 0:
                    raise ValueError("unterminated Rust raw string")
                end += len(terminator)
                blank(raw_start, end)
                index = end
                continue

        if source[index] == '"':
            start = index
            index += 1
            escaped = False
            while index < length:
                character = source[index]
                index += 1
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == '"':
                    break
            else:
                raise ValueError("unterminated Rust string")
            blank(start, index)
            continue
        index += 1
    return "".join(masked)


def _extract_rust_constant(source: str, name: str) -> object:
    executable = _mask_rust_comments_and_strings(source)
    matches = list(
        re.finditer(
            rf"^\s*const\s+{re.escape(name)}\s*:[^=]+?=\s*(.*?);",
            executable,
            flags=re.DOTALL | re.MULTILINE,
        )
    )
    if not matches:
        raise ValueError(f"missing Rust coordinate-oracle constant {name}")
    if len(matches) != 1:
        raise ValueError(f"duplicate Rust coordinate-oracle constant {name}")
    return ast.literal_eval(matches[0].group(1))


def rust_golden_errors(receipt: dict[str, object], rust_source: str) -> dict[str, float]:
    """Compare Rust golden literals to the numerical coordinate-oracle state."""
    coordinate = receipt["coordinate"]
    rust_direction = np.asarray(
        _extract_rust_constant(rust_source, "COORDINATE_ORACLE_DIRECTION"),
        dtype=float,
    )
    rust_log_energy = float(
        _extract_rust_constant(rust_source, "COORDINATE_ORACLE_LOG_ENERGY_SHIFT")
    )
    rust_transport = np.asarray(
        _extract_rust_constant(rust_source, "COORDINATE_ORACLE_SPATIAL_TRANSPORT"),
        dtype=float,
    )
    if rust_direction.shape != (3,) or rust_transport.shape != (3, 3):
        raise ValueError("Rust coordinate-oracle constants have invalid shapes")
    return {
        "direction_max_abs": float(
            np.max(np.abs(rust_direction - np.asarray(coordinate["direction"])))
        ),
        "log_energy_abs": abs(rust_log_energy - float(coordinate["log_energy_shift"])),
        "spatial_transport_max_abs": float(
            np.max(
                np.abs(
                    rust_transport - np.asarray(coordinate["spatial_transport"])
                )
            )
        ),
    }


def format_rust_golden(receipt: dict[str, object]) -> str:
    """Render copy/paste Rust literals from the independent numerical oracle."""
    coordinate = receipt["coordinate"]
    direction = json.dumps(coordinate["direction"])
    log_energy = repr(float(coordinate["log_energy_shift"]))
    transport = json.dumps(coordinate["spatial_transport"])
    return "\n".join(
        [
            f"const COORDINATE_ORACLE_DIRECTION: [f64; 3] = {direction};",
            f"const COORDINATE_ORACLE_LOG_ENERGY_SHIFT: f64 = {log_energy};",
            "const COORDINATE_ORACLE_SPATIAL_TRANSPORT: [[f64; 3]; 3] = "
            f"{transport};",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--print-rust-golden", action="store_true")
    modes.add_argument("--check-rust-golden", type=Path)
    args = parser.parse_args()
    receipt = compute_receipt()
    if args.print_rust_golden:
        print(format_rust_golden(receipt))
        return
    if args.check_rust_golden is not None:
        errors = rust_golden_errors(receipt, args.check_rust_golden.read_text())
        print(json.dumps(errors, sort_keys=True))
        failed = [
            name
            for name, error in errors.items()
            if error > RUST_GOLDEN_TOLERANCES[name]
        ]
        if failed:
            raise SystemExit(
                "Rust coordinate-oracle golden mismatch: " + ", ".join(failed)
            )
        return
    output = Path(__file__).with_name("typeii_polarized_liouville_coordinate_oracle.json")
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
