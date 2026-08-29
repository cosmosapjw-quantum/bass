#!/usr/bin/env python3
"""Render the five bounded RF04-POL-01 diagnostics from retained machine data."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)
FOOTER = "DIAGNOSTIC — not a publication claim"


def csv_rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finish(fig: plt.Figure, name: str) -> None:
    fig.text(0.5, 0.01, FOOTER, ha="center", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIGURES / name, dpi=150, metadata={"Software": "BASS RF04-POL-01"})
    plt.close(fig)


def p1() -> None:
    rows = csv_rows("substep_convergence.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    styles = {
        "endpoint_linear_inner_substeps": ("o", "#b54b4b"),
        "source_panels_inner_1": ("s", "#3268a8"),
        "source_panels_inner_2": ("^", "#438c57"),
    }
    for policy, (marker, color) in styles.items():
        selected = [r for r in rows if r["profile"] == "curved_callback" and r["policy"] == policy]
        x = np.array([int(r["resolution"]) for r in selected])
        y = np.array([float(r["error"]) for r in selected])
        ax.loglog(x, y, marker=marker, color=color, label=policy)
    x = np.array([1, 2, 4, 8, 16], dtype=float)
    ax.loglog(x, 0.012 / x**2, "k--", alpha=0.55, label="second-order guide")
    ax.set(title="P1: curved-background substep candidates", xlabel="outer source panels / inner subdivisions", ylabel="max state error vs callback-8192")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    finish(fig, "P1_substep_convergence.png")


def p2() -> None:
    rows = [r for r in csv_rows("stencil_feasibility.csv") if r["status"] == "PASS"]
    grids = list(dict.fromkeys(r["grid"] for r in rows))
    algorithms = list(dict.fromkeys(r["candidate"] for r in rows))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    x = np.arange(len(grids))
    width = 0.24
    for i, algorithm in enumerate(algorithms):
        selected = [next(r for r in rows if r["grid"] == grid and r["candidate"] == algorithm) for grid in grids]
        offset = (i - 1) * width
        axes[0].bar(x + offset, [float(r["angular_moment_error"]) for r in selected], width, label=algorithm)
        axes[1].bar(x + offset, [float(r["profile_trace_error"]) for r in selected], width, label=algorithm)
    for ax, ylabel in zip(axes, ("angular moment error", "nonconstant profile trace error")):
        ax.set_xticks(x, grids, rotation=25, ha="right")
        ax.set_yscale("log")
        ax.set_ylabel(ylabel)
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].set_title("P2: all 12 convex candidates pass")
    axes[1].set_title("Different accepted candidates give different errors")
    axes[0].legend(fontsize=7)
    finish(fig, "P2_stencil_feasibility.png")


def p3() -> None:
    data = json.loads((ROOT / "remap_support_mutations.json").read_text(encoding="utf-8"))
    bounds = data["predeclared_bounds"]
    labels = [str(item["minimum_transport_dot"]) for item in bounds]
    accepted = [item.get("accepted_real_donor_calls", 0) for item in bounds]
    rejected = [item.get("rejected_real_donor_calls", 12 - a) for item, a in zip(bounds, accepted)]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
    x = np.arange(len(labels))
    axes[0].bar(x, accepted, label="accepted", color="#438c57")
    axes[0].bar(x, rejected, bottom=accepted, label="rejected", color="#b54b4b")
    axes[0].set(xticks=x, xticklabels=labels, xlabel="predeclared minimum_transport_dot", ylabel="real donor calls", title="P3: two bounds remain admissible")
    axes[0].legend()
    mutations = data["hostile_mutations"]
    axes[1].bar([m["id"] for m in mutations], [1, 1], color="#b54b4b")
    axes[1].set(ylim=(0, 1.2), ylabel="fail-closed (1=yes)", title="Hostile remap mutations")
    axes[1].tick_params(axis="x", rotation=20)
    for ax in axes:
        ax.grid(True, axis="y", alpha=0.25)
    finish(fig, "P3_support_mutations.png")


def p4() -> None:
    rows = csv_rows("composition_differential.csv")
    candidates = [r for r in rows if r["record_type"] == "CANDIDATE"]
    mutants = [r for r in rows if r["record_type"] == "MUTANT"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for name, marker in (("collision_outer", "o"), ("geometry_outer", "s")):
        selected = [r for r in candidates if r["name"] == name]
        axes[0].loglog([float(r["h"]) for r in selected], [float(r["max_abs_error"]) for r in selected], marker=marker, label=name)
    axes[0].invert_xaxis()
    axes[0].set(xlabel="step size h", ylabel="max error vs independent dense reference", title="P4: both compositions are first order")
    axes[0].grid(True, which="both", alpha=0.25)
    axes[0].legend(fontsize=8)
    axes[1].bar([r["name"].removeprefix("mutant_") for r in mutants], [float(r["max_abs_delta_from_pristine"]) for r in mutants], color=["#b54b4b", "#d39b38", "#d39b38"])
    axes[1].set_yscale("log")
    axes[1].set(ylabel="max state delta from pristine", title="Compiled-action mutations")
    axes[1].tick_params(axis="x", rotation=20)
    axes[1].grid(True, axis="y", alpha=0.25)
    finish(fig, "P4_composition_differential.png")


def p5() -> None:
    data = json.loads((ROOT / "history_association_receipt.json").read_text(encoding="utf-8"))
    fixed = data["candidates"]["fixed_eulerian"]
    lag = data["candidates"]["evolved_lagrangian"]
    diff = data["candidate_difference"]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
    axes[0].bar(["fixed Eulerian", "evolved Lagrangian"], [fixed["minimum_coherency_eigenvalue"], lag["minimum_coherency_eigenvalue"]], color=["#3268a8", "#438c57"])
    axes[0].set(ylim=(0.30, 0.312), ylabel="minimum coherency eigenvalue", title="P5: both histories remain physical")
    axes[0].grid(True, axis="y", alpha=0.25)
    labels = ["state max diff", "observable diff", "direction shift"]
    values = [diff["state_max_abs_after_remap_to_fixed"], diff["observable_absolute"], lag["maximum_direction_shift"]]
    axes[1].bar(labels, values, color=["#6f58a8", "#a8648e", "#d39b38"])
    axes[1].set_yscale("log")
    axes[1].set(ylabel="absolute difference", title="Mutually different valid semantics")
    axes[1].tick_params(axis="x", rotation=20)
    axes[1].grid(True, axis="y", alpha=0.25)
    finish(fig, "P5_history_association.png")


def main() -> None:
    p1()
    p2()
    p3()
    p4()
    p5()


if __name__ == "__main__":
    main()
