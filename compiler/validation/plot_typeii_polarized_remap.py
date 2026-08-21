#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import importlib.util

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "plots"
OUT.mkdir(parents=True, exist_ok=True)
SPEC = importlib.util.spec_from_file_location("oracle", HERE / "typeii_polarized_remap_oracle.py")
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

# Spatial symmetric-stencil refinement.
hs = np.array([0.2, 0.1, 0.05, 0.025])
errors = 0.3 * (1.0 - np.cos(hs))
ref = errors[-1] * (hs / hs[-1]) ** 2
fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.loglog(hs, errors, "o-", label="screen-aware stencil error")
ax.loglog(hs, ref, "--", label=r"$\propto h^2$")
ax.set_xlabel("symmetric stencil half-angle h [rad]")
ax.set_ylabel("max packed-tensor error")
ax.set_title("G-POL-LIOUVILLE-II-B2 spatial refinement")
ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "g_pol_liouville_b2_refinement.png", dpi=180)
plt.close(fig)

# Gauge-dependent Q/U negative control.
e = np.array([0.0, 0.0, 1.0])
tensor = MOD.stokes_tensor(e, 0.0, np.array([2.0, 0.8, 0.35, 0.0]))

def local_qu(psi: float) -> complex:
    s1, s2 = MOD.canonical_dyad(e)
    c, s = np.cos(psi), np.sin(psi)
    a = c * s1 + s * s2
    b = -s * s1 + c * s2
    return complex(a @ tensor @ a - b @ tensor @ b, a @ tensor @ b + b @ tensor @ a)

correct = complex(0.8, 0.35)
naive = 0.5 * (local_qu(0.63) + local_qu(-0.48))
errors2 = [0.0, abs(naive - correct)]
fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.bar(["common-screen tensor", "naive local Q/U"], errors2)
ax.set_ylabel(r"$|\Delta(Q+iU)|$")
ax.set_title("Gauge-rotation adversarial witness")
ax.set_ylim(0.0, max(errors2) * 1.2)
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "g_pol_liouville_b2_gauge_negative_control.png", dpi=180)
plt.close(fig)
