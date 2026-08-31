# RF-04 LOCAL-01 PHYS-MATH-CODE audit

Disposition: `BLOCKED_BY_MISSING_AUTHORIZED_V2_PUBLIC_MAPPING`

Reviewed commit/tree:

```text
c27643051bf3f1baca257b87cb0264bae9d61da6
80d3487b4cac8ae7fa833b17a49caa75c49a7124
```

The reviewed code diff is limited to five LOCAL-01-allowlisted paths and passes
`git diff --check`.

## Findings

- P0: none.
- P1: the source-owned Liouville donor is linked only through test-only kinetic
  modules. The v2 PyO3 module explicitly reserves registration, and
  `register_rf04` exposes only v1. The rebuilt production wheel confirms that
  all three v1 symbols exist and all three v2 symbols are absent. R5 explicitly
  forbids inferring the missing symbol, receipt, serialization, or error-mapping
  authority. This is a blocking authority gap, not permission to implement an
  ad-hoc bridge.
- P2: the six focused native-owner tests are valid but partial. They establish
  no-split, nested split, multiple root panels, one bounded midpoint failure,
  and both nonfinite donor regressions. They do not close ordinary-corpus full
  carrier parity, callback fractions/order, post-recursion carrier/projection/
  realizability failures, serialization consumers, or Python success/error
  mapping.

## Positive scoped checks

- Split and accepted-leaf counters use checked `u64` arithmetic, while the
  recursion depth is bounded to eight. Overflow is source-reviewed and not
  safely executable at runtime.
- Validator hardening replaces optimization-removable Python assertion gates
  with explicit exceptions and uses `git --no-replace-objects` for internal
  blob reads. Its normal and optimized unit tests pass, and the historical
  old-as-candidate mismatch remains detected.
- The safety delta uses existing `NonFiniteBackground` and `NonFiniteOutput`
  errors. It introduces no new public error type or fabricated receipt.
- The production wheel was built with Rust/Cargo 1.94.1, Python 3.12.13,
  maturin 1.14.1, and offline/locked Cargo operation. The clean isolated
  install proves v1 remains available and fail-closed while v2 is missing.

No repair follows from this audit: inventing the missing public mapping would
cross the controlling authority boundary. `LOCAL-01` remains non-PASS and
`LOCAL-02` remains `NOT_RUN`.
