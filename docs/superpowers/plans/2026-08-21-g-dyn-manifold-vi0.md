# G-DYN-MANIFOLD-VI0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an exact, branch-aware VI0 moving-equilibrium manifold classification without implementing a VI0 solver.

**Architecture:** A hash-pinned authority intake feeds a SymPy classifier for constraints, tangent spaces and projector differentials. Exact Wolfram witnesses provide an independent oracle. The output is a neutral operator program for later Rust lowering, not runtime code.

**Tech Stack:** Python 3.12+, SymPy 1.14, Wolfram Engine 15, JSON, pytest.

**Spec:** `docs/superpowers/specs/2026-08-21-g-dyn-manifold-vi0-design.md`

## Global Constraints

- Preserve metric signature `(-,+,+,+)` and the project connection/orientation conventions.
- Natural units are not assumed; every imported authority must declare its normalization.
- Exact predicates and exact ranks are authoritative; numerical rank is diagnostic only.
- Do not copy the Type-II `P(v2)` form into VI0.
- Do not write production or Rust runtime code in this gate.

---

### Task 1: Authority and branch intake

**Files:**
- Create: `compiler/manifolds/vi0_authority.json`
- Create: `compiler/tests/test_vi0_authority.py`

**Interfaces:**
- Produces: canonical state names, constraints, branch predicates, formula source paths and SHA-256 hashes.

- [ ] Write a failing test that requires every formula, convention and branch field and rejects a registry-only record.
- [ ] Run `python -m pytest -q compiler/tests/test_vi0_authority.py` and verify the missing intake fails.
- [ ] Build `vi0_authority.json` from exact project sources and record all hashes.
- [ ] Re-run the test and verify it passes.
- [ ] Commit with `compiler: pin VI0 manifold authority`.

### Task 2: Exact constraint tangent space

**Files:**
- Create: `compiler/manifolds/vi0_classification.py`
- Create: `compiler/tests/test_vi0_manifold_classification.py`

**Interfaces:**
- Consumes: `vi0_authority.json`.
- Produces: exact constraint Jacobian, tangent basis and generic/boundary rank records.

- [ ] Write failing tests for the generic branch, zero-tilt branch and one declared degeneracy boundary.
- [ ] Verify failure because no classifier exists.
- [ ] Implement canonical symbolic loading, exact Jacobian construction and nullspace extraction.
- [ ] Verify exact ranks and branch-separated dimensions pass.
- [ ] Add a mutation test that deletes one constraint and must fail.
- [ ] Commit with `compiler: classify VI0 constraint tangent space`.

### Task 3: Projector differential and minimal coordinates

**Files:**
- Modify: `compiler/manifolds/vi0_classification.py`
- Modify: `compiler/tests/test_vi0_manifold_classification.py`
- Create: `compiler/manifolds/vi0_operator_program.json`

**Interfaces:**
- Produces: minimal `z^A`, exact `P_,A`, `Pdot`, `K=[Pdot,P]` operator program.

- [ ] Write a failing test that attempts the Type-II one-coordinate ansatz and requires rejection unless exact reconstruction succeeds.
- [ ] Implement the restricted projector differential and exact rank reduction modulo proven gauge directions.
- [ ] Serialize the minimal coordinates and derivative actions to the neutral operator program.
- [ ] Verify `P^2=P`, differentiated projector identities and `[K,P]=Pdot` exactly.
- [ ] Commit with `compiler: derive VI0 moving-projector operator program`.

### Task 4: Independent Wolfram oracle and hostile audit

**Files:**
- Create: `compiler/oracle/WOLFRAM_VI0_MANIFOLD_ORACLE.json`
- Create: `compiler/manifolds/G_DYN_MANIFOLD_VI0_AUDIT.md`
- Create: `compiler/manifolds/G_DYN_MANIFOLD_VI0_RECEIPT.json`

**Interfaces:**
- Consumes: exact operator program.
- Produces: exact rational parity and claim boundary.

- [ ] Write Wolfram exact-rational witnesses for every declared branch.
- [ ] Compare constraint ranks, projector derivatives and Kato identities against SymPy.
- [ ] Run hostile mutations for dropped constraints, numerical-rank substitution, false gauge elimination and Type-II ansatz transplantation.
- [ ] Run the full compiler test suite.
- [ ] Record P0/P1/P2 findings and allowed/forbidden claims.
- [ ] Commit with `validation: close VI0 manifold classification`.
