# WSC-2 Structural Graph Compiler Implementation Plan

**Goal:** Compile Neutral Continuum SymIR v1 into deterministic equation/variable structural metadata without performing DAE index reduction.

**Architecture:** Python owns graph orchestration and provenance. Exact predicates may specialize structure; numerical hints may not. Wolfram graph/SCC and future DAE transformations remain independent oracles, not hidden compiler contracts.

**Tech Stack:** Python standard library, pytest, BASS SymIR v1.

## Tasks
- [x] reference extraction and exact-predicate activation
- [x] exact alias elimination
- [x] equation/unknown incidence graph
- [x] deterministic maximum matching
- [x] dependency graph and Tarjan SCC
- [x] BLT ordering metadata
- [x] stage extraction and diagnostics
- [x] deterministic pass hash/proof receipts
- [x] regression tests
- [ ] branch commit/push and stacked PR

## Deferred to WSC-3
Pantelides/dummy derivatives, residual/mass-matrix DAE lowering and initialization-system generation.
