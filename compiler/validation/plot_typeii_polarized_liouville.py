"""Generate deterministic convergence figures for G-POL-LIOUVILLE-II-A.

The script reads the machine-readable runtime receipt rather than parsing test
stdout.  It creates one figure per convergence claim and intentionally leaves
Matplotlib's default color cycle unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "compiler/runtime/G_POL_LIOUVILLE_II_A_RECEIPT.json"
OUTPUT = ROOT / "artifacts"


def _second_order_reference(x: np.ndarray, y0: float, x0: float) -> np.ndarray:
    return y0 * (x0 / x) ** 2


def _save_generic(receipt: dict[str, object]) -> None:
    numerics = receipt["numerics"]
    substeps = np.asarray([4.0, 8.0, 16.0, 32.0])
    errors = np.asarray(numerics["generic_errors"], dtype=float)
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.loglog(substeps, errors, marker="o", label="Type-II characteristic error")
    ax.loglog(
        substeps,
        _second_order_reference(substeps, errors[0], substeps[0]),
        linestyle="--",
        label="second-order reference",
    )
    ax.set_xlabel("substeps")
    ax.set_ylabel("max composite error")
    ax.set_title("Polarized Liouville Lie-midpoint convergence")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT / "g_pol_liouville_ii_a_convergence.png", dpi=144)
    plt.close(fig)


def _save_source(receipt: dict[str, object]) -> None:
    source = receipt["numerics"]["source_trajectory"]
    substeps = np.asarray([1.0, 2.0, 4.0, 8.0])
    errors = np.asarray(source["errors"], dtype=float)
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.loglog(substeps, errors, marker="o", label="source-trajectory error")
    ax.loglog(
        substeps,
        _second_order_reference(substeps, errors[0], substeps[0]),
        linestyle="--",
        label="second-order reference",
    )
    ax.set_xlabel("substeps per 0.0005 interval")
    ax.set_ylabel("max composite error")
    ax.set_title("Source-derived Type-II trajectory convergence")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT / "g_pol_liouville_ii_a_source_trajectory.png", dpi=144)
    plt.close(fig)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    receipt = json.loads(RECEIPT.read_text())
    _save_generic(receipt)
    _save_source(receipt)


if __name__ == "__main__":
    main()
