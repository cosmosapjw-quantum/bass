# RF-02B closeout

Status: `PASS_RF02B_CODE_AND_IMMUTABLE_R4_DELTA`.

RF-02B closes the fixed-size non-tilted scalar pointwise layer for class A,
class B, exceptional VI*_-1/9, and Type-IX D (past/future). The Rust production
boundary now exposes typed packed schemas, the unchanged RHS, analytic JVP,
ordered signed constraints, and pointwise Gauss-Newton projection. Existing
tilted native RHS compatibility is preserved; tilted derivatives belong to
RF-03. Solver JVP wiring, events, transitions, batches, and histories remain
RF-02C.

Source authority is implementation commit `01d1bed4afb75c648c5f13652c7073a014f8f1ac`
on draft PR #32. Focused PR CI passed: oracle 4, Cargo 6, native/affected Python
29, plus rustfmt and clippy. Independent review passed, including 250 hostile
randomized JVP cases. The exact R4 substrate was reassembled and the RF-02B
delta was rebuilt/tested offline in run 32877249403.

The durable native delta is on
`artifact/native-r4-delta-rf02b-20260826-r1` at
`eb01d5e9528704e9ff422a792709b3993b9123ab`.
Machine truth is in `EVIDENCE.json`; logs, source hashes, wheel, and the restore
receipt live in the artifact branch package and are referenced rather than
reproduced here.

No physics RHS, tolerance, reference, grid, seed, solver behavior, performance
claim, Wolfram execution, or formula-authority promotion occurred. The full
suite and inherited PASS lanes were not rerun.

Exactly one next action: execute RF-02C from the live draft PR #32 head while
keeping PRs draft and unmerged.
