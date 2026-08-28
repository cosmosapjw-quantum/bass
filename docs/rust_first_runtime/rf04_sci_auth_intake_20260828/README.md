# BASS RF-04 + SCI-AUTH-04 Intake Package

This package starts from the scoped RF-03 terminal branch:

```text
agent/architecture/rust-first-rf03-20260828-r2
6e53664d56694f7a7ad5f65be262302d5c8866b2
tree bb743717e8115821d72268d8384dc5cc7cc11975
draft PR #45
```

The compiled graph does **not** permit RF-04 to start directly. Its second
predecessor is the authority-only node `SCI-AUTH-04`, fixed to RF-02B commit
`0563c080e54fcd90d6160bec35e4f20d240d8d2e` / tree `40ae99f9e7465d6332e98b65a5269a1f71eadfb5`.

Execution order:

```text
SCI-AUTH-04
→ exact remote authority receipt
→ RF04-INTAKE-00
→ RF-04
```

The authority and runtime nodes use separate worktrees and branches. They may be
coordinated in one Codex run, but RF-04 source mutation begins only after
`PASS_SCI_AUTH_04_VALIDATOR` is remotely read back.

This is progress-enabling authority work: RF-04 explicitly depends on it. It is
not a new governance layer and must terminate after one validator/review cycle.

No BASS-12–15 optimization bytes are inputs. No merge, ready transition,
timing, GPU, Wolfram, full-suite reassurance, performance claim, or scientific
promotion is authorized.

Validate:

```bash
sha256sum -c MANIFEST.sha256
python validate_package.py
python validate_package.py --live --repo /path/to/bass
```

Then read `CODEX_HANDOFF.md`.
