# Validation receipt

- Partial outer ZIP SHA-256: `9d0cd053db614521d5a853542fe253a3337e62c660cdde09b0cfe8ca735d2729`.
- Partial bundle internal manifest: **21/21 PASS**.
- Closure-control verifier: **PASS**, 47 files, 16 tasks, 12 claims, 12 risks.
- A previously reused `/tmp` extraction failed closed on its own unmanifested
  `scripts/__pycache__/verify_package.cpython-312.pyc`. A fresh extraction of
  the same immutable control ZIP then passed the verifier; this is preserved as
  derived-cache contamination, not package-byte or scientific-integrity
  failure.
- Quarantined earlier candidate: 514231 bytes and
  `5532588b554029d31d9fff1cd9ea994862a354436a1febc6a2c19c63de3dbace`.
- Authenticated Actions inventory contains four 2A evidence artifacts and no
  2B.3 artifact.
- The original outer sidecar's digest is correct but its `/mnt/data` absolute
  pathname is nonportable. The portable sidecar in this directory changes only
  that filename field.
- No final 633703-byte / `23d7…` ZIP and no frozen-complete rebuild corpus is
  present. Final package scientific gates were not run and are not claimed.
