# BASS Task 3–10 recovery report

- Recovery date: 2026-08-09
- Target: `cosmosapjw-quantum/bass`
- Publication branch: `agent/longrun-checkpoints`
- Remote baseline before recovery: `d9e5ba7577ccb05b648b11ea7ac991bf6e09d8b9`
- Overall classification: `PARTIALLY_RECOVERED / IMPLEMENTATION_MISSING_OR_MASKED`

## Outcome

The interrupted Task 3–10 production source tree and its reported Git objects were not
recovered. The investigation did recover and preserve two exact, useful predecessors:

1. a 72-file immutable background/high-ell harness, byte-identical to nested archive SHA-256
   `cd80b4e9ee4a0d292e99bba7fffd60bd313d765e4510498ae1c8e99ec0ff3b64`;
2. an 18-file historical Rust/Python/test overlay, byte-identical to archive SHA-256
   `53597fb5dd2aee25a75bfedc2f001574db90b1a5580ad60410b575f76c8aa9fb`.

The first is explicitly a `HARNESS_ONLY` package with `solver_code_included=false`. The
second is an incomplete overlay with no full Python baseline, Git identity, execution
receipts, or lost `bianchi/full` modules. They are preserved in separate namespaces so
neither can be mistaken for the Task 3–10 solver.

## Search coverage

### Filesystem and Git

Accessible `/workspace`, `/tmp`, and `/root` paths were searched for Git directories,
object stores, worktrees, reflogs, unreachable objects, known SHA prefixes, `bianchi/full`,
target test names, recent BASS/Bianchi paths, caches, and editor recovery files. The denied
`/root/.codex/sessions` tree was not accessed.

The apparent original `.git` paths at the current scratch root, `/workspace`, and `/tmp`
are empty mode-0555 `tmpfs` mounts rather than Git repositories. Consequently, an object
store hidden behind the current scratch-root mount cannot be examined or honestly declared
absent from this namespace. This is the primary remaining recovery lead.

Three initially visible, unrelated Git object stores were checked with `cat-file`, reflog
enumeration, and `fsck --full --no-reflogs --unreachable`. None resolved the target
locators. Two unreachable blobs in an unrelated RRSS repository were inspected and had no
BASS terms. The BASS checkout now in this workspace was created during this recovery and
must not be treated as evidence of a pre-existing checkout.

### Processes, deleted files, caches, and runtime logs

A direct `/proc` snapshot found 27 PIDs and no running pytest, Git, or project Python
process. Direct descriptor inspection and `lsof +L1` found no visible deleted-open file.
These are point-in-time negative results, not proof about earlier process state. No BASS
pytest cache, bytecode cache, editor swap/backup, or autosave was found. The accessible
Codex SQLite log passed integrity checks but covered the current recovery runtime, not the
prior ten-hour implementation, and yielded no source tree or Git object.

### Attached archives

All 15 inputs were hashed. Inputs 01–13 match all 13 identities preserved in the 2026-08-02
interruption bundle. Archive member paths were screened for traversal, duplicates, links,
special files, `.git/objects`, Git bundles, patches, `bianchi/full`, `HistoryV2`, and
`EMTSource`.

- Bundle 14 is the strongest provenance package, but explicitly contains no solver. Its
  canonical H0/H1 harness is preserved unchanged. Current machine state is OD0 blocked.
  The immutable `docs/HARNESS_AUDIT_REPORT.md` also contains stale prose saying that OD0
  was completed; the source bundle labels this a known quarantined defect. That prose is
  non-authoritative. `state/gates.json` (`G-OD0=BLOCKED`) and `state/run_state.json`
  (OD001–004 pending, no OD0 authorization receipt) take precedence.
- Archive 12 contains real code bytes: a Rust crate, two Python overlays, and two tests.
  It is a historical partial overlay only and is quarantined accordingly.
- Archive 13 is an automation/process kit. It contains no solver, target test suite,
  execution receipt, or commit object.
- The other inputs are specifications, generic harnesses, prompts, audit protocols, or
  external toolchain/dependency packages.

The 192 MB Rust distribution and xAct archive were verified as inputs but deliberately not
committed as vendor binaries.

### GitHub

Before this recovery publication, Git protocol v2 advertised only `main` and
`agent/longrun-checkpoints`; both pointed to the same bootstrap checkpoint. A separate
`git ls-remote --tags origin` exited 0 with zero advertised tag refs. Public branch history
contained only the checkpoint and initial LICENSE commits. Direct GitHub commit lookup
returned `422 No commit found` for every transcript locator in the object-search table.
There were no open pull requests.

GitHub public APIs and Git ref advertisement do not enumerate server-side unreachable or
dangling objects. Therefore, zero advertised tag refs does not prove that an object never
existed or that no unreachable server object remains.

Raw host-filesystem inode/block undelete was not attempted because the underlying store is
outside the visible namespace and such access would exceed the authorized safety boundary.

## Recovery classifications

| Class | Meaning in this checkpoint | Material |
|---|---|---|
| `DURABLE_VERIFIED` | Identity and bytes verified against durable hashes/manifests | 15 input identities; 72-file harness |
| `PARTIALLY_RECOVERED` | Exact bytes recovered, but dependency/baseline or provenance is incomplete | 18-file Rust/Python overlay |
| `RECONSTRUCTED` | New record derived from current observations, not historical execution proof | inventory, manifests, this report |
| `TRANSCRIPT_ONLY` | Detailed behavior survives only as conversational evidence | Task 3–10 stage ledger and short locators |
| `MISSING_OR_MASKED` | Not found in accessible evidence, with a material namespace limitation | production solver tree and Git objects |

## Verification performed

| Check | Result |
|---|---|
| Original input manifest | 15/15 SHA-256 identities reproduced |
| Nested immutable harness ZIP | safe paths; 72 files; 0 mismatches; 0 extras |
| Partial overlay TAR | safe paths; 18 files; 0 mismatches; 0 extras |
| Harness internal manifest | 71/71 governed files OK |
| Harness at recorded execution path | validator PASS; 38/38 unit tests PASS |
| Harness after relocation | expected fail-closed: four execution-context errors; 36/38 tests pass |
| Recovered Python syntax | 4/4 files compile in memory |
| Rust crate metadata | supplied Rust 1.94.1; `cargo metadata --offline --no-deps` PASS |
| Rust crate tests | stopped before build: empty offline Cargo cache lacked `nalgebra` |
| Partial-overlay Python tests | not run: pytest is not installed and the complete Python baseline is absent |
| Final recovery-tree manifest | size + SHA-256 + path for every changed/recovered file except the manifest itself |

The recorded-path result is a fresh path-sensitivity control on the unchanged harness, not
a solver validation or a reissued historical receipt. Full commands and interpretation are
in `HARNESS_RELOCATION_CHECK_20260809.md`.

`manifests/RECOVERY_TREE_SHA256_20260809.txt` deliberately excludes itself to avoid a
self-referential hash. Its path set is required to equal the complete recovery scope, and
each row records decimal byte count, SHA-256, and repository-relative path.

## Preserved Task 3–10 state

`TRANSCRIPT_TASK3_10_STATE_20260809.md` records the surviving behavioral claims, reported
test counts, review states, locators, and reconstructable invariants. None is promoted to a
source, commit, or scientific PASS. In particular, Task 10 was last reported with 65 focused
tests green, but no final cumulative regression, commit, or independent review survives.

## Safest continuation point

1. Obtain a read-only view or export of the object store hidden behind the scratch-root
   `.git` tmpfs, or another external checkout/bundle, before declaring the old objects lost.
2. If exact objects remain unavailable, acquire the complete canonical Python baseline.
3. Reconstruct Task 3–5 interfaces first; then rebuild Tasks 6–10 from the transcript ledger
   using observed RED tests, fresh focused and cumulative GREEN runs, and independent review.
4. Commit and push each approved task/fix round separately. Do not resume beyond Task 10
   from the partial overlay alone.

The next executable development state is therefore not “Task 10 complete.” It is
“Task 3 baseline/API recovery pending, with Task 6–10 invariants preserved for testing.”
