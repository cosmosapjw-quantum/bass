#!/usr/bin/env python3
"""R113 truncation study: harmonic-route lmax convergence in focusing geometries.

Strongly anisotropic tilted VII_h, VI*_-1/9 and IX histories (shear 0.18-0.25 and
the R109 structure scale 0.3, recoil scattering, opposed tilted baryon/CDM
streams) are solved with the ray route on a fine mesh and with the harmonic route
for lmax = 8 ... 48. Reported: relative l = 1..4 difference of the direct outputs,
relative l = 1..32 difference of the line-of-sight replays, harmonic-route
self-convergence and wall time. Every number is read from the run outputs.
"""
import argparse
import hashlib
import json
import os
import subprocess
import time

from run_cross_route_atlas import max_rel, read_modes, read_run

CASES = {
    "VIIh_focus": ["--family", "VIIh:0.25", "--shear", "0.18", "--dust-beta", "0.16,-0.08,0.04"],
    "VIstar_focus": ["--family", "VIstar", "--shear", "0.2", "--dust-beta", "0.1,0.05,-0.03"],
    "IX_focus": ["--family", "IX", "--shear", "0.25", "--dust-beta", "0.08,-0.06,0.05"],
}
COMMON = ["--duration", "1.2", "--steps", "96", "--lmax", "4", "--feedback", "recoil",
          "--tau", "0.4", "--dust-fraction", "0.22", "--baryon-fraction", "0.157",
          "--observer-beta", "0.1,0.035,-0.025", "--collision", "sdirk2",
          "--lie-update", "congruence", "--los-lmax", "32", "--los-ntheta", "64",
          "--los-nphi", "128"]
LMAXES = [8, 12, 16, 24, 32, 48]


def run(binary, out, extra):
    t0 = time.time()
    proc = subprocess.run([binary, "--out", out] + extra, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"error": proc.stderr.strip(), "seconds": time.time() - t0}
    return {"modes": read_modes(os.path.join(out, "modes.tsv")),
            "los": read_modes(os.path.join(out, "los_modes.tsv")),
            "run": read_run(os.path.join(out, "run.txt")),
            "seconds": time.time() - t0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=False)
    with open(a.binary, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    rows = []
    for name, extra in CASES.items():
        rays = run(a.binary, os.path.join(a.work, f"{name}_rays"),
                   COMMON + extra + ["--nmu", "40", "--nphi", "88"])
        rays_coarse = run(a.binary, os.path.join(a.work, f"{name}_rays_coarse"),
                          COMMON + extra + ["--nmu", "24", "--nphi", "52"])
        row = {"case": name, "args": COMMON + extra,
               "rays_fine_mesh": [40, 88], "rays_coarse_vs_fine_l1_4":
                   max_rel(rays["modes"], rays_coarse["modes"], 1, 4),
               "rays_coarse_vs_fine_los_l1_32": max_rel(rays["los"], rays_coarse["los"], 1, 32),
               "lie_type": [rays["run"].get("lie_type_initial"), rays["run"].get("lie_type_final")],
               "harmonic": []}
        previous = None
        for lmax in LMAXES:
            h = run(a.binary, os.path.join(a.work, f"{name}_h{lmax}"),
                    COMMON + extra + ["--nmu", "16", "--nphi", "36", "--route", "harmonic",
                                      "--harmonic-lmax", str(lmax)])
            if "error" in h:
                entry = {"lmax": lmax, "seconds": h["seconds"], "failed_closed": h["error"]}
                row["harmonic"].append(entry)
                print(json.dumps({"case": name, **entry}), flush=True)
                continue
            entry = {"lmax": lmax, "seconds": h["seconds"],
                     "vs_rays_l1_4": max_rel(rays["modes"], h["modes"], 1, 4),
                     "los_vs_rays_l1_32": max_rel(rays["los"], h["los"], 1, 32),
                     "self_l1_4": None if previous is None
                     else max_rel(h["modes"], previous["modes"], 1, 4)}
            row["harmonic"].append(entry)
            previous = h
            print(json.dumps({"case": name, **entry}), flush=True)
        row["rays_seconds"] = rays["seconds"]
        rows.append(row)
    with open(a.out, "x") as f:
        json.dump({"schema": "bass.r113.truncation_study/1", "binary_sha256": sha,
                   "cases": rows}, f, indent=1)


if __name__ == "__main__":
    main()
