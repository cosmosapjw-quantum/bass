# Original BASS Type-II | Paired-grid moving equilibrium and Kato amplitude transport

Base owner: `cosmosapjw-quantum/bass`, immutable parent PR #322 at `5a6c28239dd30ca02cd9c8329b45d7b2c984168d`.
This is a **new theory loop R1–R10**, NOT a production activation. All proof claims have explicitly bounded domains.
BASS upper DAG stays **9/15 scoped/source-mapped**, with **0** newly completed production DAG nodes pending independent production and Stage-II gates.

## R1. Narrow scientific question and acceptance contract

Determine whether the original BASS scalar Type-II collision generator combined with the **full derivative of a paired moving angular quadrature projector** transports an electron-rest isotropic bolometric-intensity amplitude faithfully when the actual Type-II tilt `v_2(tau)` changes. Distinguish exactly:
(i) the source's *fixed-node/weight partial* `dP/dv`;
(ii) the *full paired-grid* `dP/dv`, including moving directions and solid-angle weights;
(iii) Kato `K=[Pdot,P]` (subspace intertwinement);
(iv) a separately chosen rest-intensity-amplitude-preserving connection; and
(v) the **physical** covariant Liouville term, not determined by Kato alone.

Source inputs: original BASS five-state aligned Type-II background `generated/rust/typeii/typeii_background.rs`, stored canonical 401-row `compiler/validation/typeii_fixture_canonical.json`, original `typeii_collision.rs` and `typeii_kato.rs`, parent PR #318 direct moving comparison, PR #322 real RustCore host adapter.

Conventions: metric (-,+,+,+); gamma-law fluid `gamma=1.3` for the original fixture (NOT Lorentz gamma), `v=v2` with `|v|<1`, `Gamma=(1-v^2)^(-1/2)` Lorentz factor. Dimensionless WE-normalized Type-II background time `d tau=H dt`. Normal-frame direction `n`; electron-rest direction `e` with `m=e_y`; Doppler `D=Gamma(1-v n_y)`; unpolarized *bolometric intensity* `I_e=D^4 I_n`; `dOmega_e=dOmega_n / D^2`. Source generator owns one factor `q=1-v n_y`.  No second Doppler factor, no original Saha-history attribution, no polarization/P8, no backreaction.

Domains: paired fixed electron-rest quadrature `(e_i,W_i)` with `W_i>0`, `sum_i W_i=4 pi`, `sum_i W_i m_i=0`; second-order exactness when invoking exact Thomson null/conservation. The normal-frame quadrature is the Lorentz transform of that rest grid; `N1>0` and positive Type-II Gauss matter constraint on the background.

Success conditions: derive the exact pair `r(v),a(v)` and `s=a^Tr`; derive Kato versus amplitude-preserving transport and a sharp counterexample with finite `v`; verify against original 401-state tilt history and original source code; separate exact results from scientific interpretation. One hostile self-review and objective small numerical check. No global strong no-go or production claim.

**R1 decision:** original source-bound, mathematical, scalar moving-grid theory; `DAG=9/15`; `StageII=11/11 historical only`; `J1=0/2 full pass HOLD`. Checkpoint via Git and independently hashed local archive after the stage.

## R2. Primary literature and source reuse

**Original source, not a new formula:** `generated/rust/typeii/typeii_collision.rs` constructs the finite-tilt scalar Thomson generator with `D=Gamma(1-v n_y)`, rest angles `e`, transformed bolometric intensity `D^4 y`, rest angular weights `w_n/D^2`, Thomson kernel `(3/16pi)(1+(e_i.e_j)^2)`, and a *single* output relative-flux `q=1-v n_y`. Source lineages are locked by `research/typeii_host_preflight_20261101/SOURCE_LOCK.json`; parent #322 compiled actual Type-II original RHS on all 401 canonical states.

**Original low-rank source:** `generated/rust/typeii/typeii_kato.rs` uses `r_i=D_i^-4`, `a_i=w_i q_i/(4pi)`, `P=r a^T/(a^Tr)`, `K=[Pdot,P]`. Its `rv_i=4r_i(mu_i/q_i-Gamma^2 v)` and `av_i=-w_i mu_i/(4pi)` are **partial derivatives at fixed normal nodes and weights**. Thus they are correct for its fixed-frame definition, not automatically for a family of moving paired grids.

**Source-owned paired geometry:** `research/typeii_stageii_preflight_20261101/source/frozen_uniformization.py::paired` uses inverse aberration of a fixed rest grid, normal weights `w_n=w_e D^2`, and validates forward aberration. `research/typeii_aem2_compare_20261101/source/replay_from_original_fixture.py::pv` explicitly differentiates the **full paired `P(v)`** by complex-step when `mode=paired`, whereas its fixed-grid branch uses the partial analytic derivative. These are two explicitly different established source computational paths. The already published 96-row comparison cannot be reclassified here without its full operator and frame contract.

**Foundational literature, used only in supported scope:**
- Davis & Gammie, *Covariant Radiative Transfer for Black Hole Spacetimes*, ApJ **888** 94 (2020), DOI https://doi.org/10.3847/1538-4357/ab5950: tetrad-frame radiative transfer and conservative invariant phase-space treatment; motivates handling the full frame transformation and frequency transport, not a claim of Type-II-specific results.
- Blanes, Casas, Oteo & Ros, *The Magnus expansion and some of its applications*, Phys. Rep. **470**, 151–238 (2009), https://arxiv.org/abs/0810.5488: time-dependent matrix evolutions and commutators; relevant to distinguishing instantaneous frozen semigroups from nonautonomous evolution.
- Joye, *General Adiabatic Evolution with a Gap Condition*, Commun. Math. Phys. **275** (2007), https://arxiv.org/abs/math-ph/0608059: spectral projections and intertwinement in adiabatic evolution; **not** a proof that a Kato gauge fixes a particular physical amplitude.
- Pitrou, *The radiative transfer at second order: a full treatment of the Boltzmann equation with polarization*, https://www2.iap.fr/users/pitrou/publi/compton10.pdf: scope warning that scalar bolometric intensity must not be promoted to polarized/frequency-resolved photon-number conservation.

**Dependency status:** `TypeII=gamma-law five-state, prescribed tilt v_2(tau)`; original `401/401` fixture source from owner is accepted as source-conditioned trajectory, not a native Saha/recombination physical receipt. Prior frozen scalar Metzler/Poisson proof is valid only when *the same discrete C* satisfies `Cr=0` and `a^TC=0`; moving `a(t)` creates a separate transport question.

**R2 decision:** primary-source and source-code mapping complete for the new scope; BASS upper DAG **9/15**, new full nodes **0**.

## R3. Scope/convention cross-check (source, derivation and hypothesis separate)

On the *paired* grid the fixed rest-frame directions `e_i` and positive weights `W_i` are independent of `v`, while the normal directions `n_i(v)` and weights `w_i(v)` are **not**. In the original collision generator `y_i` denotes bolometric intensity in the normal tetrad. This is **not** a frequency-resolved photon occupation number. The source `a(v)^T y` is a left invariant of an **instantaneously frozen** eligible collision matrix, not by itself the covariant photon number of a time-dependent universe.

The exact rest quadrature criteria for the unpolarized Thomson kernel are `sum W=4pi` and `sum W e_i e_i^T = (4pi/3) I_3`. For the amplitude theorem additionally `sum W m_i=0`, already implied by symmetric first moment of the six-axis/Lebedev26 grids. Positivity of `W`, `q` and `D` gives Metzler offdiagonal entries. This implies `C(v) r(v)=0` and `a(v)^T C(v)=0` at each v for the paired family; it does NOT give `d(a(v)^T y)/dtau=0` when v varies.

Background fluid `gamma=1.3` and Lorentz `Gamma(v)=(1-v^2)^(-1/2)` are distinct. Time derivative below is `d/dtau` with `d tau=H dt`; physical `n_e sigma_T c/H` is a *separately sourced positive scalar rate*, not supplied by the gamma-law fluid. Existing 401-record opacity is a 3-anchor log-quadratic proxy only.

Core question admits **no assumption** that the original fixed-frame generated Kato derivative was coded incorrectly: the fixed-grid partial expression is valid for its stated arguments. The new proof addresses its use after a coordinate-dependent **paired** angular transformation. The previous PR #318 Python comparison computes total paired `dP/dv` by complex-step, so its existing numerical claims are not refuted by this distinction.

Kato's `[Pdot,P]` intertwines `P(tau)`, but amplitude conservation/normalization is a second choice. Merely transporting a mathematically moving equilibrium subspace is not the same as solving the physical cosmological Liouville equation, which also depends on shear, gravitational redshift, angular advection, and the chosen intensity/frequency moment.

**R3 verdict:** source facts distinguished from upcoming novel direct algebra; `DAG 9/15`, `0` new upper nodes.

## R4. Divergent constructive candidate connections

Let `P(v)=r(v)a(v)^T/s(v)`, `s(v)=a(v)^T r(v)>0`, and `C(v)r=0=a^T C(v)`. Evaluate three **different mathematical transports** of the same source:

1. **A | Kato geometric subspace connection:** `G_A=alpha nu(tau) C(v)+K(v)`, `K=[Pdot,P]`, full time derivative including `n(v),w(v)`. Guaranteed `P(tau) U_A(tau,tau0)=U_A(tau,tau0) P(tau0)` if the finite-dimensional smooth equation is solved exactly. This does **not** fix how the amplitude of `r(v)` evolves.

2. **B | Rest-isotropic-amplitude calibration:** `G_B=alpha nu C + K + lambda(tau) P`, `lambda=(a^T rdot)/s`. For any scalar `c` initial `y=c r(v0)`, the path `y=c r(v(tau))` is an exact solution (the collision term vanishes). If `s` is constant and `a^TC=0`, then `a(tau)^T y` is also constant for **all** solutions of `G_B`. This is a choice of center mode/gauge, not by itself a physical free-streaming law. For `s\ne constant` the two normalization goals are distinct.

3. **C | Rest-label frame-pullback:** `G_C=alpha nu C + diag(rdot_i/r_i)` on the *specific* paired rest-labelled bolometric vector. Its geometric term gives `y_i=r_i(v)J_i` for constant (possibly anisotropic) rest-frame `J_i` if collisions vanish. The full covariant Liouville equation instead introduces real geometric redshift/shear/angular evolution of `J_i`, so `G_C` alone is not its replacement. Unlike B, the diagonal term is generally different off the equilibrium subspace.

Distinguishing diagnostic: for an isolated tilt change from `v0=0` to `v=0.2` and a symmetric paired grid, candidate A predicts the rest-intensity amplitude ratio `(1-v^2)^2=0.9216`, while B and C give exactly `1` for initially isotropic rest intensity. This is a **finite, falsifiable mathematical discrepancy**, not a production or observational prediction.

Core decision for R5: derive the analytic paired-grid `r,a,s,rdot,adot,K` and both propagation laws, quantify the discrepancy on the original 401-state Type-II tilt history. Keep candidate C as the physical-coordinate comparator rather than silently labeling B as covariant transport.

**R4**: 3 explicit candidates, one distinguishing case; `DAG 9/15`, `0` new full upper nodes.

## R5. Exact finite-grid derivation (the principal new result)

### Geometry and instantaneous collision invariants
Fix rest directions \(e_i\), first-moment symmetric positive weights \(W_i\) and \(m_i=e_{iy}\). The corresponding **normal** direction, boost and measure are
\[
 \mu_i(v)=\frac{m_i+v}{1+v m_i},\quad
 q_i=1-v\mu_i=\frac{1-v^2}{1+v m_i},\quad
 D_i=\Gamma q_i=\frac{\sqrt{1-v^2}}{1+v m_i},\quad
 w_i(v)=W_iD_i^2.
\]
The original scalar normal-to-rest bolometric map is \(J_i=D_i^4y_i\). The original source generator is
\[
 C(v)=\operatorname{diag}(q_iD_i^{-4})
       [K\operatorname{diag}(W_i)-I]\operatorname{diag}(D_i^4),
 \quad K_{ij}=\frac3{16\pi}(1+(e_i\cdot e_j)^2).
\]
If \(\sum_iW_i=4\pi\) and \(\sum_iW_i e_ie_i^T=(4\pi/3)I\), then \([K\operatorname{diag}(W)-I]\mathbf1=0\) and \(W^T[K\operatorname{diag}(W)-I]=0\). Define source-owned
\[
 r_i(v)=D_i^{-4}=\Gamma^4(1+v m_i)^4,\qquad
 a_i(v)=\frac{w_i(v)q_i}{4\pi}
       =\frac{W_i}{4\pi}\Gamma^{-4}(1+v m_i)^{-3}.
\]
Then \(C(v)r(v)=0\), since \(D^4r=\mathbf1\). Also
\(a_iq_iD_i^{-4}=W_i/(4\pi\Gamma^2)\), giving \(a(v)^TC(v)=0\).
The product and normalizing denominator are *exactly*
\[
 a_i(v)r_i(v)=\frac{W_i}{4\pi}(1+vm_i),\quad
 s(v)=a^Tr=1+v\frac{\sum_i W_i m_i}{4\pi}.
\]
Hence for both symmetric original rest grids, **\(s(v)\equiv1\)**. This is NOT the same as \(a(v)\) being constant.

### Full paired-grid derivatives versus fixed-normal partial derivatives
Holding fixed \((e_i,W_i)\), not \((\mu_i,w_i)\), yields
\[
 \frac{\partial_v r_i}{r_i}=4\frac{v}{1-v^2}
                              +\frac{4m_i}{1+vm_i},\quad
 \frac{\partial_v a_i}{a_i}=-4\frac{v}{1-v^2}
                              -\frac{3m_i}{1+vm_i}.
\]
For symmetric first moment, \((\partial_v a)^Tr=-4v/(1-v^2)\),
\(a^T(\partial_v r)=4v/(1-v^2)\), \(s'=0\). Dots are \(\partial_\tau = v'(\tau)\partial_v\), not physical seconds.
Explicit Wolfram CAS independently simplified both componentwise derivatives and the product identity to residual **0** on \(|v|<1,\ |m|\le1,\ W>0\). This check does not rely on the BASS numeric fixture.

### Kato intertwinement and center amplitude
Set \(P(v)=ra^T/s\), \(K=[\dot P,P]\). By \(P^2=P\), differentiating gives \(P\dot PP=0\) and \([K,P]=\dot P\). The original **paired** scalar collision \(C\) satisfies \(CP=PC=0\). Therefore the propagator of
\[
 \dot y=(\alpha\nu(\tau)C(v(\tau))+K(\tau))y
\]
obeys \(P(\tau)U(\tau,\tau_0)=U(\tau,\tau_0)P(\tau_0)\) for smooth \(v\) and nonnegative, finite \(\alpha\nu\), irrespective of commutativity of \(C(\tau_1)\) and \(C(\tau_2)\).

But
\[
 K r=\dot r-\lambda r,\qquad
 \lambda=\frac{a^T\dot r}{a^Tr}
        =\frac{4v\dot v}{1-v^2}
\]
for the symmetric paired grid. If \(y_0=c_0r(v_0)\), then \(y_A(\tau)=c_A(\tau)r(v(\tau))\) with
\[
 \dot c_A=-\lambda c_A,\qquad
 \boxed{\frac{c_A(\tau)}{c_0}=
       \left(\frac{1-v(\tau)^2}{1-v_0^2}\right)^2}.
\]
The same relation holds independently of the opacity scale because \(Cr=0\). Therefore **intertwinement does not imply constant rest-isotropic bolometric amplitude**. This is a source-specific mathematical distinction; not a claim that Kato's theorem is wrong.

### Minimal center-mode correction, and precise interpretation
The explicitly *chosen* scalar calibration
\[
 \boxed{G_B=\alpha\nu C+[\dot P,P]+\lambda P}
\]
satisfies \(G_Br=\dot r\). Hence \(y_B(\tau)=c_0r(v(\tau))\) is exact for initially rest-isotropic data. More generally,
\[
 \frac{d}{d\tau}(a^Ty)\Big|_{G_B}
   =\frac{\dot s}{s}(a^Ty),
\]
so it is identically zero on the **paired symmetric** family \(\dot s=0\), not on arbitrary moving grids. This follows from \(a^T K=-\dot a^T+(\dot a^T r/s)a^T\) and \(\dot s=\dot a^Tr+a^T\dot r\).

The full fixed-rest-label pullback \(G_C=\alpha\nu C+\operatorname{diag}(\dot r_i/r_i)\) equals \(G_B\) **only on the instantaneously isotropic subspace**. A physical Boltzmann Liouville term (shear, ray advection, redshift, spectral redistribution, frame tetrad) has NOT been derived from these purely algebraic conditions; do not replace the original BASS transport with \(G_B\) or \(G_C\) without that reconciliation. No photon-number conservation claim is made for bolometric \(y\).

**R5 exact mathematical result:** moving scalar paired-grid normalization and center-mode transport identity. Source ownership, boundary and physical interpretation explicitly scoped; upper DAG **9/15** and new complete upper nodes **0**.

## R6. Same-author hostile referee, actual negative controls

This is **self-adversarial source-aligned checking**, NOT a blind distinct-author reviewer nor native subagent. Source: immutable PR #318 paired-grid \`replay_from_original_fixture.py\`, its independent source \`bg_rhs\`, original 401-state initial \`v=0.05\` and \`dv/dtau=-0.016845446584938688\`. For both grids construct \`C,P\` from actual source; \`dP_total/dv\` via complex-step of fully paired \`P(v)\`, and independently evaluate the source's **fixed-normal partial** derivative at the same instantaneous normal directions/weights. Evaluated \`K=\dot P P-P\dot P\`, \`H=K+\lambda P\` using the explicit analytic \(\lambda\), and both \(\dot r,\dot a\) from independently differentiated paired component formulas.

Observed at initial source state:

| Matrix/vector check | axis6 | Lebedev26 |
|---|---:|---:|
| max |Cr| | 2.22e-16 | 4.44e-16 |
| max |a^T C| | 2.78e-17 | 1.73e-17 |
| a^T r | 1.0000000000000002 | 1.0 |
| lambda | -0.003377533149862394 | same |
| max |Kr-(rdot-lambda r)| | 1.39e-17 | 3.47e-17 |
| max |(K+lambda P)r-rdot| | 1.39e-17 | 3.47e-17 |
| |adot^T y+a^T H y|, fixed seeded positive y | 8.67e-19 | 1.08e-18 |
| max |dP_total/dv-dP_fixed/dv| entry | **0.47375327** | **0.13535808** |
| smallest offdiagonal entry of H | **-0.01368471** | **-0.00460992** |

**Finding F1 (BLOCK_NOW for paired Kato reuse, not the source's fixed-frame path):** total paired-grid projector derivative differs strongly from keeping normal directions/weights fixed; replacing one by the other is mathematically invalid for an evolving paired grid. This is already handled in the former PR #318 Python total complex-step path. Do not retroactively claim PR #318 is broken.

**Finding F2 (BLOCK_NOW for an unconditional positivity claim):** although each eligible scalar collision C is Metzler, the geometric connection \`H\` alone has negative off-diagonal entries on real source states. Therefore \`C + H\` is **not guaranteed** to be Metzler for arbitrary collision rate or opacity. The frozen-scalar Poisson stochasticity proof does not automatically apply to nonautonomous \`C+K\` or \`C+H\`; a separate positivity argument or explicit physical transport implementation is required. For zero or sufficiently small positive collision prefactor, the negative offdiagonal of H survives.

**Finding F3 (scope correction):** equality of the algebraic center amplitude \`a^T y\` with genuine photon number, full Einstein-photon energy conservation, or polarization/linear Stokes evolution is NOT established. This scalar energy-integrated angular representation has no frequency integration sufficient to reconstruct conserved photon occupation number. Do not use \`G_B\` as an automatic physical transport law.

**Finding F4 (singular boundary):** \(|v|\to1\) makes \(\Gamma\) singular, and a paired rest grid with nonzero first moment has \(\dot s\ne0\). The exact constant-amplitude/conserved-center equivalence is scoped to \(\sum W m=0\). The Type-I boundary \(N_1=0\) is outside the previous original 4D constraint chart.

**Verdict:** exact amplitude theorem stands; physical production admission and generic positivity are **HOLD**. No new universal no-go; no new full BASS DAG node. Upper **9/15**, new **0**.

## R7. Source-locked 401-state numerical discriminant

Run on authorized owner device, isolated original-source worktree with \`PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/typeii_moving_kato_amplitude_20261101/verify_moving_amplitude.py\`. The script explicitly checks the canonical 401-fixture Git SHA-1 blob \`dea22f0fce116b61314b13cea7d0bdd38efe48bc\` and original source file blobs against immutable main \`9c6506e4e2087129a8b674ff10438e5db1a55c9d\`, reuses the same source-matched PR #318 paired quadrature generator, and independently reconstructs the analytical \`r,a,rdot,adot\` for six-axis and Lebedev26.

Actual outputs in \`R7_NUMERIC_RESULTS.json\` (frozen source-conditioned numerical diagnostics):
- 401/401 original states for **both** axis6 and Lebedev26, **PASS**; each grid has the correct positive quadrature normalization, second angular moment, and first-moment symmetry.
- Axis6 maximal \`|Cr|=8.326672684688674e-16\`, \`|aC|=1.457167719820518e-16\`, \`|s-1|=6.661338147750939e-16\`, analytic \`r\` gap \`1.5543122344752192e-15\`, analytic \`a\` gap \`1.6653345369377348e-16\`.
- Lebedev26 maximal \`|Cr|=9.020562075079397e-16\`, \`|aC|=4.85722573273506e-17\`, \`|s-1|=6.661338147750939e-16\`, analytic \`r\` gap \`1.5543122344752192e-15\`.
- Full paired projector derivative complex-step versus independent analytic full derivative: max \`1.734723475976807e-17\` for axis6 and \`4.228388472693467e-18\` for Lebedev26, tested at original fixture indices 0, 200, 400.
- \`|(K+lambda P)r-rdot|\` maximal \`5.551115123125783e-17\` axis6, \`9.71445146547012e-17\` Lebedev26. Seeded positive arbitrary \`y\` has \`|adot^Ty+a^T(K+lambda P)y|\` less than \`1.3e-17\`.
- Original tilt endpoint: \`v0=0.05\`, \`v(0.2)=0.046733834290499716\`; exact Kato amplitude ratio \`1.0006335814925333\`, **fractional +0.0006335814925333416**.
- Independent DOP853 integration of the *actual source-conditioned scalar collision matrix and original 3-anchor opacity proxy* with a cubic-spline interpolated prescribed v(t), self-consistent spline derivative, \`atol=2e-13\`, \`rtol=3e-11\`, \`max_step=0.005\`, 482 RHS evaluations per scenario: pure Kato exact endpoint max difference \`2.220446049250313e-15\`; amplitude-calibrated exact endpoint max difference \`1.3322676295501878e-15\`. Corresponding final moments \`a^Ty=1.0006335814925351\` and \`a^Ty=1.000000000000001\`.

**No hidden production inference:** the 401 fixture is the original deterministic gamma-law source-conditioned RK4 trajectory; opacity is still the existing original-model three-anchor log-quadratic proxy, not an original SahaHistory implementation. The independent ODE is a scalar moving-equilibrium diagnostic, not photon free streaming, collision/Einstein feedback, or CMB spectra. Numerical pass does not prove positivity of the full corrected nonautonomous generator.

**R7** completed for this scoped theory object; BASS upper DAG **9/15** unchanged; zero new full upper nodes.

## R8. Claim admission and scientific relevance

**Established by immutable BASS source:** the five-state Type-II background at fixed gamma-law parameter, original scalar source's finite-v \`C(v)\` and source \`r,a,P\` definitions; direct PR #318 Python use of full paired \`dP/dv\` vs source fixed-normal analytic partial. True source ownership is the exact Git objects, not this document.

**Derived exactly in R5, independently CAS-checked:** on a symmetric rest-labelled paired angular quadrature, \(a^Tr=1\), \(Cr=0\), \(a^TC=0\), Kato subspace intertwinement, pure-Kato center amplitude law, and the chosen \(\lambda P\) amplitude correction. The law is mathematical and conditional on a scalar generator and the stated frame convention, not a novel theorem about all relativistic Thomson evolution.

**Numerically checked (R6–R7):** 401/401 BASS states on both axis6 and Lebedev26; exact component residuals \(\lesssim 2\cdot10^{-15}\), independent DOP853 endpoint differences \(\lesssim 3\cdot10^{-15}\) for either candidate. The original 401-state tilt produces \(\Delta c_A/c_0=+6.335814925333416\times10^{-4}\) for Kato versus the amplitude-normalized family. The finite 0.9216 counterexample from \(v=0\rightarrow0.2\) is exact on the algebraic branch.

**Adversarial correction retained:** positive scalar collision \`C\` does not imply geometric Kato + calibrated connection is a Markov/Metzler generator. On real initial Type-II states, \`K+lambda P\` has negative off-diagonal entries. Fixed-normal \`partial_v P\` is not the total paired-grid derivative. No global impossibility, no CMB inference, no original Saha equivalence.

**Decision:** ACCEPT the result as a scoped new *mathematical physics* constraint and executable discriminant for subsequent \`P-MIG-II-PREFLIGHT\` theory/implementation; HOLD physically calibrated positivity, exact Boltzmann-Liouville compatibility, native opacity, production dispatch, Stage II canonical evidence, and full observational prediction. Do not merge the draft. Next scientifically substantive path is to derive and test the *actual original BASS source-owned* Liouville frame derivative and collision number/energy moment with these new benchmarks, not to optimize a placeholder.

**DAG:** \`BASS_UPPER=9/15 scoped/source-mapped\`; \`NEW_COMPLETED_UPPER=0\`; \`STAGEII=11/11 historical, current canonical missing\`; \`G_DYN_MANIFOLD_VI0=PARTIAL\`; \`P_MIG_II_PREFLIGHT=PARTIAL\`; \`JOIN_J1=0/2 FULL PASS HOLD\`. Theory R8 **completed**, not production promotion.

## R9. Reusable computational mathematical contract for the *next coding loop*

**Inputs and owners:** \`tau\`, source-owned physical Type-II \`(SigmaPlus,SigmaMinus,Sigma13,N1,v2)\` with fixed gamma-law \`gamma=1.3\` in the canonical fixture, original RHS \`generated/rust/typeii/typeii_background.rs\` to obtain \`vprime=rhs(state,gamma)[4]\`, plus a **fixed electron-rest** quadrature \`(e_i,W_i)\`. Rate source \`nu_tau(tau)\` must have an explicit provider/version/frame and unit convention; for an SI-resolved owner it is a scalar of the form \`n_e sigma_T c/H\` after the frame density convention is settled. The old three-anchor proxy is allowed only for regression and exploratory runs, not native Saha admission.

**Exact functions in original source notation** (do not call the ordinary-fluid adiabatic index \`gamma\` the Lorentz factor): given \`m=e[:,1]\`, \`v=state.x[4]\`, \`vp=vprime\`,
\[
 \mu_i=\frac{m_i+v}{1+v m_i},\quad
 D_i=\frac{\sqrt{1-v^2}}{1+v m_i},\quad
 q_i=\frac{1-v^2}{1+vm_i},\quad
 w_i=W_iD_i^2;
\]
\[
 r_i=\frac{(1+vm_i)^4}{(1-v^2)^2},\quad
 a_i=\frac{W_i}{4\pi}\frac{(1-v^2)^2}{(1+vm_i)^3},\quad
 s=a^Tr,\quad P=\frac{ra^T}{s};
\]
\[
 \dot r_i=4vp\,r_i\left(\frac{v}{1-v^2}+\frac{m_i}{1+vm_i}\right),\quad
 \dot a_i=vp\,a_i\left(-\frac{4v}{1-v^2}-\frac{3m_i}{1+vm_i}\right);
\]
\[
 \dot P=\frac{\dot r\,a^T+r\,\dot a^T}{s}-P\frac{\dot s}{s},
 \quad K=[\dot P,P],\quad \lambda=\frac{a^T\dot r}{s},\quad H=K+\lambda P.
\]
For symmetric paired rest grids \(\dot s=0\), \(\lambda=4vvp/(1-v^2)\).
Call the original source's \`collision_generator_apply(normal_dirs,normal_weights,v,axis=1,y)\` **exactly once** per operator action: the generated source already supplies its output \`q\`. Its rest-angular weights are \`w_i/D_i^2\`; do not multiply by an external second q or reaberrate the rest nodes.

**Output contract:** \`(C,P,Pdot,K,lambda,H,r,a,D,q,normal_dirs,normal_weights,vprime,nu_tau)\` plus source IDs. For a candidate geometry-only comparison use \`G_A=alpha nu_tau C+K\` and \`G_B=alpha nu_tau C+H\` as **theoretical comparators only**. The source original physical streaming term \`A=-4(1+sigma_nn)\` and angular Liouville must be independently reconciled; neither comparator can be silently placed into \`RuntimePlanCore::run_fixture\` as a replacement for a physical photon RHS. Preserve original full-dimensional Arnoldi/Pade13 exp/phi reference backend; do not make adaptive Krylov or scalar uniformization a polarized default.

**Must-test observables and precise acceptance:**
- Original immutable 9 Git objects byte exact. No original generated-file or main mutation.
- Two source-matched paired grids, 401 original v(tau) records: \`Cr\`, \`aC\`, \`a^Tr-1\`, \`Pdot_analytic-Pdot_total_complexstep\`, \`H r-rdot\` all bounded by the *predeclared* \`1e-11\` local absolute tolerance; negative source sign/frame tests fail closed.
- Endpoints for gamma-law fixture: \`v0=.05\`, \`vend=.046733834290499716\`, \`ratio_A=1.0006335814925333\`, \`ratio_B=1.0\`; original positive-opacity proxy DOP853 comparator agrees within \`5e-9\`.
- Separate **negative** controls for fixed-v source partial substituted for paired total derivative, unsymmetric non-unit rest angular weights, double q, \`v=1\`, \`N1=0\`, and attempts to infer positivity from \`C\` alone. Differential equations in physical seconds must explicitly convert \`d tau=H dt\`.
- For a genuine physical photon evolution, test scalar angular remap and frequency moment against a source-owned covariant kinetic conservation law; test positivity only after adding the full physical Liouville term. Original opacity and Stage II canonical verifier must be acquired independently.

**R9 status:** equations and finite-grid numerical targets are implementation-ready as a *theory contract*; actual production callback wiring and live photon outputs remain \`NOT_RUN\`. Upper DAG **9/15**; no newly complete upper node.
