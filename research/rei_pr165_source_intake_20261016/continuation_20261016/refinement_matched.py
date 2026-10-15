"""Matched-input PR165 interpolation check for an NCP bounded run.

This script generates new PR164 source tables. It does not run chemistry,
change the REI driver, or reuse a checkpoint. Run it with a fresh --out path.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "source_pr164"))

from export_rei_bridge import generate
from kinetic_tangent import EinsteinTangent
from source_table import H0, OL, OM, OR, XRANGE, BackgroundTable


CASES = ("COLD_FLRW", "MASSIVE_A_PLUS", "MASS3_A_PLUS", "SIGNED_MINUS")
COUNTS = (121, 241, 481)
METRICS = ("H_rel", "b_abs", "s_over_href_abs", "time_rel")
THRESHOLDS = {
    "H_rel": {121: 3e-10, 241: 2e-11, 481: 2e-12},
    "b_abs": 5e-11,
    "s_over_href_abs": 2e-9,
    "time_rel": 8e-10,
    "hamiltonian_normalized": 3e-12,
}


def original_hamiltonian(source_csv: Path, source_receipt: Path) -> dict:
    """Read the exact PR164 source and check every original producer row."""
    table = BackgroundTable(source_receipt, source_csv)
    maximum = 0.0
    worst = None
    rows = 0
    with source_csv.open(newline="") as handle:
        for row in csv.DictReader(handle):
            case = row["case"]
            params = next(c["params"] for c in table.info["cases_receipt"] if c["case"] == case)
            fraction = float(params["fraction"])
            a = float(row["a"])
            h = float(row["H_mean_per_s"])
            s = float(row["s_per_s"])
            rho = float(row["massive_rho_norm"])
            expected = H0**2 * (OM * (1 - fraction) / a**3 + OR / a**4 + OL + rho) + s**2
            observed = h**2
            residual = abs(observed - expected) / max(abs(expected), abs(observed))
            if residual > maximum:
                maximum, worst = residual, {"case": case, "case_row_x": float(row["x"])}
            rows += 1
    return {"rows": rows, "source_sha256": table.source_sha256,
            "max_normalized_residual": maximum, "worst": worst,
            "threshold": THRESHOLDS["hamiltonian_normalized"],
            "pass": rows == 968 and maximum <= THRESHOLDS["hamiltonian_normalized"]}


def run(out: Path, source_csv: Path, source_receipt: Path) -> dict:
    out = Path(out)
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    hamiltonian = original_hamiltonian(source_csv, source_receipt)
    tables = {}
    generated = {}
    for count in COUNTS:
        directory = out / f"n{count:04}"
        meta = generate(directory, n=count)
        tables[count] = BackgroundTable(directory / "PRODUCER_RECEIPT.json",
                                        directory / "PROPOSED_REI_BACKGROUND.csv")
        generated[count] = meta

    # One set of physical abscissae and one tighter oracle per case. Each of
    # the three interpolants is evaluated at all 480 finest-grid midpoints.
    xs = [XRANGE * (j + 0.5) / 480 for j in range(480)]
    results = {count: {case: {metric: 0.0 for metric in METRICS} for case in CASES}
               for count in COUNTS}
    for case in CASES:
        params = next(c["params"] for c in generated[121]["cases_receipt"]
                      if c["case"] == case)
        oracle = EinsteinTangent(**params)
        dense = oracle.solution(rtol=6e-13, atol=2e-14, n=101)
        for x in xs:
            b, v, tau = dense.sol(x)[:3]
            b, v, tau = float(b), float(v), float(tau)
            _, h, _, _ = oracle.field(x, b, v)
            s = oracle.href * v
            t = tau / oracle.href
            for count in COUNTS:
                p = tables[count].point_at_x(case, x)
                errors = {
                    "H_rel": abs(p.h_per_s / h - 1.0),
                    "b_abs": abs(p.b - b),
                    "s_over_href_abs": abs(p.s_per_s - s) / oracle.href,
                    "time_rel": abs(p.time_s - t) / t,
                }
                for metric, value in errors.items():
                    results[count][case][metric] = max(results[count][case][metric], value)

    maxima = {count: {metric: max(results[count][case][metric] for case in CASES)
                      for metric in METRICS} for count in COUNTS}
    ratios = {f"{coarse}_to_{fine}": {
        metric: maxima[coarse][metric] / maxima[fine][metric]
        if maxima[fine][metric] else None for metric in METRICS}
        for coarse, fine in zip(COUNTS[:-1], COUNTS[1:])}
    case_ratios = {f"{coarse}_to_{fine}": {
        case: {metric: results[coarse][case][metric] / results[fine][case][metric]
               if results[fine][case][metric] else None for metric in METRICS}
        for case in CASES} for coarse, fine in zip(COUNTS[:-1], COUNTS[1:])}
    checks = {count: {
        metric: maxima[count][metric] <=
        (THRESHOLDS[metric][count] if metric == "H_rel" else THRESHOLDS[metric])
        for metric in METRICS} for count in COUNTS}
    record = {
        "schema": "bass.rei.pr165.matched_refinement.v1",
        "source": "PR164 source-only EinsteinTangent; same tighter DOP853 oracle per case",
        "original_hamiltonian": hamiltonian,
        "node_counts_per_case": list(COUNTS),
        "oracle_midpoints": 480,
        "cases": list(CASES),
        "oracle_tolerances": {"rtol": 6e-13, "atol": 2e-14},
        "thresholds": THRESHOLDS,
        "generated_source_sha256": {str(c): generated[c]["csv_sha256"] for c in COUNTS},
        "producer_clock_max_relative": {str(c): tables[c].producer_clock_max_rel for c in COUNTS},
        "per_case_maxima": {str(c): results[c] for c in COUNTS},
        "maxima": {str(c): maxima[c] for c in COUNTS},
        "coarse_over_fine_ratios": ratios,
        "per_case_coarse_over_fine_ratios": case_ratios,
        "checks": {str(c): checks[c] for c in COUNTS},
        "pass": hamiltonian["pass"] and all(all(row.values()) for row in checks.values()),
        "native_HHe": "NOT_RUN",
    }
    (out / "MATCHED_REFINEMENT.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--source-csv", type=Path,
                        default=ROOT / "source_pr164/PROPOSED_REI_BACKGROUND.csv")
    parser.add_argument("--source-receipt", type=Path,
                        default=ROOT / "source_pr164/PRODUCER_RECEIPT.json")
    args = parser.parse_args()
    result = run(args.out, args.source_csv, args.source_receipt)
    print(json.dumps({"pass": result["pass"], "maxima": result["maxima"],
                      "hamiltonian": result["original_hamiltonian"]}))
    sys.exit(0 if result["pass"] else 1)
