# FA03 C8: 비회색 에너지 구적의 엄밀한 상계, RK4·반올림 분할, 정확도-비용 최적화

2026-10-15 KST. \`$physmath-research-loop 1.3.0\`의 이번 **선택된 C8 numerical accuracy/reproducibility 단계**를 수행했다. 물리 유도와 실제 Ubuntu Python 실행·최적화가 포함되며 별도 local Codex는 사용하지 않았다. 기본 commit \`049f615f29175e2fddd3860374dd23e2296a394b\`와 이전 R8 original certified finite36 detector source는 불변이다.

## 1. Frozen physical model / conventions

Signature (-,+,+,+), non-tilted Kasner (2/3,2/3,-1/3), x=t/to ∈ [1/2,1], normalized photon energy e=Ew/E* in [49/50,51/50], finite detector GL3x12 at observer chi=1/125 psi=1/100 cap 1/50 rad, zero incoming coherency. Real ε∈[-1/10,1/10]. Unchanged original FA02 source SHA \`1e89e75f7a08d2eec1851a58e602c2683b1888a37b3e1fe10b1be4234756eee5\`, FA03 SHA \`ad865127da7c2f9ea613541571f9b842f9da7630af9bb951a3df5968ad44ecf7\`.

At real ray/angular coordinates the 2x2 polarization matrix obeys
\[
 F'(x,e) = B(x,e)-G(x,e)F-FG^T,\qquad
 G=\alpha(e)H+\omega J,\quad
 \alpha(e)=1+\epsilon(ek-1),\quad
 B=e^3(1+\tfrac1{10}e k)P ,
\]
with H=.5 S^T K3 S >=0, J^T=-J, omega real, P=S^T P3 S >=0 and Tr(P)<=Tr(P3)=1 for real orthonormal screen. Source k=L x^{-2/3} v, not merely x^{-2/3}v.

## 2. New rigorous spectral quadrature theorem

For real ray direction \(v=\sqrt{1-(1-x^2)n_3^2}\), x≤v≤1. The observer factor \(L=\cosh\chi+\sinh\chi m_0\), m0∈[-1,1] satisfies
\[
 L\le e^{1/125}\le \frac{125}{124}<\frac{101}{100}, \qquad
 x^{-2/3}\le 2^{2/3}<\frac85.
\]
Therefore \(0<k\le(101/100)(8/5)=202/125\). In complex energy disk \(|e-1|\le1/2\), \(|e|\le3/2\), and **real** ε, the Hermitian part of G is
\[
 \tfrac12(G+G^\dagger)=\operatorname{Re}\alpha\,H,\quad
 \operatorname{Re}\alpha\ge1-\tfrac1{10}\bigl(1+\tfrac32\tfrac{202}{125}\bigr)
 =\frac{411}{625}>0.
\]
Hence the non-autonomous Jones propagator U(x,s;e) solving U'=-G U is a contraction in operator 2-norm even at complex e inside the disk. The analytically continued coherency formula \(F(x,e)=\int_{1/2}^x U(x,s;e) B(s,e)U(x,s;e)^T ds\) is holomorphic in e and satisfies, by the Schatten 1-norm ideal inequality,
\[
 \|B(s,e)\|_1\le\left(\frac32\right)^3
 \left(1+\frac1{10}\frac32\frac{202}{125}\right)
 =\frac{41931}{10000},\qquad
 \|F(x,e)\|_1\le\frac{41931}{20000}=:M.
\]
Taylor coefficients at e=1 are bounded by M R^{-j}, R=1/2. A Taylor polynomial of degree 2n−1 has remainder \(\le M(\delta/R)^{2n}/(1-\delta/R)\), with δ=1/50 and δ/R=1/25. Since the normalized energy integral and the n-point normalized positive Gauss–Legendre rule both have operator norm1 and agree on polynomials of degree at most2n−1,
\[
\boxed{\displaystyle
\|Q_nF-\langle F\rangle_e\|_1
\le\frac{41931}{9600}\,25^{-2n}}
\]
for each exact continuous-time trajectory in the frozen real-ray model. The same bound holds for a normalized positive finite-ray average (e.g., the 36-ray model), by positivity of detector weights, **without certifying the continuum angular-cap integral**. Source and numerical proof checked with actual Wolfram15.0.1 exact rational expressions. Values:

| GL n | exact-real ODE spectral bound |
|---:|---:|
| 2 | 1.1181600e-5 |
| 3 | 1.7890560e-8 |
| 4 | **2.8624896e-11** |
| 5 | **4.57998336e-14** |
| 6 | 7.327973376e-17 |
| 8 | 1.875961184256e-22 |

Hence a user-selected **spectral** tolerance ≤1e-10 requires GL4, ≤1e-13 requires GL5, ≤1e-16 requires GL6 in this conservative model-specific certificate. It does not bound RK4 time error, numerical Gauss nodes/weights or source floating roundoff.

### Real RED -> GREEN correction (essential physics)

The first derivation incorrectly dropped the observer L in k, giving Bmax=837/200 and a nominal GL4 upper2.85696e-11. A physical source test at x=.5, e=1.5 produced trace norm4.185045378374459, **larger than the old bound4.185**. This was a genuine failed physics gate, not a test nuisance. We corrected k upper to 202/125, Bmax to41931/10000 and GL4 bound to2.8624896e-11, retaining all original numerical outputs and archived \`*PRECORRECTION.json\` plus the negative regression \`test_real_observer_L_factor_source_regression\`. No source or threshold changed; Wolfram independently verifies the exact inequalities.

## 3. Exact conservative time-defect method, manufactured model

On the passive matrix equation with constant H=diag(1/5,2/5), source P3 physical 2x2 Hermitian block, J rotation=0 and same time span1/2, the exact Jones error propagator is contractive. For a continuous reconstructed path P(t) and residual R=P'-B+GP+PG^T, the **exact** error identity/estimate is
\[
 E(t)=\int_{1/2}^t U(t,s)\,R(s)\,U(t,s)^T ds,\quad
 \|E(t)\|_1\le\int_{1/2}^t\|R(s)\|_1 ds .
\]
In \`manufactured_defect.py\`, each scalar matrix component uses exact Fraction RK4 and endpoint Hermite cubic p(u). The residual is degree3 with exact rational Bernstein coefficients β_i. Positive Bernstein shape functions yield
\[
 \int_{\mathrm{step}}\!|r|dt
 \le\frac h4\sum_{i=0}^3|\beta_i|.
\]
Summing all components and steps exactly gives a **validated manufactured constant-coefficient** RK4 trace-norm bound. 64-step bound7.390486822589052e-10; independent mpmath70 exact solution shows actual error ≈1.51e-12, lying inside it. This validates a constructive method, **not** the variable-coefficient FA03 time error. The latter requires interval enclosures of the physical x-dependent residual and input roundoff.

## 4. Actual source-matched numeric error experiment

\`convergence_c8.py\` executed the frozen C7 real Stokes solver for GL3x12, GL6x24 and GL10x48, ε=(-.1,0,.1), energy GL2/3/4/5/6/8 against GL24 at the SAME RK4 steps128, plus steps16/32/64/128/256/512 against the *finer discrete reference* steps1024, energy GL6. On all three grids the observed time-difference series is nearly identical:

| steps | observed trace delta to 1024-step comparator |
|---:|---:|
|16|1.7345e-9|
|32|1.0771e-10|
|64|6.7098e-12|
|128|4.1855e-13|
|256|2.6094e-14|
|512|~1.56e-15|

Successive time refinement gives observed order close to4, but difference from a 1024-step **numerical** reference is not an interval true-ODE error bound. The GL4 vs GL24 numerical output difference at same steps128 was ≲2e-16; GL2 ≈9.15225e-10. The GL8 exact-ODE spectral bound is far below IEEE64 rounding, so any direct binary64 GL8-to-GL24 difference ~1e-16 is a floating-point floor, **not a refutation of the exact integration theorem**.

## 5. Performance, memory, parallelism actually measured

Same source + three ε, RK4 steps128, warmed wall time medians (three repeats), same rays and source-matched original Jones ε loops, actual Ubuntu, no GPU:

| rays | real GL4 median(s) | real GL8 median(s) | GL4 speedup over original Jones GL8 |
|---:|---:|---:|---:|
|36|0.04086|0.04046|4.47x|
|144|0.06378|0.08962|7.43x|
|480|0.13910|0.18692|**10.85x**|

At 480 rays independently rerun \`resource_probe.py\`: GL4 0.14611s vs GL8 0.19773s. \`tracemalloc\` traced peaks 2,170,072 vs4,243,784 bytes, a 48.9% reduction. This is Python/NumPy traced allocation, not whole RSS. The nominal real-Stokes state for 3 eps ×480 rays ×GL4 contains 184,320 bytes, compared to C7 original complex Jones GL8 737,280 bytes, exactly 1/4 for state arrays; temporary allocations and source integrals are not covered by that nominal ratio.

At 480 rays, 4 chunks with real-Stokes GL4 and 128step have medians 1worker0.2263s, 2thread0.3615s, 4thread0.54938s, all slower than the single unchunked0.14611s. Multiple workers were **actually executed** with deterministic ordered reduction, but do not merit default activation. Ray partition sizes1,4,12,whole observed trace differences ≲2e-16 on small grids. Keep default one worker and use chunking for constrained memory only.

## 6. Conditionally bounded summation roundoff

Under IEEE754 binary64 \`u=2^-53\`, assuming **exact** positive Gaussian weights and **exact** per-ray/per-energy Stokes inputs, standard gamma_N=uN/(1-uN) bounds a scalar dot-product weighted reduction. Exact-real spectral positivity gives all scalar Stokes magnitudes ≤TrF≤(1/2)(51/50)^3(1+(1/10)(51/50)(202/125)). With four Stokes components, a conservative trace bound for the output assembly is \(\le4M_\mathrm{real}\gamma_{N}\), N=rays×energy order. At GL4, 36/144/480 ray conditional assembly bounds are 3.95245e-14,1.58098e-13,5.26994e-13. This **excludes** errors in numerical source/Stokes input, float generated quadrature weights and RK4 operations and is not a full float solver error certificate. On small angular caps the different actual ray-reduction orders give ~1e-16 differences.

## 7. Wolfram, xAct and cross-repo reuse

Cloud Wolfram15.0.1 verified revised positive complex-energy disk alpha_min=411/625, M=41931/20000 and exact rational GLn upper. Preliminary first spectral proof FAILED its real-source regression due omitted observer L; fix is preserved. Local Wolfram Engine15.0.0 and xTensor1.3.0 on authorized Ubuntu: seven 4D normal-frame shear/screen/photon/null and energy conventions exactly zero, EXIT0. SciSpace and Exa primary references: Trefethen–Weideman *The Exponentially Convergent Trapezoidal Rule*, SIAM Review 56(3) (2014), DOI https://doi.org/10.1137/130932132 (Fourier angle error conditional on M4); rigorous defect a-posteriori literature, e.g. https://doi.org/10.1007/S00211-009-0254-2. These are method references, **not** source documents for BASS-specific coefficient values.

Latest other repos read: rec_bianchi PR89 Bianchi-I conservative phase-volume and shared geometric clock; BASS_HE PR60 warm 4th saved-cell with interval source errors and moderate sparse acceleration; bass_cr PR68 actual Verner curvature control enables 48→22 cohorts with directed numeric bounds; WU088_HH PR75 exact source-cancellation and vectorized angular residual. Reuse is conceptual methods (positive rays, source binding, exact monotone inequalities, measured parallel costs), not a mixed or imported atomic rate calculation. Active rei_bianchi owner independent.

## 8. Scoped decision

**C8 numerical/reproducibility stage evidence:** rigorously admitted for the exact physical FA03 finite-ray *energy quadrature only*, using corrected real observer L and positive Jones generator; independently exact-rational validated for manufactured constant-coefficient RK4 Hermite residual. Actual 36–480ray numeric convergence, resource, vectorization and thread costs measured with clear empirical tags. HOLD: time-dependent actual FA03 validated RK4 defect, full binary64/BLAS/geometry roundoff, angular complex-strip M4 and radial GL3 interval remainder, full continuum cap/cosmological observer observable, actual H/He photoionization histories. **Original R8 fixed36ray <4.75e-7 remains untouched** and cannot be silently combined with absent parts into a stronger full continuum theorem.

Next incomplete stage is C9 adversarial independent-code audit of these exact proofs and optimizations, *not executed here*. New publication claims must wait for independent review and whole model error budgets. Source locks/original plots/input remain unchanged.
