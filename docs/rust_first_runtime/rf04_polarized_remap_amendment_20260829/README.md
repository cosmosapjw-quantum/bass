# RF-04 Polarized Remap Amendment A2

This publication resolves the source-contract gap for
`polarized_rank9_v1` trajectory remapping by freezing the existing RF-03 donor
semantics. It does not add a new formula, grid, tolerance, interpolation
family, or standalone Kato operator.

The direct package ZIP contains the complete machine-readable contract,
source-authority map, schema, work units, acceptance matrix, implementation
plan, Codex handoff, and validator.

Key identities are in `PACKAGE_INDEX.json`. The immutable package commit/tree
is supplied by `PUBLICATION_RECEIPT.json` after publication.

Claims remain:

```text
PASS_RF03
PASS_SCI_AUTH_04_VALIDATOR
NO_PASS_RF04
exact next action: RF04-GREEN-02
```

The retained local RF-04 RED commit is reused; intake and RED must not be
rerun unless this amendment explicitly invalidates them (it does not).
