# Reproduced pre-existing nonfinite-boundary findings

## Classification

```text
TWO_REPRODUCED_PREEXISTING_BOUNDARY_DEFECTS
NOT_INTRODUCED_BY_TELEMETRY_PATCH
DO_NOT_FIX_OUTSIDE_THE_AUTHENTICATED_LOCAL_EVIDENCE_WORKTREE
```

An independent late PHYS-MATH read found two source-owned boundaries where
finite inputs can return an otherwise successful result containing nonfinite
derived values. The telemetry patch does not touch either relevant
pre-existing arithmetic or validation boundary.

## 1. Nonfinite transport receipt

With a zero geometry background except `expansion = 1.0`, finite
`step = 1.0e308`, one root panel, and a valid screen projector, the tensor scale
underflows harmlessly to zero and the packed coherency remains finite. The
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

The baseline donor already contains the same `4.0 * log_energy_shift`
construction and lacks a final scalar-finiteness gate. The immutable telemetry
patch adds counters/error plumbing only; it has no diff hunk changing
`log_energy_shift` or `log_bolometric_shift`. Therefore this is a pre-existing
owner-boundary defect, not a telemetry regression and not evidence against the
counter identities.

Because this workspace lacks the genuine local RED chain and public/PyO3
schema, no production fix is authored or pushed here. After the preserved-chain
gate passes, reproduce this RED in the authenticated worktree against both the
baseline and patched donor, classify severity under the project contract, and
make the smallest source-owned typed-failure fix only if authorized. Test every
returned scalar and the real Python error mapping. Do not silently clamp,
saturate, fabricate a receipt, or invent a new public error schema from this
document.

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

This adapter path is present independently of the immutable telemetry delta,
so the observed failure is also pre-existing rather than a telemetry
regression. Direct callers can receive invalid success even though a later
transport boundary may reject the derived values.

After the preserved-chain gate passes, reproduce this second RED through its
source-owned seam against both baseline and candidate. A fix must use the
existing authorized error boundary and validate all returned background fields;
do not clamp overflowing values or infer a new public/PyO3 error contract.

## Related semantic concerns, not reproduced defects

- `max_screen_leakage` is computed after screen projection, so current evidence
  supports only a post-projection residual, not raw transport leakage.
- Split/leaf/depth telemetry is driven by midpoint fixed-point convergence and
  measures adaptive work; without a truncation-error estimate it is not an
  integration-accuracy certificate.
