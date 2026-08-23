# BASS-8B.1 electron applicability decision — preservation supplement

This directory preserves the exact decision package produced after the bounded
BASS-8B.1 applicability comparison. It is attached to, but does not rewrite,
the earlier E1–E4 checkpoint backup.

## Exact artifact

- `BASS8B1_ELECTRON_APPLICABILITY_DECISION_20260823.zip`
- SHA-256: `cbd1dc32971194de633aa03223d3a994e544621ba79805a3d58ed334fd276d1c`
- Decision: `SELECT_EXPLICIT_TYPED_ELECTRON_SPECIES_ADAPTER__ROW7_REMAINS_BLOCKED`
- Status: `PASS_DECISION_ONLY__NO_PROJECTOR_PROMOTION`

The ZIP is stored as eight lossless binary parts because the connector payload
limit is smaller than the archive. Run `./restore_archive.sh` from this
directory to verify every part, reconstruct the exact ZIP, verify the outer
SHA-256, and run its ZIP CRC test. The complete 15-file package—including the
decision, source snapshots, source ledger, SymPy/Wolfram witnesses, and package
verifier—is contained in the reconstructed archive.

The sibling `SUPPLEMENT_INDEX.md` gives a directly browseable comparison with
the preserved E1–E4 state.

## Comparison result

The decision agrees with the existing E1–E4 architecture on the points that
matter for authority control: independent and exact-comoving electron closures
remain distinct; a generic gamma-law fluid tilt cannot become electron velocity
by fallback; local observer/output boosts cannot replace the forward collision
frame; and authority rows 7–8 remain blocked.

The earlier E4 checkpoint names `BASS-8B.1E.5` as its next local implementation
node, while this package names `BASS-8B.2A` and `BASS-8B.2B` as control-plane
successors. This preservation backup records that naming seam without silently
superseding either route.

## Non-claims

This directory is not an authority-row promotion, classifier, solver, runtime
integration, production migration, merge candidate, or PR.
