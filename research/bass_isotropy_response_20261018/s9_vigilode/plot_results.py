#!/usr/bin/env python3
"""Render recorded S9 histories, fixed gates and host-local work diagnostics.

Reporting only: no solver, projection, observer or preparation code is imported
or executed. Missing/incomplete records are explicit; no missing samples are
interpolated. The immutable preregistration and S8 reference are read as data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import tempfile

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="bass_s9_mpl_"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np

HERE = Path(__file__).resolve().parent
COLORS = {"mf_into_ls": "#2166ac", "small_clock4": "#b65a00"}
ARMS = {"mf_into_ls": "MF", "small_clock4": "Small+clock"}
STYLE = {1e-8: ":", 1e-10: "--", 1e-12: "-"}
VARIABLES = [r"$h=H/H_\star$", r"$b$", r"$y=s/H_\star$"]
METRICS = [
    ("hamiltonian_relative", "max_hamiltonian_relative", "Hamiltonian"),
    ("cohort_energy_relative", "max_native_cohort_energy_identity_relative", "Cohort identity"),
    ("event_energy_relative", "max_event_energy_relative", "Birth energy"),
    ("donor_endpoint_relative", "donor_endpoint_relative", "Donor endpoint"),
    ("clock_abs", "max_clock_abs", "Clock"),
    ("fine_reference_abs", "reference_max", "Reference"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load_optional(path, inputs, notices):
    if not path.is_file():
        notices.append({"path": str(path), "status": "missing"})
        return {}
    inputs.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)})
    try:
        value = json.loads(path.read_text())
        if not isinstance(value, dict):
            raise ValueError("expected a JSON object")
        return value
    except (ValueError, UnicodeError) as error:
        notices.append({"path": str(path), "status": "unparseable", "error": str(error)})
        return {}


def absmax(values):
    numbers = [abs(v) for v in values if finite(v)]
    return max(numbers) if numbers else None


def expected_rows(raw, case, reference):
    if case["model"] == "S8_closed_donor":
        return {r["x"]: [r["h"], r["b"], r["y"]] for r in reference["rows"]}
    config = raw.get("input", {}).get("config", {})
    if not all(k in config for k in ["donor0", "old_isotropic", "cosmological_constant", "b0"]):
        return {}
    return {
        x: [math.sqrt(config["donor0"] * math.exp(-3*x)
                      + config["old_isotropic"] * math.exp(-4*x)
                      + config["cosmological_constant"]), config["b0"], 0.0]
        for x in raw.get("input", {}).get("output_times", [])
    }


def collect(run, prereg, reference, inputs, notices):
    records = []
    for case in prereg["cases"]:
        folder = run / case["name"]
        raw = load_optional(folder / "RAW.json", inputs, notices)
        process = load_optional(folder / "PROCESS.json", inputs, notices)
        assessment = load_optional(folder / "ASSESSMENT.json", inputs, notices)
        if process.get("raw_sha256") and raw:
            if process["raw_sha256"] != sha(folder / "RAW.json"):
                raise ValueError("RAW_PROCESS_HASH_MISMATCH: " + case["name"])
        complete = (assessment.get("completed") is True and raw.get("status") == "completed"
                    and process.get("exit_code") == 0)
        good = complete and assessment.get("all_quality_gates") is True
        state = "PASS" if good else "GATE FAIL" if complete else "PREFIX" if raw else "NO RAW"
        observations = []
        for row in raw.get("observations", []):
            values = row.get("state", [])
            if finite(row.get("x")) and len(values) == 3 and all(finite(v) for v in values):
                observations.append(row)
            else:
                notices.append({"case": case["name"], "status": "invalid_observation_omitted"})
        expected = expected_rows(raw, case, reference)
        pairs = [(r, expected[r["x"]]) for r in observations if r["x"] in expected]
        residuals = [[abs(r["state"][i] - ref[i]) for i in range(3)] for r, ref in pairs]
        metrics = {}
        for gate, key, _ in METRICS:
            value = assessment.get(key) if complete else None
            if key == "reference_max":
                value = absmax(assessment.get("max_abs_h_b_y_reference", [])) if complete else None
                if value is None:
                    value = absmax(v for row in residuals for v in row)
            if value is None and gate == "hamiltonian_relative":
                value = absmax(r.get("c_relative") for r in observations)
            if value is None and gate == "clock_abs":
                value = absmax(r.get("clock_error") for r in observations)
            if value is None and gate == "event_energy_relative" and raw:
                value = absmax(e.get("energy_jump_relative") for e in raw.get("events", []))
                if not raw.get("events") and observations:
                    value = 0.0
            metrics[gate] = {"value": value if finite(value) else None,
                             "ratio": value / prereg["gates"][gate] if finite(value) else None,
                             "scope": "complete_history" if complete else "recorded_prefix"}
        counters = {}
        for segment in raw.get("segments", []):
            for key, value in segment.get("counters", {}).items():
                if finite(value):
                    counters[key] = counters.get(key, 0) + value
        elapsed = process.get("elapsed_seconds")
        records.append({"case": case, "raw": raw, "assessment": assessment,
                        "process": process, "complete": complete, "state": state,
                        "failure": assessment.get("failure") or raw.get("failure"),
                        "observations": observations, "pairs": pairs, "residuals": residuals,
                        "metrics": metrics, "counters": counters,
                        "elapsed_seconds": elapsed if finite(elapsed) else None})
    return records


def write_figure(fig, out, name):
    paths = []
    for ext in ["png", "svg"]:
        path = out / (name + "." + ext)
        fig.savefig(path, dpi=200, facecolor="white", metadata={"Creator": "BASS S9 plot_results.py"})
        paths.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)})
    plt.close(fig)
    return paths


def trajectory_figure(records, reference, prereg, out):
    fig, axs = plt.subplots(3, 2, figsize=(180/25.4, 167/25.4), sharex=True,
                            layout="constrained")
    closed = [r for r in records if r["case"]["model"] == "S8_closed_donor"]
    reference_x = [r["x"] for r in reference["rows"]]
    keys = ["h", "b", "y"]
    for i in range(3):
        left, right = axs[i]
        left.plot(reference_x, [r[keys[i]] for r in reference["rows"]],
                  color="black", lw=1.3, alpha=.75, label="Frozen S8 reference", zorder=2)
        for rec in closed:
            arm = rec["case"]["solver"]["arm"]
            tol = rec["case"]["solver"]["rtol"]
            rows = rec["observations"]
            if rows:
                left.plot([r["x"] for r in rows], [r["state"][i] for r in rows],
                          color=COLORS[arm], ls=STYLE[tol], lw=1.2, alpha=.85)
                if not rec["complete"]:
                    left.plot(rows[-1]["x"], rows[-1]["state"][i], "x", color=COLORS[arm], ms=6)
            if rec["pairs"]:
                xx = [pair[0]["x"] for pair in rec["pairs"]]
                yy = [row[i] for row in rec["residuals"]]
                right.plot(xx, yy, color=COLORS[arm], ls=STYLE[tol], lw=1.15)
                if not rec["complete"]:
                    right.plot(xx[-1], yy[-1], "x", color=COLORS[arm], ms=6)
        right.set_yscale("symlog", linthresh=1e-17, linscale=.5)
        right.axhline(prereg["gates"]["fine_reference_abs"], color="#8b1a1a", lw=.8, ls="-.")
        right.set_ylim(bottom=0)
        left.set_ylabel(VARIABLES[i])
        right.set_ylabel(r"Absolute residual")
        completion = f"; {sum(r['complete'] for r in closed)}/{len(closed)} complete" if i == 0 else ""
        left.set_title(f"({chr(97+2*i)}) State" + completion, loc="left", fontsize=9)
        right.set_title(f"({chr(98+2*i)}) Against S8 samples", loc="left", fontsize=9)
        for ax in [left, right]:
            ax.grid(alpha=.22, lw=.6)
            ax.set_xlim(min(reference_x), max(reference_x))
    for ax in axs[-1]:
        ax.set_xlabel(r"$x=\ln(a/a_0)$")
    handles = [Line2D([], [], color="black", label="S8 reference")]
    handles += [Line2D([], [], color=c, label=ARMS[a]) for a, c in COLORS.items()]
    handles += [Line2D([], [], color=".3", ls=s, label=f"rtol={t:.0e}") for t, s in STYLE.items()]
    fig.legend(handles=handles, loc="outside upper center", ncol=3, frameon=False,
               fontsize=8, handlelength=2.6, columnspacing=1.4)
    return write_figure(fig, out, "S9_01_trajectories_residuals")


def case_label(rec):
    case = rec["case"]
    model = "FLRW" if case["model"] == "analytic_FLRW" else "closed"
    return f"{ARMS[case['solver']['arm']]} {model} {case['solver']['rtol']:.0e}\n{rec['state']}"


def gate_figure(records, prereg, out):
    ratios = np.array([[r["metrics"][key]["ratio"] if r["metrics"][key]["ratio"] is not None
                        else np.nan for key, _, _ in METRICS] for r in records])
    # Clipping changes only the color scale; printed ratios retain actual values.
    color = np.ma.masked_invalid(np.log10(np.maximum(ratios, 1e-6)))
    fig, ax = plt.subplots(figsize=(180/25.4, 155/25.4), layout="constrained")
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#eeeeee")
    im = ax.imshow(color, aspect="auto", cmap=cmap, norm=TwoSlopeNorm(vmin=-6, vcenter=0, vmax=3))
    for row, rec in enumerate(records):
        for col in range(len(METRICS)):
            ratio = ratios[row, col]
            if not np.isfinite(ratio):
                label = "n/a"
            else:
                label = "0" if ratio == 0 else f"{ratio:.1e}"
                if not rec["complete"]:
                    label = "p " + label
            ax.text(col, row, label, ha="center", va="center", fontsize=8,
                    color="white" if np.isfinite(ratio) and (ratio <= 1e-4 or ratio >= 1e2) else "black")
            if np.isfinite(ratio) and ratio > 1:
                ax.add_patch(Rectangle((col-.48, row-.48), .96, .96, fill=False,
                                       edgecolor="#8b0000", linewidth=1.6))
    ax.set_xticks(range(len(METRICS)), [label+"\n"+f"{prereg['gates'][key]:.0e}"
                                       for key, _, label in METRICS], fontsize=8)
    ax.set_yticks(range(len(records)), [case_label(r) for r in records], fontsize=8)
    ax.set_xticks(np.arange(-.5, len(METRICS), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(records), 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title("Recorded error / fixed gate   (failure: ratio > 1)", fontsize=11, pad=10)
    cb = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=.06, pad=.06,
                      ticks=[-6, -3, 0, 3], extend="both")
    cb.ax.set_xticklabels([r"$\leq10^{-6}$", r"$10^{-3}$", "1", r"$\geq10^3$"])
    cb.set_label("Color encodes ratio; p = prefix only; n/a = not assessed", fontsize=8)
    return write_figure(fig, out, "S9_02_fixed_gates")


def work_figure(records, out):
    fig, axs = plt.subplots(1, 2, figsize=(180/25.4, 113/25.4), layout="constrained")
    ax, timeax = axs
    metrics = [("rhs_calls", "RHS", "-"), ("jvp_calls", "JVP", "--"),
               ("jacobian_builds", "Jacobian", ":")]
    drew = False
    handles = []
    for arm in ARMS:
        rr = [r for r in records if r["case"]["model"] == "S8_closed_donor"
              and r["case"]["solver"]["arm"] == arm]
        rr.sort(key=lambda r: r["case"]["solver"]["rtol"], reverse=True)
        for key, label, linestyle in metrics:
            use = [r for r in rr if key in r["counters"] and r["counters"][key] > 0]
            if not use:
                continue
            drew = True
            xx = [r["case"]["solver"]["rtol"] for r in use]
            yy = [r["counters"][key] for r in use]
            ax.plot(xx, yy, color=COLORS[arm], ls=linestyle, lw=1.2,
                    label=f"{ARMS[arm]} {label}")
            handles.append(Line2D([], [], color=COLORS[arm], ls=linestyle,
                                  marker="o" if arm == "mf_into_ls" else "s",
                                  markerfacecolor=COLORS[arm] if arm == "mf_into_ls" else "none",
                                  label=f"{ARMS[arm]} {label}"))
            for x, y, rec in zip(xx, yy, use):
                marker = ("o" if arm == "mf_into_ls" else "s") if rec["complete"] else "x"
                ax.plot(x, y, marker=marker, color=COLORS[arm], ms=6,
                        markerfacecolor=COLORS[arm] if arm == "mf_into_ls" else "none")
    if not drew:
        ax.text(.5, .5, "No solver counters\nin recorded segments", ha="center", va="center",
                transform=ax.transAxes, fontsize=9)
    else:
        ax.set_yscale("log")
        fig.legend(handles=handles, fontsize=8, frameon=False,
                   loc="outside upper center", ncol=2)
    ax.set_xscale("log")
    ax.set_xlim(2e-8, 5e-13)
    ax.set_xticks([1e-8, 1e-10, 1e-12])
    ax.set_xlabel("Requested rtol")
    ax.set_ylabel("Calls in recorded segments")
    ax.set_title("(a) Solver work", loc="left", fontsize=10)
    ax.grid(alpha=.22)
    labels = []
    for i, rec in enumerate(records):
        case = rec["case"]
        labels.append(f"{ARMS[case['solver']['arm']]}\n"
                      + ("FLRW" if case["model"] == "analytic_FLRW" else f"{case['solver']['rtol']:.0e}"))
        elapsed = rec["elapsed_seconds"]
        if elapsed is None:
            timeax.text(.02, i, "not recorded", fontsize=7.5, va="center")
            continue
        timeax.barh(i, elapsed, color=COLORS[case["solver"]["arm"]], alpha=.75,
                    height=.7, hatch="//" if not rec["complete"] else None)
    timeax.set_yticks(range(len(records)), labels, fontsize=8)
    timeax.invert_yaxis()
    timeax.set_xlabel("Process elapsed time (s)")
    timeax.set_title("(b) This host only", loc="left", fontsize=10)
    timeax.grid(axis="x", alpha=.22)
    return write_figure(fig, out, "S9_03_work_diagnostics")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("REPORT_OUTPUT_NOT_EMPTY")
    if not args.run_dir.is_dir():
        raise ValueError("ACTUAL_RUN_DIRECTORY_REQUIRED")
    out.mkdir(parents=True, exist_ok=True)
    inputs, notices = [], []
    prereg = load_optional(HERE / "PREREGISTRATION.json", inputs, notices)
    reference = load_optional(HERE / "reference/S8_PRIMAL.json", inputs, notices)
    if not prereg or not reference:
        raise ValueError("FIXED_PREREGISTRATION_AND_REFERENCE_REQUIRED")
    campaign = load_optional(args.run_dir / "CAMPAIGN_RETURN.json", inputs, notices)
    inputs.append({"path": str(Path(__file__).resolve()), "bytes": Path(__file__).stat().st_size,
                   "sha256": sha(Path(__file__))})
    records = collect(args.run_dir, prereg, reference, inputs, notices)
    if not any(r["raw"] or r["process"] or r["assessment"] for r in records):
        raise ValueError("NO_ACTUAL_RECORDED_CASES")
    matplotlib.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                                "axes.labelsize": 9, "xtick.labelsize": 8,
                                "ytick.labelsize": 8, "svg.fonttype": "none",
                                "svg.hashsalt": "BASS_S9_REPORT_V1",
                                "axes.spines.top": False, "axes.spines.right": False})
    figures = trajectory_figure(records, reference, prereg, out)
    figures += gate_figure(records, prereg, out)
    figures += work_figure(records, out)
    case_data = [{"name": r["case"]["name"], "state": r["state"], "complete": r["complete"],
                  "failure": r["failure"], "observations": len(r["observations"]),
                  "matched_reference_samples": len(r["pairs"]),
                  "last_recorded_x": r["observations"][-1]["x"] if r["observations"] else None,
                  "metrics": r["metrics"], "counters": r["counters"],
                  "elapsed_seconds": r["elapsed_seconds"]} for r in records]
    report = {"schema": "BASS_S9_RECORDED_FIGURES_V1", "campaign_state": campaign.get("state"),
              "source_publication": campaign.get("source_publication"),
              "inputs": inputs, "figures": figures, "notices": notices, "cases": case_data,
              "python": platform.python_version(), "matplotlib": matplotlib.__version__,
              "numpy": np.__version__, "target_width_mm": 180,
              "scopes": ["Recorded output samples and frozen S8 numerical reference only",
                         "No ODE rerun, interpolation, quadrature update or gate change",
                         "Incomplete prefixes are not complete-history gate passes",
                         "Timing and work are host-local diagnostics; no portable speedup claim"],
              "visual_review_status": "AWAITING_08_THEN_07_DIRECT_INSPECTION"}
    (out / "PLOT_SOURCE_MANIFEST.json").write_text(json.dumps(report, ensure_ascii=False, indent=2,
                                                              allow_nan=False) + "\n")
    captions = ["# S9 figure captions\n",
                "All three figures target 180 mm width. State variables h, b, y and x are dimensionless.\n",
                "## Figure 1: Recorded histories and absolute sample residuals\n",
                "Left: actual recorded h, b, y samples for both solver arms and three tolerances, overlaid on the fixed S8 numerical reference. Right: absolute differences at exactly matching output times; no reference interpolation. The residual scale is symlog with a linear interval up to 1e-17, so zeros remain zero. The dash-dot line is the fixed 1e-9 fine-reference comparison gate. Crosses mark the last retained sample of an incomplete history. Curves join samples for display and do not certify dense interpolation or continuum angular accuracy.\n",
                "## Figure 2: Recorded error divided by the unchanged gate\n",
                "The denominator is printed below each column label. Ratios above one are failures and have a red outline. Labels retain measured ratios while only colors saturate below 1e-6 or above 1e3. A prefix is explicitly marked p; n/a denotes an unavailable assessment. A small prefix ratio does not pass a complete-history gate. PASS/GATE FAIL are the recorded complete-history observer verdicts; PREFIX and NO RAW remain incomplete. Additional exact-stock, moment and workspace contracts are included in the case verdict, not represented by a continuous numeric ratio here.\n",
                "## Figure 3: Solver work and elapsed time in this execution environment\n",
                "Left: native counters summed over recorded segments of each closed history; crosses mark incomplete histories. Circles denote MF and open squares denote Small+clock, including coincident counts. Work from a failing segment that returned no counters is not invented. Right: elapsed process time from PROCESS.json, including process and I/O overhead; hatched bars mark incomplete histories. These are host-local diagnostics with no portable speedup claim.\n",
                "## Case states\n\n| Case | State | Output samples | Last x | Failure |\n|---|---|---:|---:|---|\n"]
    for row in case_data:
        failure = json.dumps(row["failure"], ensure_ascii=False) if row["failure"] else "—"
        captions.append(f"| {row['name']} | {row['state']} | {row['observations']} | {row['last_recorded_x']} | {failure} |\n")
    (out / "FIGURE_CAPTIONS.md").write_text("\n".join(captions))
    print(json.dumps({"figures": len(figures), "cases": len(records),
                      "complete": sum(r["complete"] for r in records),
                      "output": str(out), "visual_review": report["visual_review_status"]}))


if __name__ == "__main__":
    main()
