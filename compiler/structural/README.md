# WSC-2 Structural Graph Compiler

This pass consumes Neutral Continuum SymIR v1 and emits deterministic structural metadata.

Implemented in WSC-2:
- exact-predicate activation and provenance propagation;
- exact variable-alias elimination;
- equation/unknown incidence graph;
- deterministic maximum bipartite matching;
- variable dependency graph;
- strongly connected components;
- block-lower-triangular ordering metadata;
- stage extraction and under/over-determined diagnostics;
- deterministic content hashing.

Explicitly deferred to WSC-3:
- Pantelides/dummy-derivative index reduction;
- mass-matrix/residual DAE lowering;
- consistent initialization-system generation.

The compiler never uses `numerical_hint` or `physical_approximation` predicates to rewrite authority structure.
