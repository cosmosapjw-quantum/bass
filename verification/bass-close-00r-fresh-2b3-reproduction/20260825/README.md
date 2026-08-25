# BASS-CLOSE-00R — fresh 2B.3 scientific-content identity seal

This directory seals a deterministic **content transport capsule**, not a
byte-identical copy of the original ZIP container.

The original fresh ZIP identity remains frozen as:

```text
BASS8B2B3_PROJECTOR_LEFT_KATO_FRESH_REPRODUCTION_20260825.zip
size 1991574
SHA-256 3abfb5b9b41627521369fe69576f6dce58371a7d6ce82d0f31d21cf80aed2a9d
```

The GitHub transport capsule contains every load-bearing non-binary byte,
a complete 78-member original atlas, exact hashes for three provenance ZIPs,
and exact hashes plus generators for four figures. Its different transport
SHA-256 is expected and is not an identity collision.

Restore with `./restore_content_capsule.sh`; then run the restored
`./run_content_replay.sh` for the full numerical/figure replay.

This is a fresh reproduction, never a recovery of the historical
633703-byte / `23d7ff...` artifact. No authority row is promoted here.
