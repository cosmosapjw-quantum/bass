# SYNC-MAP-02F-R2C — BASS projection and closure certificate graph

## Scope

This is a **BASS-only** semantic and exact-witness stage. It follows the native-green formula-consumer role graph from PR #116 and precedes any consumer-binding or provider admission.

It does not modify or execute REC, REI, or HTT source. It does not claim runtime parity, a production closure, polarized transport, or science readiness.

## Why this stage exists

The BASS state registry distinguishes six state surfaces:

```text
GRID_F_Q_E
PSTF_F_AELL_Q
J_I_AELL
G_ANGULAR_ENERGY
FLUID_COMPONENT_SUMMARY
POLARIZED_COHERENCY
```

Only `GRID_F_Q_E <-> PSTF_F_AELL_Q` is a candidate representation equivalence for the same frequency-resolved distribution. The `J` and `G` surfaces are generally noninvertible projections, fluid variables require exchange ledgers, and scalar intensity does not determine a polarized coherency state.

R2C turns these distinctions into typed certificate families and mutation-sensitive exact witnesses.

## Certificate families

### `ANGULAR_REPRESENTATION_CERTIFICATE`

Required for grid/PSTF analysis and synthesis. It records the basis, normalization, sphere measure, quadrature or transform, exactness degree, `ell_target`, `ell_work`, both round-trip residuals, a stability or conditioning bound, and input/output state identities.

A linear analysis-synthesis round trip does **not** by itself certify multiplication by an angle-dependent source.

### `SPECTRAL_PROJECTION_CLOSURE_CERTIFICATE`

Required for `PSTF_TO_J` and `GRID_TO_G`. It records the spectral measure and weight, source-operator class, source-coefficient representation, separate output/source/work orders in the radial and angular directions, projection residual, tail or quadrature bound, nonlocal-frequency policy, and source authority.

For polynomial-like radial bases a sufficient product-space condition is

```text
radial_work_order >= radial_output_order + radial_source_order.
```

For spherical-harmonic products a sufficient angular condition is

```text
angular_work_rank >= angular_output_rank + angular_source_rank.
```

An exact invariant-subspace proof may replace these sufficient bounds.

### `MOMENT_EXCHANGE_CERTIFICATE`

Required when a kinetic state is reduced to fluid moments. It records normalization, species inventory, radiation and matter four-forces, the total residual, number/energy/momentum exchange ledgers, units, and source authority.

With the convention used here,

```text
G_rad^a + G_mat^a = 0
```

must hold for the combined system.

### `POLARIZED_SCREEN_CERTIFICATE`

The scalar-to-polarized relation remains prohibited. A polarized state needs a screen projector, projector and orthogonality residuals, trace-two check, transported screen basis, the screen U(1) connection, a spin-phase convention, a polarized collision operator, and coherency Hermiticity/positivity policy.

## Exact witnesses

The Wolfram source contains six fixed exact controls:

1. Three-node Gauss-Legendre analysis/synthesis of an axisymmetric degree-two distribution.
2. A radial product `(1+2 q)(3+4 q)=3+10 q+8 q^2`, showing that work order one aliases an order-two term.
3. Two frequency-bin states with equal `G` and unequal frequency-dependent losses.
4. Equal-and-opposite radiation/matter four-force cancellation.
5. The rational screen direction `e=(3/5,4/5,0)` with `S=I-e e^T`, `S^2=S`, `S e=0`, and `Tr S=2`.
6. Two coherency matrices with the same scalar intensity and different polarization.

These are bounded exact witnesses, not production runtime validation.

## Local validation

```bash
bash scripts/run_sync_map02f_r2c_projection_closure_local.sh
```

Expected gate:

```text
Python verifier                    PASS
Python unittest                    9/9
Wolfram MUnit                     17/17
failed / not evaluated             0 / 0
strict JSON round trip             PASS
exit code                          0
```

Outputs:

```text
artifacts/sync_map02f_r2c_projection_closure/
  SYNC_MAP_02F_R2C_WOLFRAM_REPLAY_RECEIPT.json
  SYNC_MAP_02F_R2C_LOCAL_VALIDATION_SUMMARY.json
  SHA256SUMS
```

## Literature role

- Schween and Reville support conversion between tensor and spherical-harmonic coefficients of the same distribution.
- Huffenberger and Wandelt support explicit band-limit and sampling contracts for exact spin spherical-harmonic transforms.
- Pitrou reviews relativistic radiative transport, momentum moments, collisions, and polarization geometry.

These references have `authority_effect=NONE` over BASS signs, hashes, source status, stage acceptance, or promotion.

## Claim boundary

```text
CERTIFICATE_SCHEMA_AND_EXACT_WITNESSES_ONLY
NO_GRID_PSTF_RUNTIME_PARITY
NO_J_OR_G_SPECTRAL_CLOSURE_ADMISSION
NO_FLUID_EXCHANGE_RUNTIME_PASS
NO_SCREEN_BASIS_TRANSPORT_IMPLEMENTATION
NO_POLARIZED_COLLISION_RUNTIME
NO_CONSUMER_PROVIDER_OR_SCIENCE_PROMOTION
```
