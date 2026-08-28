# RF-03 Exact R2 Direct-Package Rebind

This is a transport/identity repair for the observed
`BLOCKED_BY_STATE_DIVERGENCE`. It is not a new science contract and earns no
RF-03 claim.

Canonical authority package:

```text
agent/plans/rf03-authority-resolution-20260828-r2
@ 55335d3817a82da7e0f9bf24ef7632a2533645d3
tree 7c02689430d01abdf998c5b7ab1c5a6eb48859f4
docs/rust_first_runtime/rf03_authority_resolution_20260828/direct/
```

The canonical format is `DIRECT_TEXT_FILES`. The historical R1 tree and all
ZIP/multipart transports are non-executable for this handoff.

## Validate this bootstrap package

```bash
sha256sum -c MANIFEST.sha256
python validate_rebind.py
python validate_rebind.py --live --repo /path/to/bass
```

## Execute

Read `CODEX_HANDOFF.md`. It materializes the exact R2 direct package into a
temporary directory, validates it, and leaves only implementation work for the
isolated local RF-03 worktree.
