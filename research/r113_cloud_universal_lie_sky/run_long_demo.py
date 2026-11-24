#!/usr/bin/env python3
"""R113 long-epoch demonstration: z = 1100 -> 0 with both photon routes.

One small-Lie-data VII_h history (h = 1/4, |N|, |A| ~ 1e-2, shear 1e-4) with the
pinned HYREC x_e table (`research/r109_native_sky/hyrec_1100`), opposed tilted
baryon/CDM streams (f_b = 0.157, |beta| = 1e-4), collisionless neutrinos
(N_eff = 3.046 share of radiation), Lambda, SDIRK2 Thomson cells, the congruence
Lie update and an observer comoving with the baryons. Both routes write all-m
T/E/B modes to l = 64 by line-of-sight replay. Reported: final H, optical depth,
constraints, Lie type and h, frames, C_l of both routes, the route difference of
the replayed modes, a time-step refinement of the harmonic route and wall time.
This is a deterministic single-history template, not a fit or a covariance.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import time

from run_cross_route_atlas import max_rel, read_modes, read_run

LIE = "shear 0 1e-4 -1e-4 0 0 0\nn 0 0.01 0.01 0 0 0\na 0.005 0 0\n"


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
    col = {k: i for i, k in enumerate(header)}
    gauss = max(abs(r[col["gauss"]]) for r in diag)
    codazzi = max(math.sqrt(sum(r[col[k]] ** 2 for k in ("codazzi_x", "codazzi_y", "codazzi_z")))
                  for r in diag)
    _, cl = read_table(os.path.join(out, "los_cl.tsv"))
    return {"seconds": seconds,
            "los": read_modes(os.path.join(out, "los_modes.tsv")),
            "run": read_run(os.path.join(out, "run.txt")),
            "final": dict(zip(header, diag[-1])),
            "max_abs_gauss": gauss, "max_codazzi_norm": codazzi,
            "los_cl": {int(r[0]): r[1:] for r in cl}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=768)
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=False)
    lie = os.path.join(a.work, "viih_small.lie")
    with open(lie, "x") as f:
        f.write(LIE)
    table = os.path.join(a.repo, "research/r109_native_sky/hyrec_1100/hyrec_xe.tsv")
    with open(a.binary, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    with open(table, "rb") as f:
        table_sha = hashlib.sha256(f.read()).hexdigest()
    duration = math.log(1101.0)
    common = ["--lie-ic", lie, "--duration", repr(duration), "--lmax", "4",
              "--feedback", "recoil", "--dust-fraction", "0.7554963357761493",
              "--baryon-fraction", "0.157", "--dust-beta", "1e-4,0,0",
              "--neutrino-fraction", "0.40891358316585885",
              "--omega-lambda", "1.2329076547173954e-09",
              "--ionization", table, "--n-h-emit-m3", "253202790.82151973",
              "--h-emit-s", "5.148602492099132e-14", "--collision", "sdirk2",
              "--lie-update", "congruence", "--observer-frame", "host",
              "--los-lmax", "64", "--los-ntheta", "96", "--los-nphi", "192"]
    runs = {}
    plan = [("rays", ["--steps", str(a.steps), "--nmu", "16", "--nphi", "36"]),
            ("harmonic16", ["--steps", str(a.steps), "--nmu", "16", "--nphi", "36",
                            "--route", "harmonic", "--harmonic-lmax", "16"]),
            ("harmonic16_2x", ["--steps", str(2 * a.steps), "--nmu", "16", "--nphi", "36",
                               "--route", "harmonic", "--harmonic-lmax", "16"])]
    for name, extra in plan:
        r = run(a.binary, os.path.join(a.work, name), common + extra)
        runs[name] = r
        print(name, f"{r['seconds']:.1f}s", "tau", r["final"]["proper_depth"],
              "H", r["final"]["hubble_ratio"], "C2TT", r["los_cl"][2][0], flush=True)
    summary = {}
    for name, r in runs.items():
        summary[name] = {
            "seconds": r["seconds"],
            "final_hubble_ratio": r["final"]["hubble_ratio"],
            "final_proper_depth": r["final"]["proper_depth"],
            "max_abs_gauss": r["max_abs_gauss"],
            "max_codazzi_norm": r["max_codazzi_norm"],
            "lie_type": [r["run"].get("lie_type_initial"), r["run"].get("lie_type_final")],
            "lie_h": [r["run"].get("lie_h_initial"), r["run"].get("lie_h_final")],
            "frames": {k: r["run"].get(k) for k in (
                "frame_photon_energy_beta", "frame_radiation_energy_beta", "frame_host_beta",
                "frame_spectator_beta", "local_boost_observer_vs_radiation",
                "global_tilt_host_vs_radiation")},
            "los_cl_TT_TE_TB_EE_EB_BB": {str(l): v for l, v in r["los_cl"].items() if l in
                                         (1, 2, 3, 4, 8, 16, 32, 64)},
        }
    comparisons = {
        "rays_vs_harmonic16_los_l2_64": max_rel(runs["rays"]["los"], runs["harmonic16"]["los"], 2, 64),
        "rays_vs_harmonic16_los_l1": max_rel(runs["rays"]["los"], runs["harmonic16"]["los"], 1, 1),
        "harmonic16_dt_vs_dt2_los_l2_64": max_rel(runs["harmonic16_2x"]["los"],
                                                   runs["harmonic16"]["los"], 2, 64),
    }
    print(json.dumps(comparisons), flush=True)
    with open(a.out, "x") as f:
        json.dump({"schema": "bass.r113.long_demo/1", "binary_sha256": sha,
                   "ionization_table_sha256": table_sha,
                   "settings": {"common": [x if x != lie else "viih_small.lie" for x in common],
                                "lie_ic": LIE, "steps": a.steps},
                   "runs": summary, "comparisons": comparisons}, f, indent=1)


if __name__ == "__main__":
    main()
