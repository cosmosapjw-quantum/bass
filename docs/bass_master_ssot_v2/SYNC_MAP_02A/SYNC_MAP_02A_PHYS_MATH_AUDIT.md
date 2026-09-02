# PHYS-MATH audit — SYNC-MAP-02A

## Verdict

`PASS_WITH_SEMANTIC_SCOPE`

The registry contains fourteen unique BASS-owned geometry formulas. Every record is valid `EquationIR`, contains exact coefficients only, preserves assumptions/domain/dimensions/branch predicates/known limits, and has a 64-character semantic SHA-256. The dependency graph has fifteen closed edges and includes the load-bearing chain

```text
STRUCTURE_CONSTANTS
→ LEVI_CIVITA_CONNECTION
→ SPATIAL_RIEMANN
→ SPATIAL_RICCI
→ SPATIAL_SCALAR.
```

The semantic projection deliberately drops only `schema_version`, `formula_id`, `authority_theorem`, and `provenance`. A mutation of ID or provenance therefore leaves the semantic hash invariant, while a mathematical assumption, coefficient, dimension, domain or limit mutation changes the payload.

This is a registry/provenance theorem, not a new tensor derivation. It does not assert that any REC or REI formula is equivalent to a BASS formula. No P0/P1 mathematical defect was reproduced within this scope.
