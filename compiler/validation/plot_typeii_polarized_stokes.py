#!/usr/bin/env python3
from pathlib import Path
import json, math
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'plots'; OUT.mkdir(exist_ok=True)
angles=np.linspace(-math.pi, math.pi, 257)
q,u=0.7,-0.3
z=(q+1j*u)*np.exp(-2j*angles)
fig,ax=plt.subplots(figsize=(6.4,4.0))
ax.plot(angles,z.real,label="Q passive")
ax.plot(angles,z.imag,label="U passive")
ax.set_xlabel(r"$\psi$")
ax.set_ylabel("Stokes component")
ax.set_title("B1 passive spin-2 phase")
ax.legend()
fig.tight_layout(); fig.savefig(OUT/'g_pol_liouville_b1_spin_phase.png',dpi=180); plt.close(fig)

m=json.loads((HERE/'typeii_polarized_stokes_oracle.json').read_text())
keys=['passive_phase_max_abs_error','active_phase_max_abs_error','active_passive_inverse_max_abs_error','invariant_max_abs_defect','handedness_max_abs_error','v_zero_max_abs_generation','canonical_p8_sign_error']
fig,ax=plt.subplots(figsize=(7.2,4.1))
vals=[max(float(m[k]),1e-18) for k in keys]
ax.bar(range(len(keys)),vals)
ax.set_yscale('log'); ax.set_ylabel('absolute defect')
ax.set_xticks(range(len(keys)),['passive','active','inverse','invariants','handedness','V=0','p8 sign'],rotation=25,ha='right')
ax.set_title('B1 independent finite-angle defects')
fig.tight_layout(); fig.savefig(OUT/'g_pol_liouville_b1_invariant_defects.png',dpi=180); plt.close(fig)
