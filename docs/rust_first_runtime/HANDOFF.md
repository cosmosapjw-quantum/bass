# RF-02B handoff

## Resume authority

- Repository: `https://github.com/cosmosapjw-quantum/bass`.
- Continue exclusively from draft PR #32, branch
  `agent/architecture/rust-first-rf02b-20260826-r1`.
- Require implementation commit
  `01d1bed4afb75c648c5f13652c7073a014f8f1ac` to be an ancestor of the live
  branch and keep the PR open, draft, and unmerged.
- Verify `artifacts/rust_first_runtime/rf02b/EVIDENCE.json` against the SHA-256
  supplied in the enclosing delivery message.
- Immutable native delta: `artifact/native-r4-delta-rf02b-20260826-r1` at
  `eb01d5e9528704e9ff422a792709b3993b9123ab`; package
  `repro/native/BASS-RF02B-R4-DELTA-20260826`.

## Closed contract

RF-02B is `PASS_RF02B_CODE_AND_IMMUTABLE_R4_DELTA`. Typed schemas, unchanged scalar RHS, analytic
pointwise JVP, signed constraints, pointwise projection, explicit Python/JAX
oracles, and rust-required no-callback dispatch are closed for class A, class B,
exceptional, and Type-IX D past/future. Existing tilted native RHS is preserved;
tilted JVP/constraints/projection remain RF-03-owned.

Reuse the focused PR CI, immutable R4-delta restore, RF-02A, RF-01, R5b, and
unchanged science receipts. Do not rerun them for reassurance. Performance and
Wolfram were not run and have no new claim.

## Exactly one next action

Execute RF-02C only: integration, exact-JVP solver wiring, events, chart
transitions, background batches, and geometry histories. Do not start RF-03+,
SIMD/GPU, timing acceptance, Wolfram, merge, ready transition, or authority
promotion.
