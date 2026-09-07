# BG-02 — ambient curvature definition → Gauss/Codazzi/normal-Ricci blocks

Date: 2026-09-07 KST. Node: `BG02_CURVATURE_DEFINITION_TO_BLOCKS_V1`.

This note starts from the accepted conditional abstract-projection result and closes the one explicitly withheld premise as a new, separately executable xTensor task. It does not rerun AP, SC, AUX, capture6 or native17.

## 1. Accepted predecessor and exact remaining gap

Accepted AP evidence:

- tested code: `4149649462758165e64673ebb86498b708ef9a0e`
- AP evidence publication: `d34606f2754da02b58b38946dc414fe50f257ed6`
- AP00--AP12: 13 Success / 0 Failure / 0 unevaluated, actual exit 0
- whole-invocation messages empty, runtime failures empty
- AP12 actual computed fixed-reference witness: 4
- accepted ceiling: `PASS_CONDITIONAL_ABSTRACT_CONTRACTION_ONLY`

The retained false field is exactly `curvature_definition_to_blocks_verified=false`. AP assumed the Gauss, Codazzi and normal-Ricci blocks, then contracted them into Ricci/Einstein and all four projections. Therefore the correct next node is not another projection comparison. It is a native proof from the ambient curvature/commutator definition and the induced hypersurface derivative to those three blocks.

The AP first-run implementation failures and repairs remain historical evidence. No AP execution is repeated here.

## 2. BASS convention and xTensor sign adapter

Project convention:

```
g_ab signature (-,+,+,+)
n^a n_a = -1
h_ab = g_ab + n_a n_b
K_ab = + h_a^c h_b^d nabla_c n_d
A_a = n^b nabla_b n_a
```

The normal is hypersurface orthogonal. `A_a` is normal four-acceleration and is not the Bianchi commutator vector `a^B_a`.

xTensor defines an induced metric from `{ambient metric, normal}` and generates its intrinsic derivative, projector, extrinsic curvature and acceleration. For a timelike unit normal the project convention is obtained by setting

```
$ExtrinsicKSign = +1
$AccelerationSign = -1
```

before defining the induced metric. The first executable residual checks

```
GradNormalToExtrinsicK[nabla_a n_b]
 - (K_ab - n_a A_b) = 0.
```

This sign lock is necessary before interpreting any Gauss-Codazzi result.

## 3. Native Gauss derivation — two commutator paths

Let `W_a` be an arbitrary spatial covector. Define the induced covariant derivative `D` through xTensor's induced metric. Compare

```
P_h[(nabla_d nabla_c - nabla_c nabla_d) W_b]
```

with

```
(D_d D_c - D_c D_d) W_b.
```

The first path is converted to ambient Riemann by `SortCovDs`; the second path is converted to intrinsic Riemann by the same operation on the induced derivative. Independently, both raw second-derivative expressions are expanded into ambient derivatives using `ProjectDerivative`, `ProjectorToMetric` and `GradNormalToExtrinsicK`.

The difference of the two curvature paths minus the difference of the two expanded derivative paths is identically zero. Since `W_a` is arbitrary and spatial, this gives the operator form of Gauss. The explicit tensor residual is

```
P_h[R_abcd] - R3_abcd
 - K_ac K_bd + K_ad K_bc = 0.
```

No Bianchi-family component metric, coordinate chart or hand-entered spatial Ricci tensor appears in this derivation.

## 4. Native Codazzi derivation — commutator acting on n_a

Now apply the ambient commutator to the normal itself:

```
P_h[(nabla_d nabla_c - nabla_c nabla_d) n_b].
```

`SortCovDs` converts this to the projected ambient Riemann action. Expanding the same raw expression using the positive-K derivative decomposition yields the projected derivatives of `K_ab`. Comparing with the native induced-derivative expression gives

```
P_h[n^a R_abcd]
 - D_d K_bc + D_c K_bd = 0.
```

Equivalently, using the slot order with the normal in the second Riemann index reproduces the standard xTensor Gauss-Codazzi form. This identity is generic: no homogeneous `D_a K=0` specialization is made.

## 5. Native normal-Ricci block and Lie derivative adapter

Contract one derivative direction of the normal commutator with `n^a` before projecting the remaining free indices. The independent induced path contains

```
-D_c A_b - P_h[n^d nabla_d K_bc].
```

For a spatial covariant `K_ab`, positive-K implies

```
P_h[(L_n K)_bc - n^a nabla_a K_bc] = +2 K_b^a K_ac.
```

Hence the double-normal curvature block becomes

```
P_h[n^a n^d R_bdca]
 = -(L_n K)_bc + K_b^a K_ac + D_c A_b + A_b A_c.
```

This is the block that was an explicit premise of the preceding AP contraction. The sign of the `K.K` term is fixed by the positive-K Lie-vs-projected-normal identity, not by changing the AP expected projection formulas.

## 6. Executable tests

The new code lives in `research/diagnostics/bg02_curvature_definition_20260907/` and defines nine independent CB IDs:

1. `CB00_POSITIVE_K_ACCELERATION_SIGN_LOCK`
2. `CB01_GAUSS_OPERATOR_COMMUTATOR`
3. `CB02_GAUSS_TENSOR`
4. `CB03_CODAZZI_OPERATOR_COMMUTATOR`
5. `CB04_CODAZZI_TENSOR`
6. `CB05_NORMAL_RICCI_OPERATOR_COMMUTATOR`
7. `CB06_LIE_VS_PROJECTED_NORMAL_K`
8. `CB07_NORMAL_RICCI_TENSOR`
9. `CB08_XTENSOR_INDUCED_DECOMPOSITION_RECONSTRUCTION`

CB01/03/05 are the load-bearing derivations: each compares a native curvature-commutator route with an independently expanded projected-derivative route. CB02/04/07 record the corresponding tensor equations. CB08 asks xTensor's own `InducedDecomposition` to reconstruct the complete ambient Riemann after the three derivations; it is a final consistency check, not the sole proof.

The supplied runner uses an already installed xTensor only. It records the actual init path/hash/version, the three new code-file hashes, all test rows, messages, runtime failures and process exit. It does not use xCoba, family components, the BASS production init, GitHub Actions or a new package installation.

## 7. Evidence classification before execution

Current status of this new node: `PREPARED_UNEXECUTED`.

- Mathematical identities above: **derived / literature-compatible**.
- xTensor implementation: **written and statically reviewed, not executed**.
- CB observed rows: **0**.
- Native curvature-block PASS: **not claimed**.
- Prior AP PASS: **accepted and reused, not rerun**.

If all nine CB IDs pass in a clean native run with no messages/runtime failures, the new node may be classified `PASS_NATIVE_CURVATURE_BLOCK_DERIVATION_ONLY`. Combined with the already accepted AP result, the mathematical chain from ambient curvature definition through the four Einstein projections will then be closed at the research-proof level. Production API admission, background time evolution, family-wide solver readiness and RF04 remain separate gates.

## 8. Source/reference boundary

The derivation is deliberately aligned with xTensor's documented induced-metric machinery: `InducedFrom`, `ProjectDerivative`, `GradNormalToExtrinsicK`, `SortCovDs`, and the three Gauss-Codazzi examples. The project-specific sign adapter differs from the old documentation example because BASS uses positive expansion `K_ab=+h h nabla n`.

No source equation is silently adopted with an incompatible extrinsic-curvature sign. No natural units are introduced.

Relevant xTensor documentation:

- https://xact.es/Documentation/HTML/HTMLLinks/xTensorDoc.nb_56.html
- https://xact.es/Documentation/HTML/HTMLLinks/xTensorRefGuide.nb_5.html

## 9. Next action

Run only the nine CB tests with the supplied local-host handoff. Preserve the first observed result. Repair only API/index/canonicalization/runner defects in the three new files while keeping the displayed geometric equations fixed. Return the evidence Git-first. Do not rerun AP/SC/AUX or use Actions.
