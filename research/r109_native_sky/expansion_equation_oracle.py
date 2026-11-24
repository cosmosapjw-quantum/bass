"""Compare native FLRW radiation plus cold dust with its analytic H(a)."""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


def measure(binary, root, n, equation, eta, fraction):
    folder = root / f"{equation}-{n}"
    args = ["--family", "FLRW", "--shear", "0", "--feedback", "active", "--dust-fraction", str(fraction),
            "--dust-beta", "0,0,0", "--duration", str(eta), "--nmu", "6", "--nphi", "12", "--lmax", "2",
            "--steps", str(n), "--expansion-equation", equation]
    subprocess.run([str(binary), "--out", str(folder), *args], check=True)
    with (folder / "diagnostics.tsv").open() as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    if len(rows) != n + 1 or f"expansion_equation={equation}" not in (folder / "run.txt").read_text().splitlines():
        raise ValueError("native results do not match the requested trajectory")
    relative = []
    for row in rows:
        t = float(row["eta"])
        exact = math.sqrt((1 - fraction) * math.exp(-4*t) + fraction * math.exp(-3*t))
        relative.append(float(row["hubble_ratio"]) / exact - 1)
    gauss = [float(row["gauss"]) for row in rows]
    return {"n_steps": n, "equation": equation, "argv_after_out": args,
            "final_H_ratio": float(rows[-1]["hubble_ratio"]), "final_H_relative_error": relative[-1],
            "max_H_relative_error": max(map(abs, relative)), "final_Gauss": gauss[-1],
            "max_abs_Gauss": max(map(abs, gauss)), "diagnostics_sha256": hashlib.sha256((folder/"diagnostics.tsv").read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    binary = a.binary.resolve()
    eta = math.log1p(1100.)
    fraction = 0.75
    levels = (96, 192, 384)
    equations = ("raychaudhuri", "gauss-reduced")
    with TemporaryDirectory() as tmp, ThreadPoolExecutor(max_workers=3) as ex:
        tasks = [ex.submit(measure, binary, Path(tmp), n, eq, eta, fraction) for eq in equations for n in levels]
        rows = [task.result() for task in tasks]
    coarse, reduced = rows[:3], rows[3:]
    if not all(red["max_abs_Gauss"] < old["max_abs_Gauss"] and red["max_H_relative_error"] < old["max_H_relative_error"]
               for old, red in zip(coarse, reduced)):
        raise ValueError("reduced equation failed the measured H and constraint comparison")
    if not all(coarse[i+1]["max_abs_Gauss"] < coarse[i]["max_abs_Gauss"] and
               reduced[i+1]["max_abs_Gauss"] < reduced[i]["max_abs_Gauss"] for i in range(2)):
        raise ValueError("refinement failed")
    d = {"schema":"bass.r109.expansion_equation_oracle.v1", "status":"pass_scoped",
         "scope":"flat, cold dust + unpolarized isotropic collisionless radiation in an expanding normal frame",
         "H_exact":"sqrt((1-f)*exp(-4*eta) + f*exp(-3*eta))", "dust_initial_fraction":fraction,
         "final_eta":eta, "initial_redshift_for_span":1100,
         "binary_sha256":hashlib.sha256(binary.read_bytes()).hexdigest(), "runs":rows}
    a.output.write_text(json.dumps(d, indent=2, allow_nan=False)+"\n")
    for row in rows:
        print(row["equation"],row["n_steps"],row["max_abs_Gauss"],row["final_H_relative_error"])


if __name__ == "__main__":
    main()
