#!/usr/bin/env python3
"""Independent symbolic/numerical checks for the R110 theory loop (T1-T10).

Each block verifies one derivation used by the Rust implementation. The script
uses only NumPy, SciPy, SymPy and mpmath and writes THEORY_CHECKS.json next to
itself (or to --out). It does not call the Rust solver.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np
import sympy as sp
from scipy.linalg import expm


def etd2_weights(d: float) -> tuple[float, float]:
    """Start/end weights a(d), b(d) of the exponential-trapezoid source integral.

    a = (1-e^-d)/d - e^-d = sum_{j>=1} (-1)^(j+1) j d^j/(j+1)!
    b = 1 - (1-e^-d)/d    = sum_{j>=1} (-1)^(j+1)   d^j/(j+1)!
    """
    if d < 0.5:
        a = b = 0.0
        term = 1.0  # d^j/(j+1)!
        for j in range(1, 40):
            term *= d / (j + 1)
            sign = 1.0 if j % 2 == 1 else -1.0
            a += sign * j * term
            b += sign * term
        return a, b
    em = math.exp(-d)
    f = -math.expm1(-d) / d
    return f - em, 1.0 - f


def check_etd2_symbolic() -> dict:
    tau, d0, s0, s1, x0, u = sp.symbols("tau D S0 S1 X0 u", positive=True)
    # dX/dt = -D X + D S(t), with S linear on [0, tau]
    s_of = s0 * (1 - u / tau) + s1 * u / tau
    sol = sp.exp(-d0 * tau) * x0 + sp.integrate(d0 * sp.exp(-d0 * (tau - u)) * s_of, (u, 0, tau))
    d = sp.symbols("d", positive=True)
    a = (1 - sp.exp(-d)) / d - sp.exp(-d)
    b = 1 - (1 - sp.exp(-d)) / d
    target = sp.exp(-d) * x0 + a * s0 + b * s1
    diff = sp.simplify(sp.expand(sol.subs(d0, d / tau) - target))
    grid = np.concatenate([np.logspace(-14, 8, 4001), [0.5 - 1e-12, 0.5, 0.5 + 1e-12]])
    vals = np.array([etd2_weights(float(x)) for x in grid])
    mp.mp.dps = 50
    worst = 0.0
    for x in np.logspace(-14, 3, 600):
        xm = mp.mpf(float(x))
        ae = (1 - mp.e ** (-xm)) / xm - mp.e ** (-xm)
        be = 1 - (1 - mp.e ** (-xm)) / xm
        aa, bb = etd2_weights(float(x))
        worst = max(worst, float(abs((aa - ae) / ae)), float(abs((bb - be) / be)))
    return {
        "exact_linear_source_solution_residual": str(diff),
        "limit_d_to_infinity": [str(sp.limit(a, d, sp.oo)), str(sp.limit(b, d, sp.oo))],
        "series_a": str(sp.series(a, d, 0, 5).removeO()),
        "series_b": str(sp.series(b, d, 0, 5).removeO()),
        "min_weight_on_grid": float(vals.min()),
        "max_relative_error_vs_50digit": worst,
        "max_error_a_plus_b_minus_one_minus_exp": float(
            np.max(np.abs(vals.sum(axis=1) - (-np.expm1(-grid))))
        ),
    }


def toy_discrete_ordinates(kappa_dt: float, steps: int, scheme: str) -> np.ndarray:
    """Moving-scatterer toy: X_k' = -D_k X_k + D_k g sum_j w_j X_j.

    D_k varies with direction like a Doppler encounter factor; the gain is
    normalized so that constant rest-frame intensity is an equilibrium of the
    discrete operator.  The exact solution uses a matrix exponential.
    """
    n = 9
    mu = np.linspace(-0.9, 0.9, n)
    beta = 0.3
    gamma = 1 / math.sqrt(1 - beta * beta)
    dfac = gamma * (1 - beta * mu)
    w = np.full(n, 1.0 / n)
    g = 1.0 / np.sum(w)
    x0 = 1.0 + 0.3 * mu + 0.2 * mu * mu
    lmat = -np.diag(dfac) + np.outer(dfac * g, w)
    if scheme == "exact":
        return expm(kappa_dt * lmat) @ x0
    h = kappa_dt / steps
    x = x0.copy()

    def backward_euler(y: np.ndarray, depth_scale: float) -> np.ndarray:
        dk = depth_scale * dfac
        transmit = 1.0 / (1.0 + dk)
        gain = dk / (1.0 + dk) * g
        s1 = np.sum(w * transmit * y) / (1.0 - np.sum(w * gain))
        return transmit * y + gain * s1

    gam = 1.0 - 1.0 / math.sqrt(2.0)
    for _ in range(steps):
        dk = h * dfac
        if scheme == "be":
            x = backward_euler(x, h)
        elif scheme == "sdirk2":
            # Alexander L-stable, stiffly accurate SDIRK2: two BE solves of depth gamma*h.
            x1 = backward_euler(x, gam * h)
            y = -math.sqrt(2.0) * x + (1.0 + math.sqrt(2.0)) * x1
            x = backward_euler(y, gam * h)
        else:
            ab = np.array([etd2_weights(float(v)) for v in dk])
            s0 = np.sum(w * x)
            rhs = np.sum(w * (np.exp(-dk) * x + ab[:, 0] * g * s0))
            s1 = rhs / (1.0 - np.sum(w * ab[:, 1] * g))
            x = np.exp(-dk) * x + g * (ab[:, 0] * s0 + ab[:, 1] * s1)
    return x


def check_etd2_order() -> dict:
    out = {}
    for kdt in [0.3, 3.0, 30.0, 3.0e4]:
        exact = toy_discrete_ordinates(kdt, 1, "exact")
        rows = []
        for scheme in ["be", "etd2", "sdirk2"]:
            errs = [
                float(np.max(np.abs(toy_discrete_ordinates(kdt, s, scheme) - exact)))
                for s in [4, 8, 16, 32]
            ]
            orders = [
                math.log2(errs[i] / errs[i + 1]) if errs[i + 1] > 0 else None for i in range(3)
            ]
            rows.append({"scheme": scheme, "errors": errs, "observed_orders": orders})
        out[f"kappa_dt_{kdt:g}"] = rows
    return out


def check_encounter_invariant() -> dict:
    """Left null vector of -diag(D)+D g w^T is w/D: the encounter-weighted number."""
    n = 9
    mu = np.linspace(-0.9, 0.9, n)
    beta = 0.3
    gamma = 1 / math.sqrt(1 - beta * beta)
    dfac = gamma * (1 - beta * mu)
    w = np.full(n, 1.0 / n)
    x0 = 1.0 + 0.3 * mu + 0.2 * mu * mu
    inv0 = np.sum(w / dfac * x0)
    rows = {}
    for scheme in ["be", "etd2", "sdirk2"]:
        rows[scheme] = {
            f"kappa_dt_{k:g}": float(
                abs(np.sum(w / dfac * toy_discrete_ordinates(k, 8, scheme)) - inv0) / inv0
            )
            for k in [0.3, 30.0, 3.0e4]
        }
    z = -np.logspace(-3, 6, 20000)
    gam = 1.0 - 1.0 / math.sqrt(2.0)
    rz = (1 + (1 - 2 * gam) * z) / (1 - gam * z) ** 2
    return {
        "relative_invariant_drift": rows,
        "sdirk2_stability_min": float(rz.min()),
        "sdirk2_stability_at_minus_1e6": float(rz[-1]),
        "positivity_bound": "X_new - X_eq = R(z)(X_old - X_eq), R >= min R; a ray brighter than "
        "(1+1/|min R|) times its local equilibrium can become negative in one stage",
    }


def check_lambda_raychaudhuri() -> dict:
    eta = sp.symbols("eta", real=True)
    om_r, om_d, om_l = sp.symbols("Omega_r Omega_d Omega_L", positive=True)
    h2 = om_r * sp.exp(-4 * eta) + om_d * sp.exp(-3 * eta) + om_l
    total = om_r + om_d + om_l
    h = sp.sqrt(h2 / total)
    r = om_r * sp.exp(-4 * eta) / h2
    dd = om_d * sp.exp(-3 * eta) / h2
    ll = om_l / h2
    # q = Sigma^2/3 + (1/2) Omega_m (1 + tr P/E) - Omega_Lambda, tr P/E = 1 (radiation), 0 (dust)
    q = sp.Rational(1, 2) * r * 2 + sp.Rational(1, 2) * dd - ll
    return {
        "dlnH_deta_plus_1_plus_q": str(sp.simplify(sp.diff(sp.log(h), eta) + 1 + q)),
        "gauss_flat_residual": str(sp.simplify(r + dd + ll - 1)),
        "omega_lambda_minus_initial_over_h2": str(sp.simplify(ll - (om_l / total) / h**2)),
        "domega_lambda_deta_minus_2_1pq_omega_lambda": str(
            sp.simplify(sp.diff(ll, eta) - 2 * (1 + q) * ll)
        ),
    }


def sphere_quadrature(nmu: int, nphi: int):
    x, wx = np.polynomial.legendre.leggauss(nmu)
    phi = 2 * np.pi * np.arange(nphi) / nphi
    st = np.sqrt(1 - x * x)
    e = np.stack(
        [np.outer(st, np.cos(phi)), np.outer(st, np.sin(phi)), np.outer(x, np.ones(nphi))], -1
    ).reshape(-1, 3)
    w = np.outer(wx, np.full(nphi, 2 * np.pi / nphi)).reshape(-1)
    return e, w


def check_sobolev_escape() -> dict:
    rng = np.random.default_rng(20261124)
    e, w = sphere_quadrature(96, 192)
    rows = []
    for trial in range(6):
        a = rng.normal(size=(3, 3))
        s = 0.5 * (a + a.T)
        s -= np.trace(s) / 3 * np.eye(3)
        s *= 0.7 / np.max(np.abs(np.linalg.eigvalsh(s)))
        rate = 1.0 + np.einsum("ki,ij,kj->k", e, s, e)
        for tau0 in [0.3, 3.0, 30.0, 3.0e3, 3.0e8]:
            taus = tau0 / rate
            pbar = np.sum(w * (-np.expm1(-taus)) / taus) / (4 * np.pi)
            tail = np.sum(w * np.exp(-taus) / taus) / (4 * np.pi)
            rows.append(
                {
                    "trial": trial,
                    "tau0": tau0,
                    "lambda_min_sigma_over_H": float(np.linalg.eigvalsh(s).min()),
                    "pbar_times_tau0_minus_1": float(pbar * tau0 - 1.0),
                    "identity_residual": float(pbar - (1.0 / tau0 - tail)),
                    "mean_rate_minus_1": float(np.sum(w * rate) / (4 * np.pi) - 1.0),
                }
            )
    return {
        "max_identity_residual": max(abs(r["identity_residual"]) for r in rows),
        "max_abs_mean_rate_minus_1": max(abs(r["mean_rate_minus_1"]) for r in rows),
        "max_abs_pbar_tau0_minus_1_for_tau0_ge_3e3": max(
            abs(r["pbar_times_tau0_minus_1"]) for r in rows if r["tau0"] >= 3.0e3
        ),
        "thin_examples": [r for r in rows if r["tau0"] <= 3.0][:4],
    }


def check_wien_jensen() -> dict:
    e, w = sphere_quadrature(64, 128)
    rows = []
    for x in [3.4 / 0.26, 10.2 / 0.26]:
        for amp in [1e-5, 1e-3, 1e-2, 1e-1]:
            delta = amp * (3 * e[:, 2] ** 2 - 1) / 2
            delta -= np.sum(w * delta) / (4 * np.pi)
            exact = np.sum(w * np.exp(-x / (1 + delta))) / (4 * np.pi) / math.exp(-x) - 1
            d2 = np.sum(w * delta**2) / (4 * np.pi)
            second = (x * x / 2 - x) * d2
            rows.append(
                {
                    "x_E_over_kT": x,
                    "quadrupole_amplitude": amp,
                    "exact_ratio_minus_1": float(exact),
                    "second_order_prediction": float(second),
                    "relative_difference": float((exact - second) / exact),
                }
            )
    return {"rows": rows}


def boosted_flrw_alm(beta: float, lmax: int) -> tuple[list[float], list[float]]:
    """a_l0 of T(n)=(beta/artanh beta)/(1-beta n_z)-1, observer moving along +z."""
    mp.mp.dps = 40
    b = mp.mpf(beta)
    norm = b / mp.atanh(b)
    out = []
    for ell in range(lmax + 1):
        def f(mu, ell=ell):
            return mp.legendre(ell, mu) * (norm / (1 - b * mu) - 1)

        out.append(float(mp.quad(f, [-1, 1]) * 2 * mp.pi * mp.sqrt((2 * ell + 1) / (4 * mp.pi))))
    closed = []
    for ell in range(1, min(lmax, 12) + 1):
        q = mp.legenq(ell, 0, 1 / b, type=3)
        closed.append(float(mp.sqrt((2 * ell + 1) * mp.pi) * norm * 2 / b * mp.re(q)))
    return out, closed


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(Path(__file__).with_name("THEORY_CHECKS.json")))
    args = p.parse_args()
    alm01, closed01 = boosted_flrw_alm(0.1, 40)
    alm03, closed03 = boosted_flrw_alm(0.3, 40)
    pairs = list(zip(alm01[1:13] + alm03[1:13], closed01 + closed03))
    result = {
        "schema": "bass.r110.theory_checks/1",
        "T4_etd2_symbolic": check_etd2_symbolic(),
        "T4_etd2_toy_order_and_stiff_limit": check_etd2_order(),
        "T4_encounter_invariant_and_sdirk2_stability": check_encounter_invariant(),
        "T5_lambda_raychaudhuri": check_lambda_raychaudhuri(),
        "T7_sobolev_escape_lemma": check_sobolev_escape(),
        "T7_directional_wien_jensen": check_wien_jensen(),
        "T9_boosted_flrw_oracle": {
            "beta_0.1_alm_l0": alm01,
            "beta_0.3_alm_l0": alm03,
            "max_quadrature_vs_legendre_Q_relative": max(abs(a - c) / abs(c) for a, c in pairs),
        },
    }
    Path(args.out).write_text(json.dumps(result, indent=1) + "\n")
    print(Path(args.out))


if __name__ == "__main__":
    main()
