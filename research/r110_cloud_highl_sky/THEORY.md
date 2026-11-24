# R110 theory loop: deterministic all-m skies to arbitrary multipole on nonperturbative Bianchi backgrounds

Base: BASS `3966f2a08` (R109 native homogeneous sky), REC `f3797f42c`, REI `25fbae98b`,
htt_base `423165ab2` (R109 bridge). Conventions are those of R109
`research/r109_native_sky/NATIVE_SOLVER.md`: signature (−,+,+,+), right-handed
orthonormal normal tetrad, ε₁₂₃=+1, e-fold clock η=ln(a/a_emit), Hubble-normalized
Σ=σ/H, N, A, structure constants Cᵏᵢⱼ=εᵢⱼₗNˡᵏ+Aᵢδᵏⱼ−Aⱼδᵏᵢ, photon propagation
direction e, outward sky direction n=−e, HEALPix spin convention
Q±iU=−Σ(E±iB) ±2Y. Equation numbers "I-(x)" and "II-(x)" refer to
`/dossier/Dossier_I_Homogeneous_Geometry.pdf` and
`/dossier/Dossier_II_Kinetic_Transport.pdf` (14 Oct 2026).

All numbers quoted below come from `THEORY_CHECKS.json`, written by
`theory_checks.py` in this directory (NumPy/SciPy/SymPy/mpmath only; it does
not call the Rust solver).

## Phase 1 · Contract

**Question.** What must be derived, beyond R109, so that BASS produces the full
deterministic mode products D^{XY}_{ℓm}=a^X_{ℓm}a^{Y*}_{ℓm} (X,Y∈{T,E,B}) to an
arbitrary multipole ℓ_max on a nonperturbative homogeneous background, for every
Bianchi Lie algebra, with finite material tilt and an observer boost, using a
single Lie-algebra-generated formulation rather than per-type code?

**Sub-questions.**
- Q1. How can the observed field be evaluated at arbitrary sky directions without
  losing consistency with the R109 Lagrangian forward solution?
- Q2. Which harmonic analysis gives exact coefficients at high ℓ and the same
  conventions as R109 `sky_spectrum::analyze`?
- Q3. Which Thomson time integrator raises the collision accuracy to second order
  while staying correct in the optically thick limit with moving electrons?
- Q4. How does a cosmological constant enter the Hubble-normalized
  orthonormal-frame system for all Lie algebras?
- Q5. Which statements make the "all families from Lie data" claim testable?
- Q6. What changes in the hydrogen recombination source when the radiation
  field and the expansion are anisotropic (REC support)?

**Out of scope.** Spatial perturbations and primordial covariance; spectral
(frequency-resolved) transport and Compton redistribution; H=0 turnaround charts;
an astrophysical z<4 REI history. These remain as stated in R109.

**Evidence standard.** A claim is promoted only with (i) a derivation from a cited
equation, and (ii) an executable check (symbolic, numeric oracle, or Rust test)
with a stated tolerance.

**Completion bar.** Each Q has a surviving formulation, a rejected alternative
where one was considered, and a test with a pass/kill criterion carried into the
coding loop.

## Phase 2 · Evidence

| Source | Content used |
|---|---|
| Dossier I §1.1–1.4 | I-(1.2) structure constants; I-(1.5)–(1.6) curvature; I-(1.7)–(1.12) Codazzi strata and VI₋₁/₉; I-(1.14) Hamiltonian with Λ; I-(1.23)–(1.25) evolution with Λ; I-(1.26)–(1.27) type preservation and invariance of h |
| Dossier II §1.4–1.5, 1.7 | II-(1.25)–(1.29) characteristic, screen generator, Jacobian; II-(1.40)–(1.46) moving-electron Thomson operator, rank-9 gain, drag; II-(1.70)–(1.72) E/B and PSTF maps |
| R109 BASS | `homogeneous_sky::{scatter_kernel, recoil, solve}`, `kinetic::{lie_history::advance_ray, sky_spectrum::analyze}`; first-order backward-Euler (BE) collision; ℓ_max=4 atlas; GL×φ Lagrangian rays |
| R108 htt_base | Python LoS vs native ≤1.6×10⁻⁴ at ℓ≤4 (768 cells); high-ℓ cell convergence non-asymptotic (ratio ≈1.2, S3); BJS VII_h correlation ≥0.99892 (S4); Python LoS at Nside 128 took 609 s single process (S7) |
| Literature | Challinor 2000 (polarized transport in general spacetimes), Pontzen & Challinor 2007 (Bianchi CMB polarization), van Elst & Uggla 1997 (orthonormal frames), Hervik et al. 2008 (VI₋₁/₉), Alexander 1977 (L-stable SDIRK2), Castor 1970 / Rybicki & Hummer 1978 (escape probability for a velocity-gradient tensor), Ali-Haïmoud & Hirata 2011 and Lee & Ali-Haïmoud 2020 (HyRec/HYREC-2 effective atom) |

## Phase 3 · Claim–source audit

| Claim | Source | Status |
|---|---|---|
| Free transport has angular coupling width ‖ℓ−ℓ′‖≤2 in the normal frame | II-(1.34)–(1.38) | SUPPORTED (normal frame only; boosts and collisions break it) |
| Per-ray collision update depends on the global field only through a 3×3 rest-frame tensor | II-(1.43)–(1.44); R109 `scatter_kernel` | SUPPORTED (bolometric k=4, real symmetric coherency, no V) |
| h=A²/(N₂N₃) is invariant under the exact evolution | I-(1.27) | SUPPORTED |
| Λ enters the Raychaudhuri equation as +Λ/3 | I-(1.23) | SUPPORTED |
| Alexander SDIRK2 (γ=1−√2/2) is L-stable and stiffly accurate | Alexander 1977; Hairer & Wanner II | SUPPORTED |
| Angle-averaged Sobolev escape depends only on H in the thick limit | derived below (D8), Castor 1970 form of the escape integral | INFERENCE, verified numerically |
| The Thomson stiff limit preserves the encounter-weighted invariant | derived below (D5) | INFERENCE, verified numerically |

## Phase 4 · Hypothesis space (design candidates)

| Gap | Candidates |
|---|---|
| G1 high-ℓ sky (Q1) | H1a refine the Lagrangian mesh until ℓ_max is resolved; H1b PSTF/spin hierarchy truncated at large L; H1c **replay**: record the global collision sources of the forward solve, then evaluate the same per-ray discrete map along exact backward characteristics from an observer grid |
| G2 harmonic analysis (Q2) | H2a per-sample Wigner recursion (R109, O(N_pix L²)); H2b **ring transform** on GL×uniform-φ observer grids, O(L³), same Wigner columns |
| G3 collision order (Q3) | H3a keep BE; H3b exponential-trapezoid (ETD2) with linear source interpolation; H3c **Alexander SDIRK2** as two BE-type closures |
| G4 Λ (Q4) | H4a external H(η) table; H4b **Ω_Λ=Ω_Λ,i/h²** inside the Hubble-normalized system |
| G5 universality (Q5) | H5 type invariants and rotation covariance as executable certificates |
| G6 REC (Q6) | H6a transplant an FLRW x_e table (R109); H6b **anisotropic effective-atom source**: direction-averaged escape and photoionization from the actual sky |

## Phase 5 · Adversarial review

- H1a scales as O(ℓ²_max) rays inside every implicit collision solve and needs
  the Lagrangian sample to stay well distributed under focusing; aliasing of the
  final weighted quadrature is uncontrolled. Rejected for ℓ_max≫4.
- H1b changes the scheme the R109 atlas was validated with; a finite closure adds
  an error that must be measured separately (Dossier II after (1.72)); a boosted
  observer and moving electrons couple all ℓ. Kept as an external comparator
  only (htt_base native hierarchy).
- H1c attack: the replay field is only as good as the recorded sources. Answer:
  the sources are 6-component rest-frame tensors (ℓ≤2 information), whose
  quadrature converges with the Lagrangian mesh independently of the observed
  ℓ_max; the replay at the forward ray directions must reproduce the forward
  solution bitwise (kill criterion V3).
- H1c attack: a backward trace that is not the exact inverse of the forward
  characteristic map misplaces the replay. Answer: the R109 characteristic
  integrator is a Lie-group implicit midpoint rule, self-adjoint under h→−h for
  the same midpoint background (`transport_characteristic_profile`); measure the
  forward-replay landing error (V4).
- H3b attack (decisive): the stiff limit. See D5 — ETD2 fails.
- H3c attack: positivity is not unconditional (R(z)≥−0.2071). Answer: the R109
  positivity check stays active; the bound is documented and tested.
- H4b attack: Λ must not enter Codazzi or the anisotropic stress. Answer: I-(1.7)
  and I-(1.24) contain no Λ.
- H6b attack: Sobolev escape needs a monotone flow. Answer: the lemma requires
  λ_min(Σ)>−1, i.e. every principal expansion rate is positive; the code must
  fail closed otherwise.

## Phase 6 · Physics and mathematics validation

### D1 · Discrete replay theorem (Q1)

R109 advances the Lagrangian bundle {(e_k, w_k, F_k)} through steps
[η_l, η_r] as C_l G_{l→r} C_r, where C are collision cells (one per opacity
knot or accepted recoil trial) and G is the characteristic map `advance_ray`.
A BE cell with bare depth τ, electron velocity β and optional gain normalization
T acts on every ray as

    X_k = J_k F_k J_kᵀ D_k⁴,  d_k = τ D_k,  D_k = γ(1−β·e_k),
    X_k′ = X_k/(1+d_k) + GAIN·d_k/(1+d_k)·Π_k S Π_kᵀ,  Π_k = P(e_k^u) T,
    F_k′ = J_k⁻¹ X_k′ J_k⁻ᵀ D_k⁻⁴,

where S solves the six-dimensional closure
(I − Σ_k A_k GAIN d_k/(1+d_k) Π_k⊗Π_k) S = Σ_k A_k X_k/(1+d_k), A_k=w_k/D_k²
(II-(1.43) with k=4: S=M_{u,4}).

**Theorem.** Given the recorded sequence {(τ_c, β_c, T_c, S_c)} and nodes, the
map (e, F) ↦ (e′, F′) of one ray is a composition of affine maps that does not
involve any other ray. Hence (i) replaying a forward ray from its initial
direction reproduces its final coherency with the same floating-point
operations, and (ii) replaying from any other initial direction evaluates the
same discrete scheme at that direction.

*Proof.* S enters each ray only through Π_k S Π_kᵀ; given S, the boost, d_k and
Π_k depend on the ray's own direction; G acts per ray. ∎

**Consequence.** The observed angular resolution decouples from the Lagrangian
mesh. The mesh only sets the accuracy of S(η) (a 6-dimensional rest-frame
moment), while the observed field is evaluated exactly along each characteristic.
The error decomposes into (a) time discretization of the forward scheme,
(b) quadrature error of S on the Lagrangian mesh, and (c) the analysis-grid
aliasing of D4. (a) and (b) are tested by refinement; (c) by oversampling.

### D2 · Backward characteristic

The direction flow e′=g×e (II-(1.26)) is the flow of a smooth tangent field on
S², so each step map is a diffeomorphism of S². The R109 integrator uses the
Lie-group implicit midpoint e_m=exp[(h/2)Ω(e_m)]e_n per substep with the same
midpoint background for ±h; hence `advance_ray(r,l,·)` inverts
`advance_ray(l,r,·)` up to the fixed-point tolerance (8×10⁻¹⁵ per substep;
R109 test: forward/backward 2×10⁻¹³ after 24 steps). The replay starts from the
traced-back direction e₀ and reports the landing error |e_N(replay)−e_N(target)|
as a diagnostic (V4).

### D3 · Observer sampling

For an observer moving with β_o in the final normal tetrad and an observed
outward direction n′, the observer-frame propagation direction is e′=−n′ and the
normal-frame direction is e=boost(e′,−β_o) (R109 `boost` is inverted by
β↦−β, tested to 4×10⁻¹⁴). After replay, the observed screen is
J F Jᵀ D⁴ with D=γ(1−β_o·e) (R109 `transformed`). No solid-angle Jacobian is
needed because the analysis grid is placed directly in the observer frame. For a
boosted FLRW observer the exact field is

    T(n′) = (β/artanh β)/(1−β·n′) − 1,

with T=I^{1/4}/⟨I^{1/4}⟩−1 (R109 definition); for ℓ≥1,
a_{ℓ0} = √((2ℓ+1)π)·(β/artanh β)·(2/β)·Q_ℓ(1/β) along β. The mpmath quadrature
and the Legendre-Q closed form agree to the double-precision floor
(`T9_boosted_flrw_oracle`); for β=0.3: a₁₀=0.62947, a₂₀=0.099884,
a₃₀=0.015559, a₄₀=2.4084×10⁻³, a₅₀=3.7170×10⁻⁴.

### D4 · Spin-harmonic analysis on GL rings

On a grid of N_θ Gauss–Legendre nodes in cos θ and N_φ uniform azimuths, for
fixed m the θ-integrand of a spin-s field against ₛY*_{ℓm} is a polynomial in
cos θ (the Wigner factors share the powers (|m+s|,|m−s|)), so the rule is
exact for band limit L_f when N_θ≥⌈(L_f+ℓ+1)/2⌉ and N_φ≥L_f+ℓ+1. Writing
F_j(m)=Σ_k f(θ_j,φ_k)e^{−imφ_k}, the R109 per-sample sum reorders into
a_{ℓm}=Σ_j w_j(2π/N_φ)·√((2ℓ+1)/4π)·d^ℓ_{m,−s}(θ_j)·F_j(m) with the same Wigner
columns and the same E=−(a₊+a₋)/2, B=i(a₊−a₋)/2 combination; only the
floating-point summation order changes (V5). Cost O(N_θN_φL+N_θL²).
A field that is not band-limited (boosted Doppler, VII_h focusing) aliases power
above the exactness limit; the code exposes N_θ, N_φ for oversampling (V8).

### D5 · Thomson time integration with moving electrons (Q3)

For frozen geometry and electron velocity, the bolometric collision subsystem is
linear, dX_k/dτ = −D_kX_k + D_k GAIN Π_k S Π_kᵀ, S=Σ_j A_jX_j. Its left null
functional is

    ℓ(X) = Σ_k (A_k/D_k) tr X_k = Σ_k w_k D_k tr F_k,

because dℓ/dτ = −tr S + tr(KS) = 0 with K S = GAIN Σ_k A_kΠ_kSΠ_kᵀ and the
discrete normalization tr(KS)=tr S (R109 `gain_map`; without the map this holds
to quadrature accuracy). ℓ is the encounter-weighted bolometric content; it is
conserved by every Runge–Kutta method applied to this linear system, and by BE.

*ETD2 (H3b).* Integrating each ray with its exact factor e^{−d_k} and a linear
source S(τ′)=S₀(1−τ′/τ)+S₁τ′/τ gives X_k′=e^{−d_k}X_k+GAIN Π_k(a_kS₀+b_kS₁)Π_kᵀ
with a=(1−e^{−d})/d−e^{−d}, b=1−(1−e^{−d})/d (symbolic residual 0; weights ≥0;
a→0, b→1 as d→∞). The closure for S₁ has its conserved direction at eigenvalue
O(1/d), so O(1/d) per-ray consistency errors are amplified to O(1): unless all
D_k are equal, ETD2 violates ℓ. In the 9-direction toy with β=0.3 the invariant
drifts by 1.9% (κΔ=30) and 3.0% (κΔ=3×10⁴), and the error stays at 3.28×10⁻²
for 4…32 substeps at κΔ=3×10⁴. **Rejected.**

*SDIRK2 (H3c).* Alexander's two-stage method with γ=1−√2/2:

    X⁽¹⁾ = BE(X; γτ, S⁽¹⁾),  Y = −√2 X + (1+√2) X⁽¹⁾,  X′ = BE(Y; γτ, S⁽²⁾),

where BE(·;γτ,S) is the R109 closure with depth γτ (each stage solves its own
6×6 system). It is second order (toy: orders 2.00 at κΔ=0.3 and 3), L-stable
and stiffly accurate (error 5×10⁻¹⁴ at κΔ=3×10⁴ with 32 steps; BE 2×10⁻¹²;
ETD2 3×10⁻²), and preserves ℓ to the conditioning floor (≤3×10⁻¹²). Its
stability function R(z)=(1+(1−2γ)z)/(1−γz)² has min R=−0.2071; a ray brighter
than 5.83 times its local stage equilibrium can turn negative within a stage,
which the R109 positivity check rejects (fail-closed, "refine mesh"). The replay
records both stage sources.

*Splitting.* R109 composes C_{Δ/2}(l) G_Δ C_{Δ/2}(r) with second-order geometry
(midpoint characteristic, linear node interpolation) and a midpoint
predictor–corrector for the active Einstein step. With SDIRK2 every component is
second order; the global order is measured (V9), not assumed.

### D6 · Cosmological constant in the Hubble-normalized system (Q4)

From I-(1.14), (1.23)–(1.25) with Ω_Λ=Λ/(3H²):

- Gauss: 1 = Ω_m + Ω_Λ + Σ:Σ/6 + K, K=−³R/(6H²).
- Deceleration: q = Σ:Σ/3 + ½Ω_m(1+tr P/E) − Ω_Λ; dln h/dη = −(1+q), h=H/H_i.
- Σ′, N′, A′ keep their R109 form; Codazzi and π contain no Λ.
- Ω_Λ(η) = Ω_Λ,i/h(η)² exactly, equivalently Ω_Λ′ = 2(1+q)Ω_Λ.
- Gauss-reduced deceleration uses Ω_m,geo = 1−Σ:Σ/6−K−Ω_Λ.

SymPy confirms dlnH/dη+1+q=0, the flat Gauss identity, Ω_Λ=Ω_Λ,i/h² and
Ω_Λ′=2(1+q)Ω_Λ for radiation+dust+Λ FLRW (`T5_lambda_raychaudhuri`, all
residuals 0). Constraint propagation I-(1.29) is unchanged because Λ is
conserved.

### D7 · Universality from Lie data (Q5)

1. Every R109 evolution and transport operator is a polynomial in (Σ, N, A, W)
   and the matter moments: curvature from Koszul (I-(1.3), (1.5)), Codazzi map
   I-(1.7), evolution I-(1.25), photon generator II-(1.25)–(1.26), Jacobian
   II-(1.29). A Bianchi type is therefore an initial condition, not a code path.
2. Type is a dynamical invariant: N=PN₀Pᵀ, A=(det P)P^{−T}A₀ (I-(1.26)) preserve
   rank and inertia of N, the vanishing of A, and h=A²/Δ (I-(1.27)), including
   h=−1/9. Certificate: `BianchiGroup::classify` and κ=1/h are constant along a
   numerical history for every family and for randomly rotated Lie data (V10).
3. Proper rotations act covariantly: rotating (Σ,N,A), material velocities and
   the observer velocity by R maps the observed screen field as
   F_R(n) = R F(Rᵀn) Rᵀ. With replay this is testable pointwise at arbitrary
   directions, without Wigner matrices (V11).

### D8 · Anisotropic effective-atom source (Q6)

*Escape.* For a homogeneous flow with velocity-gradient tensor K=H(I+Σ), the
Lyα Sobolev depth along e is τ_S(e)=τ₀/(1+Σ:ee), τ₀ the isotropic value, and
the direction-averaged escape probability is P̄=⟨(1−e^{−τ_S})/τ_S⟩. Exactly,

    P̄ = 1/τ₀ + ⟨Σ:ee⟩/τ₀ − ⟨e^{−τ_S}/τ_S⟩ = 1/τ₀ − ⟨e^{−τ_S}/τ_S⟩,

because ⟨Σ:ee⟩=tr Σ/3=0. **Lemma.** If λ_min(Σ)>−1, the shear correction to the
thick-limit escape rate vanishes to all orders in Σ, and the remainder is bounded
by e^{−τ₀/(1+λ_max)}·(1+λ_max)/τ₀. Numerically the identity holds to
3.2×10⁻¹⁵ and |P̄τ₀−1|≤1.0×10⁻¹⁵ for τ₀≥3×10³ over six random shears with
|λ|≤0.7 (`T7_sobolev_escape_lemma`). Recombination therefore sees the shear
through H(η), the radiation field and the matter density, not through the
optically thick escape rate. If λ_min(Σ)≤−1 a direction is contracting and the
Sobolev reduction is not applicable (fail closed).

*Photoionization and line occupation.* For a sky that is Planckian per direction
with temperature T(e) (exact for free streaming from isotropic Planck initial
data, II-(1.28)), the n=2 photoionization rate and the blue-wing Lyα occupation
are direction averages of Wien factors ⟨exp(−E/kT(e))⟩ (escape-weighted with
w(e)=1+Σ:ee for the line). With T=T̄(1+δ), ⟨e^{−x/(1+δ)}⟩/e^{−x} = 1 +
x⟨δ⟩ + (x²/2−x)⟨δ²⟩ + O(δ³), x=E/kT̄. For x=13.1 (Balmer edge at z≈1100) the
second-order formula is accurate to 8×10⁻⁶ relative at δ=10⁻⁵ but misses 9.6% at
a quadrupole amplitude 0.1, and 50% at x=39 (Lyα) (`T7_directional_wien_jensen`).
The anisotropic source must therefore evaluate the direction average itself
(a nonperturbative Jensen effect), not a monopole temperature.

### D9 · Closed-form oracles for high-ℓ tests

- FLRW, static observer: a_{ℓm}=0 for ℓ≥1 at every multipole.
- FLRW, boosted observer: D3, all ℓ, T only; E=B=0.
- Bianchi I with constant Σ=diag(s) (prescribed nodes): for observed
  propagation direction e_N, u_i=e_{N,i}e^{Δη s_i}, ln E/E₀ = −Δη − ln|u|, so
  T(n)=|u(−n)|⁻¹/⟨|u|⁻¹⟩−1 at every ℓ (R109 test formula).

### D10 · Meaning of the output

Unchanged from R109 R8: for one history, orientation and observer the output is
the deterministic mode product D^{XY}_{ℓm}=a^X_{ℓm}a^{Y*}_{ℓm} with
D_{ℓ,−m}=D*_{ℓm} and C_ℓ=(2ℓ+1)⁻¹Σ_mD_{ℓm}; a centered covariance requires a
probability law. The replay extends the multipole range, not the statistical
meaning.

## Phase 7 · Verification design

| ID | Test | Pass | Kill |
|---|---|---|---|
| V1 | Default BE path unchanged | all R109 tests pass; R109 example outputs byte-identical | any diff |
| V2 | Recorded events cover every collision of the accepted step | event count equals cells (+recoil trials) | missing or extra events |
| V3 | Replay of forward rays | final coherency equal to forward ≤1×10⁻¹⁵ relative (bitwise expected) | >10⁻¹² |
| V4 | Backward trace + forward replay landing error | ≤10⁻⁹ | >10⁻⁶ |
| V5 | Ring SHT vs R109 `analyze` on identical samples | ≤10⁻¹² relative | >10⁻⁹ |
| V6 | FLRW static/boosted observer to ℓ=40 | static ≤10⁻¹⁴; boosted vs D3 oracle ≤10⁻¹⁰ | >10⁻⁸ |
| V7 | Bianchi I constant Σ map at ℓ≤40 | second-order convergence to D9 | order <1.5 |
| V8 | Low-ℓ agreement LoS vs forward Lagrangian | ≤ forward quadrature error, decreasing with mesh | grows with mesh |
| V9 | SDIRK2 vs BE time convergence (scattering, recoil, tilt) | SDIRK2 ratio ≈4, BE ≈2 per halving | SDIRK2 ratio <3 |
| V10 | Type/h invariance along histories, 12 families + rotated data | classification constant; relative h drift ≤10⁻¹⁰ | change of type |
| V11 | Map-level rotation covariance with replay | ≤10⁻¹⁰ | >10⁻⁸ |
| V12 | ΛCDM FLRW h(η) vs closed form; Gauss residual | second order | order <1.5 |
| V13 | REC anisotropic source: isotropic limit equals HYREC-2 TLA source; lemma; Jensen sign | ≤10⁻¹⁴ isotropic | any sign violation |

## Phase 8 · Decision gate

| Candidate | Decision | Reason |
|---|---|---|
| H1a Lagrangian refinement for high ℓ | REJECT | cost and uncontrolled aliasing |
| H1b high-L hierarchy | HOLD (external comparator) | separate closure error |
| H1c replay line of sight | PROMOTE | D1–D3; V3–V8 |
| H2b ring transform | PROMOTE | D4; V5 |
| H3b ETD2 | REJECT | violates the encounter invariant in the stiff limit (D5) |
| H3c SDIRK2 | PROMOTE (opt-in) | D5; default stays BE for R109 reproducibility |
| H4b internal Ω_Λ | PROMOTE | D6; V12 |
| H5 certificates | PROMOTE | D7; V10–V11 |
| H6b anisotropic effective-atom source (REC) | PROMOTE as pointwise library | D8; V13. Coupling into a BASS x_e history: HOLD (needs an absolute T anchor and He) |

## Phase 9 · Survivor formalization (implementation contract)

1. `CollisionEvent{depth, beta, gain_map, scheme, sources}` is emitted by every
   collision cell; BE has one source, SDIRK2 two.
2. `StepRecord{left,right,first,second}` stores the accepted step only (the
   active predictor is not recorded).
3. `replay(records, e₀)` applies first-half events, `advance_ray(l,r)`,
   second-half events, starting from the unit isotropic coherency ½P(e₀).
4. `trace_back(records, e_N)` applies `advance_ray(r,l)` in reverse order.
5. `los_sky(records, β_o, N_θ, N_φ)` evaluates D3 on a GL×φ observer grid in
   parallel, normalizes T,Q,U exactly as R109 `observed_sky`, and returns ring
   samples for `analyze_rings`.
6. CLI: `--los-lmax L [--los-ntheta --los-nphi]`, `--collision
   backward-euler|sdirk2`, `--omega-lambda Ω_Λ,i`; outputs `los_modes.tsv`,
   `los_cl.tsv` with the R109 column schema.
7. REC: `rec_microphysics::anisotropic` with the escape average, Wien
   averages, mixture Compton temperature and an anisotropic HYREC-2 TLA source.

## Phase 10 · Closeout

- Confirmed (derivation + check): D1, D3, D4 equivalence, D5 (ETD2 failure,
  SDIRK2 properties), D6, D8 lemma and Jensen amplification, D9 oracles.
- Negative result kept: ETD2 with linear source interpolation is not
  asymptotic-preserving for moving electrons (encounter invariant).
- Open: global order of the full split scheme (V9, measured in the coding
  loop); He and Compton-heating coupling of a native anisotropic recombination
  history; z<4 REI physics; H=0 turnaround charts.

## References

- A. Challinor, Phys. Rev. D 62, 043004 (2000), arXiv:astro-ph/9911481.
- A. Pontzen and A. Challinor, MNRAS 380, 1387 (2007), arXiv:0706.2075.
- H. van Elst and C. Uggla, Class. Quantum Grav. 14, 2673 (1997), arXiv:gr-qc/9603026.
- S. Hervik, R. van den Hoogen, W. C. Lim, A. Coley, Class. Quantum Grav. 25, 015002 (2008), arXiv:0706.3184.
- R. Alexander, SIAM J. Numer. Anal. 14, 1006 (1977), doi:10.1137/0714068.
- J. I. Castor, MNRAS 149, 111 (1970); G. B. Rybicki and D. G. Hummer, ApJ 219, 654 (1978).
- Y. Ali-Haïmoud and C. M. Hirata, Phys. Rev. D 83, 043513 (2011); N. Lee and Y. Ali-Haïmoud, Phys. Rev. D 102, 083517 (2020).
- J. D. Barrow, R. Juszkiewicz, D. H. Sonoda, MNRAS 213, 917 (1985); J. D. McEwen et al., MNRAS 369, 1858 (2006).
- HEALPix conventions: https://healpix.sourceforge.io/html/intro_HEALPix_conventions.htm
