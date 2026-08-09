# Independent H0 supply-chain review

- Verdict: PASS
- Blocking findings: 0
- Reviewer run: `audit-rust-bundle-20260802-final-a1f7767`
- Reviewer assignment: `review-h0-final-a1f7767`
- Reviewer lane: `rust-supply-chain-independent`
- Producer evidence: `evidence/E-H0-20260801-V2.json`
- Producer evidence physical SHA-256: `a1f7767ad762e26de5ac2d42b61d0acc232d823c4c7084990bb47c4f06b4a5f2`
- Producer evidence canonical fingerprint: `5874078a5e37b9dd320c9bc27d10089c5c0b9faa37a13006707ef7a5fde165e8`
- Governing fingerprint: `3b2a4751248c298587961ffc4c434f84162580e1522235fcc1421d987955075b`
- Producer static-log SHA-256: `43e2fdaaf65c0275839aa3328a67d6b043f55cb3bad1cb65ea82869c5f22fed8`
- Bundled reviewer static-log SHA-256: `8cc4d1d89423ede8f7b6331db1c1c3fc3e97c36cc9ee706afc22bba55f9240c3`
- Reviewer-owned post-submission rerun SHA-256: `6ad1f5c2da5f24d13b6f80cf12e3baa0d6ae94d7ec45770da9c3a7ee3d35d994`

The reviewer independently recomputed all governing, evidence, environment, artifact,
and source hashes against the exact producer submission. The separate post-submission
run started at `2026-08-02T02:04:14.458273+09:00`, after producer recording at
`2026-08-02T02:03:40.181669+09:00`, and completed 19/19 exact canonical argv/cwd and
result-specific semantic checks. Pre/post governing snapshots were identical. The
bundled reviewer execution is also post-submission, distinct from the producer log, and
passes the current validator with zero static-plan errors.

SRC01--SRC13 match current bytes, the inventory, and producer evidence. The four small
archives contain 59, 46, 23, and 38 entries with no unsafe paths, links, special files,
duplicates, or integrity failures. A separate streamed hostile pass over the Rust tar
counted 51,085 entries (49,640 files and 1,445 directories), 1,566,109,282 regular bytes,
and no unsafe path, link, special, privileged-mode, or duplicate entry.

The Rust 1.94.1 tar matches official SHA-256
`294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40`.
The supplied detached signature is byte-identical to the official ASC and verifies Good
under full fingerprint `108F66205EAEB0AAA8DD5E1C85AB96E6FA1BE5FE`. The repository
origin is `https://github.com/cosmosapjw-quantum/bianchi_phase_r.git`; porcelain is clean;
local and remote HEAD/main equal `539fcd6acc81dfd19d05951c2c5cbc3602eda077`; and tree is
`7f155a4c815495c519f30d78ea8682bf3e3b0162`.

No dependency, Rust toolchain, or harness was installed; no archive was overlaid; and no
solver source was read, built, executed, or modified. H0 has no dependency, obligation,
or claim effect and remains limited to input/provenance audit.

Explicit non-blocking boundaries: compiler binaries and third-party build scripts were
not semantically audited; the XZ has no internal checksum but is authenticated by official
SHA-256 plus GPG; the partial Rust-core provenance remains unresolved and historical-only;
and the Git repository remains a read-only external oracle with no production authority.
