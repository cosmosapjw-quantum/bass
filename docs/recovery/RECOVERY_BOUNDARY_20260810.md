# BASS recovery boundary — 2026-08-10

## Purpose

This checkpoint records the final non-destructive recovery boundary reached after the
2026-08-09 Task 3–10 runtime interruption. It does not promote conversational reports to
source code, Git objects, test evidence, or a scientific PASS.

## Durable baseline

- Repository: `cosmosapjw-quantum/bass`
- Branch: `agent/longrun-checkpoints`
- Baseline commit: `5365125a584b1c8c384e7cebfb6dd44aff8268de`
- Baseline tree: `59fff39dee9f900924d528b41cc97d454d014852`
- Local and upstream refs matched before this follow-up.
- The worktree was clean before this follow-up.

The baseline preserves a 72-file harness-only package, an 18-file quarantined historical
overlay, recovery records, and transcript-only Task 3–10 invariants. It contains no
production `bianchi/full` solver tree.

This follow-up also preserves a byte-identical durable copy of the user-supplied low-ell
audit/acceptance contract at
`docs/specs/LOWELL_BIANCHI_FINAL_CODE_AUDIT_CONTRACT_20260810.txt`, SHA-256
`de4c4d3d467e91d3f8420b5b2748ee7294db3ca8e809df4045b2f8c2d71881f1`.

## Additional read-only checks

The following checks were performed after the baseline commit:

1. The scratch-root `.git` path remains an empty mode-0555 read-only `tmpfs` mount.
2. All visible processes shared the same mount namespace. Reading the target through
   `/proc/<pid>/root/workspace/scratch/5f62256bcea8/.git` exposed the same empty mount; no
   alternative namespace revealed the underlying object store.
3. Every visible Git repository under `/workspace` was checked again for the known short
   locators. None resolved them. The only BASS repository was the recovery checkout.
4. The accessible Codex SQLite log began at 2026-08-09 18:29 local runtime time and covers
   the recovery runtime, not the preceding implementation run. It contains recovery tool
   calls and transcript references but no Task 3–10 patch bodies or Git objects.
5. The 15 supplied attachments were reclassified against their own locked provenance:
   the low-ell text is an audit/acceptance rubric, the Rust/Python archive is a partial
   historical overlay, the automation kit is legacy process material, and the BASS v1
   archive is a harness-only high-ell package with no solver.
6. GitHub advertised only `main` and `agent/longrun-checkpoints`, no tags or pull requests.
   Direct commit lookup still failed for `3347547`, `eaf13af`, `4e1a3b6`, `54fb3bf`,
   `29327f9`, `e993691`, `6d786e1`, and `c3d45f3`.
7. Conversation-continuity search found no exact approved Task 1–10 body, API/file list,
   canonical Python archive, or original checkout path. Earlier BASS bootstrap material
   used a different `src/bass` package shape and is not silently substituted for the lost
   `bianchi/full` implementation.

## Final classification in this sandbox

| Material | Classification | Reason |
|---|---|---|
| Recovery commit `5365125` | `DURABLE_VERIFIED` | Local/upstream SHA and manifests agree |
| Harness-only package | `DURABLE_VERIFIED / NON_SOLVER` | Byte-preserved and self-declared `solver_code_included=false` |
| Historical Rust/Python overlay | `PARTIALLY_RECOVERED / QUARANTINED` | Exact bytes, incomplete dependency and Python baseline |
| Task 6–10 behavioral invariants | `TRANSCRIPT_ONLY` | Useful as future RED-test input, not implementation evidence |
| Task 3–5 exact APIs and source | `MISSING_OR_MASKED` | No source, object, plan body, or canonical baseline visible |
| Original Task 3–10 Git objects | `MISSING_OR_MASKED` | Hidden object store cannot be viewed; all visible stores unresolved |

## Safe continuation

There are exactly two admissible continuations:

1. **Exact recovery:** open the original long-running Work/Chat thread once and run the
   companion export prompt in `docs/handoff/ORIGINAL_RUNTIME_EXPORT_PROMPT_20260810.md`.
   Accept only a resolvable Git object/tree, complete checkout, verified all-object pack,
   Git bundle, or byte-hashed source archive that has passed the sensitive-data gate.
2. **Clean reconstruction:** if exact recovery fails, approve a new design cycle. The new
   design must choose a canonical package namespace and API rather than pretending the
   missing Task 3–5 interface is known. The low-ell audit text becomes an acceptance
   contract; the historical overlay remains reference-only; transcript invariants become
   RED tests. No observational NPZ/B execution is included.

The current thread can perform the clean reconstruction after design approval. A different
thread is not technically required unless it is the original runtime that may still retain
the masked checkout.
