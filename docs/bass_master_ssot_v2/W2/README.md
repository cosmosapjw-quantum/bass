# BASS Master SSOT v2 — W2 Abstract 1+3 Geometry after current ALG-01

**Program ID:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `W2` / canonical DAG bridge `ALG-01 → W2 → W3 → BG-02`  
**Current parent commit/tree:** `24e8d5ae3b7e929e34ca62d7070ce00e0960fb46` / `a0f8f9b3de4a6eb445333110e42bc1e1d331cc8b`  
**Jira owner:** `BASS-17`  
**Status before fresh successor execution:** `IMPLEMENTED_PENDING_CURRENT_BASE_GREEN_RECEIPT`

## Purpose

ALG-01 fixes the homogeneous Bianchi Lie-algebra inputs, branch predicates, exceptional `VI_{-1/9}` witness obligations and `O(3)` covariance checks. W2 supplies the abstract normal-frame geometry that W3 will lower to an orthonormal-frame connection/curvature generator before BG-02 derives Einstein–matter background equations.

This successor composition is based on the current ALG-01 head. PR #75 is the earlier W0/W1 sibling and PR #76 is the earlier composition against a stale ALG-01 parent; both remain audit trails, not the canonical next DAG edge.

## Conventions

\[
\operatorname{sig}(g)=(-,+,+,+),\qquad n^a n_a=-1,
\]
\[
h_{ab}=g_{ab}+n_a n_b,\qquad
\varepsilon_{abc}=n^d\eta_{dabc},\qquad \epsilon_{123}=+1,
\]
\[
A_a=n^b\nabla_b n_a,\qquad
K_{ab}=h_a{}^c h_b{}^d\nabla_c n_d,
\]
\[
\nabla_a n_b=-n_a A_b+K_{ab},\qquad
K_{ab}=H_{\rm geom}h_{ab}+\sigma_{ab},\qquad K=3H_{\rm geom}.
\]

The Bianchi background normal is hypersurface orthogonal. Fluid/electron global tilt is a separate matter variable; it is not normal-congruence vorticity.

Dimensions are

\[
[n_a]=[h_{ab}]=[\varepsilon_{abc}]=1,
\quad [A_a]=[K_{ab}]=[H_{\rm geom}]=[\sigma_{ab}]=L^{-1},
\quad [{}^{(3)}R]=L^{-2}.
\]

## Curvature sign registry

W2 stores the exact semantic coefficient ordering

\[
h_a{}^e h_b{}^f h_c{}^g h_d{}^hR_{efgh}
={}^{(3)}R_{abcd}+K_{ac}K_{bd}-K_{ad}K_{bc},
\]
\[
h_a{}^e h_b{}^f h_c{}^g n^hR_{efgh}
=D_aK_{bc}-D_bK_{ac},
\]
\[
{}^{(3)}R=R+2R_{ab}n^an^b+K_{ab}K^{ab}-K^2.
\]

Independent xCoba component and Bianchi-I/V/IX witnesses remain W3 obligations; W2 does not claim them.

## Deterministic canonicalization

The formula-authority lane explicitly selects xPerm's pure-Wolfram canonicalizer before defining the metric. The external executable may be loaded for other stages, but is not part of W2 expression identity.

## Composed run

```bash
wolframscript -file wolfram/scripts/run_stage.wls \
  --stage W2 \
  --source-commit <exact-current-composition-source-commit> \
  --source-tree <exact-current-composition-source-tree>
```

The W2 runner includes W0/W1, ALG-01, ALG-01-R1 and W2 tests in one fresh kernel.

## Claim boundary

```text
ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED
ALG_01_EXCEPTIONAL_SHEAR_AND_O3_COVARIANCE_VERIFIED
W2_ABSTRACT_1PLUS3_PROJECTOR_AND_KINEMATIC_INFRASTRUCTURE_VERIFIED
GAUSS_CODAZZI_SIGN_REGISTRY_VERIFIED
NO_XCOBA_COMPONENT_DUAL_PROOF
NO_ONF_CONNECTION_CURVATURE_PROOF
NO_BACKGROUND_EINSTEIN_EQUATIONS
NO_ALL_FAMILY_SOLVER_SUPPORT
NO_GENERIC_ELL_COMPILER_CORRECTNESS
NO_NUMERICAL_PARITY
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_SCIENCE_VALIDITY
NO_PASS_RF04
```
