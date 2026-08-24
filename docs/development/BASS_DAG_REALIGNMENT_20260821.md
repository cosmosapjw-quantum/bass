# BASS DAG Realignment — 2026-08-21

## Decision

The project returns to the original architecture path:

```text
formula authority
→ generated Type-II Rust reference kernel
→ Kato runtime reference
→ conservation/quadrature seal
→ isolated production migration
```

The later polarized collision/Liouville/remap work is retained as a valuable
reference lane, but it no longer occupies the production critical path.

The critical path is now gated by two parallel prerequisites:

1. `G-DYN-MANIFOLD-VI0`: the first non-Type-II manifold classification;
2. `P-MIG-II-PREFLIGHT`: an explicit BASS-owned production host/interface
   contract with no production mutation.

Only after both pass may `G-PRODUCTION-MIGRATION-II-0` begin.

## Why the realignment is necessary

PR #5–#7 established the original reference path: symbolic lowering, actual
Rust compilation, Kato exponential/phi actions, scalar conservation and
quadrature. Subsequent PRs added useful polarized and numerical capabilities,
but the Type-II exemplar gradually became a self-contained polarized solver
program. Cross-family classification and the production landing zone remained
open.

This is scope drift, not evidence that the polarized work is invalid. The
correction is to restore lane ownership and join conditions rather than delete
verified artifacts.

## Authoritative lanes

### Lane A — Type-II reference and production mainline

```text
PR #5  G-SYMBOLIC-LOWERING-II
  ↓
PR #6  G-RUNTIME-KATO-II
  ↓
PR #7  G-CONSERVATION-II + G-QUAD-II
  ↓
P-MIG-II-PREFLIGHT
  └────────────── JOIN J1 ──────────────┐
                                         ↓
                               G-PRODUCTION-MIGRATION-II-0
                                         ↓
                               G-PRODUCTION-MIGRATION-II-1
```

`G-PRODUCTION-MIGRATION-II-0` must use the full-dimensional Arnoldi/Pade13
backend as the default reference. It must also restore two originally requested
checks that are not durably closed in PR #6:

- an independent frozen-collision uniformization auditor;
- a direct old midpoint-frozen AEM2 versus Kato-AEM2 order comparison.

The repaired adaptive Krylov backend remains an optional same-physics backend
until a real hierarchy benchmark establishes same-output/same-tolerance parity
and a practical advantage.

### Lane B — cross-family manifold classification

```text
G-DYN-MANIFOLD-VI0
  ↓
G-DYN-MANIFOLD-VII0
  ↓
G-DYN-MANIFOLD-VIII
  ↓
class B
  ↓
IX / exceptional branches
```

The first deliverable is classification, not a solver. No Type-II relation
`P=P(v2)` may be copied into VI0 without deriving the actual manifold
coordinates and tangent projector derivatives.

### Lane C — polarized reference R&D

```text
PR #8  finite-tilt polarized collision/Kato
  ↓
PR #9  adaptive Krylov repair
  ↓
PR #10 physical-screen/AP safety
  ↓
PR #11 ray-level tensor Liouville
  ↓
PR #13 local tensor/Stokes adapter
  ↓
PR #14 common-screen convex remap
  ↓
B2B local package / noncanonical upload
```

This lane is frozen after PR #14 until Join J1 and the B1 convention
reconciliation are recorded. No `G-POL-LIOUVILLE-II-C`, E/B, observed-sky,
Wigner or map-level output gate is opened before then.

## Join J1

All conditions are mandatory:

```text
G-DYN-MANIFOLD-VI0 classification       PASS
P-MIG-II-PREFLIGHT                       PASS
B1 internal V convention                 RECONCILED
PR #5–#7 reference baseline              UNCHANGED
production owner / rollback boundary     EXPLICIT
```

Join J1 permits only an isolated Type-II production reference path. It does not
permit a claim of cross-family production readiness.

## Production ownership

BASS owns the final runtime decision and the geometry–transport–collision
contract. External context providers, diagnostics and observable/statistics
layers may annotate or audit the decision, but may not silently mutate the BASS
runtime state or claim authority over production branch dispatch.

The preflight must identify:

- canonical production repository and branch;
- host state and generated Type-II state adapters;
- collision, Kato and exp/phi callback interfaces;
- error and claim labels;
- exact offline reproduction command from the crate root;
- rollback and quarantine boundaries;
- the distinction between lab/reference code and production-owned code.

## Frozen work and non-authority artifacts

The following remain preserved but are not current production authorities:

- the local B2B package;
- `agent/g-pol-liouville-ii-b2b-upload` and its transient chunks/workflow;
- the superseded local `packed[8]=+V/2` diagnostic package;
- temporary PR #12 and its staging branch.

No result may be promoted from these artifacts without a canonical branch,
parent/tree verification and a focused PR.

## Stacked-PR policy

Each PR must own one reviewable change and maintain a fully linear parent chain.
A lower-layer correction must be made in the owning layer and propagated
up-stack; it must not be hidden in an unrelated upper layer. Temporary upload
or workflow branches are never scientific authorities.

## Immediate execution order

1. Publish this realignment ledger on top of PR #7.
2. Publish the B1 convention reconciliation on top of PR #14.
3. Close temporary PR #12 without merge.
4. Start `G-DYN-MANIFOLD-VI0` and `P-MIG-II-PREFLIGHT` in parallel.
5. Review Join J1; only then open isolated production migration.
