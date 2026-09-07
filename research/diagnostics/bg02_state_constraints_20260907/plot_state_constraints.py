#!/usr/bin/env python3
"""Plot only data emitted by the real state-constraint runner.

PREPARED_UNEXECUTED. No Wolfram execution, expected-value substitution,
GitHub Actions, downloads, or source mutation occurs in this script.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON constant: {value}")


def numeric(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Non-numeric diagnostic value: {value!r}")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite diagnostic value")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path,
                        help="New directory: existing directories are never overwritten")
    args = parser.parse_args()
    lines = args.stdout.read_text(encoding="utf-8").splitlines()
    starts = [i for i, line in enumerate(lines) if line == "SC_FINAL_BEGIN"]
    ends = [i for i, line in enumerate(lines) if line == "SC_FINAL_END"]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValueError("Missing, duplicate, or unordered SC final markers; preserve raw stdout")
    payload = "\n".join(lines[starts[0]+1:ends[0]]) + "\n"
    result = json.loads(payload, object_pairs_hook=unique_object,
                        parse_constant=reject_constant)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "STATE_CONSTRAINT_RESULT.json").write_text(payload, encoding="utf-8")
    if result.get("status") != "PASS_RESEARCH_COMPONENT_ONLY":
        raise SystemExit("Result preserved; no validation plot generated for a non-PASS run")
    if not result.get("source_unchanged") or not result.get("exact_ids"):
        raise ValueError("Source or exact-ID checks are absent")
    rows = result.get("diagnostic_rows")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("Expected five actually evaluated diagnostic rows")
    xs = [numeric(row["u"]) for row in rows]
    full = [numeric(row["Hfull"]) for row in rows]
    deleted = [numeric(row["Hdeleted"]) for row in rows]
    if xs != [-2.0, -1.0, 0.0, 1.0, 2.0]:
        raise ValueError("Diagnostic input grid differs from the frozen test file")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(6.4, 4.0))
    ax = fig.add_subplot(111)
    ax.plot(xs, full, marker="o", label="Full input shear")
    ax.plot(xs, deleted, marker="s", label="Deleted shear; same expansion")
    ax.set_xlabel(r"Input off-diagonal amplitude $u$")
    ax.set_ylabel(r"$\ell_*^2\,\mathcal{H}$")
    ax.set_title("State-to-constraint evaluation (not time evolution)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.out / "constraint_vs_shear.png", dpi=180)
    fig.savefig(args.out / "constraint_vs_shear.svg")
    plt.close(fig)

    fig = plt.figure(figsize=(6.4, 4.0))
    ax = fig.add_subplot(111)
    ax.plot(xs, [cut - val for cut, val in zip(deleted, full)],
            marker="o", linestyle="none")
    ax.set_xlabel(r"Input off-diagonal amplitude $u$")
    ax.set_ylabel(r"$\ell_*^2(\mathcal{H}_{\rm deleted}-\mathcal{H}_{\rm full})$")
    ax.set_title("Deletion response from evaluated states")
    fig.tight_layout()
    fig.savefig(args.out / "deletion_response.png", dpi=180)
    fig.savefig(args.out / "deletion_response.svg")
    plt.close(fig)
    (args.out / "PLOT_SCOPE.txt").write_text(
        "Five exact-algebraic mapper evaluations at a fixed reference length.\n"
        "Plotted data are read from the actual runner JSON.\n"
        "Connecting lines are visual guides, not computed intermediate states.\n"
        "No numerical time evolution, convergence, or solver stability is tested.\n"
        "Generation is not visual inspection; record inspection separately.\n",
        encoding="utf-8")
    print(f"Plots and the extracted original JSON: {args.out}")


if __name__ == "__main__":
    main()
