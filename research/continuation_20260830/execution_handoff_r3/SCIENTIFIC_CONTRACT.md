# Scientific contract snapshot R3

This document is subordinate to the exact R5 `CODEX_HANDOFF.md` at commit
`57ec56393de43eb78d758222f78478aea8b14517` and
`REMOTE_PUBLICATION.json` v6 at commit
`cb9b2c84c593733e6f8944b417d3876a2aad9407`.  It records no new scientific
result.  R4 and execution handoff R2 are retained as historical evidence but
their execution instructions are superseded.

## Claims

- Retained scoped result: `PASS_RF04_SCALAR_RAW_SLICE_PROOF`.
- Current overall result: `NO_PASS_RF04`.
- R5 proves remote locator compatibility evidence and byte readback only.
- Authenticated exact-host intake, native telemetry parity, carrier/PyO3
  mapping, physical-generator differential, convergence, AP/stiff behavior,
  trajectory, performance, GPU, and RF-05 remain unproved.

## Gate order

1. Verify R5 remote commit/tree/blob/SHA identities and run its 56-test normal
   and optimized gates with the intended trusted Git installation.
2. Run R5 against the authenticated complete BASS clone.  Require
   `PASS_IMMUTABLE_PAYLOAD_INTAKE_ONLY`, 18 entries, `NO_PASS_RF04`, and next
   action `BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY`.
3. Only then verify local commits `148d590…` and `d3df4ce…`, RED tree
   `208dc7e…`, ancestry, and a clean canonical worktree.  Missing or mismatched
   objects yield `BLOCKED_BY_MISSING_LOCAL_EVIDENCE` without a remote fallback.
4. Create one new ordinary linked worktree and execute LOCAL-01.  LOCAL-02 is
   forbidden until every required LOCAL-01 item is `PASS`.

## Frozen telemetry semantics

For a successful characteristic call:

```text
S = total actual internal split events
D = maximum accepted-leaf recursion depth
L = accepted subinterval count
N_root = input/root subinterval count

L = N_root + S
expected background callback count = 2 + N_root + 2*S
```

All counters use checked arithmetic.  Overflow is a typed failure, never
saturation.  Failed calls expose no fabricated success receipt or partial
API-owned telemetry/history.  Callback-owned external side effects are not
transactional.  Split/leaf/depth counts measure adaptive work; they are not a
truncation-error estimator or an integration-accuracy certificate.

On the ordinary telemetry corpus, all pre-existing numerical fields, arrays,
accepted intervals, callback fractions/order/count, and background-call order
must retain bit parity.  `max_screen_leakage` is evaluated after screen
projection and must not be described as raw transport leakage without an
authorized pre-projection diagnostic.

## Mandatory nonfinite boundaries after the gate is reached

The five preserved files are non-authoritative diagnostic evidence.  They do
not show that the R5 or local-object gates passed.  After both gates pass,
reproduce these cases independently on the authenticated baseline and exact
candidate:

1. finite transport inputs returning `Ok` with
   `log_bolometric_shift = -inf`;
2. finite Type-II state `[f64::MAX, 0.0, 0.0, 1.0, 0.0]` returning `Ok` with a
   nonfinite derived background.

Every field of a successful returned receipt and derived background must be
finite.  For exactly these two cases, the candidate may instead return an
existing authorized typed failure through the real result carrier and PyO3
mapping.  Do not clamp, saturate, fabricate success, or invent a public error
variant or Python mapping.  If authority is ambiguous, stop.  Any authorized
safety correction is a separate commit above the byte-frozen telemetry delta,
with its own RED/GREEN logs and schema review.  No other parity waiver follows.

## LOCAL-02 ceiling

After complete LOCAL-01 only, bind the source-owned geometric generator `A`
and collision generator `C` to the same carrier, grid, measure, frame, screen
bases, time convention, units, boundary/remap rule, and opacity/electron
state.  Compare native `(A+C)y` against an independently assembled dense
oracle on a nondegenerate frozen grid where both operators are nonzero and
noncommuting.  Missing representation authority is a blocker; do not invent
it.  The maximum allowed result is
`SCOPED_FROZEN_PHYSICAL_OPERATOR_PROOF`, not RF-04.

Never use uncompensated `K/2-C/2-G-C/2-K/2`, a Bloch/dephasing toy as Thomson
physics, exact reversal of a dissipative remap, row sums in place of weighted
conservation, a rounded dot product as a rigorous support bound, or source-
absent q1/q3 nodes or closures.
