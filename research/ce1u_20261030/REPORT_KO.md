# BASS CE1-U | 정확한 연속 source와 새 Gauss source, 실제 Einstein–Vlasov 이력의 결합 검산

**Date:** 2026-10-30 KST. **Research type:** bounded new physical-science and exact-rational comparison result. **Upper DAG:** 9/15 (21 edges), CE1=PARTIAL, merge_ready=false, production_ready=false, auto_next=false.

## 1. Position in live project

The latest relevant BASS branch is CE1-T PR #263 HEAD `db144f755eacaade0cf34cb6555631d5a73feaad` (independent Draft), deriving 41-step source GL order convergence but keeping the same inherited GL40 Einstein background. CE1-S PR #262 is an independent sibling. PR #261 has actual BASS-native Rust Liouville radiation transport; #258 gives original Einstein–Vlasov physical histories; #253 is the frozen six-cell source lock. Other BASS/REI chemistry or BASS_CR research branches are out of this unit's matter model and must not be silently imported.

The physical source remains the exact binary64 six-cell table with eight reflections; massless collisionless positive reflection-even diagonal Bianchi-I spacetime, Lambda=0, `(-,+,+,+)`, proper `u=t/Tstar∈[0,.08]`, initial scale factors unity, shear `(.2,-.13,-.07)`. The source SHA-256 is `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

## 2. Theory: a new full-box source comparison

`S0_THEORY_KO.md` gives a complete constructive derivation. Source stresses have the exact integral `P_i=exp(-Σell) ∫U0 exp(-2ell_i)n_i²/sqrt(Σ exp(-2ell_j)n_j²) dΩ0`. In `0≤ell_i≤.08` we take `B=23/25` and `q=1/11`, then apply 12 terms of the reciprocal square-root binomial expansion with a closed positive tail. All 559 polynomial monomials in the preserved physical angular cells integrate into exact rational combinations `A+(B+C√2)/π`. We bound π by alternating Machin arctangents and √2 by integer rational floor/ceiling; stored float64 GL6/GL8 ray/mass coefficients are interpreted exactly as dyadic rationals. Importantly, an explicit additive term covers the fact that stored binary64 ray norms differ infinitesimally from unity.

The resulting exact-rational uniform source pressure bounds are:

- **GL6 (216 rays):** `ε_P ≤ 3.010630537202566e-12` (rounded display of a larger exact-rational bound stored in JSON).
- **GL8 (384 rays):** `ε_P ≤ 6.164277064237367e-14` (rounded display; use stored exact-rational numerator/denominator as authority).

These are bounds against the original physical *continuous* six-cell source, not the GL40 numerical reference. Existing CE1-M MPFR192 source/time result is not silently reused for this new source identity.

For the exact-source ODE `ell'=h, h'_i=-θh_i+P_i`, positivity and the barrier `0<h_i<1` hold over `[0,.08]`. Then the conserved trace and pressure Jacobian bound give `Z'≤7Z+ε`, `Z=||Δell||∞+||Δh||∞`; the rational Grönwall enclosure `Z≤(25/11)δE0/3+(2/11)ε` yields

- **GL6:** `max|Δh| ≤ 5.474586575721355e-13`.
- **GL8:** `max|Δh| ≤ 1.1315891404909281e-14`.

Here Δ compares the **exact continuum Einstein–Vlasov solution** with the **exact stored-binary64 GL source Einstein–Vlasov solution**, as mathematical ODE solutions. It is not an enclosure around a particular scipy or Rust floating-point trajectory. The target `1e-5` is satisfied at the exact-model comparison level; full numerical IVP certificate remains pending.

## 3. Code: genuine new model-data production

New independent numerical integration, DOP853 `rtol=3e-12`,`atol=3e-14`, creates 41 records for each newly coupled GL6 and GL8 source. The resulting scalar and anisotropic stresses drive `h_i` self-consistently and determine the observer-frame unpolarized `C2,C4,C2',C4'` through exact kinetic second/fourth/sixth moment formulas. These 82 records and plots are in the new full package. Not a replacement hydrodynamic pressure closure.

| observable | GL6 coupled | GL8 coupled |
|---|---:|---:|
| `E(u=.08)` | 0.7584190590089546 | 0.7584190590089558 |
| `h1(u=.08)` | 0.6877105036637844 | 0.6877105036637805 |
| `h2(u=.08)` | 0.3936332688276597 | 0.3936332688276636 |
| `h3(u=.08)` | 0.45102523161617675 | 0.4510252316161767 |
| `C4'(u=.08)` | -0.00014789130142318007 | -0.00014789130274591168 |
| `max|h-h(GL40)|` empirical | 4.108e-15 | 7.772e-16 |
| `max Hamiltonian defect` | 2.552e-13 | 2.551e-13 |
| 4-panel RK4-vs-DOP853 `max|Δh_end|` | 1.992e-9 | 1.992e-9 |

The original GL40 reference is numeric and not certified. The RK4-vs-DOP853 comparison also is numeric and does not constitute an MPFR-certified trajectory error.

## 4. Scientific validation and provenance

- Independent SciPy `sph_harm_y` reconstructions of axis-aligned even-ℓ moments agree with the positive-ray polynomial formulas to <`1e-12` at 3 epochs per channel.
- Five-point time differences agree with analytic `C2'`,`C4'` for all 37 inner time points; GL6/GL8 maximum errors per mode are in `SCIENCE_RESULTS.json` (of order `1e-11` for C2, `1e-13` for C4).
- Exact-massless trace `E=ΣP_i`, energy continuity `E'=-θE-Σh_iP_i`, pressure derivative via independent fourth moment, Hamiltonian constraints all checked numerically.
- **Real MPFR 192-bit directed rounding**: E/P evaluated at knots `u=0,.02,.04,.06,.08` for both GL6 and GL8, using exact saved binary64 ray/mass and sampled state bits. Maximum binary64 evaluation offset outside the enclosures: GL6 `1.39e-16`, GL8 `2.78e-16`. These MPFR tests check source evaluation, not uncertain states.
- Scoped local science `pytest 20/20 PASS`; `compileall PASS`. Formal distinct-author R6/C9 `NOT_RUN`; host native subagents `NOT_EXPOSED`; no current PR-specific remote CI PASS until such a run is observed.

## 5. External relevant literature

- H. Lee, E. Nungesser, K. Tod, *The Einstein-Vlasov system in a Bianchi I cosmology*, arXiv:1911.04937 (conserved Bianchi-I covariant momenta and massless kinetic source).
- F. Johansson and M. Mezzarobba, *Fast and rigorous arbitrary-precision computation of Gauss–Legendre quadrature nodes and weights*, SIAM J Sci Comput 40 (2018), C726–C747 (the distinction between rigorously bounded ideal GL and numerical nodes).
- D. R. Jandrlić et al., *Error bounds for Gaussian quadrature formulae with Legendre weight function for analytic integrands*, ETNA 55 (2022), 424ff, DOI 10.1553/etna_vol55s424. The current calculation uses its **own finite binomial/moment construction**, not an unverified import of that paper's contour-kernel hypotheses.

## 6. Decision, DAG and remaining gate

New exact source and exact-ODE comparison claim: **DERIVED + EXACT_RATIONAL_VERIFIED in specified expanding box**. New 82-row coupled source data: **NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED scoped**. Five-knot MPFR source: **EXECUTED**. Full four-panel outward MPFR192 numerical IVP path error for newly produced data: **NOT_RUN**. Strict formal code-independent author R6/C9: **NOT_RUN**. Therefore top DAG remains **9/15**, CE1=PARTIAL, production/merge/auto-next false.

Future single bounded unit, only on explicit next request: build a complete outward MPFR192 numerical trajectory enclosure for GL6/8 4-panel RK4/Hermite including floating evaluation and derivative bounds; then, if admitted, transport the exact continuum source comparison to a certified numerical-state enclosure. A separate optional physical hypothesis is unequal-time same-source energy multipole cross-power; do not silently start it.
