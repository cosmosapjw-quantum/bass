#!/usr/bin/env python3
"""R113 cross-route atlas: Lagrangian rays vs the Lie-generated spin-harmonic route.

For every Bianchi family (plus the flat FLRW control) the same physics is solved
with both photon representations: active Einstein feedback, Thomson recoil on a
tilted baryon host (f_b = 0.157), collisionless neutrinos (30 % of radiation) and
an observer boost. Reported per family:

* V7: max |a_lm(harmonic L) - a_lm(rays fine)| / max |a_lm(rays fine)| over
  l = 1..4, all m and T/E/B, for L = 8, 12, 16, 24, and rays coarse vs fine;
* V8: harmonic-route replay (line of sight) vs its direct output at l <= 4;
* high l: line-of-sight modes of both routes to l = 32;
* Lie type and h on the first and last slice, final Gauss/Codazzi residuals,
  wall time per run.

Only the Python standard library is used; every number comes from the TSV/run
files written by the binary in this run.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import time

FAMILIES = ["FLRW", "I", "II", "III", "IV", "V", "VI0", "VIh", "VIstar",
            "VII0", "VIIh", "VIII", "IX"]
HARMONIC_L = [8, 12, 16, 24]


def read_modes(path):
    out = {}
    with open(path) as f:
        f.readline()
        for line in f:
            v = line.split()
            out[(int(v[0]), int(v[1]))] = [float(x) for x in v[2:8]]
    return out


def read_run(path):
    out = {}
    with open(path) as f:
        for line in f:
            if "=" in line:
                k, v = line.rstrip("\n").split("=", 1)
                out[k] = v
    return out


def last_diagnostics(path):
    with open(path) as f:
        header = f.readline().split()
        rows = [line.split() for line in f if line.strip()]
    return dict(zip(header, (float(x) for x in rows[-1])))


def max_rel(a, b, lmin, lmax):
    keys = [k for k in a if lmin <= k[0] <= lmax and k in b]
    scale = max((abs(x) for k in keys for x in a[k]), default=0.0)
    if scale == 0.0:
        return None
    return max(abs(x - y) for k in keys for x, y in zip(a[k], b[k])) / scale


def args_for(family, route, steps=24):
    base = ["--duration", "0.3", "--steps", str(steps), "--lmax", "4",
            "--feedback", "recoil", "--tau", "0.2", "--dust-fraction", "0.3",
            "--baryon-fraction", "0.157", "--neutrino-fraction", "0.3",
            "--observer-beta", "0.01,0.005,-0.008", "--collision", "sdirk2",
            "--lie-update", "congruence"]
    if family == "FLRW":
        base += ["--family", "FLRW", "--shear", "0"]
    else:
        base += ["--family", family, "--shear", "0.05",
                 "--dust-beta", "0.03,-0.01,0.02"]
    kind, value = route
    if kind == "rays":
        base += ["--nmu", str(value[0]), "--nphi", str(value[1])]
    else:
        base += ["--nmu", "16", "--nphi", "36", "--route", "harmonic",
                 "--harmonic-lmax", str(value)]
    return base


def run(binary, work, family, route, los, steps=24):
    kind, value = route
    label = value if kind == "harmonic" else "x".join(map(str, value))
    out = os.path.join(work, f"{family}_{kind}_{label}_s{steps}")
    cmd = [binary, "--out", out] + args_for(family, route, steps)
    if los:
        # Oversampled observer grid: the boosted sky is not band-limited.
        cmd += ["--los-lmax", str(los), "--los-ntheta", str(max(2 * los, 33)),
                "--los-nphi", str(max(4 * los, 66))]
    t0 = time.time()
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    seconds = time.time() - t0
    result = {
        "modes": read_modes(os.path.join(out, "modes.tsv")),
        "run": read_run(os.path.join(out, "run.txt")),
        "diag": last_diagnostics(os.path.join(out, "diagnostics.tsv")),
        "seconds": seconds,
    }
    if los:
        result["los"] = read_modes(os.path.join(out, "los_modes.tsv"))
    return result


def codazzi(d):
    return math.sqrt(sum(d[k] ** 2 for k in ("codazzi_x", "codazzi_y", "codazzi_z")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=False)
    with open(a.binary, "rb") as f:
        binary_sha = hashlib.sha256(f.read()).hexdigest()
    cases = []
    for family in FAMILIES:
        fine = run(a.binary, a.work, family, ("rays", (24, 52)), 32)
        coarse = run(a.binary, a.work, family, ("rays", (16, 36)), None)
        harm = {L: run(a.binary, a.work, family, ("harmonic", L), 32 if L == 24 else 4)
                for L in HARMONIC_L}
        row = {
            "family": family,
            "lie_type_initial": fine["run"].get("lie_type_initial"),
            "lie_type_final": fine["run"].get("lie_type_final"),
            "lie_h_initial": fine["run"].get("lie_h_initial"),
            "lie_h_final": fine["run"].get("lie_h_final"),
            "harmonic_lie_type_final": harm[24]["run"].get("lie_type_final"),
            "rays_fine_gauss_final": fine["diag"]["gauss"],
            "rays_fine_codazzi_final": codazzi(fine["diag"]),
            "harmonic24_gauss_final": harm[24]["diag"]["gauss"],
            "harmonic24_codazzi_final": codazzi(harm[24]["diag"]),
            "rays_coarse_vs_fine_l1_4": max_rel(fine["modes"], coarse["modes"], 1, 4),
            "harmonic_vs_rays_fine_l1_4": {
                str(L): max_rel(fine["modes"], harm[L]["modes"], 1, 4) for L in HARMONIC_L},
            "harmonic_replay_vs_direct_l1_4": {
                str(L): max_rel(harm[L]["modes"], harm[L]["los"], 1, 4) for L in HARMONIC_L},
            "los_harmonic24_vs_rays_fine_l1_32": max_rel(fine["los"], harm[24]["los"], 1, 32),
            "los_harmonic24_vs_rays_fine_l5_32": max_rel(fine["los"], harm[24]["los"], 5, 32),
            "seconds": {"rays_fine": fine["seconds"], "rays_coarse": coarse["seconds"],
                        **{f"harmonic{L}": harm[L]["seconds"] for L in HARMONIC_L}},
            "frames": {k: fine["run"].get(k) for k in (
                "frame_photon_energy_beta", "frame_radiation_energy_beta", "frame_host_beta",
                "local_boost_observer_vs_radiation", "global_tilt_host_vs_radiation")},
        }
        cases.append(row)
        print(json.dumps({k: row[k] for k in (
            "family", "lie_type_initial", "lie_type_final", "harmonic_vs_rays_fine_l1_4",
            "rays_coarse_vs_fine_l1_4", "harmonic_replay_vs_direct_l1_4",
            "los_harmonic24_vs_rays_fine_l1_32")}), flush=True)
    # Time refinement: both routes share the Strang split and the linear background
    # interpolation; their difference must shrink with the e-fold step.
    refinement = []
    refine_dir = os.path.join(a.work, "refine")
    os.makedirs(refine_dir)
    for family in ["V", "VIIh", "VIstar", "VIII"]:
        row = {"family": family, "steps": [24, 48, 96, 192], "route_gap_l1_4": [],
               "rays_self_l1_4": [], "harmonic_self_l1_4": []}
        prev = None
        for steps in row["steps"]:
            r = run(a.binary, refine_dir, family, ("rays", (24, 52)), None, steps)
            h = run(a.binary, refine_dir, family, ("harmonic", 16), None, steps)
            row["route_gap_l1_4"].append(max_rel(r["modes"], h["modes"], 1, 4))
            if prev is not None:
                row["rays_self_l1_4"].append(max_rel(r["modes"], prev[0]["modes"], 1, 4))
                row["harmonic_self_l1_4"].append(max_rel(h["modes"], prev[1]["modes"], 1, 4))
            prev = (r, h)
        refinement.append(row)
        print(json.dumps(row), flush=True)
    with open(a.out, "x") as f:
        json.dump({"schema": "bass.r113.cross_route_atlas/1",
                   "binary_sha256": binary_sha,
                   "time_refinement": refinement,
                   "settings": {"common": args_for("I", ("rays", (24, 52)))[:-4],
                                "rays_fine": [24, 52], "rays_coarse": [16, 36],
                                "harmonic_lmax": HARMONIC_L, "los_lmax": 32},
                   "cases": cases}, f, indent=1)


if __name__ == "__main__":
    main()
