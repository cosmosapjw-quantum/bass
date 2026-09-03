# SYNC-MAP-02F-R2 — BASS state-surface registry bootstrap

This stacked BASS-only node begins at exact parent commit
`8b73919e0e2a2326c338c796ac80b0684fe49db1`, after the native PR #110
local replay passed at source head
`65be780c06b014e8b699a8af4835b2290f39b252`.

It does **not** mutate REC, REI, or HTT. Those repositories remain future
consumers only.

## State surfaces

The registry separates six distinct mathematical state types:

1. `GRID_F_Q_E`: frequency-resolved distribution `f(t,q,e)`;
2. `PSTF_F_AELL_Q`: frequency-resolved angular multipoles `F_Aell(t,q)`;
3. `J_I_AELL`: momentum-integrated weighted moments;
4. `G_ANGULAR_ENERGY`: radially integrated angular energy;
5. `FLUID_COMPONENT_SUMMARY`: finite covariant moments such as
   `rho,p,q_a,pi_ab`;
6. `POLARIZED_COHERENCY`: screen-dependent coherency or spin multipoles.

`GRID_F_Q_E` and `PSTF_F_AELL_Q` are representation-equivalence candidates
only after basis, measure, band-limit, and forward/inverse residual contracts
are fixed. Runtime parity remains withheld.

`J_I_AELL`, `G_ANGULAR_ENERGY`, and fluid summaries are noninvertible
projections in general. They must never be relabelled as exact state-equivalent
consumer implementations. A frequency-dependent source acting on `G(e)` needs
source-grid quadrature, an invariant radial basis, or a declared spectral
closure certificate.

The polarized surface cannot be inferred from a scalar state. It requires at
least the screen projector, screen-basis transport, spin-phase convention, and
polarized collision operator.

## Exact two-bin closure witness

For

```text
f_A=(1,0),  f_B=(0,1),  G_A=G_B=1,
```

frequency-dependent multiplicative losses are

```text
L_A=chi_1,  L_B=chi_2.
```

Thus `G(e)` alone cannot determine the source unless
`chi_1=chi_2=chi_eff` on the represented spectral subspace.

## Local validation

```bash
bash scripts/run_bass_state_surface_registry_local.sh
```

Expected gates:

```text
Python verifier          PASS
Python unittest          7/7
Wolfram MUnit            7/7
failed/not evaluated     0/0
```

The current branch provides source and contracts only. Native replay is still
required before this node can be promoted.

## Literature role

Schween–Reville (2022) supports conversion between Cartesian tensor and
spherical-harmonic expansions of the same distribution coefficients. Moment
closure literature, including Pons–Miralles, supports explicit closure typing
for reduced angular moment systems. These references are regression evidence
only and have no authority over BASS signs, source ownership, semantic hashes,
or stage promotion.
