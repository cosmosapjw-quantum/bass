# Original-runtime export prompt — BASS Task 3–10

Paste the following prompt into the original Work/Chat thread that performed the long
Task 3–10 run. Do not use it in an unrelated new thread.

---

Treat this as `RUNTIME_INTERRUPTION_EXPORT`, not implementation continuation.

Goal: recover the exact BASS Task 3–10 checkout and Git objects, if they still exist in
this thread's original runtime. Do not recreate missing code from conversation text.

Known reported commit locators:

- Task 5 review head: `3347547`
- Task 6: `eaf13af`, fix `4e1a3b6`
- Task 7: `54fb3bf` plus unknown later fixes
- Task 8: `29327f9`, fix `e993691`
- Task 9: `6d786e1`, fix `c3d45f3`
- Task 10: in progress, no retained final SHA

Safety rules:

- Read first. Do not run `git reset`, `git clean`, `git checkout --`, `git gc`, pruning,
  rebasing, force-push, deletion, dependency installation, or solver/scientific execution.
- Do not overwrite or overlay any checkout.
- Preserve dirty, staged, and untracked state separately.
- Do not access policy-denied paths.
- Do not print environment variables, raw process command lines, raw credential-bearing
  remote URLs, secret values, or file contents identified by a secret scan.
- Keep every recovery artifact in a private mode-0700 temporary directory until the
  sensitive-data gate below passes. Hashes and names-only inventories may be reported
  before that gate; raw artifacts may not.
- A conversational PASS is not evidence; report only current files, Git objects, hashes,
  and fresh read-only command results.

Procedure:

1. Record `pwd`, mount information for the current path and `.git`, all visible Git roots
   under the workspace, relevant process IDs plus executable basenames only, and the
   current UTC/local time. Do not collect environments or raw process arguments.
2. For each candidate Git root, record:
   - `git rev-parse --show-toplevel --git-dir --git-common-dir`
   - `git status --porcelain=v2 --branch`
   - `git worktree list --porcelain`
   - remote names plus URLs redacted to scheme/host/path only; remove userinfo, query,
     fragment, embedded token, and password before recording
   - `git show-ref --head --dereference`
   - reflog object IDs only, for example `git reflog show --all --format='%H'`; do not
     record reflog messages
   - `git fsck --full --no-reflogs --unreachable`
   - for every locator, require all three of: exit status zero from
     `git rev-parse --verify --end-of-options '<locator>^{commit}'`, exactly one full
     40-hex SHA, and success from `git cat-file -e '<full-sha>^{commit}'`. A short string
     printed with nonzero status is unresolved, not evidence.
3. If any locator or the production `bianchi/full` tree is found, create recoverable
   artifacts without changing the original repository state:
   - set `umask 077`, create a new private temporary directory, and initialize a disposable
     bare recovery repository inside it;
   - preserve the complete visible object database, including unreachable objects, by
     streaming the object IDs from `git cat-file --batch-all-objects` through
     `git pack-objects --stdout`, retaining the pack and importing it into the disposable
     bare repository with `git index-pack`;
   - reproduce existing refs only in the disposable repository. Add namespaced disposable
     refs for every verified locator commit and every independently verified unreachable
     commit. Never add recovery refs to the original repository;
   - create a Git bundle from the disposable repository after those refs exist. Retain the
     all-object pack as a separate artifact because a bundle still omits unreachable
     non-commit objects;
   - a binary working-tree patch and binary staged patch;
   - a NUL-safe archive of untracked files, if any;
   - a complete source snapshot excluding caches, credentials, vendor toolchains, and the
     `.git` directory;
   - a manifest containing byte count, SHA-256, and relative path for every artifact.
4. Apply a fail-closed sensitive-data gate before any attachment or push:
   - inspect tracked-history paths, staged/unstaged paths, and untracked paths for names such
     as `.env`, credentials, tokens, private keys, PEM/key files, auth stores, and secrets;
   - run an available trusted secret scanner over recovered history, source, patches, and
     untracked capture. Report only finding counts and paths, never matched secret text;
   - separately enumerate every object imported from the all-object pack by OID and type.
     Feed the raw bytes of **every blob**, including unreachable non-commit blobs that have
     no path or ref, to the trusted scanner inside the private temporary directory. Record
     only OID, scanned/not-scanned status, and finding count; never print matched bytes.
     Names-only and reachable-history scans do not satisfy this blob-completeness gate;
   - require the enumerated blob count, successfully scanned blob count, and zero-finding
     blob count to agree exactly. Treat an unreadable, oversized, unsupported, interrupted,
     or otherwise unscanned blob as a finding. Withhold the all-object pack whenever this
     complete blob-level proof is unavailable, even if every other artifact is clean;
   - preflight the exact destination repository and require private visibility, confirmed
     write permission, and absence of `refs/heads/agent/recovered-original-task3-10`;
   - if a trusted scanner is unavailable, any finding is nonzero, destination privacy is
     not verified, or the branch already exists, do not attach or push raw artifacts. Stop
     with hashes and a names-only inventory and request an approved restricted destination.
5. Verify the all-object pack in the disposable repository, run `git fsck --full` there,
   verify the bundle with `git bundle verify`, and clone the bundle into a second private
   temporary directory. Confirm every recovered locator resolves in the clone and record
   its full SHA, parent, tree, subject, and changed paths. Do not claim tests pass unless
   they are already represented by a durable receipt; this export stage must not execute
   the solver.
6. Only after every prior gate passes, preserve the highest verified descendant that
   contains the recovered Task 3–10 history by a direct, non-force SHA-to-ref push to the
   absent branch `agent/recovered-original-task3-10`. Do not modify `main`,
   `agent/longrun-checkpoints`, or local refs in the original repository. If ancestry is
   ambiguous or authenticated push is unavailable, do not guess a head; retain the private
   artifacts and report the blocker. After a push, require `git ls-remote` to return exactly
   the intended full SHA for the new branch.
7. Return links or attach artifacts only after the sensitive-data gate passes, plus a
   concise inventory. Explicitly distinguish:
   `DURABLE_VERIFIED`, `DIRTY_WORKTREE_CAPTURE`, `TRANSCRIPT_ONLY`, and `MISSING`.

If the original checkout/object store is absent or masked in this thread too, stop after
the inventory and state that exact recovery failed. Do not synthesize a substitute.

---
