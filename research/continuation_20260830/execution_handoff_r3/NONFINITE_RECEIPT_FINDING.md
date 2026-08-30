# Reproduced pre-existing nonfinite-boundary findings

## Classification

```text
TWO_REPRODUCED_PREEXISTING_BOUNDARY_REDS
NOT_INTRODUCED_BY_TELEMETRY_PATCH
REPRODUCED_ON_NONAUTHORITATIVE_PATCHED_SANDBOX
PREEXISTING_BASIS_STATIC_UNCHANGED_BASELINE_PATHS
BASELINE_EXECUTION_NOT_RUN
SEVERITY_UNCLASSIFIED_PENDING_AUTHENTICATED_OWNER_CONTRACT
DO_NOT_FIX_OUTSIDE_THE_AUTHENTICATED_LOCAL_EVIDENCE_WORKTREE
```

An independent late PHYS-MATH read found two source-owned boundaries where
finite inputs can return an otherwise successful result containing nonfinite
derived values. The telemetry patch does not touch either relevant
pre-existing arithmetic or validation boundary.

## 1. Nonfinite transport receipt

With a zero geometry background except `expansion = 1.0`, finite
`step = 1.0e308`, one root panel, and a valid screen projector, the tensor scale
underflows to finite zero and the packed coherency remains finite. The
function checks only the packed coherency before constructing the result.
`log_energy_shift` remains finite at approximately `-1.0e308`, but
`log_bolometric_shift = 4.0 * log_energy_shift` becomes `-inf`; the call returns
`Ok` rather than a typed failure.

The scratch regression test failed exactly at:

```text
assertion failed: receipt.log_bolometric_shift.is_finite()
```

Command:

```sh
cargo test --lib --locked --offline \
  finite_inputs_do_not_return_a_nonfinite_energy_receipt \
  -- --nocapture --test-threads=1
```

Result: exit `101`, one intended test failure. Raw log SHA-256:

```text
326f26db8342c464453dfae148f6dc1dff7e332dba07cc635cda84120580066b
```

### Provenance and scope

Exact static comparison shows the baseline donor contains the same
`4.0 * log_energy_shift` construction and lacks a final scalar-finiteness gate.
The immutable telemetry patch adds counters/error plumbing only; it has no diff
hunk changing `log_energy_shift` or `log_bolometric_shift`. The executed RED was
on the patched sandbox; baseline execution was not run. Thus the evidence rules
out a telemetry regression statically, but does not replace authenticated
baseline execution or severity classification.

Because this workspace lacks the genuine local RED chain and public/PyO3
schema, no production fix is authored or pushed here. After the preserved-chain
gate passes, retain separate baseline and exact-patched-donor runs, then
classify severity under the project contract. Final R4 makes this a mandatory
LOCAL-01 gate regardless of severity: require a fully finite success or an
existing authorized typed failure through the real carrier and Python mapping.
If the candidate still violates the gate, make the smallest source-owned
authorized correction in a separate safety commit above the frozen telemetry
delta. Do not silently clamp, saturate, fabricate a receipt, or invent a new
public error schema from this document; stop if error authority is ambiguous.

## 2. Nonfinite derived Type-II background

`typeii_background_from_state` validates that its five input state values are
finite before constructing the background, but does not revalidate the derived
fields after multiplication and addition. With finite state
`[f64::MAX, 0.0, 0.0, 1.0, 0.0]`, a derived shear component overflows and the
adapter returns `Ok` with a nonfinite background.

The scratch regression test failed exactly at:

```text
assertion failed: values.into_iter().all(f64::is_finite)
```

Command:

```sh
cargo test --lib --locked --offline \
  finite_typeii_state_does_not_return_a_nonfinite_background \
  -- --nocapture --test-threads=1
```

Result: exit `101`, one intended test failure. Raw log SHA-256:

```text
cff06d701f4d581fbdb7f3ddd6c0e305ddc10e6e10297fd57f3f164c41ae8756
```

Exact static comparison shows this adapter path is unchanged by the immutable
telemetry delta, so the observed candidate failure is not a telemetry
regression. Direct adapter callers can receive invalid success, while the full
transport path revalidates and rejects the derived values. This is therefore a
`PREEXISTING_ADAPTER_BOUNDARY_RED_PENDING_OWNER_EXPOSURE_CLASSIFICATION`, not a
claim that every public route is affected.

After the preserved-chain gate passes, reproduce this second RED through its
source-owned seam first on baseline and then candidate. This is also a mandatory
LOCAL-01 gate regardless of severity. Require a fully finite success or an
existing authorized typed failure through the real carrier/PyO3 boundary. If
the candidate still violates the gate, use only the source-owned authorized
error boundary in a separate safety commit and validate every returned
background field; do not clamp overflowing values or infer a new public/PyO3
error contract. Ambiguous authority blocks LOCAL-01.

## Source-to-run evidence

- Final six-test sandbox source retained as
  `SANDBOX_LATE_RED_REPRODUCER.rs`: Git blob
  `8b4fb327aa4bf2480c6d829936d838d56cd1ade3`, SHA-256
  `8530b875e0011c9f76ff90f52d0b7ee60637b5a08fc8aab88e19c131ed40acc4`.
- Frozen patched donor: Git blob
  `e4d0f9c44fc26740d3a1cad6938b522fe514ae37`, SHA-256
  `ae38f315e84314ed7fef5360ac7f3a44c8f140c5d27d4ddb3a0a539bcef70cab`.
- Cargo lock: Git blob `98e67c4be673f342c254495b3f340c9252910aaf`,
  SHA-256 `18b62b9b792058ab789521d1c69764bed7915b550cd4fc389e848a6ec02c07ed`.
- Receipt RED binary SHA-256:
  `b8d40804efeb71074e08b1f4765fcf00e1047d55f3bd10e2f99854ac28a12fc2`.
  Its full first-run source snapshot was not retained; the exact test function
  is byte-identical in the final retained source.
- Background RED binary SHA-256:
  `6ceeec9fa87b7f1987b66b4fae1b7945539ac3206c633e62faa2b30fa8e4125c`;
  the final retained source is the exact source snapshot for this run.

The environment, commands, module wiring, exit codes, and log identities are
recorded machine-readably in `SANDBOX_SPIKE_RECEIPT.json`. This improves the
diagnostic binding but does not make the sandbox authoritative.

## Related semantic concerns, not reproduced defects

- `max_screen_leakage` is computed after screen projection, so current evidence
  supports only a post-projection residual, not raw transport leakage.
- Split/leaf/depth telemetry is driven by midpoint fixed-point convergence and
  measures adaptive work; without a truncation-error estimate it is not an
  integration-accuracy certificate.
