# Historical partial Rust/Python overlay

This directory preserves the exact regular-file payload of
`bianchirustcoreRDAGcomplete.tar.gz` without installing it into the repository's
production package namespace.

- Source archive SHA-256:
  `53597fb5dd2aee25a75bfedc2f001574db90b1a5580ad60410b575f76c8aa9fb`
- Extracted regular files: 18
- Evidence class: `PARTIALLY_RECOVERED`
- File manifest: `../../manifests/LEGACY_PARTIAL_SHA256_20260809.txt`

The payload contains a Rust crate, two Python dispatch overlays, two differential or
integration test files, and historical prose. It does **not** contain the complete Python
solver baseline, its dependency environment, a Git commit identifier, execution logs, or
the lost `bianchi/full/{geometry,fluids,history,opacity,sources}.py` implementation.

The archive's embedded test counts, numerical residuals, and performance measurements are
self-reported historical claims and are not promoted by this recovery. The files are kept
here for byte-level comparison and later selective transplant onto a separately verified
complete baseline. They must not be imported or released as a standalone BASS solver.
