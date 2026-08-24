# G-DYN-MANIFOLD-VI0 Design

## Purpose

Classify the moving-equilibrium manifold for the first non-Type-II Bianchi
family before any VI0 production solver or generic family dispatcher is written.
The output is an exact, branch-aware mathematical classification and a
machine-readable operator program for later lowering.

## Scope

This gate answers:

1. What exact branch predicates define the project VI0 chart?
2. Which variables independently parameterize the collision-equilibrium
   manifold?
3. What is the generic dimension of that manifold?
4. Is the projector `P` a function of one coordinate, several coordinates, or
   additional frame/gauge data?
5. What are the exact tangent derivatives `P_,A`, `Pdot`, and
   `K=[Pdot,P]`?
6. Which Type-II simplifications fail for VI0?

It does not implement a VI0 Boltzmann solver, time integrator, output map,
production dispatch, or numerical fit.

## Authority intake

The classifier consumes only exact project-owned formula sources with recorded
SHA-256 values. Registry labels, README claims and floating-point samples are
not formula authority. Intake fails closed if the background equations,
constraints, tilt variables, frame gauge and equilibrium carrier cannot be
traced to explicit sources.

The first receipt records:

- VI0 structure-constant/chart predicates;
- metric, orientation and connection conventions;
- state vector and algebraic constraints;
- fluid/tilt domain assumptions;
- collision-equilibrium state and left invariants;
- source hashes and supersession relationships.

## Classification method

Let the exact state be `x`, constraints be `C(x)=0`, and the equilibrium
projector be `P(x)`. The gate computes:

\[
T_x\mathcal C=\ker D C(x),
\]

then restricts the exact differential of `P` to the constraint tangent space.
The generic manifold dimension is the exact rank of that restricted map after
removing gauge directions that act trivially on the physical carrier.

A minimal coordinate set `z^A` is accepted only if:

\[
P=P(z^1,\ldots,z^d),
\qquad
\dot P=\dot z^A P_{,A},
\]

and the reconstruction is proven symbolically on the declared branch. Exact
rank and identity predicates are authoritative; floating-point SVDs are only
hostile diagnostics.

## Branch policy

The classifier separates:

- generic tilted VI0;
- zero-tilt invariant subspace;
- frame-degenerate or symmetry-enhanced boundaries;
- any equation-of-state bifurcation surfaces supported by the authority.

A generic result is never inferred from a boundary sample. A numerical value
close to zero never activates an exact branch predicate.

## Required negative controls

- Copying the Type-II ansatz `P=P(v2)` must fail unless the exact VI0 equations
  prove it.
- Dropping a VI0 constraint must change the tangent-rank receipt or fail.
- Replacing exact rank with pointwise numerical rank must be rejected.
- A gauge direction that changes coordinates but not the physical projector
  must not be counted as a manifold coordinate.
- A physical projector variation must not be removed as gauge.

## Outputs

```text
compiler/manifolds/vi0_authority.json
compiler/manifolds/vi0_classification.py
compiler/manifolds/vi0_operator_program.json
compiler/manifolds/G_DYN_MANIFOLD_VI0_AUDIT.md
compiler/manifolds/G_DYN_MANIFOLD_VI0_RECEIPT.json
compiler/tests/test_vi0_manifold_classification.py
compiler/oracle/WOLFRAM_VI0_MANIFOLD_ORACLE.json
```

## Acceptance

- all formula inputs and conventions are hash-pinned;
- exact branch predicates are explicit;
- constraint Jacobian rank and projector differential rank are exact;
- generic and boundary dimensions are reported separately;
- minimal coordinates reconstruct `P` exactly;
- `P^2=P` and differentiated projector identities hold;
- `K=[Pdot,P]` satisfies `[K,P]=Pdot` on the classified tangent space;
- independent Wolfram/SymPy parity holds at exact rational witnesses;
- Type-II one-coordinate transplantation negative control fails;
- no solver, production or cross-family generality claim is made.
