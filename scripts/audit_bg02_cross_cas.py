#!/usr/bin/env python3
"""Independent BG-02 algebra and connection-order audit.

SymPy supplies exact polynomial/tensor checks. mpmath supplies deterministic
100-digit numerical checks. Optional external executables are probed but never
silently substituted for one another.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import mpmath as mp
import sympy as sp


def eps3(i: int, j: int, k: int) -> sp.Integer:
    return sp.LeviCivita(i, j, k)


def structure(a: list[sp.Expr], n: sp.Matrix) -> list[list[list[sp.Expr]]]:
    c = [[[sp.S.Zero for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for g in range(3):
        for alpha in range(3):
            for beta in range(3):
                c[g][alpha][beta] = sp.simplify(
                    sum(eps3(alpha, beta, d) * n[d, g] for d in range(3))
                    + a[alpha] * int(g == beta)
                    - a[beta] * int(g == alpha)
                )
    return c


def generated_connection(a: list[sp.Expr], n: sp.Matrix) -> list[list[list[sp.Expr]]]:
    c = structure(a, n)
    return [
        [
            [
                sp.simplify((c[g][alpha][beta] - c[alpha][beta][g] + c[beta][g][alpha]) / 2)
                for beta in range(3)
            ]
            for alpha in range(3)
        ]
        for g in range(3)
    ]


def as_locked(generated: list[list[list[sp.Expr]]]) -> list[list[list[sp.Expr]]]:
    return [
        [[generated[g][alpha][beta] for g in range(3)] for beta in range(3)]
        for alpha in range(3)
    ]


def scalar_from_locked(a: list[sp.Expr], n: sp.Matrix, gamma: list[list[list[sp.Expr]]]) -> sp.Expr:
    c = structure(a, n)
    scalar = sp.S.Zero
    for gidx in range(3):
        beta = gidx
        ricci = sp.S.Zero
        for alpha in range(3):
            delta = alpha
            term = sp.S.Zero
            for mu in range(3):
                term += (
                    gamma[beta][gidx][mu] * gamma[alpha][mu][delta]
                    - gamma[alpha][gidx][mu] * gamma[beta][mu][delta]
                    - c[mu][alpha][beta] * gamma[mu][gidx][delta]
                )
            ricci += term
        scalar += ricci
    return sp.simplify(scalar)


def connection_order_witnesses() -> dict[str, dict[str, str]]:
    specs = {
        "I": ([sp.S.Zero] * 3, sp.zeros(3), sp.S.Zero, sp.S.Zero),
        "V": ([sp.S.One, sp.S.Zero, sp.S.Zero], sp.zeros(3), sp.Integer(-6), sp.Integer(4)),
        "II": ([sp.S.Zero] * 3, sp.diag(1, 0, 0), sp.Rational(-1, 2), sp.Rational(3, 2)),
        "IX": ([sp.S.Zero] * 3, sp.eye(3), sp.Rational(3, 2), sp.Rational(3, 2)),
    }
    out: dict[str, dict[str, str]] = {}
    for name, (a, n, expected_locked, expected_wrong) in specs.items():
        generated = generated_connection(a, n)
        locked = scalar_from_locked(a, n, as_locked(generated))
        wrong = scalar_from_locked(a, n, generated)
        if sp.simplify(locked - expected_locked) != 0:
            raise AssertionError(f"{name} locked witness mismatch: {locked}")
        if sp.simplify(wrong - expected_wrong) != 0:
            raise AssertionError(f"{name} wrong-order witness mismatch: {wrong}")
        out[name] = {
            "locked": str(locked),
            "wrong_order": str(wrong),
            "diagnostic": "REQUIRED" if name in {"V", "II"} else "FALSE_NEGATIVE",
        }
    return out


def exact_algebra() -> dict[str, object]:
    R3, H, sigma2, divA, A2, lam, kg, rho, p, tau = sp.symbols(
        "R3 H sigma2 divA A2 Lambda kappaG rho p tau"
    )
    hres = (R3 + 6 * H**2 - sigma2 - 2 * lam - 2 * kg * rho) / 2
    ftrace = -R3 / 12 - sp.Rational(3, 2) * H**2 - sigma2 / 4 + (divA + A2) / 3 + lam / 2 - kg * p / 2
    fadm = -R3 / 3 - 3 * H**2 + (divA + A2) / 3 + kg * (rho - p) / 2 + lam
    fray = -H**2 - sigma2 / 3 + (divA + A2) / 3 - kg * (rho + 3 * p) / 6 + lam / 3
    identities = [
        sp.factor(fadm - ftrace + hres / 2),
        sp.factor(ftrace - fray + hres / 6),
        sp.factor(fadm - fray + sp.Rational(2, 3) * hres),
    ]
    if identities != [0, 0, 0]:
        raise AssertionError(f"off-shell identities failed: {identities}")
    de_sitter = [sp.simplify(x.subs({R3: 0, sigma2: 0, divA: 0, A2: 0, rho: 0, p: 0, lam: 3 * H**2})) for x in (ftrace, fadm, fray)]
    kasner_subs = {R3: 0, H: 1 / (3 * tau), sigma2: sp.Rational(2, 3) / tau**2, divA: 0, A2: 0, lam: 0, rho: 0, p: 0}
    kasner = [sp.simplify(x.subs(kasner_subs)) for x in (hres, ftrace, fadm, fray)]
    expected_kasner = [0] + [sp.Rational(-1, 3) / tau**2] * 3
    if de_sitter != [0, 0, 0] or kasner != expected_kasner:
        raise AssertionError(f"limit mismatch: deSitter={de_sitter}, Kasner={kasner}")
    return {
        "off_shell_identity_residuals": [str(x) for x in identities],
        "flat_de_sitter_rate_residuals": [str(x) for x in de_sitter],
        "kasner_hamiltonian_and_rates": [str(x) for x in kasner],
    }


def high_precision_numeric() -> dict[str, object]:
    mp.mp.dps = 100
    max_abs = mp.mpf("0")
    for i in range(1, 33):
        vals = [mp.mpf(i + j) / mp.mpf(7 + 2 * j) for j in range(9)]
        R3, H, sigma2, divA, A2, lam, kg, rho, p = vals
        hres = (R3 + 6 * H**2 - sigma2 - 2 * lam - 2 * kg * rho) / 2
        ftrace = -R3 / 12 - mp.mpf(3) * H**2 / 2 - sigma2 / 4 + (divA + A2) / 3 + lam / 2 - kg * p / 2
        fadm = -R3 / 3 - 3 * H**2 + (divA + A2) / 3 + kg * (rho - p) / 2 + lam
        fray = -H**2 - sigma2 / 3 + (divA + A2) / 3 - kg * (rho + 3 * p) / 6 + lam / 3
        residuals = [fadm - ftrace + hres / 2, ftrace - fray + hres / 6, fadm - fray + 2 * hres / 3]
        max_abs = max(max_abs, *(abs(x) for x in residuals))
    tolerance = mp.mpf("1e-90")
    if max_abs > tolerance:
        raise AssertionError(f"mpmath residual too large: {max_abs}")
    return {"dps": mp.mp.dps, "cases": 32, "max_abs_residual": mp.nstr(max_abs, 15), "tolerance": "1e-90"}


def availability() -> dict[str, object]:
    probes = {
        "wolframscript": ["wolframscript"],
        "gnu_octave": ["octave-cli", "octave"],
        "sagemath": ["sage"],
        "singular": ["Singular", "singular"],
        "lean_mathlib": ["lake", "lean"],
    }
    return {key: next((path for name in names if (path := shutil.which(name))), None) for key, names in probes.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        payload = {
            "schema_version": "1.0.0",
            "stage_id": "BG_02_CROSS_CAS_AUDIT",
            "repository_scope": "BASS_ONLY",
            "sympy": {"version": sp.__version__, "status": "PASS", **exact_algebra(), "connection_order_witnesses": connection_order_witnesses()},
            "mpmath": {"version": mp.__version__, "status": "PASS", **high_precision_numeric()},
            "external_executable_availability": availability(),
            "authority_effect": "INDEPENDENT_AUDIT_ONLY_NATIVE_XACT_STILL_REQUIRED",
            "status": "PASS_AVAILABLE_CAS_AXES",
        }
    except Exception as exc:
        payload = {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
        code = 1
    else:
        code = 0
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
