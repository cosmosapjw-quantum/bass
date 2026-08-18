# BASS Wolfram/xAct/Python Structural-Compiler Plan
Date: 2026-08-18
Status: ARCHITECTURAL DESIGN — IMPLEMENTATION REQUIRES EXPLICIT APPROVAL

## 0. Decision

Do **not** add Julia/ModelingToolkit as a core dependency now.

Reproduce the ModelingToolkit capabilities BASS actually needs with:

- Wolfram Engine 15 + xAct/xTensor/xPerm/xCoba: mathematical/tensor authority and
  symbolic transformation oracle;
- Python: compiler orchestration, graph algorithms, pass registry, provenance,
  caching, testing;
- SymPy: portable scalar/matrix symbolic lowering, CSE, independent Jacobians,
  Rust printer/code generation;
- Rust: only production numerical runtime/backend.

Wolfram C generation is **not** a core backend. Treat it as a separate optional
verification project with the same approval/cost level as adding Julia.

## 1. Architecture

Formula Authority
  -> Continuum SymIR
  -> Structural Compiler Passes
  -> Exact Branch/Invariant Specialization
  -> Discretization IR
  -> Generated Rust Kernel IR
  -> Rust Runtime

Wolfram/xAct and SymPy are independent symbolic engines around the neutral IR;
neither engine owns the source of truth.

## 2. ModelingToolkit capability parity

### P0: already required by BASS

1. Hierarchical component/equation graph
2. Typed unknown/parameter/observable metadata
3. Dependency graph and stage extraction
4. Exact branch specialization
5. Symbolic Jacobian/JVP generation
6. Jacobian/block sparsity
7. Common-subexpression elimination
8. Transformation provenance/ledger
9. Parameter-update vs compile-time cache separation
10. Consistent initialization/constraint checks
11. DAE residual/mass-matrix representations
12. Equation-variable structural matching
13. SCC/BLT decomposition
14. Tearing/algebraic variable elimination
15. Index reduction
16. Generated Rust scalar/vector/operator kernels

### P1: near-term

17. Hessian / second directional derivative metadata when needed
18. Event/domain-boundary metadata without changing physics equations
19. Sensitivity/JVP/VJP hooks
20. Static dimension/unit/frame checks
21. Observed-variable graph and once-only map tokens
22. Compile-time stiffness/commutator diagnostics
23. Matrix-free low-rank operator programs
24. Compile cache keyed by formula/branch/representation/discretization hashes

### P2: later

25. Automatic solver recommendation metadata
26. Large-system tearing heuristics
27. Symbolic parameter identifiability/degeneracy checks
28. Multi-target code-generation optimization

## 3. Division of labor

### Wolfram/xAct

Owns:
- abstract tensor algebra and canonicalization;
- tensor symmetries and index equivalence;
- exact branch/invariant-manifold proofs;
- Reduce/Solve/Eliminate/GroebnerBasis-based exact algebraic reduction;
- symbolic differentiation of authority expressions;
- DAE/index-reduction reference calculations;
- symbolic sparse matrices and structural incidence validation;
- theorem/identity oracle;
- optional FunctionCompile acceleration **inside the verifier/compiler process**.

Does not own:
- production code generation;
- Rust source layout;
- runtime solver;
- discretization authority.

### Python compiler orchestrator

Owns:
- neutral IR schema;
- component registry;
- graph construction;
- equation-variable bipartite matching;
- SCC/BLT decomposition;
- deterministic pass scheduling;
- transformation ledger;
- content-addressed caches;
- differential/property-based test generation;
- Wolfram and SymPy subprocess/session orchestration.

Prefer public Python algorithms or small owned implementations. Do not make
undocumented Wolfram internals part of the compiler contract.

### SymPy

Owns:
- independent scalar/matrix oracle;
- CSE and algebraic lowering;
- numerical lambdify reference;
- sparse/Jacobian cross-checks;
- RustCodePrinter/RustCodeGen output;
- generated-code expression normalization.

### Rust

Owns:
- generated low-rank/matrix-free operators;
- numerical kernels;
- exponential/phi actions;
- sparse/iterative runtime;
- production integration and tests.

## 4. MTK feature replacement map

| ModelingToolkit feature | BASS replacement |
|---|---|
| System/component model | Neutral SymIR component graph |
| structural_simplify | Owned pass registry + Wolfram/SymPy simplifiers |
| alias elimination | Union-find / exact equality pass |
| tearing | bipartite equation-variable graph + SCC/BLT |
| index reduction | owned Pantelides-style pass; NDSolve as oracle |
| initialization system | generated constraint system; Wolfram Reduce/FindRoot + Python numerical fallback |
| observed variables | typed derived/observable nodes |
| symbolic Jacobian | Wolfram D + SymPy Matrix.jacobian cross-check |
| jacobian sparsity | structural incidence + SparseArray/SymPy sparse |
| Hessian/tgrad | generated derivative passes as demanded |
| build_function | SymPy/WXF -> deterministic Rust codegen |
| problem specialization | compile-keyed generated kernel packages |
| parameter updater | runtime parameter block, no recompilation |
| solver integration | Rust runtime + SciPy/Wolfram reference lanes |

## 5. Important non-goals

- No automatic approximation switching.
- No near-manifold equation replacement.
- No finite discretization promoted to continuum authority.
- No silent angular-rate -> scalar coercion.
- No reliance on NDSolve private ProcessEquations interfaces.
- No Julia dependency in the default build.
- No Wolfram-generated C in the default build.

## 6. Work packages

### WSC-0 — Wolfram capability probe
Verify Engine-15 availability/behavior for FunctionCompile, sparse symbolic
arrays, DAE/index reduction, Python ExternalEvaluate, WXF exchange, and xAct.

### WSC-1 — Neutral compiler IR v1
Schema for variables, equations, operators, tensors, domains, frames, units,
stages, exact predicates, observables, transforms, provenance and hashes.

### WSC-2 — Structural graph compiler
Incidence graph, matching, SCC/BLT, dependency/stage extraction, alias
elimination, exact-specialization pass.

### WSC-3 — DAE/initialization parity
Mass-matrix/residual forms, owned Pantelides-style index reduction, generated
initialization constraints, NDSolve oracle comparison.

### WSC-4 — Derivative/sparsity parity
Jacobian/JVP/tgrad/Hessian where required, sparsity/block metadata, Wolfram vs
SymPy differential seals.

### WSC-5 — Rust lowering
CSE, deterministic naming, RustCodeGen, low-rank operator templates, generated
manifest/provenance, compile cache.

### WSC-6 — Type-II generated Kato kernel
First vertical slice: generated 5-state background, P, dP/dv, Kato connection,
collision actions and Kato-AEM2.

### WSC-7 — Cross-branch expansion
VI0 -> VII0 -> VIII first; then class B; IX/exceptional last.

## 7. Verification policy

For every generated physical kernel:
1. formula-authority hash;
2. Wolfram/xAct seal;
3. SymPy independent seal;
4. generated Python reference;
5. generated Rust differential test;
6. continuum/discretization contract tests;
7. branch oracle;
8. source/provenance manifest.

## 8. C-code policy

Wolfram C code generation is OFF by default.

If later approved, create a separate `W-CODEGEN-VERIFY` project to generate an
independent native verifier. It is not allowed to become a production backend
or a hidden dependency of the Rust build.
