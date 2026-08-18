# Type-II generated Rust kernel integration

This directory is the generated-source artifact produced by
`compiler/lowering/rust_typeii.py`.

Reference integration fixture: the lockfile-exact `_rustcore` bundle with
`Cargo.lock` SHA-256
`d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310`.

To integrate into that crate without vendoring the environment into Git history:

1. copy `mod.rs` and the three generated `.rs` files to `src/generated/`;
2. add `pub mod generated;` to `src/lib.rs`;
3. run `cargo test --lib --locked --offline`.

Verified in the 2026-08-18 intake environment with Rust/Cargo 1.94.1:

- generated-module tests: 6/6 PASS;
- complete RustCore unit suite: 128/128 PASS.

The BASS public repository stores generated source and provenance, not the
32 MiB Cargo vendor bundle or the 184 MiB Rust distribution.
