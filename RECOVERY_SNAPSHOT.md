# Background evolution v87 source recovery

Snapshot date: 2026-08-24

```text
RECOVERED_SOURCE_SNAPSHOT
ORIGINAL_GIT_LINEAGE_UNAVAILABLE
NO_AUTHORITY_PROMOTION
FULL_PYTHON_RUNTIME_SUITE_ENVIRONMENT_BLOCKED
INDEPENDENT_RECOVERY_REVIEW_CONFIRMED
```

## What was recovered

This branch restores the latest complete source-bearing attachment,
`bianchireview87.tar(3).gz` (SHA-256
`6bb094d30a6d24b3feee11a1d9ae2827049945dae8281ed37d0d0796a6e9ea84`).
It includes the Python background-evolution implementation, the Rust backend,
tests, independent audits, scripts, and the Q-layer sources present in that
87th-cycle archive.

The earlier `bianchicoverage87.tar.gz` is a strict predecessor: every one of
its source files is present in the review archive, while the review archive
adds Q19/Q20/P9-related files and changes later-cycle files. It was therefore
used for lineage comparison, not overlaid on the restored tree.

The separate `bianchirustcoreRDAGcomplete.tar.gz` is an older, partial Rust
background overlay. Its equations and interfaces already occur in the review
archive; it was not treated as a newer source generation.

## Formula authority included as provenance

Selected, byte-preserved receipts from `Bianchi_Core_Closure_Final(1).zip`
are under `provenance/formula_core/`. Its supplied wrapper verifier freshly
passed 21/21 integrity and claim-consistency gates, including its 179-row
manifest and formula Git-bundle checks. This is not a fresh Wolfram or
mathematical-engine replay. The archive's own claim policy explicitly says
that it does not contain an Einstein-evolution or background solver. It
therefore supports conventions and formula provenance only; it is not merged
into runtime code.

Important namespace and time-coordinate firewalls remain unresolved:

- Rust `kappa = 1/h` is not Thomson opacity `kappa = n_e sigma_T`.
- Rust `Omega` is a density parameter, not the closure `OmegaTriad`.
- Wainwright--Ellis normalized `tau` and variables require an explicit bridge
  to the closure archive's physical `t`, `Hgeom`, `sigma`, `n`, and `a`.

## Deliberate exclusions

The recovery tree omits reproducible or inappropriate backup payloads:

- Python/test caches and bytecode;
- generated PDF/PNG reports and plots (their TeX, JSON, Mermaid, scripts, and
  source data remain);
- TeX auxiliary/log/output files and a transient runtime log;
- `refs_neutrinos_LewisChallinor.tex`, a complete third-party manuscript
  source rather than project code.

Two required generated inputs remain: `bianchi/generated/riemann_frame.pkl`
and `bianchi/matter/gaunt_tables.npz`. The pickle is provenance-pinned and was
only opcode-parsed here; it must still be treated as untrusted data before any
future load.

No scientific source file in the retained review-tree set was edited. New
files are limited to recovery metadata, hashes, ignore rules, and selected
formula-authority receipts.

## Claim boundary

This is a recoverable source snapshot, not a production promotion. Historical
test counts in `README.md`, `STATE.md`, reports, or receipts are preserved as
archive statements and are not automatically inherited as fresh results.
See `provenance/recovery/RECOVERY_PROVENANCE.json` and
`provenance/recovery/SOURCE_TREE.sha256` for the exact recovery record.

## Fresh checks on the recovery host

The retained tree passed byte-identity and secret-pattern checks plus Python
compile (302/302 files), JSON parse (30/30), TOML parse (3/3), shell parse
(3/3), Rust parse (40/40), and locked/offline Cargo metadata. The generated
pickle was opcode-parsed without execution; the NPZ asset opened with pickle
loading disabled.

The full Python runtime suite was not run because this host lacks pytest, JAX,
diffrax, sympy, and maturin. A locked/offline Rust test build reached dependency
resolution and stopped because `nalgebra` is not cached. These are environment
limits, not passing test results and not evidence of a source failure.

The previously recorded external oracle
`cosmosapjw-quantum/bianchi_phase_r@539fcd6acc81dfd19d05951c2c5cbc3602eda077`
was also inspected. It is an older, structurally distinct Phase-R
authority/design repository and shares no nonempty source blob with this v87
tree. It remains an external oracle, not recovered ancestry.

A fresh read-only reviewer independently reproduced the archive selection,
retained-byte counts, static gates, manifest coverage, and formula wording.
Its post-fix verdict is `CONFIRMED`; this confirms the bounded recovery claim,
not solver correctness or production readiness.

Git records only executable/non-executable file modes. Two archive files that
arrived as mode `0600` are therefore normalized to regular Git mode `100644`;
the two executable shell scripts remain `100755`. File contents are unchanged.
