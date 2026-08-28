# Local Codex continuation after R4 validator repair

Use the separately delivered exact-pinned entry prompt to fetch this bootstrap.
This file governs continuation AFTER R4 intake. Do not run either old
bootstrap validator or R2's obsolete `validate_package.py --live` command.
R4 runs the original R2 offline semantic checker AND the corrected complete
live identity checks. No original R2 bytes or expected hashes may be changed.

## Frozen inputs and precedence

Repository: cosmosapjw-quantum/bass.
R2 authority: 55335d3817a82da7e0f9bf24ef7632a2533645d3,
tree 7c02689430d01abdf998c5b7ab1c5a6eb48859f4, PR #39 draft/unmerged.
RF-02C base: dfa17457d402bd441d3fdf786c2d79c529512ee5,
tree 9fc67fb0ba10e091e25a14d7e1fac88b77a0241e, PR #36 draft/unmerged.
Historical R1 scope: b7cda09d337906c17821a2b815032c985ff86bdf,
tree 1eba9fc7f4ba8832545c403ca4ce92d81bcb8915.
Implementation branch: agent/architecture/rust-first-rf03-20260828-r2.
Next action after intake: RF03-AUTH-01.

R4 changes transport/identity validation only. R2 authority semantics override
conflicting R1 wording; unaffected R1 implementation/acceptance scope survives.
Read the retained authority directory's AUTHORITY_CONTRACT.json and
WORK_UNITS.json. Read these historical files with raw `git cat-file blob`:

```text
b7cda09d337906c17821a2b815032c985ff86bdf:
docs/rust_first_runtime/rf03_matter_thermo_tilt_closure_20260828/
    IMPLEMENTATION_PLAN.md
    WORK_UNITS.json
    ACCEPTANCE_MATRIX.json
    SOURCE_INVENTORY.json
```

Treat historical CURRENT_STATE/README/bootstrap commands as historical, not
current authority. Do not search for an R2 ZIP or normalize digests.

## Preserve local state

Record current root status and worktree inventory; do not require the untracked
count to stay globally fixed across other agents. Preserve the user's reported
41 pre-existing untracked entries, prior blocker worktree and
SCHEMA_AND_ROUTE_FREEZE.json. Never clean, stash, reset, rebase, amend,
force-push, or switch an occupied worktree. A missing prior temporary blocker
artifact is recorded as unavailable, not invented and not a scientific blocker.

Create a new isolated worktree from the exact RF-02C base on the named R2
implementation branch only if that branch does not exist locally or remotely.
If it exists, prove ownership, base ancestry and allowed changed paths before
resuming; do not overwrite it or silently choose a different branch. Keep the
materialized package, logs and worktree available after the run.

## Execute, do not restart planning

First land only:

```text
provenance/authority/rf03/RF03_AUTHORITY.json
tools/authority/verify_thermodynamics_authority.py
tests/rf03/test_authority_contract.py
artifacts/rust_first_runtime/rf03/authority/**
```

Run the authority verifier and focused authority test. Bootstrap PASS is NOT
PASS_RF03_AUTHORITY. Only after the actual authority gates pass, record that
node result and continue in the SAME run:

RF03-RED-02 (genuine runtime failing tests) -> RF03-IMPL-03 -> RF03-AUDIT-04
-> RF03-EVIDENCE-05. The bootstrap RED logs shipped here do NOT satisfy
RF03-RED-02. They concern the transport validator only.

Preserve explicit caller-selected gamma-law model, [Omega,v1,v2,v3] order,
force/JVP at fixed context, domain rules and RF-02C routing/history semantics.
T_gamma remains exogenous; verify its force/JVP invariance. Do not invent an
EOS, tilted-temperature law or hidden constant-w/Python/surrogate fallback.
Historical Type-II thermodynamics remains surrogate-reference-only.

Run scoped parity/domain/determinism tests, the four bounded figures and
hostile mutations specified by R1/R2, then the two required bounded audits.
At most one reproduced P0/P1 repair pass. Build native wheel/content-addressed
delta and restore evidence; bind them to the actual implementation commit.
Use ordinary push and create/update ONE draft implementation PR against the
RF-02C base branch, with exact remote readback. Do not merge or mark ready.

Do not use BASS-12--15 optimization bytes; no timing/GPU/Wolfram, full-suite
reassurance, or RF-04+ expansion. A new failure requires its exact command,
observed/expected identity, traceback and preserved checkpoint, not a generic
state-divergence label or a silent bypass.

## Terminal report

STATUS / ACTUAL PROGRESS / VERIFIED / DEFERRED / BLOCKERS / NEXT.
Report exact source/evidence/remote SHAs and PR. Distinguish bootstrap
validation, PASS_RF03_AUTHORITY and PASS_RF03. No performance or scientific
promotion is authorized. Stop after the draft implementation PR.
