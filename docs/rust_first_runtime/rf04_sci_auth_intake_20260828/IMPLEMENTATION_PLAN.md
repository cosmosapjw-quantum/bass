# Implementation Plan — SCI-AUTH-04 then RF-04

## 0. Immutable inputs

```text
RF-03 base branch: agent/architecture/rust-first-rf03-20260828-r2
RF-03 head: 6e53664d56694f7a7ad5f65be262302d5c8866b2
RF-03 tree: bb743717e8115821d72268d8384dc5cc7cc11975
RF-03 PR: #45 draft/unmerged

SCI-AUTH-04 base branch: agent/architecture/rust-first-rf02b-20260826-r1
SCI-AUTH-04 head: 0563c080e54fcd90d6160bec35e4f20d240d8d2e
SCI-AUTH-04 tree: 40ae99f9e7465d6332e98b65a5269a1f71eadfb5
SCI-AUTH-04 base PR: #32 draft/unmerged

Compiled work graph blob:
026afd0348d29b0afa90d30fcf8a11b9cf1187dd
```

## 1. SCI-AUTH-04

Create a clean isolated worktree and branch:

```text
agent/authority/sci-auth-04-20260828-r1
```

Inventory existing authority labels and domains without changing any
coefficient, generated source, runtime source, tolerance, or claim. Define a
typed manifest schema for background, collision, projector, Kato and
thermodynamics; explicitly classify historical/surrogate thermodynamics.

Write the verifier and hostile fixtures first. Required failures include
overbroad scope, missing authority, surrogate promoted as fresh, mismatched
generated manifest and claim policy. Run only the compiled primary/negative
checks and changed manifest tests.

Freeze one implementation commit plus at most one review/evidence repair.
Ordinary push and one draft authority PR. Read back exact head/tree/path set and
evidence. `PASS_SCI_AUTH_04_VALIDATOR` does not promote scientific authority.

## 2. RF04-INTAKE-00

In a read-only step, resolve:

- exact RF-03 terminal head/tree/evidence;
- exact SCI-AUTH-04 terminal head/tree/evidence;
- typed authority manifest identities;
- RF-04 source-tree and route-capability identities.

No code mutation occurs. Any mismatch is
`BLOCKED_PREDECESSOR_IDENTITY`, not a request for a new contract.

## 3. Genuine RF-04 RED

Create:

```text
agent/architecture/rust-first-rf04-20260828-r1
```

from exact RF-03 head `6e53664d56694f7a7ad5f65be262302d5c8866b2`.

Freeze the current Rust kinetic tree and Python oracle paths. The existing
Rust kinetic tree already contains collision, quadrature, polarized collision,
hierarchy and transport modules; do not rewrite working code solely to satisfy
directory names. Establish actual ownership and move only remaining
production-inner-loop paths.

Write real failing tests for:

1. direction-dependent right kernel and inverse-transpose left invariant;
2. projector idempotence and moving-equilibrium connection/commutator;
3. route-specific conservation, positivity and equilibrium null;
4. fixed-grid versus paired/AP-corrected quadrature capability separation;
5. projected-residual-only Krylov certificate on hostile non-normal matrices;
6. explicit I/Q/U/V route capabilities and typed unsupported errors;
7. scalar portable versus independent-work parallel deterministic identity.

Record the genuine RED before implementation.

## 4. Implementation

Keep formulas, signs, state order, tolerances, grids and seeds unchanged.
Use modular Rust ownership and PyO3 registration-only wiring. Python may remain
API/config/oracle but not production inner loop or silent fallback.

Keep no-fast-math and a scalar portable path. Use SoA/vectorizable layouts only
where they preserve numerical contracts. Parallelize independent angular/batch
work only, with deterministic order and isolated failures.

## 5. Targeted verification

Run only:

```text
pytest -q tests/rf04/test_kinetic_contract.py
pytest -q tests/rf04 -k 'mutation or nonnormal or unsupported or fixed_grid'
affected Rust selectors with rf04_ filter
changed Type-II/Kato/conservation/quadrature/polarization receipts only when invalidated
fresh no-index verified native trajectory/batch call
```

Generate and read four bounded diagnostics:

1. right/left invariant residuals by rate route;
2. projector/idempotence and moving-connection residuals;
3. quadrature conservation/equilibrium/positivity margins by capability;
4. non-normal Krylov projected residual versus actual error, annotated with
   polarization capability/fail-closed routes.

Hostile mutations must visibly fail the corresponding gates.

## 6. Review, evidence and delivery

Perform PHYS-MATH then PHYS-MATH-CODE once. Repair only reproduced P0/P1
findings and perform at most one differential re-review.

If native bytes change, build a content-addressed delta and fresh no-index
restore proof. Record exact source, route, authority, tests, figures, mutation,
review and native identities without claiming performance.

Ordinary push, open one stacked draft RF-04 PR against the RF-03 branch, exact
remote readback, then stop. No merge or ready transition.
