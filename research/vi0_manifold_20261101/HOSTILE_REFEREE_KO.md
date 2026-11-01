# VI0 original-owner dynamics | same-author blind-referee / adversarial verification

**No native subagent**, same-author hostile review; independence status is NOT distinct-author. No formal continuum solver certification or downstream production access. Referee objective: falsify the actual derived constraints and rotating-projector contract, not introduce new gates.

## Claims tested

1. `C_G'=2 q_dec C_G` and `C'=[(2q_dec-2)I-Sigma+W] C` on class A for BASS source-owned perfect-fluid ODE, with arbitrary physical `W` and non-diagonal `Sigma`.
2. 7D physical principal-frame VI0 constrained vector field is tangent to full original ambient ODE, including off-diagonal shear and Omega derivatives.
3. Moving angular rays carry `n'_W=Wn` along with `v'_W=Wv`; pure frame gauge contributes zero `P'_W`. This does not close *physical* Liouville transport.
4. The scalar bolometric Thomson rank-1 projector is **oblique/nonorthogonal**, not an orthogonal spectral projector. `K=[Pdot,P]` intertwinement does not imply ordinary Hilbert-space unitarity.

## Actual counterfactual controls (all sampled at source-owned VI0 physical state)

| Mutation | Why physically invalid | Measured defect |
|---|---|---:|
| Omit `W @ v` in velocity ODE but retain rotating geometry | frame-gauge inconsistency breaks transported Codazzi | max `DC.F - M C` **0.25076676381833124** |
| Omit `epsilon(v,Nv)` curvature torque | changes gamma-law VI0 momentum transport | max Codazzi propagation discrepancy **0.017398259170237906** |
| Rotate `v` but freeze angular `n_alpha` labels | produces unphysical moving-projector gauge term | max `|Pdot|` **0.13493534547916913** |
| Rotate rays with opposite `-W n` sign | doubles spurious gauge effect | test detects `|Pdot| > 1e-3` |
| Claim scalar collision P is Hermitian and scalar K anti-Hermitian | false in original nonuniform boosted weights | `max|P-P^T|=0.20565940148803666`, `max|K+K^T|=0.13738641065917678` |
| Let `N22` or `-N33` reach zero and still call it regular VI0 | invalid distinct-eigenvalue p/r>0 chart | explicit physical domain exception |

## Positive controls and proof evidence

- Arbitrary symmetric 3×3 N, symmetric-tracefree Sigma, Pi and skew W polynomial source operators checked symbolically: three components of momentum identity **exact zero**; curvature derivative identity **exact zero**.
- Original gamma-law perfect-fluid Q derivative coefficient checked in SymPy and separate Wolfram: **exact zero**.
- Wolfram separate rational 3×3 physical VI0 witness: momentum polynomial vector **{0,0,0}**, off-diagonal eigenframe Ndot **{0,0,0}**, curvature identity **0**.
- 12 physical BASS VI0 gamma-law reduced Einstein ODEs, 41 time samples each, 492 actual states; DOP853 `rtol=2e-11`, `atol=2e-13`. Maximum |Gauss|=**4.440892098500626e-16**, max |Codazzi|=**1.1102230246251565e-16**, max full ambient versus 7D chart directional derivative and propagated-constraint discrepancy **8.881784197001252e-16**. The directional derivative used *complex step* `h=1e-27`, not unstable subtractive finite differences.
- Co-rotated pure-gauge `Pdot` max **3.851859888774472e-34**; `max|[K,P]-Pdot|=2.7755575615628914e-17` on the physical witness.
- Normal Python `16 passed, 1 skipped`: skipped source-blob checkout test because original Git tree not available in local model container, **not** a scientific test failure. Clean GitHub checkout must execute that additional positive source guard. Do not count local skip as local PASS.

## Remaining P1 and claim ceiling

The new construction proves local class-A / regular VI0 exact constraint tangency and the **pure angular gauge** part of scalar P/Kato chain rule. It does not produce physically propagated `n'_phys` with shear+collision, complete polarized screen, degenerate eigenframe branches or production Rust compile+host. The class A conservation identity is not a novel theorem in the literature; the source-specific constructive crosswalk and verified exact implementation contract is this unit's output.

`G-DYN-MANIFOLD-VI0=PARTIAL`, `P-MIG-II-PREFLIGHT=OPEN`, `Join J1=0/2 PASS`, original scoped/source-mapped unrelated upper DAG `9/15`, new fully completed upper nodes `0`, production/merge HOLD.
