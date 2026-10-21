# BASS PR174 backup intake — 2026-10-19

No new execution result was found in the inspected /BASS_BACKUPS locations. The latest actual closeout receipt names final publication `a9c3e495fb460b3ec25bfa297b89c8fbd09c07fc` and implementation `930406550ce6d4d1b2e87f016c5c18fba48c4ccd`. It records the new Rust projection as NOT_RUN, the P4 extension as DEFERRED_NOT_RUN, and NCP as NOT_RUN. These are historical receipt states, not inherited runtime incapabilities.

## Examined coverage

- Dropbox: 18 direct entries and 17 entries in all four direct child folders; each listing had has_more=false. Latest archive server time: 2026-10-18T14:45:16Z.
- Drive: 33 direct entries (scan limit 200; no pagination token returned) and 17 entries in all four direct child folders. Latest archive modified time: 2026-10-18T14:45:32.746Z.
- Actual content: newest closeout and nested/original recovery archives, including publication, test, recovery and original native execution receipts. Original NATIVE.jsonl has 58 measurement records plus one completion footer; five negative controls have exit code 3. No campaign was reexecuted.

## Byte and source identity

- Closeout: 82,208 bytes; SHA256 `25d0031aa6c99e55508a4ce76479ca13a9ab12f79c20e182a23ae44b5d64d84c`; all eight manifest entries match.
- Recovery: 77,758 bytes; SHA256 `8d71c52d7709b6d1867c14fe21af0a6a592eaf86c3099c2d2151c4aecb22c92e`; all 28 manifest entries match.
- Drive supplied raw bytes through its connector. Dropbox supplied extracted archive text and an independent provider content hash matching the Dropbox block hash computed from the Drive bytes for each archive. This is not labeled as a current raw Dropbox redownload.

## Current transfer limitations

Direct sandbox HTTPS was denied by its network environment. Automatic escalation review could not complete because its selected model was at capacity; the download action was not executed and the review made no unsafe determination. Supported connector reads completed the intake without requesting user action.

Full provider object IDs, source identities, coverage, and exact failures are in BACKUP_INTAKE_20261019.json.
