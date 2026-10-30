# BASS CE1-AA | 원본 연속체 K4 2시점 비공선성의 MPFR192 인증

2026-10-30 · PR #273 (Draft, unmerged), direct child of PR272 original HEAD \`cd597ace92dabafa71a59779242910c3cbcd21c7\`. **Actual science CI #41005087995 SUCCESS, 11/11 scoped pytest PASS**. Original BASS Rust \`comoving.rs\` blob \`a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84\`; original exact-binary physical six positive angular cells SHA256 \`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035\`; prior PR270 exact-rational ℓ4 source, PR268/270 MPFR192 time/geometry carrier unchanged. No new 6-cell source, no model/closure change, no merge.

## 1. Exact model, observable and theorem

Massless collisionless all-expanding reflection-even diagonal Bianchi I, Λ=0, metric signature (-,+,+,+), u=t/Tstar from 0 to 0.08, initial shear (.2,-.13,-.07), normal-observer bolometric anisotropic sky. Original angular cells with eight reflections, GL6 216 or GL8 384 stored binary64 positive rays. The *original* strict geometry target \`max|Δh|<1e-5\` remains unchanged, already achieved by GL6 N4 in PR268.

Write \`X(u)=(α40(u),sqrt(2)α42(u),sqrt(2)α44(u))/3\` with \`α4m=4π a4m/E\`. For two epochs 0,T, \`T=.08\`, the exact-real continuum Gram kernel obeys
\`\`\`
K4(u,v) = X(u)·X(v)
D = det[[K4(0,0), K4(0,T)], [K4(T,0), K4(T,T)]]
  = ||X(0)||² ||X(T)||² - [X(0)·X(T)]²
  = sum_{i<j} [X_i(0) X_j(T) - X_j(0) X_i(T)]².
\`\`\`
The last identity was separately checked with SymPy, symbolic residual zero. D>0 proves the endpoint sky vectors are **not collinear**. For 41 epochs, full \`K4=XX^T⪰0\`, rank≤3, and the positive 2×2 principal minor certifies rank≥2. Eigenvalue interlacing additionally implies the full 41×41 second eigenvalue is at least the principal-minor second eigenvalue. This is a **single deterministic Bianchi-I angular-energy sky**, not cosmic-variance covariance, thermal temperature perturbations or observational likelihood.

## 2. The missing original-binary64-Rust-to-exact-real interval bridge

Previous CE1-Z had physical Rust binary64 K4 numerical centers but not interval rounding proof. CE1-AA **does not** pretend the native Rust float CSV is an interval. Instead, for each source/order N4/N8/N16:
1. Exact source immutable original six-cell SHA and original BASS Rust blob, stored ray/mass byte SHA, saved parent PR270 \`real_time_mpfr.json\` and \`l4_source_and_transfer.json\` Git blobs are checked. Reconstruct same original \`rk4_path\`, demand **bit-identical Hermite coefficient SHA** to both parent source/geometry proofs.
2. At u=0 (first cubic v=0) and u=.08 (last cubic v=1) evaluate *the exact real polynomial defined by stored binary64 coefficients*, preserving all Horner additions through MPFR192 outward intervals. Do **not** replace exact cubic v=1 with the rounded RK4 \`path.states[-1]\` or binary64 \`path.at\`.
3. For each stored ray n and positive mass w, calculate \`b_i=e^{-2ell_i}\`, \`r²=Σb_i n_i²\`, \`volume=e^{-Σell_i}\`, \`E=Σw volume sqrt(r²)\`, and the exact real Condon–Shortley \`a40,a42,a44\` polynomials with 192-bit directed MPFR exp/sqrt, enclosing the true mathematical π via directed \`mpfr_const_pi\`.
4. Calculate outward exact stored K00,K0T,KTT intervals and add the **already certified** PR270 exact-rational source+geometry entrywise envelope \`eps\` with exact upward 27-digit display. Both original stored-sky endpoint energies have strictly positive lower bound >.6. Confirm native Rust CSV center agreement to better than \`2e-12\` only as an independent *diagnostic*, not evidence used for the interval conclusion.
5. With \`A=lower(K00_stored)-eps>0\`, \`B=lower(KTT_stored)-eps>0\`, \`C=upper(K0T_stored)+eps>0\`, obtain \`D_cont>=A B-C²\` using directed MPFR. If positive, the exact-real continuum D>0 under the inherited, source- and path-bound PR270 mathematical premises. This **completes the missing float-center gap** without repeating the costly 680×2 source proof or all-panel time residual campaign.

## 3. New actual measured and enclosed results

All six GL6/GL8 × N4/8/16 conditional on immutable source and original signed-positive geometry premises were executed in actual GitHub CI #41005087995.

| Original rays | panels | **Exact-continuum D lower** (outward) | **Exact-continuum D upper** | Certified λ_min of 2×2 principal minor lower |
|---|---:|---:|---:|---:|
| GL6 216 | 4 | −2.100786959769450e−6 | 2.329023445315485e−6 | inconclusive |
| GL6 216 | 8 | −1.637384155271712e−7 | 3.919749149932963e−7 | inconclusive |
| **GL6 216** | **16** | **+7.435842304090848e−8** | 1.538780772787773e−7 | **+3.441883476554002e−6** |
| GL8 384 | 4 | −2.094948752444345e−6 | 2.323185229829427e−6 | inconclusive |
| GL8 384 | 8 | −1.579002067283154e−7 | 3.861366980334861e−7 | inconclusive |
| **GL8 384** | **16** | **+8.019663167264269e−8** | 1.480398604860885e−7 | **+3.712167422247990e−6** |

The two N16 positive lower bounds are strict, even after accounting for the full PR270 *source plus continuous-time geometry* interval and all new MPFR rounding for the previously uncertified sky center. An independent rational calculation using exact fractions of the outward-exported MPFR binary64 interval endpoints also yields strictly positive (conservatively ~\`7.435842304085945e-8\` GL6 and \`8.019663167259325e-8\` GL8), without assuming a posterior numerical tolerance.

**Conclusion, conditional on the reused PR270 proof premises:** the original fixed physical continuum K4 on [0,.08] has **two genuinely independent temporal angular pattern modes**, and the 41×41 continuum Gram has \`2≤rank(K4)≤3\`. This is stronger than CE1-Z's purely binary64 numerical spectral suggestion. Does not certify the third eigenmode or general Bianchi family; N4/8 negative *lower bounds* are only inconclusive envelopes, not physically negative determinants.

Why 16 panels? Only this **new scientific rank2 proof** requires a tighter source/geometry envelope, whereas the **unchanged original geometry h tolerance is already met at 4 panels**. Do not silently change production integrator or gate from this pilot.

## 4. Implementation, tests and boundaries

Actual new code \`research/ce1aa_20261030/two_epoch_mpfr.py\`, adversarial \`tests/test_two_epoch_mpfr.py\` and \`package_artifacts.py\`. Source files and original Rust CSV reused without modifying BASS Rust. GitHub original science run \`41005087995\`: **SUCCESS**, **11 passed in 8.27s**, S0/S1/S2 ZIP generated with original source-inclusive data and raw MPFR JSON, CRC and member SHA PASS. The original BASS source byte SHA, original PR270 Git blobs, GL ray/mass byte SHA and exact binary path coefficient SHA were enforced inside the same run. Saved actual Rust output CSVs were diagnostic, max GL8 N16 center-to-exact MPFR midpoint gap \`8.33e-17\`. Original positive \`h\` goal remains met.

Scientific admission type: **mathematically derived + numerically checked with 192-bit directed MPFR**, dependent on PR270 source/geometry theorem and correct MPFR/library/program implementation; **whole-program formal proof NOT_RUN**, human distinct-author independent R6/C9 NOT_RUN, native subagents NOT_RUN. Never promote this to generic astrophysical/temperature observable claims.

**Upper DAG 9/15, 21 edges, CE-1 PARTIAL**, 0 newly completed *upper* nodes. \`production_ready=false,merge_ready=false,auto_next=false\`. No auto merge and STOP_AFTER_ONE_BOUNDED_UNIT.
