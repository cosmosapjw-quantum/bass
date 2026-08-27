# BASS-12R1 quiet-host retry package

This is a minimal successor to the existing BASS-12 plan after the observed
`BLOCKED_HOST_OR_ENVIRONMENT` result. It does not create a new optimization,
review layer, or Git delivery lane.

It adds only:

1. a machine-resolvable two-snapshot quiet-host preflight;
2. a predeclared 10% RSS non-regression gate, closing the previously named but
   unspecified memory gate before any new timing is observed;
3. exact one-shot paired 1T/12T commands;
4. machine adjudication preserving `NOT_ATTEMPTED != REJECTED`.

The logical ZIP is stored as six ordered content-addressed parts. This is a
transport representation only; `UNPACK_AND_VERIFY.sh` verifies each part,
reconstructs the 18,264-byte ZIP, checks its SHA-256, and verifies the internal
manifest and contract tests.

Run:

```bash
./UNPACK_AND_VERIFY.sh /tmp/bass12-retry-package
```

Then follow `CODEX_HANDOFF.md`. The work unit is local-only: no commit, push,
PR, merge, Jira update, RF-02C mutation, or BASS-13 execution is authorized.
