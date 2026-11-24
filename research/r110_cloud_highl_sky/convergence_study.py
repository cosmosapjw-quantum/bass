#!/usr/bin/env python3
"""R110 numerical validation driver for the native homogeneous-sky binary.

Runs the R109 atlas configurations with the backward-Euler (BE) and SDIRK2
collision integrators and additive/congruence Lie updates over halving steps,
and records relative L2 changes of the complex T/E/B modes, both from the
forward Lagrangian quadrature (l<=4) and from the line-of-sight replay (l<=L).

Usage:
  python research/r110_cloud_highl_sky/convergence_study.py \
      --binary _rustcore/target/release/examples/homogeneous_sky --out RESULT.json
Each run writes into a fresh temporary directory; nothing is overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np

CASES = {
    "VIstar_recoil": [
        "--family", "VIstar", "--shear", "0.18", "--duration", "0.35", "--nmu", "10",
        "--nphi", "24", "--feedback", "recoil", "--tau", "0.22", "--dust-fraction", "0.22",
        "--dust-beta", "0.16,-0.08,0.04", "--observer-beta", "0.1,0.035,-0.025",
    ],
    "VIIh_recoil_thick": [
        "--family", "VIIh:0.25", "--shear", "0.18", "--duration", "0.35", "--nmu", "10",
        "--nphi", "24", "--feedback", "recoil", "--tau", "3.0", "--dust-fraction", "0.22",
        "--dust-beta", "0.16,-0.08,0.04", "--observer-beta", "0.1,0.035,-0.025",
    ],
    "VIII_tracer": [
        "--family", "VIII", "--shear", "0.12", "--duration", "0.35", "--nmu", "10",
        "--nphi", "24", "--feedback", "tracer", "--tau", "0.22",
        "--electron-beta", "0.14,-0.03,0.02", "--observer-beta", "0.1,0.035,-0.025",
    ],
}


def run(binary: str, args: list[str], steps: int, extra: list[str], los_lmax: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="r110_conv_") as tmp:
        out = Path(tmp) / "run"
        cmd = [binary, "--out", str(out), "--steps", str(steps), "--lmax", "4",
               "--los-lmax", str(los_lmax), *args, *extra]
        t0 = time.time()
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        seconds = time.time() - t0
        fwd = np.loadtxt(out / "modes.tsv", skiprows=1)
        los = np.loadtxt(out / "los_modes.tsv", skiprows=1)
        run_txt = (out / "run.txt").read_text()
    pick = lambda a, i: a[:, 2 + 2 * i] + 1j * a[:, 3 + 2 * i]
    return {
        "seconds": seconds,
        "forward": [pick(fwd, i) for i in range(3)],
        "los": [pick(los, i) for i in range(3)],
        "run_txt_sha256": hashlib.sha256(run_txt.encode()).hexdigest(),
    }


def rel(a: np.ndarray, b: np.ndarray) -> float | None:
    n = np.linalg.norm(b)
    return None if n == 0 else float(np.linalg.norm(a - b) / n)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--binary", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--steps", default="18,36,72,144,288")
    p.add_argument("--los-lmax", type=int, default=12)
    args = p.parse_args()
    steps = [int(s) for s in args.steps.split(",")]
    variants = {
        "be_additive": ["--collision", "backward-euler"],
        "sdirk2_additive": ["--collision", "sdirk2"],
        "sdirk2_congruence": ["--collision", "sdirk2", "--lie-update", "congruence"],
    }
    result = {
        "schema": "bass.r110.convergence/1",
        "binary_sha256": hashlib.sha256(Path(args.binary).read_bytes()).hexdigest(),
        "steps": steps,
        "los_lmax": args.los_lmax,
        "cases": {},
    }
    for case, cargs in CASES.items():
        case_out = {}
        for name, extra in variants.items():
            if case == "VIII_tracer" and "congruence" in name:
                continue  # the tracer background uses its native QState step
            runs = [run(args.binary, cargs, s, extra, args.los_lmax) for s in steps]
            rows = []
            for k in range(len(steps) - 1):
                a, b = runs[k], runs[k + 1]
                rows.append({
                    "steps": [steps[k], steps[k + 1]],
                    "forward_rel_change_TEB": [rel(a["forward"][i], b["forward"][i]) for i in range(3)],
                    "los_rel_change_TEB": [rel(a["los"][i], b["los"][i]) for i in range(3)],
                })
            ratios = []
            for k in range(len(rows) - 1):
                ratios.append([
                    (rows[k]["los_rel_change_TEB"][i] / rows[k + 1]["los_rel_change_TEB"][i])
                    if rows[k + 1]["los_rel_change_TEB"][i] else None
                    for i in range(3)
                ])
            case_out[name] = {
                "changes": rows,
                "successive_ratio_los_TEB": ratios,
                "seconds": [r["seconds"] for r in runs],
            }
        result["cases"][case] = case_out
    Path(args.out).write_text(json.dumps(result, indent=1) + "\n")
    for case, v in result["cases"].items():
        for name, w in v.items():
            print(case, name, [[None if x is None else round(x, 2) for x in r] for r in w["successive_ratio_los_TEB"]])


if __name__ == "__main__":
    main()
