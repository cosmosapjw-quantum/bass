# OpenAI Work artifact-loss incident request — BASS Task 3--10

## Submission route

1. Review the affected long-running Work chat for credentials, private data, or sensitive
   command output. Then type `/`, choose feedback, and opt to share the existing session.
2. Preserve the session ID returned by the UI. This session-sharing route is documented in
   [OpenAI troubleshooting](https://learn.chatgpt.com/docs/reference/troubleshooting).
3. Open the chat bubble at the lower right of
   [help.openai.com](https://help.openai.com/en/articles/6614161-how-can-i-contact-support)
   and submit the redacted request below privately, including the session ID.
4. The troubleshooting page also documents checking/opening a Codex GitHub issue. Use that
   public route only for a redacted report; do not post the session ID, shared-session
   contents, credentials, or an unscanned recovered artifact publicly.

The session ID is intentionally absent from this file because it is generated only after
the user submits feedback. The current sandbox cannot submit or retrieve it.

## Suggested private-support title

`Server-side recovery/export request: inaccessible or missing-or-masked ChatGPT Work sandbox artifacts and Git objects from BASS Task 3--10 run on 2026-08-09`

## Request body

I am requesting a server-side artifact recovery/export investigation, not code
reimplementation assistance.

On 2026-08-09, a long-running ChatGPT Work task reported implementing BASS Task 3--10
inside a managed Work sandbox. During that run I noticed that no durable artifact had yet been
delivered, so I created the public GitHub repository
`https://github.com/cosmosapjw-quantum/bass` and explicitly instructed the task to back up
the work there. The conversation subsequently reported implementation/review progress and
short Git commit locators, but the implementation, checkout, dirty state, and Git objects
did not reach the repository and are no longer visible in the current sandbox.

Reported locators:

- Task 5 review head: `3347547`
- Task 6: `eaf13af`; fix: `4e1a3b6`
- Task 7: `54fb3bf`; later fix identifiers were not retained
- Task 8: `29327f9`; fix: `e993691`
- Task 9: `6d786e1`; fix: `c3d45f3`
- Task 10: in progress; no final locator was delivered

A non-destructive recovery audit checked every accessible workspace Git root, locally
reachable and unreachable object, archive, reflog, GitHub-advertised ref, and API-visible
repository object. None of the locators or the reported production `bianchi/full` tree
could be resolved. The original workspace-root `.git` was masked by an empty read-only
`tmpfs` in the later runtime. All processes visible to that audit shared the inspected
mount namespace; server-only snapshots and GitHub dangling objects were not enumerable.
The evidence-supported classification is therefore `MISSING_OR_MASKED`, not proof of
physical deletion.

Durable recovery investigation records are preserved at:

- repository: `https://github.com/cosmosapjw-quantum/bass`
- branch: `agent/longrun-checkpoints`
- recovery checkpoint: `c9cd8ecb8765649ace77ea8f22890ff4c24153eb`
- boundary document:
  `docs/recovery/RECOVERY_BOUNDARY_20260810.md`
- original-runtime export procedure:
  `docs/handoff/ORIGINAL_RUNTIME_EXPORT_PROMPT_20260810.md`

Please determine whether OpenAI still retains any of the following for the shared Work
session/task:

1. the original task environment or filesystem snapshot;
2. the underlying Git object store hidden below the later `.git` mount;
3. a retained task diff, patch, checkout snapshot, generated artifact, or upload staging
   object;
4. a server-side command/action record containing patch bodies or full commit object IDs;
5. a restorable Codex/Work worktree snapshot associated with the affected session.

If any item exists, please preserve it and provide a read-only export or a supported secure
recovery procedure. A complete Git bundle/all-object pack, exact checkout archive, or
binary patch with provenance metadata would be suitable. Please do not publish recovered
material to the public repository automatically; notify me so it can first pass a
blob-complete sensitive-data scan in a private location.

If no recoverable artifact exists, please state, if available, whether the cause was
retention expiry, environment replacement, worktree cleanup, runtime interruption, or a
platform incident, and whether any preservation hold can still be placed on the associated
session metadata.

## Candidate attachments after owner review

- The shared affected session and its UI-generated session ID, only after reviewing the
  shared-session contents for credentials, private data, and sensitive command output.
- The public recovery commit and documents linked above.
- Hashes and names-only inventories from the recovery audit.

Review every attachment separately. Do not attach raw environment variables,
credential-bearing remote URLs, private keys, unscanned logs, or any future recovered
object pack. Keep the session ID out of the public repository and any public issue. OpenAI's
troubleshooting documentation also advises reviewing logs for sensitive material before
sharing them.

## Local continuation policy

Route A clean reconstruction proceeds independently and does not wait for support. Any
later recovered object is quarantined and compared against Route A; it does not overwrite
the clean-rebuild branch or retroactively validate reconstructed code.
