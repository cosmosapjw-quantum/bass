# BASS CE1-AA | 원본 Bianchi-I 두 시점 ℓ=4 연속체의 rank ≥ 2 인증

S0 physical scope, 2026-10-30. Immutable immediate parent PR272 HEAD \`cd597ace92dabafa71a59779242910c3cbcd21c7\`; PR270 ℓ4 source+geometry proof HEAD \`9141d6dcfc66e721fa30390d697f6cd982244eae\`; original source six exact-binary positive cells SHA256 \`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035\`; BASS Rust source blob \`a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84\`. Parent, main, siblings not merged/modified.

Physics: massless collisionless reflection-even expanding diagonal Bianchi I, Λ=0, metric (-,+,+,+), proper u=t/Tstar ∈[0,0.08], initial shear (.2,-.13,-.07), six original positive angular cells; GL6=216, GL8=384 stored binary64 rays/masses; original strict h<1e-5 remains unchanged and met by GL6 N4.

## Mathematical target
For each u, real three-component \`X(u)=(alpha40,sqrt2 alpha42,sqrt2 alpha44)/3\`. Exact-real deterministic continuum K4δ(u,v)=X(u)·X(v), so K≥0, rank≤3. For s=0 and T=.08, 2×2 principal minor \`D=K00*KTT-K0T^2\` is strictly positive iff endpoint sky vectors are linearly independent, hence exact physical continuum kernel has rank at least 2 and nonstationary angular pattern. This is NOT ensemble covariance, CMB temperature spectrum or likelihood.

For stored exact-real dyadic GL source on the *exact-real cubic defined by the stored binary64 Hermite coefficients*, construct 192-bit MPFR directed intervals for energy E and Condon–Shortley (a40,a42,a44) using the exact positive ray masses and directions, exp(-ell), volume factor and analytic ℓ4 polynomials. Evaluate at first panel v=0 and last panel v=1 using **outward evaluation of the cubic coefficients**, not the rounded floating result of \`path.at\` and not the raw Rust float sky centers. The true mathematical π is enclosed with MPFR directed \`mpfr_const_pi\`.

Frozen PR270 mathematical continuum-vs-exact-real stored RK4/Hermite kernel entrywise envelope \`epsilon_{GL,N}\` is already proved conditionally on original input, source, path and geometry. Recheck source byte SHA, original time/source proof input metadata, generated path-coefficient SHA. With outward stored-source intervals \`k00,k0T,kTT\`, define exact-real continuum conservative bounds
\`\`\`
A = lower(k00) - epsilon
B = lower(kTT) - epsilon
C = upper(abs(k0T)) + epsilon
Dlower = A*B - C^2.
\`\`\`
Require A>0, B>0 and k0T>0, so monotonicity holds. Compute this combination using MPFR192 **outward** intervals, not binary64 intermediates; demand Dlower>0. For the 2×2 principal submatrix, λ_min≥Dlower/(upper(k00)+upper(kTT)+2epsilon)>0, conditional on the reused PR270 claim premises. The exact mathematical positivity proof requires no posterior tolerance or precision tightening.

Original CE1-Z binary64-centered pilot yields D~1.14118e-7 and provisional GL6/GL8 N16 margins >7.4e-8 and >8.0e-8. These are NONAUTHORITATIVE until actual outward code executes. N4/8 may be mathematically inconclusive under inherited envelope; **never call that a physical zero mode**.

## Claim gates
- S1 actual new direct MPFR192 evaluation of all six frozen GL6/8 x N4/8/16 path pairs, 41×41 PR271 sky CSV used **only** as diagnostic, exact SHA and original BASS Rust identity preserved.
- S2 actual GitHub CI positive determinant lower for GL6/8 N16; negative/mutated-input tests and archive hashes; distinguish exact-real certificate under PR270 model premises from Rust binary64 and whole-program formal proof.
- Do not rerun the costly K12 source proof or full MPFR time residual campaign. Its earlier exact result is reused with exact source/path binding. No production, no merges.
- Upper DAG **9/15**, CE-1 PARTIAL, new upper completed nodes=0, \`production_ready=false,merge_ready=false,auto_next=false\`; distinct-author native R6/C9 and whole-program formal verification NOT_RUN.

STOP_AFTER_ONE_BOUNDED_UNIT=true.
