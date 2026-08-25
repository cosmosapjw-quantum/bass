# RF-01 final closeout

1. **Verdict:** `CODE_CONTRACT_PASS`; `PERFORMANCE_NOT_RUN_BLOCKED_ENVIRONMENT`.
2. **Source implementation:** `agent/architecture/rust-first-rf01-20260825-r1`
   at `dea69b0d82a3e157cc452c8dfd4a27b1dbb3bd49`, tree
   `1bd251b0dfa098fa5d15790aec29c0355b23ab73`.
3. **Architecture:** immutable private-pool `RuntimePlan`, plan-bound flat reusable
   `Workspace`, typed PyO3/GIL/buffer errors, and per-plan counters were added;
   legacy numerical bindings remain assigned to RF-02--RF-05/RF-07.
4. **Focused proof:** fmt, clippy, 128 locked/offline Cargo tests, 36 focused
   Python tests, deterministic wheel/install checks, and the real non-timed RF-01
   corpus adapters passed. Details are indexed by the machine evidence.
5. **Review:** the sole independent review found three RF-01 blockers; the one
   bounded repair closeout passed all three. The final three-file propagation is
   mechanical and preserves `_rustcore` tree `51abf8aab66a16fa837c77fa90b76b5394e2bb4c`.
6. **Native R4:** `artifact/native-repro-bundle-20260825-r4` at
   `b069e46eeb649b7b33e5ca30c3508d144fcd0e2c`, tree
   `53da650f50cc140acf57a6e6044f0675bfb8b17c`; 178,065,696 bytes in 22 parts.
7. **Artifact checks:** fresh clone, ordered reassembly, content verification,
   offline restore, byte-identical normalized wheel/SO, fresh no-index install,
   RuntimePlan call, and 34 focused tests passed.
8. **Claims:** performance acceptance `NONE`; scientific behavior change `NONE`;
   formula authority `UNCHANGED_UNPROMOTED`.
9. **Reuse:** unchanged RF-00, r3 dependency, R5b/science, and Wolfram receipts
   were not rerun; their lane-relevant predicates are unchanged.
10. **Machine authority:** `artifacts/rust_first_runtime/rf01/EVIDENCE.json`,
    SHA-256 `bc04ef51412c59fcdd5f2ae87f8898531e99fab633b031fccc16e829268c768d`.
11. **Rollback:** `git switch agent/architecture/rust-first-rf01-20260825-r1 && test "$(git rev-parse HEAD^)" = dea69b0d82a3e157cc452c8dfd4a27b1dbb3bd49 && git revert --no-edit "$(git rev-parse HEAD)"`.
12. **Exactly one next action:** execute `RF-02` from the live stacked draft-PR
    head; do not start RF-03+, SIMD, GPU, performance timing, or Wolfram work.
