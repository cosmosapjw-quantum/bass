# BASS generic-vector PR/merge execution package

This package compiles the already implemented default-off native host parity
candidate into the shortest safe integration path:

```text
fresh differential review
→ PR creation
→ explicit user-approved merge commit
→ post-merge targeted native execution
```

It deliberately does **not** create another authority review, evidence schema,
historical replay, full-suite campaign, or runtime/classifier project.

## Frozen identities

```text
base branch  agent/architecture/rust-first-rf02c-20260826-r1
base commit  445e50184823e58401a8212ceaaf736e72bb35f2
head branch  agent/integration/bass-generic-vector-host-parity-20260826
head commit  a979af6b022eb832215a2342a01fe6b85374b914
head tree    86cdac8dc695c4e6c012294c73eaedf4a55cc1ce
oracle       58d649d438415def3e646d8eee8d0e1f3159ed7f
```

The GitHub package is bound by its Git tree and verified semantically:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 VERIFY_PACKAGE.py .
```

Required marker:

```text
PASS_BASS_GENERIC_VECTOR_PR_MERGE_PACKAGE
```

A separate deterministic ZIP with an internal SHA-256 manifest is supplied for
local handoff and archival transport.

Start with `CODEX_HANDOFF.md` and execute WU-001 only.
