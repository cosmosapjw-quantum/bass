# RF-02A closeout

- Verdict: `PASS_RF02A_CODE`; performance `NOT_RUN_BY_CONTRACT`.
- Base: PR #28 `fc8c02eda2b3e7dbc5eeca77af152e33caac9165`.
- Implementation: `agent/architecture/rust-first-rf02a-20260825-r1` at
  `f7192686d8c3374b1973deee8a1dd337fbdb403b` (tree
  `9d164c81d2604bba09987d88b0c87ed105088310`).
- The raw nonzero Bianchi components are retained as diagnostics; exact
  Jacobi-surface reduction passes all three pivot charts and the `a=0` branch.
- The deliberate `ndot[n00]` sign mutation is detected by a nonzero witness.
- Geometry convention/state hashes and the six existing native-required
  `q.group.*` routes are machine-bound in `EVIDENCE.json`.
- Focused proof: 50 passed with the verified R4 wheel; no full suite, timing,
  Wolfram, or RF-02B+ work.
- Native decision: `REUSED_NATIVE_R4_NO_NATIVE_BYTE_CHANGE`.
- Scientific behavior, formula authority, tolerances, references, grids,
  seeds, and solver semantics: unchanged.
- Machine evidence: `artifacts/rust_first_runtime/rf02a/EVIDENCE.json`.
- Exactly one next action: `RF-02B` after this draft PR is reviewed.
