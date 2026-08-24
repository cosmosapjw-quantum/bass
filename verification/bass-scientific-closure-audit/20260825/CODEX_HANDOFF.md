# Codex handoff — BASS closure program

Continue from repository `cosmosapjw-quantum/bass`, base `ccc679e6623407fd32393c38f9b052517bcdc257`. Candidate host is `cosmosapjw-quantum/htt_base` at `50ea6d76ace70dec57b8794ab0d1cf9b8fab42cb`.

Do not invent new theory. Active reference/frontend is pure Python + NumPy/SciPy/SymPy/pytest. Rust 1.94.1 is a future locked/offline backend. Do not add JAX/JAXlib/Equinox/Diffrax as active targets.

Read in order: `MACHINE_PLAN.json`, `TASKS.jsonl`, `SCIENTIFIC_CONTRACT.md`, `VALIDATION_MATRIX.md`, `ADVERSARIAL_AUDIT_SUMMARY.md`.

## Execute only `BASS-CLOSE-00`

Recover or explicitly supersede the exact final 2B.3 package.

Expected final identity:

```text
BASS8B2B3_PROJECTOR_LEFT_FUNCTIONAL_KATO_AUDIT_CANDIDATE_20260824.zip
size 633703
sha256 23d7ff71dff3d10f15efbebefe52839effa28bfb93fba5b725ab2faa2c12b0cc
```

Current same-name earlier candidate:

```text
size 514231
sha256 5532588b554029d31d9fff1cd9ea994862a354436a1febc6a2c19c63de3dbace
```

Never update the expected hash to fit the earlier bytes.

### Research loop

1. Inventory every local, Dropbox and GitHub copy with path, size, SHA-256 and mtime.
2. Decide Route A exact recovery or Route B explicit superseding deterministic rebuild.
3. Preserve negative/contradictory evidence.
4. Confirm no physics source/test change.

### Coding loop

1. Use a separate worktree and bounded descendant verification branch.
2. Write a task receipt before edits.
3. Reproduce the identity failure.
4. Apply only the smallest provenance/package patch.
5. Run CRC, manifest, frozen-input hashes, the final test surface, SymPy, Wolfram/xAct receipts or native replay, numerical receipts and plot-presence checks.
6. Run PHYS-MATH and PHYS-MATH-CODE audits.
7. Run fresh-context independent diff review.
8. Commit once and push normally. No PR, merge or tag.

Stop on incomplete final sources, gate mismatch, required physics change, weakened hash/tolerance, or any request to start classifier, Rust, runtime or fitting.

Report branch/head/base, route, inventory, exact identity, gates, no-physics diff, evidence directory, commit/push and hard-boundary confirmation. Recommend but do not execute the next task.