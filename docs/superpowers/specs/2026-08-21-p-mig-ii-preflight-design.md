# P-MIG-II-PREFLIGHT Design

## Purpose

Identify the canonical production landing zone and freeze the interface for an
isolated Type-II reference migration before any production code is modified.

## Non-mutation rule

This gate is documentation, inventory and executable contract tests only. It
must not change a production solver, select the adaptive backend by default, or
claim cross-family readiness.

## Required decisions

1. Canonical production repository, branch and Rust crate.
2. BASS-owned runtime decision point and rollback boundary.
3. Adapter between the five-state generated Type-II chart
   `(SigmaPlus,SigmaMinus,Sigma13,N1,v2)` and the host state.
4. Exact time/rate/opacity normalization and unit contract.
5. Collision, projector, Kato, exp and phi-action callback interfaces.
6. Reference versus optional numerical backends.
7. Error taxonomy and machine-readable claim labels.
8. Crate-root locked/offline reproduction command.
9. Quarantine boundary for reference/lab-only code.

## Reference migration interface

The preflight defines, but does not yet install, a narrow host adapter:

```text
host background state
→ validated TypeIIState adapter
→ generated F/JVP/P/Pv/K/C actions
→ full-Arnoldi exp/phi reference backend
→ host output/state update
```

Every conversion is explicit and roundtrippable. No local-observer boost,
statistics layer or map convention enters this interface.

## Numerical authority

`G-PRODUCTION-MIGRATION-II-0` will initially use the PR #6 full-dimensional
Arnoldi/Pade13 backend. The repaired adaptive Krylov backend is opt-in until a
real hierarchy same-physics/same-tolerance benchmark passes.

The migration acceptance plan restores:

- scalar frozen-collision uniformization as an independent auditor;
- dense Python small-system oracle;
- direct old midpoint-frozen AEM2 versus Kato-AEM2 order comparison;
- `alpha={1,1e3,1e5}` source-derived stiff regression;
- production-interface conservation and rollback checks.

Uniformization is an auditor only for a scalar collision lane whose generator
satisfies the required positivity/rate structure. It is not silently extended
to the full polarized coherency operator.

## Outputs

```text
docs/development/P_MIG_II_PREFLIGHT.md
docs/development/P_MIG_II_HOST_INVENTORY.json
runtime/contracts/typeii_production_contract.rs
runtime/contracts/tests/typeii_production_contract.rs
docs/development/P_MIG_II_ACCEPTANCE_MATRIX.json
```

The Rust files are compile-only interfaces and mock adapters. They must not be
wired into production execution in this gate.

## Acceptance

- one canonical host is named with commit/tree and crate root;
- all candidate hosts are classified as production, reference, lab or
  quarantine;
- state and unit adapters roundtrip without loss;
- callback ownership and error semantics are explicit;
- full-Arnoldi remains default reference;
- uniformization and old-AEM2 comparator plans are executable and scoped;
- rollback requires one branch/ref change, not data migration;
- no production file or runtime dispatch is changed.
