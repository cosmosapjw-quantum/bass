# BASS RF-03 Authority Direct Handoff R2

This direct-text package resolves the RF-03 authority blocker without inventing
new physics. It supersedes only the conflicting R1 clauses; all unaffected R1
numerical, audit, plot, reproducibility, and draft-PR gates remain active.

The selected production matter model is the existing explicit gamma-law tilted
perfect fluid in `bianchi/matter/fluid.py`, with caller-supplied `gamma` and
`p = (gamma - 1) rho`. The forbidden behavior is an implicit or hidden
constant-w fallback, not that explicit identity.

No source-authoritative tilted-temperature formula exists. RF-03 therefore
keeps `T_gamma` exogenous and proves that changing it does not change the
matter force or JVP. Historical Type-II thermodynamics remains surrogate-only.

Validate:

```bash
sha256sum -c MANIFEST.sha256
python validate_package.py
python validate_package.py --live --repo /path/to/bass
```

Then execute `CODEX_HANDOFF.md`. Keep PR #36 and PR #37 draft/unmerged.
