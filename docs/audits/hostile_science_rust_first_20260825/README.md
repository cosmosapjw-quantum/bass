# BASS hostile science + Rust-first audit package

This is a docs-only audit and executable development contract bound to PR #27 head `e4d9833b5d314ff6cdd0b0a12fe2a8c9a660664c`. It changes no runtime, formula, tolerance, reference, solver, performance claim, or authority.

## Verdict

- Engineering: RF-01 code-contract PASS; RF-02 needs a compiled, fail-closed contract.
- Science: strong exploratory solver with major closure required; no positive physics conflict or integrity failure is established.
- Production/publication: not established.
- Performance: not run on a qualifying host; no speedup claim.
- Formula/Wolfram: scoped and partial; PR #22 remains unpromoted.

The highest-priority new finding is an acceptance-detector defect: `audit/manifest.json` says 72/72 PASS while `r4_bianchi_constraints.json` records `bianchi_identity_vanishes=false`, and `run_all.py` does not gate that boolean. This is not yet proof of a bad Einstein equation. RF-02A must diagnose the exact symbolic reduction and make the detector fail closed before geometry/constraint promotion.

Other promotion blockers include E1/E2 near-null Lorentz conditioning and E3 certificate forgery, formula-hash scope collision, surrogate rather than original Type-II thermodynamics, missing final 2B.3 bytes, incomplete full-output/statistics routes, and an exact-digest benchmark comparator incompatible with legitimate SIMD/parallel low-bit changes.

## Files

- `CURRENT_STATE.json`: live continuation and artifact refs; owns dynamic state.
- `AUDIT.json`: claim register, findings, P0/P1 threats, RF-02A–E and RF-03–FINAL work units, benchmark/artifact/Wolfram policies.
- `PROMPT_CONTRACT.json`: exact executable Codex contract in canonical order.
- `HANDOFF.md`: short copy/paste handoff.
- `INDEPENDENT_REVIEW.json`: fresh-context package review.
- `MANIFEST.sha256`: content seal; excludes itself.
- `verify.py`: local structural verifier.

## Anti-accretion

Evidence stays machine-readable. Human documents cite it rather than repeating hashes, part lists, receipts, logs, restore transcripts, or the entire handoff recursively.

Exactly one next action: `RF-02A_BIANCHI_IDENTITY_AND_GEOMETRY_AUTHORITY`.
