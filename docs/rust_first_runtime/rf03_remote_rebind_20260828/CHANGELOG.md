# RF-03 Remote Rebind Change Log

## Observed failure

The previous local handoff pinned:

```text
ref: b7cda09d337906c17821a2b815032c985ff86bdf
transport: ZIP + sidecar
```

That tree contains the historical R1 package but not the R2 ZIP/sidecar. Codex
correctly stopped rather than guessing.

## Root cause

The durable R2 authority package exists on a different branch and uses a
different canonical transport:

```text
branch: agent/plans/rf03-authority-resolution-20260828-r2
head:   55335d3817a82da7e0f9bf24ef7632a2533645d3
tree:   7c02689430d01abdf998c5b7ab1c5a6eb48859f4
PR:     #39
format: DIRECT_TEXT_FILES
index:  docs/rust_first_runtime/rf03_authority_resolution_20260828/PACKAGE_INDEX.json
path:   docs/rust_first_runtime/rf03_authority_resolution_20260828/direct
```

`PACKAGE_INDEX.json` explicitly marks the intermediate multipart/ZIP transport
as `NONCANONICAL_DO_NOT_EXECUTE`.

## Corrections in this package

1. Rebind execution to the exact immutable R2 head/tree.
2. Use `git show` to materialize six direct text files; do not download,
   assemble, or search for a ZIP.
3. Verify every direct file against the SHA-256 values in the R2 package index.
4. Run the R2 package's own manifest and offline/live validator.
5. Create a new isolated RF-03 R2 worktree from the exact RF-02C terminal base.
6. Preserve the prior blocker worktree and the canonical root's unrelated
   untracked files.
7. Continue from `RF03-AUTH-01` to genuine RED and implementation in the same
   run when authority validation passes.
8. Preserve `NO PASS_RF03 CLAIM` until full terminal proof.

## Not changed

- RF-02C source, evidence, PR #36, or branch.
- R2 authority contract or scientific meaning.
- Production Rust/Python source.
- EOS, coefficients, signs, tolerances, state order, or tilted-temperature
  boundary.
- PR #37 or PR #39 merge/ready state.
