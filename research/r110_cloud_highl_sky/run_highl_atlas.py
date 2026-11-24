#!/usr/bin/env python3
"""R110 high-multipole native atlas (line-of-sight replay of the native solve).

Part A repeats the R109 recoil route for all twelve Lie families (eta span 0.35,
initial shear parameter 0.18, two dust streams with tilt, moving observer) with
the R110 integrators and writes all signed T/E/B modes to --los-lmax.
Part B evolves small-structure-constant Lie data from z=1100 to z=0 with the
fixed HYREC x_e history of R109, a cosmological constant and Thomson recoil,
at two step counts, as a convergence-checked long-epoch demonstration.
Every run writes into a new directory under --raw; the summary JSON records
argv, SHA-256 of every output and the derived spectra. The tarball keeps the
R109 member layout recoil_<FAMILY>/{modes,los_modes,cl,los_cl,diagnostics}.tsv,run.txt
so htt_base scripts/r109/commander_native.py --modes-name los_modes.tsv can read it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tarfile
import time
from pathlib import Path

import numpy as np

FAMILIES = ["I", "II", "III", "IV", "V", "VI0", "VIh", "VIstar", "VII0", "VIIh", "VIII", "IX"]
BETA = "0.1,0.035,-0.025"
HERE = Path(__file__).resolve().parent
HYREC = HERE.parent / "r109_native_sky" / "hyrec_1100"
N_H_EMIT = "253202790.82151973"
H_EMIT = "5.148602492099132e-14"
# Lambda/(3H^2) at z = 1100 for (Omega_m, Omega_r, Omega_L) = (0.315, 9.2e-5, 0.685).
OMEGA_LAMBDA_1100 = 0.685 / (0.315 * 1101.0**3 + 9.2e-5 * 1101.0**4)
LONG_LIE = {
    # name: (shear 6, n 6, a 3); all have zero Codazzi flux with isotropic photons.
    "VIIh": ("0 0.001 -0.001 0 0 0", "0 0.02 0.02 0 0 0", "0.01 0 0"),
    "V": ("0 0.001 -0.001 0 0 0", "0 0 0 0 0 0", "0.01 0 0"),
    "IX": ("0.001 -0.0005 -0.0005 0 0 0", "0.02 0.02 0.02 0 0 0", "0 0 0"),
    "VIII": ("0.001 -0.0005 -0.0005 0 0 0", "-0.02 0.02 0.02 0 0 0", "0 0 0"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(binary: Path, out: Path, args: list[str]) -> dict:
    cmd = [str(binary), "--out", str(out), *args]
    t0 = time.time()
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    files = {p.name: sha(p) for p in sorted(out.iterdir())}
    cl = np.loadtxt(out / "los_cl.tsv", skiprows=1)
    run_txt = dict(
        line.split("=", 1) for line in (out / "run.txt").read_text().splitlines() if "=" in line
    )
    return {
        "argv": cmd[1:],
        "seconds": time.time() - t0,
        "sha256": files,
        "los_cl_ell_TT_EE_BB": cl[:, [0, 1, 4, 6]].tolist(),
        "los_max_landing_error": float(run_txt["los_max_landing_error"]),
        "lie_type": [run_txt["lie_type_initial"], run_txt["lie_type_final"]],
        "lie_kappa_inverse_h": [
            run_txt["lie_kappa_inverse_h_initial"],
            run_txt["lie_kappa_inverse_h_final"],
        ],
    }


def mode_change(a: Path, b: Path) -> list[float | None]:
    x = np.loadtxt(a / "los_modes.tsv", skiprows=1)
    y = np.loadtxt(b / "los_modes.tsv", skiprows=1)
    out = []
    for i in range(3):
        u = x[:, 2 + 2 * i] + 1j * x[:, 3 + 2 * i]
        v = y[:, 2 + 2 * i] + 1j * y[:, 3 + 2 * i]
        n = np.linalg.norm(v)
        out.append(None if n == 0 else float(np.linalg.norm(u - v) / n))
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--raw", type=Path, required=True, help="new directory for all runs")
    p.add_argument("--los-lmax", type=int, default=32)
    p.add_argument("--long-lmax", type=int, default=48)
    p.add_argument("--long-steps", type=int, nargs=2, default=[700, 1400])
    p.add_argument("--summary", type=Path, default=HERE / "RESULTS" / "HIGHL_ATLAS.json")
    p.add_argument("--tarball", type=Path, default=HERE / "RESULTS" / "HIGHL_ATLAS_MODES.tar.gz")
    a = p.parse_args()
    a.raw.mkdir(parents=True, exist_ok=False)
    common = ["--collision", "sdirk2", "--lie-update", "congruence", "--lmax", "4"]
    summary = {
        "schema": "bass.r110.highl_atlas/1",
        "binary_sha256": sha(a.binary),
        "units": "T=I^(1/4)/<I^(1/4)>-1, Q,U=bolometric Stokes/(4<I>), dimensionless",
        "products": "deterministic signed modes and a^X a^Y* products; no ensemble statistics",
        "part_A": {},
        "part_B": {},
    }
    for family in FAMILIES:
        args = [
            "--family", family, "--shear", "0.18", "--duration", "0.35", "--nmu", "10",
            "--nphi", "24", "--feedback", "recoil", "--tau", "0.22", "--dust-fraction", "0.22",
            "--dust-beta", "0.16,-0.08,0.04", "--observer-beta", BETA,
            "--los-lmax", str(a.los_lmax), *common,
        ]
        runs = {}
        for steps in (18, 36):
            out = a.raw / (f"recoil_{family}" if steps == 18 else f"recoil_{family}_t2")
            runs[steps] = run(a.binary, out, [*args, "--steps", str(steps)])
        summary["part_A"][family] = {
            "steps18": runs[18],
            "steps36": runs[36],
            "relative_mode_change_18_to_36_TEB": mode_change(
                a.raw / f"recoil_{family}", a.raw / f"recoil_{family}_t2"
            ),
        }
    for name, (shear, n, avec) in LONG_LIE.items():
        lie = a.raw / f"long_{name}.lie"
        lie.write_text(f"shear {shear}\nn {n}\na {avec}\n")
        args = [
            "--lie-ic", str(lie), "--feedback", "recoil", "--dust-fraction", "0.75",
            "--ionization", str(HYREC / "hyrec_xe.tsv"), "--n-h-emit-m3", N_H_EMIT,
            "--h-emit-s", H_EMIT, "--duration", "7.0", "--nmu", "10", "--nphi", "24",
            "--omega-lambda", repr(OMEGA_LAMBDA_1100), "--los-lmax", str(a.long_lmax), *common,
        ]
        outs = []
        for steps in a.long_steps:
            out = a.raw / f"long_{name}_{steps}"
            outs.append(out)
            summary["part_B"].setdefault(name, {})[str(steps)] = run(
                a.binary, out, [*args, "--steps", str(steps)]
            )
        summary["part_B"][name]["relative_mode_change_TEB"] = mode_change(outs[0], outs[1])
        diag = np.loadtxt(outs[1] / "diagnostics.tsv", skiprows=1)
        summary["part_B"][name]["final_hubble_ratio_omega_rad_dust_gauss_depth"] = [
            float(diag[-1, 1]), float(diag[-1, 2]), float(diag[-1, 3]), float(diag[-1, 4]),
            float(diag[-1, 16]),
        ]
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(a.tarball, "w:gz") as tar:
        for family in FAMILIES:
            folder = a.raw / f"recoil_{family}"
            for f in ("modes.tsv", "los_modes.tsv", "cl.tsv", "los_cl.tsv", "diagnostics.tsv", "run.txt"):
                tar.add(folder / f, arcname=f"recoil_{family}/{f}")
        for name in LONG_LIE:
            folder = a.raw / f"long_{name}_{a.long_steps[1]}"
            for f in ("los_modes.tsv", "los_cl.tsv", "diagnostics.tsv", "run.txt"):
                tar.add(folder / f, arcname=f"long_{name}/{f}")
    summary["tarball_sha256"] = sha(a.tarball)
    a.summary.write_text(json.dumps(summary, indent=1) + "\n")
    print(a.summary, a.tarball)


if __name__ == "__main__":
    main()
