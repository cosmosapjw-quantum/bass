# Next action

Execute one bounded provenance-recovery node:

```text
BASS-8B.3R1_EXACT_2B3_PACKAGE_IDENTITY_RECOVERY
```

Acceptance has two allowed routes.

## Route A — exact recovery

Recover the exact 633703-byte final archive and require:

```text
SHA-256 23d7ff71dff3d10f15efbebefe52839effa28bfb93fba5b725ab2faa2c12b0cc
ZIP CRC PASS
manifest 57/57 PASS
focused + predecessor tests 53/53 PASS
exact SymPy/Wolfram/xAct receipts PASS
numerical receipt 500 random / 80 FD / 120 SO(3)
```

## Route B — explicit superseding reseal

If the exact archive is irrecoverable, reconstruct the final source/test/evidence
surface from exact source bytes, run the same gates, and issue a *new filename and
new SHA-256*. Do not reuse the old final checksum and do not relabel the current
514231-byte earlier archive.

After A or B passes, rerun `BASS-8B.3` as a no-new-physics readjudication. Only
then may rows 7–8 be promoted. Rows 9–10 must still be closed before any full
replacement-intake PASS or BASS-3 classifier authorization.

Forbidden during recovery:

```text
classifier implementation
Rust lowering
runtime/solver wiring
row promotion by prose only
PR/merge into production
Join J1
```
