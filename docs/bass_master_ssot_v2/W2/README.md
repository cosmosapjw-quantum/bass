# BASS Master SSOT v2 — W2 Abstract 1+3 Geometry

**Program ID:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `W2`  
**Parent commit/tree:** `82776f50869d5c76e1cab4b28734c85f136c1e6f` / `ffe65b1c48f332acdc5a7497b77a75ef64fd7500`  
**Jira owner:** `BASS-17`  
**Status before fresh execution:** `IMPLEMENTED_PENDING_GREEN_RECEIPT`

## Purpose

W2 supplies the abstract normal-frame geometry used later by the xCoba ONF and Bianchi-type generators. It fixes the sign, orientation, dimension and formula semantics before components are introduced.

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

The Bianchi background normal is hypersurface orthogonal. Fluid/electron global tilt is a separate future matter variable; it is not normal-congruence vorticity.

Dimensions are

\[
[n_a]=[h_{ab}]=[\varepsilon_{abc}]=1,
\quad [A_a]=[K_{ab}]=[H_{\rm geom}]=[\sigma_{ab}]=L^{-1},
\quad [{}^{(3)}R]=L^{-2}.
\]

## Curvature sign registry

The W2 semantic registry fixes

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

W2 validates their exact coefficients and ordering as EquationIR. Independent xCoba component and FLRW/Bianchi witnesses belong to W3.

## Deterministic canonicalization

W2 explicitly selects xPerm's pure-Wolfram canonicalization path before defining the metric. The external executable may be present, but it is not part of W2 formula identity.

## Run

```bash
wolframscript -file wolfram/scripts/run_stage.wls \
  --stage W2 \
  --source-commit <exact-commit> \
  --source-tree <exact-tree>
```

## Claim boundary

```text
W2_ABSTRACT_1PLUS3_PROJECTOR_AND_KINEMATIC_INFRASTRUCTURE_VERIFIED
GAUSS_CODAZZI_SIGN_REGISTRY_VERIFIED
NO_XCOBA_COMPONENT_DUAL_PROOF
NO_BACKGROUND_EINSTEIN_EQUATIONS
NO_BIANCHI_BRANCH_SPECIALIZATION
NO_IMPLEMENTATION_PARITY
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_SCIENCE_VALIDITY
NO_PASS_RF04
```
