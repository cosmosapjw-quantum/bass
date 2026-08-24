#!/usr/bin/env python3
"""Independent complex-Hermitian oracle for G-POL-LIOUVILLE-II-B1.

This oracle intentionally does not import the Rust implementation.  It derives
Stokes components from a complex 3x3 Hermitian coherency tensor and finite dyad
or tensor rotations.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ORACLE = HERE / "typeii_polarized_stokes_oracle.json"


def unit(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    n = np.linalg.norm(x)
    if not np.isfinite(n) or n <= 0:
        raise ValueError("invalid vector")
    return x / n


def canonical_dyad(e: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    e = unit(e)
    refs = np.eye(3)
    ref = refs[np.argmin(np.abs(refs @ e))]
    s1 = unit(ref - (ref @ e) * e)
    s2 = unit(np.cross(e, s1))
    return e, s1, s2


def stokes_matrix(i: float, q: float, u: float, v: float) -> np.ndarray:
    return 0.5 * np.array(
        [[i + q, u - 1j * v], [u + 1j * v, i - q]], dtype=complex
    )


def embed_screen(h: np.ndarray, s1: np.ndarray, s2: np.ndarray) -> np.ndarray:
    s = np.column_stack([s1, s2]).astype(complex)
    return s @ h @ s.conj().T


def extract_stokes(j: np.ndarray, s1: np.ndarray, s2: np.ndarray) -> np.ndarray:
    s = np.column_stack([s1, s2]).astype(complex)
    h = s.conj().T @ j @ s
    return np.array(
        [
            (h[0, 0] + h[1, 1]).real,
            (h[0, 0] - h[1, 1]).real,
            (h[0, 1] + h[1, 0]).real,
            (1j * (h[0, 1] - h[1, 0])).real,
        ]
    )


def rodrigues(axis: np.ndarray, angle: float) -> np.ndarray:
    x, y, z = unit(axis)
    c, s = math.cos(angle), math.sin(angle)
    k = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return c * np.eye(3) + (1.0 - c) * np.outer([x, y, z], [x, y, z]) + s * k


def passive_dyad(s1: np.ndarray, s2: np.ndarray, psi: float) -> tuple[np.ndarray, np.ndarray]:
    c, s = math.cos(psi), math.sin(psi)
    return c * s1 + s * s2, -s * s1 + c * s2


def phase_expected(stokes: np.ndarray, psi: float, sign: int) -> np.ndarray:
    i, q, u, v = stokes
    p = (q + 1j * u) * np.exp(sign * 2j * psi)
    return np.array([i, p.real, p.imag, v])


def run_oracle() -> dict[str, object]:
    e, s1, s2 = canonical_dyad(np.array([0.31, -0.42, 0.852584306]))
    states = [
        np.array([2.4, 0.6, -0.8, 0.4]),
        np.array([1.7, -0.45, 0.72, -0.21]),
    ]
    angles = [0.0, 0.17, -0.31, math.pi / 4, -math.pi / 2, 0.713, -1.137]

    passive_max = 0.0
    active_max = 0.0
    inverse_max = 0.0
    invariant_max = 0.0
    handedness_max = 0.0
    v_zero_max = 0.0
    canonical_p8_error = 0.0

    for stokes in states:
        h = stokes_matrix(*stokes)
        j = embed_screen(h, s1, s2)
        # Complex carrier implies p8=Im(J01); on the canonical xy screen p8=-V/2.
        ec, x, y = canonical_dyad(np.array([0.0, 0.0, 1.0]))
        jc = embed_screen(h, x, y)
        canonical_p8_error = max(canonical_p8_error, abs(jc[0, 1].imag + 0.5 * stokes[3]))

        for psi in angles:
            p1, p2 = passive_dyad(s1, s2, psi)
            got_passive = extract_stokes(j, p1, p2)
            exp_passive = phase_expected(stokes, psi, -1)
            passive_max = max(passive_max, float(np.max(np.abs(got_passive - exp_passive))))

            r = rodrigues(e, psi)
            jr = r @ j @ r.T
            got_active = extract_stokes(jr, s1, s2)
            exp_active = phase_expected(stokes, psi, +1)
            active_max = max(active_max, float(np.max(np.abs(got_active - exp_active))))

            got_inverse = extract_stokes(jr, p1, p2)
            inverse_max = max(inverse_max, float(np.max(np.abs(got_inverse - stokes))))

            cone0 = stokes[0] ** 2 - np.dot(stokes[1:], stokes[1:])
            cone1 = got_passive[0] ** 2 - np.dot(got_passive[1:], got_passive[1:])
            invariant_max = max(
                invariant_max,
                abs(got_passive[0] - stokes[0]),
                abs(got_passive[3] - stokes[3]),
                abs(cone1 - cone0),
            )

        left = extract_stokes(j, s1, -s2)
        expected_left = stokes * np.array([1.0, 1.0, -1.0, -1.0])
        handedness_max = max(handedness_max, float(np.max(np.abs(left - expected_left))))

    linear = np.array([1.0, 0.4, 0.2, 0.0])
    jl = embed_screen(stokes_matrix(*linear), s1, s2)
    for psi in angles:
        r = rodrigues(e, psi)
        v_zero_max = max(v_zero_max, abs(extract_stokes(r @ jl @ r.T, s1, s2)[3]))

    metrics = {
        "schema": "bass-g-pol-liouville-iib1-oracle-v1",
        "state_count": len(states),
        "angle_count": len(angles),
        "passive_phase_max_abs_error": passive_max,
        "active_phase_max_abs_error": active_max,
        "active_passive_inverse_max_abs_error": inverse_max,
        "invariant_max_abs_defect": invariant_max,
        "handedness_max_abs_error": handedness_max,
        "v_zero_max_abs_generation": v_zero_max,
        "canonical_p8_sign_error": canonical_p8_error,
        "convention": {
            "screen_matrix": "1/2 [[I+Q,U-iV],[U+iV,I-Q]]",
            "passive": "(Q+iU)'=exp(-2 i psi)(Q+iU)",
            "active": "(Q+iU)'=exp(+2 i psi)(Q+iU)",
            "canonical_pack": "packed[8]=-V/2",
        },
    }
    return metrics



METRICS = run_oracle()


def test_passive_and_active_spin_two_phases() -> None:
    assert METRICS["passive_phase_max_abs_error"] < 2e-14
    assert METRICS["active_phase_max_abs_error"] < 2e-14


def test_active_passive_inverse_composition() -> None:
    assert METRICS["active_passive_inverse_max_abs_error"] < 2e-14


def test_intensity_v_and_cone_invariants() -> None:
    assert METRICS["invariant_max_abs_defect"] < 2e-14


def test_handedness_flip() -> None:
    assert METRICS["handedness_max_abs_error"] < 2e-14


def test_linear_polarization_does_not_generate_v() -> None:
    assert METRICS["v_zero_max_abs_generation"] < 2e-14


def test_existing_pack9_v_sign() -> None:
    assert METRICS["canonical_p8_sign_error"] < 2e-14


if __name__ == "__main__":
    metrics = METRICS
    ORACLE.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metrics, indent=2, sort_keys=True))
