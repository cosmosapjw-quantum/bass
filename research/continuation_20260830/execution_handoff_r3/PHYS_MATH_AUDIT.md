# PHYS-MATH audit R3

## Verdict

```text
NOT_RUN_ON_IMPLEMENTATION — GATE NOT REACHED
PACKAGE_CONTRACT_REVIEW = PASS_SCOPED
NO_PASS_RF04
```

No production physics or numerical implementation changed in R5, publication
v6, or this R3 package.  Therefore this is a contract/readiness review, not the
mandatory post-change PHYS-MATH audit for LOCAL-01 or LOCAL-02.

| Classification | Boundary | Finding |
|---|---|---|
| PASS | Provenance order | R4 exact-host `STOP_INVALID` is separated from scientific validity; R5 exact-host intake remains `DEFERRED_LOCAL`. |
| PASS | Counter identity | The required successful-call identity is `L=N_root+S`; maximum depth is independently defined on accepted leaves. |
| PASS | Callback oracle | Expected background callbacks are independently `2+N_root+2*S`, including endpoint samples. |
| PASS | Failure meaning | Overflow must be typed; no saturation, fabricated receipt, or partial API-owned telemetry/history is allowed. |
| CONCERN | Accuracy interpretation | Split/leaf/depth counters measure adaptive work and cannot certify truncation error or integration accuracy. |
| CONCERN | Leakage interpretation | Current maximum is post-screen-projection; raw transport leakage is not established. |
| NOT_RUN | Ordinary-corpus parity | No authenticated baseline/candidate native arrays, intervals, callbacks, or carrier values exist yet. |
| NOT_REACHED | Finite receipt boundary | Historical diagnostic RED is preserved, but authenticated baseline/candidate runs have not started. |
| NOT_REACHED | Finite background boundary | Historical diagnostic RED is preserved, but owner/exposure classification remains local. |
| NOT_RUN | Typed failure authority | The real carrier, error enum, serialization, and PyO3 mapping must be recovered from the preserved local commit. |
| NOT_RUN | Physical `A+C` differential | LOCAL-02 is closed until every LOCAL-01 item passes. |
| PASS | Claim ceiling | Current claim remains `NO_PASS_RF04`; retained scalar/raw proof is not widened. |

## Required implementation audit inputs

After R5 intake and the preserved-chain gate pass, the real PHYS-MATH audit
must bind exact baseline/candidate commits, trees, donor blobs, compiler and
runtime pins, test commands, exit codes, and raw log hashes.  It must check:

- bit parity of all pre-existing fields/arrays on the ordinary corpus;
- `L=N_root+S`, independent maximum depth, callback fractions/order/count;
- no split, nested/nonuniform split, and multiple root panels;
- first-child success then second-child failure and post-recursion failures;
- both nonfinite cases on baseline and candidate, including every successful
  scalar/background field and any authorized typed-failure route;
- checked overflow and no fabricated/partial receipt or history;
- separation of any boundary-safety correction from the frozen telemetry
  commit;
- post-projection leakage wording and the absence of accuracy overclaims.

For LOCAL-02, bind units, time orientation, Hubble-normalized convention,
bolometric factor four, opacity scaling, future-photon direction, node-major
rank-9 carrier, four-real-dimensional screen subspace, packed-`V` sign,
quadrature measure, remap weights, and screen association.  Mutants must cover
added `K`, index permutation, omitted measure, and screen mismatch.  A missing
binding is a measured blocker, not permission to choose one.
