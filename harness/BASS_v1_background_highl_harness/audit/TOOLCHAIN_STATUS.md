# Toolchain and uploaded executable-material status

## Rust 1.94.1

The uploaded tarball SHA-256 is
`294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40`,
which exactly matches the 2026-03-26 official `channel-rust-1.94.1.toml` entry for
`x86_64-unknown-linux-gnu`. Its detached signature verifies against the Rust release key:

`108F 6620 5EAE B0AA A8DD 5E1C 85AB 96E6 FA1B E5FE`.

The tar structure is safe, but it expands to roughly 1.53 GiB and Rust 1.94.1 is now a
historical reproducibility toolchain rather than current stable. It was not installed.
The XZ stream declares no internal stream checksum; decodability was checked with
`xz --test`, while payload authenticity rests on the external official SHA-256 and valid
detached signature.

## Rejected environment script

`rust_1_94_1_env.sh` hard-codes `/mnt/data`, mutates ambient `PATH` and
`LD_LIBRARY_PATH`, and produces a trailing empty loader path when the prior variable is
empty. That empty element can resolve to the current directory. The script must never be
sourced. A future authorized toolchain adapter must be project-local and command-scoped.

## Rejected bootstrap

The uploaded `bootstrap.sh` is a full environment mutation/build/test script, not a
harness installer. It uses system pip and `--break-system-packages`, installs unpinned
`maturin`, edits source, builds/tests Rust, force-installs a wildcard wheel, imports project
code, suppresses full logs, skips long tests, and does not assert its printed pass counts.
It also expects files absent from the supplied partial Rust-core archive. It was not run.

## Partial Rust-core archive

The small archive contains 23 safe structural entries and no obvious first-party process,
network, or unsafe-Rust calls, but it is an unsigned partial overlay without a canonical
commit mapping. Its tests require missing modules and it cannot run standalone. It is
historical comparison material only until the user uploads canonical code.
