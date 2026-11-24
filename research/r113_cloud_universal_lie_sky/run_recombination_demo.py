#!/usr/bin/env python3
"""R113 matched-recombination demonstration (THEORY D9; REC matched_history).

Two Lie-generated VII_h (h = 1/4) histories with the pinned HYREC x_e table,
opposed tilted baryon/CDM streams, neutrinos, Lambda, SDIRK2 cells, the congruence
Lie update and a baryon-comoving observer:

* long_small: the R113 long-epoch template (shear 1e-4, z = 1100 -> 0, 768 steps);
* window_strong: shear 1e-2 and baryon tilt 1e-3 over the recombination window
  eta in [0, 0.5] (z = 1100 -> 667), 128 steps.

Each is run with the tabulated history (--recombination table) and with the
implicit matched hydrogen correction (--recombination matched) on the ray route,
and matched on the spin-harmonic route. Reported: the electron-fraction offset
delta_x_e(eta) (max, max for eta <= 1, final), its route difference, the optical
depth change and the relative change of the replayed C_l (matched vs table) where
C_l lies >= 1e12 above the a_lm roundoff floor. Deterministic
single-history templates, not fits.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import time

from run_cross_route_atlas import max_rel, read_modes, read_run

T_UNIT_K = repr(2.72548 * 1101.0)
CASES = {
    "long_small": {
        "lie": "shear 0 1e-4 -1e-4 0 0 0\nn 0 0.01 0.01 0 0 0\na 0.005 0 0\n",
        "duration": math.log(1101.0),
        "steps": 768,
        "beta": "1e-4,0,0",
        "los": ["--los-lmax", "64", "--los-ntheta", "96", "--los-nphi", "192"],
    },
    "window_strong": {
        "lie": "shear 0 1e-2 -1e-2 0 0 0\nn 0 0.01 0.01 0 0 0\na 0.005 0 0\n",
        "duration": 0.5,
        "steps": 128,
        "beta": "1e-3,0,0",
        "los": ["--los-lmax", "32", "--los-ntheta", "48", "--los-nphi", "96"],
    },
}


def read_table(path):
    with open(path) as f:
        header = f.readline().split()
        rows = [[float(x) for x in line.split()] for line in f if line.strip()]
    return header, rows


def run(binary, out, extra):
    t0 = time.time()
    subprocess.run([binary, "--out", out] + extra, check=True, capture_output=True, text=True)
    seconds = time.time() - t0
    header, diag = read_table(os.path.join(out, "diagnostics.tsv"))
    _, cl = read_table(os.path.join(out, "los_cl.tsv"))
    result = {"seconds": seconds,
              "los": read_modes(os.path.join(out, "los_modes.tsv")),
              "run": read_run(os.path.join(out, "run.txt")),
              "final": dict(zip(header, diag[-1])),
              "los_cl": {int(r[0]): r[1:] for r in cl}}
    rec = os.path.join(out, "recombination.tsv")
    if os.path.exists(rec):
        h, rows = read_table(rec)
        c = {k: i for i, k in enumerate(h)}
        result["recombination"] = [(r[c["eta"]], r[c["xe_table"]], r[c["delta_xe"]]) for r in rows]
    return result


# Replayed a_lm carry an absolute roundoff ~1e-16 of the unit monopole, so C_l has
# a floor ~1e-32 (observed). Relative C_l changes are reported only where
# C_l >= CL_FLOOR = 1e-20, i.e. 1e12 above that floor (relative roundoff <~ 2e-6).
CL_FLOOR = 1e-20


def cl_change(a, b, lmin, lmax):
    """max_l |C_l^b / C_l^a - 1| for TT and EE over C_l^a >= CL_FLOOR, plus l = 2..5."""
    out = {"floor": CL_FLOOR}
    for k, name in ((0, "TT"), (3, "EE")):
        worst, top = 0.0, lmin - 1
        for ell in range(lmin, lmax + 1):
            x, y = a["los_cl"][ell][k], b["los_cl"][ell][k]
            if abs(x) >= CL_FLOOR:
                worst = max(worst, abs(y / x - 1.0))
                top = ell
        out[name] = {"max_rel": worst, "l_max_above_floor": top,
                     "rel_l2_5": [b["los_cl"][ell][k] / a["los_cl"][ell][k] - 1.0
                                  for ell in range(2, 6)]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=False)
    table = os.path.join(a.repo, "research/r109_native_sky/hyrec_1100/hyrec_xe.tsv")
    with open(a.binary, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    report = {"schema": "bass.r113.recombination_demo/2", "binary_sha256": sha,
              "t_unit_k": float(T_UNIT_K), "cases": {}}
    for case, spec in CASES.items():
        lie = os.path.join(a.work, case + ".lie")
        with open(lie, "x") as f:
            f.write(spec["lie"])
        common = ["--lie-ic", lie, "--duration", repr(spec["duration"]), "--lmax", "4",
                  "--steps", str(spec["steps"]), "--nmu", "16", "--nphi", "36",
                  "--feedback", "recoil", "--dust-fraction", "0.7554963357761493",
                  "--baryon-fraction", "0.157", "--dust-beta", spec["beta"],
                  "--neutrino-fraction", "0.40891358316585885",
                  "--omega-lambda", "1.2329076547173954e-09",
                  "--ionization", table, "--n-h-emit-m3", "253202790.82151973",
                  "--h-emit-s", "5.148602492099132e-14", "--collision", "sdirk2",
                  "--lie-update", "congruence", "--observer-frame", "host"] + spec["los"]
        lmax = int(spec["los"][1])
        matched = ["--recombination", "matched", "--t-unit-k", T_UNIT_K]
        plan = [("rays_table", []),
                ("rays_matched", matched),
                ("harmonic16_matched", matched + ["--route", "harmonic", "--harmonic-lmax", "16"])]
        runs = {}
        for name, extra in plan:
            r = run(a.binary, os.path.join(a.work, case + "_" + name), common + extra)
            runs[name] = r
            print(case, name, f"{r['seconds']:.1f}s", "tau", r["final"]["proper_depth"],
                  "delta_xe_final", r["run"].get("delta_xe_final"), flush=True)
        rm, hm = runs["rays_matched"]["recombination"], runs["harmonic16_matched"]["recombination"]
        peak = max(rm, key=lambda t: abs(t[2]))
        early = max((t for t in rm if t[0] <= 1.0), key=lambda t: abs(t[2]))
        route_gap = max(abs(x[2] - y[2]) for x, y in zip(rm, hm))
        report["cases"][case] = {
            "settings": {"lie_ic": spec["lie"], "duration": spec["duration"],
                         "steps": spec["steps"], "dust_beta": spec["beta"], "los_lmax": lmax},
            "seconds": {k: v["seconds"] for k, v in runs.items()},
            "delta_xe_peak": {"eta": peak[0], "xe_table": peak[1], "delta_xe": peak[2],
                              "relative": peak[2] / peak[1]},
            "delta_xe_peak_eta_le_1": {"eta": early[0], "xe_table": early[1],
                                       "delta_xe": early[2], "relative": early[2] / early[1]},
            "delta_xe_final": {"eta": rm[-1][0], "xe_table": rm[-1][1], "delta_xe": rm[-1][2]},
            "delta_xe_route_gap_max": route_gap,
            "delta_xe_route_gap_over_peak": route_gap / abs(peak[2]) if peak[2] else None,
            "proper_depth": {k: v["final"]["proper_depth"] for k, v in runs.items()},
            "cl_change_matched_vs_table_l2_lmax": cl_change(runs["rays_table"],
                                                            runs["rays_matched"], 2, lmax),
            "los_route_gap_matched_l2_lmax": max_rel(runs["rays_matched"]["los"],
                                                     runs["harmonic16_matched"]["los"], 2, lmax),
            "delta_xe_samples": [rm[i] for i in range(0, len(rm), max(1, len(rm) // 16))],
        }
        print(json.dumps({k: v for k, v in report["cases"][case].items()
                          if k != "delta_xe_samples"}), flush=True)
    with open(a.out, "x") as f:
        json.dump(report, f, indent=1)


if __name__ == "__main__":
    main()
