#!/usr/bin/env python3
from pathlib import Path
import json
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RECEIPT = HERE.parent / "runtime" / "G_POL_LIOUVILLE_II_B2B_RECEIPT.json"
OUT = HERE / "plots"
OUT.mkdir(exist_ok=True)

data = json.loads(RECEIPT.read_text())
metrics = data["metrics"]

levels = list(range(len(metrics["spatial_rms_errors"])))
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.semilogy(levels, metrics["spatial_rms_errors"], marker="o", label="spatial RMS")
ax.semilogy(levels[: len(metrics["roundtrip_diffusion"])], metrics["roundtrip_diffusion"], marker="s", label="forward/backward diffusion")
ax.set_xlabel("icosphere refinement level")
ax.set_ylabel("maximum / RMS absolute error")
ax.set_title("B2B spatial refinement and repeated-remap diffusion")
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "g_pol_liouville_b2b_refinement.png", dpi=180)
plt.close(fig)

labels = ["characteristic", "remap", "combined"]
values = [metrics["characteristic_error"], metrics["remap_error"], metrics["combined_error"]]
fig, ax = plt.subplots(figsize=(6.2, 4.0))
ax.bar(labels, [max(v, 1e-18) for v in values])
ax.set_yscale("log")
ax.set_ylabel("absolute error")
ax.set_title("B2B separated characteristic and remap errors")
fig.tight_layout()
fig.savefig(OUT / "g_pol_liouville_b2b_error_split.png", dpi=180)
plt.close(fig)
