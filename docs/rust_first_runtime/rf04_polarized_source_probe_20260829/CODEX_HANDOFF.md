# Codex handoff — BASS RF-04 polarized source differential

```text
repository: cosmosapjw-quantum/bass
source branch: agent/architecture/rf04-scalar-raw-20260829-fhxMnS
source HEAD: 50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda
source tree: b32fcc26ca51dcaca9e9225d48b03fe9e02988ed
source PR: #57 OPEN / DRAFT / UNMERGED

claims:
PASS_RF04_SCALAR_RAW_SLICE_PROOF
NO_PASS_RF04

exact next action:
RF04-POL-01_EXECUTABLE_SOURCE_DIFFERENTIAL
```

Use a new isolated worktree from the exact source head. Preserve every existing
worktree, evidence directory and untracked object. Never clean, reset, stash,
amend, rebase, squash or force-push.

## Intake

Extract the package, verify `MANIFEST.sha256`, run `validate_package.py`, then
run `validate_package.py --live --repo <clone>`. Read:

1. `PACKAGE.json`
2. `SOURCE_INVENTORY.json`
3. `PROBE_MATRIX.json`
4. `WORK_UNITS.json`
5. `ACCEPTANCE_MATRIX.json`

Reuse the scalar/raw proof. Do not rerun it unless a declared dependency blob
changed, and then rerun only the invalidated selectors.

## Run the five source differentials

Execute P1-P5 exactly. Every probe must call the real Rust donor. Python may
construct an independent dense/reference calculation but may not become a
production loop or fallback.

The current source already establishes:

- common-screen convex remap with nonnegative weights;
- source-owned `RemapOptions` fields, but not the production stencil builder;
- Lie-group implicit-midpoint characteristic transport with bounded internal
  bisection;
- a source fixture showing second-order refinement for outer substeps
  1,2,4,8 against 16;
- distinct collision, projector-Kato and geometric screen-transport actions.

It does not yet establish the five full-trajectory decisions. Do not copy the
withdrawn A2, use legacy `PolQState`, or identify geometric screen transport
with equilibrium-projector Kato transport.

## Progress-first continuation

If and only if every probe yields one unique source-supported disposition:

```text
write POLARIZED_SOURCE_CONTRACT.json from the measured evidence
→ write genuine composed RED
→ implement full polarized trajectory/batch/history
→ run targeted proof and compiled numerical mutants
→ generate and host-read the five probe diagnostics plus full trajectory plots
→ one PHYS-MATH and one PHYS-MATH-CODE review
→ at most one reproduced P0/P1 repair
→ fresh content-addressed native restore
→ ordinary push and one stacked draft PR
→ exact remote readback
→ stop
```

If any probe remains nonunique, stop as:

```text
BLOCKED_RF04_POLARIZED_AUTHORITY_DECISION_WITH_MEASURED_CANDIDATES
```

Return the complete measured candidate table, source identities and
counterexamples. Do not add another governance/audit package and do not guess.

Do not run full-suite reassurance, timing, GPU, Wolfram, RF-05+, merge, ready,
Candidate B/BASS-13–15, or scientific/performance promotion.

Successful terminal:

```text
PASS_RF04
```
