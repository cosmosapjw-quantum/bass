# RF-02A handoff

STATE
- Branch: `agent/architecture/rust-first-rf02a-20260825-r1`.
- Code commit: `f7192686d8c3374b1973deee8a1dd337fbdb403b`; PR is draft/unmerged.
- Final evidence commit is the branch head returned by authenticated remote readback.

OUTCOME
- Exact Jacobi reduction closes the prior fail-open detector without changing
  physics; raw and reduced observables are separate.
- Typed geometry contract binds convention/state hashes and fails closed for
  unknown types and tilted RF-02B-owned routes.
- Focused symbolic/native proof is 50 passed; performance was not run.

EVIDENCE
- `artifacts/rust_first_runtime/rf02a/EVIDENCE.json` is the machine index.
- `artifacts/rust_first_runtime/rf02a/REVIEW.json` records the one independent
  review; `audit/r4_bianchi_constraints.json` is the exact detector receipt.
- R4 remains immutable and reused because no native bytes changed.

BOUNDARIES
- No merge, ready-state transition, Wolfram execution, RF-02B+ work, timing,
  tolerance/reference/physics change, or formula-authority promotion.

EXACTLY ONE NEXT ACTION
- Review and then start `RF-02B`, using this evidence and no inherited PASS
  rerun for reassurance.
