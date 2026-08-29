# Codex handoff — RF-04 polarized v2 implementation

```text
repository: cosmosapjw-quantum/bass
package branch: agent/plans/rf04-polarized-authority-resolution-20260829-r1
package base: 4eb8b1d89807b71f6110aafa5b50adfef2bf5433
scientific source: 50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda
scientific source tree: b32fcc26ca51dcaca9e9225d48b03fe9e02988ed
implementation branch: agent/architecture/rf04-polarized-v2-20260829-r1
exact next action: RF04-POL-EVIDENCE-00

retained:
PASS_RF04_SCALAR_RAW_SLICE_PROOF

current:
NO_PASS_RF04
```

Use a new isolated worktree from the exact package commit supplied in the remote
publication receipt. Preserve `/tmp/bass-rf04-pol-source.aUfpr6/worktree`,
all existing worktrees, canonical root files and concurrent ZIPs. Never clean,
reset, stash, amend, rebase, squash or force-push.

Read in order:

1. `PACKAGE.json`
2. `MEASURED_CANDIDATES.json`
3. `AUTHORITY_DECISIONS.json`
4. `PUBLIC_ROUTE_SCHEMA_DELTA_V2.json`
5. `WORK_UNITS.json`
6. `ACCEPTANCE_MATRIX.json`
7. `IMPLEMENTATION_PLAN.md`

## Evidence intake

Verify the preserved source-probe `MANIFEST.sha256` and confirm its SHA-256 is
`c05a78d373f3fd87c028e8535404c2b4723aff56c533163d3822355cf3987ea1`. Import the exact artifact directory into the
implementation branch with no normalization. Do not rerun P1–P5 if the
manifest and source head/tree match. Record the local-LLM rejection as
non-authoritative evidence, not as a scientific result.

## Execute

Follow `IMPLEMENTATION_PLAN.md` task by task. The five authority decisions are
now explicit route-design authorization; do not reopen them merely because
another admissible discretization exists.

The v1 scalar route stays byte/behavior compatible. The v1 polarized
capability remains fail-closed. Implement a distinct v2 polarized route with a
required serialized CSR remap plan. Different valid plan hashes are distinct
scientific inputs.

Use:

```text
two-half q1→mid→q3 characteristic profile
support-derived next-down minimum_transport_dot
fixed-Eulerian accepted history
K(q1)/2 → C(mid)/2 → G_h → C(mid)/2 → K(q3)/2
```

`G_h` is the complete backtrace/remap/characteristic screen-transport pullback.
Geometric screen transport and equilibrium-projector Kato remain separate.

Write genuine RED before implementation. Run only invalidated and directly
affected selectors. Use an independent state-array oracle and compiled native
numerical mutants. Do not use production diagnostics as their own oracle.

One PHYS-MATH review, one PHYS-MATH-CODE review, at most one reproduced P0/P1
repair, one differential rereview, fresh no-index native restore, ordinary
push and one stacked draft PR. No merge or ready transition.

Successful terminal:

```text
PASS_RF04
```

A reproduced defect terminates as:

```text
BLOCKED_RF04_POLARIZED_DEFECT
```

Do not run timing, GPU, Wolfram, full-suite reassurance, RF-05+, Candidate B,
BASS-13–15, or scientific/performance promotion.
