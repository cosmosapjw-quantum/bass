# Local Codex prompt — BASS-8B.3R1 exact 2B.3 package identity recovery

Repository: `~/bass`

## Goal

Recover or explicitly supersede the missing exact BASS-8B.2B.3 final package.
This is provenance recovery only. Do not change physics.

## Frozen identities

```text
expected final filename
BASS8B2B3_PROJECTOR_LEFT_FUNCTIONAL_KATO_AUDIT_CANDIDATE_20260824.zip

expected final size
633703 bytes

expected final SHA-256
23d7ff71dff3d10f15efbebefe52839effa28bfb93fba5b725ab2faa2c12b0cc

GitHub seal
agent/verify/bass-8b2b3-projector-left-kato-20260824
d8ba3a609855d9d8a540ae0397d665dfe420393b
```

The currently materialized file with that filename is an earlier archive:

```text
size 514231 bytes
SHA-256 5532588b554029d31d9fff1cd9ea994862a354436a1febc6a2c19c63de3dbace
```

Do not overwrite expected hashes to fit it.

## Procedure

1. Create a clean read-only inventory of every local/Dropbox/GitHub copy with
   filename, byte size, SHA-256, mtime, and source location.
2. If a copy exactly matches the expected size and SHA, restore it without
   modification and run the complete final gate.
3. Complete final gate:
   - ZIP CRC
   - manifest 57/57
   - frozen input hashes 4/4
   - 53/53 tests
   - exact SymPy
   - exact Wolfram
   - xAct/xTensor receipt or native replay
   - numerical receipt 500/80/120
   - four plots present
   - pure-Python target policy
4. If exact recovery fails, do not manufacture the old hash. Instead determine
   whether exact final source/test bytes are available. Only if they are, build
   a deterministically named superseding package with a new checksum and run the
   same gates.
5. Preserve the current 514231-byte archive under an `EARLIER_NONCANONICAL`
   quarantine name with its actual hash; do not delete it.
6. Produce a receipt explaining route A or route B, exact commands, outputs,
   hashes, and no-physics-change diff.
7. Push one verification-only commit to a descendant branch. No PR, merge, tag,
   classifier, Rust lowering, runtime, or row promotion.

## Stop conditions

```text
BLOCKED_EXACT_FINAL_BYTES_NOT_FOUND
BLOCKED_FINAL_SOURCE_BYTES_INCOMPLETE
BLOCKED_GATE_MISMATCH
```

A blocked result is valid. Never convert a receipt-only claim into exact-byte
authority.
