# R113 theory loop: one Lie-generated 1+3 PSTF engine for nonperturbative C_lm^XY

Base: BASS `40626723b` (R112), REC `3752213` (R112), REI `503508f` (R112),
htt_base `e810a4f7` (R112 record). Conventions are those of
`research/r109_native_sky/NATIVE_SOLVER.md` and R110 `THEORY.md`: signature
(-,+,+,+), right-handed orthonormal normal tetrad, epsilon_123 = +1, e-fold clock
eta = ln(a/a_emit), Hubble-normalized Sigma = sigma/H, N, A, Omega (frame
rotation), structure constants C^k_ij = epsilon_ijl N^lk + A_i delta^k_j - A_j delta^k_i,
photon propagation direction e, outward sky direction n = -e, HEALPix spin
convention Q +- iU = -sum (E +- iB) _{+-2}Y. Labels "II-(name)" refer to the
equation labels of Dossier II (`volume_II.tex`, Kinetic Transport, 14 Oct 2026);
"I-(x)" to Dossier I.

Numbers quoted as results come from files written by the R113 runs
(`RESULTS/*.json`); this document states derivations, design and acceptance.

## Phase 1 - Contract

**Question.** Which formulation lets the original BASS Rust core generate the
deterministic mode products D^XY_lm = a^X_lm conj(a^Y_lm) (X,Y in {T,E,B}) for
every Bianchi Lie algebra (I-IX, VI_h, VII_h, III, IV, V, exceptional VI*_-1/9),
with finite material tilt and an observer (local) boost, nonperturbatively in the
background anisotropy, such that the Bianchi type enters only through constants
fed to one set of Lie-generated 1+3 covariant PSTF (spin-harmonic) equations?

R109-R112 already evolve the Einstein equations from Lie data and transport
polarized radiation on Lagrangian rays (`homogeneous_sky`). The original
multipole code paths are per type or per class (`kinetic/hierarchy.rs`:
Bianchi I only; `kinetic/typev.rs`: type V; `tilted_hier.rs`: geometry from
per-type Python closed forms; Python `charts/class_a.py`, `class_b.py`,
`class_b_tilted.py`, `exceptional.py`, `type_ix_d.py`). No Rust code evolves
the PSTF/spin-harmonic radiation hierarchy of Dossier II for a general Lie
algebra, and the radiation sector has photons only.

**Sub-questions.**
- Q1. Which finite set of "type constants" determines every geometric operator,
  and how are they generated from the Lie algebra?
- Q2. What is the exact spin-harmonic (equivalently PSTF) free-streaming
  generator for arbitrary (Sigma, N, A, Omega), and how is it validated
  independently of its own derivation?
- Q3. How are Thomson collisions with moving electrons represented in the
  harmonic basis without losing the encounter invariant, energy-momentum
  exchange with the host, or the stiff limit?
- Q4. How does the harmonic route couple to Einstein, tilted matter and a
  collisionless neutrino sector, and give C_lm^XY at arbitrary l?
- Q5. Which exact quantities separate a local (observer) boost from a global
  (material) tilt?
- Q6. How is the hydrogen history made to respond to the anisotropic sky and
  expansion (REC), with an exact FLRW identity?

**Out of scope.** Spatially inhomogeneous perturbations and their ensemble
covariance; frequency-resolved transport and Compton redistribution; H=0
turnaround; astrophysical z<4 reionization sources (REI keeps the R112
explicit-tail interface).

**Evidence standard.** Promotion needs (i) a derivation from a cited equation
and (ii) an executable check with a stated tolerance that does not reuse the
derivation it checks (for the hierarchy: the exact characteristic map
`advance_ray` of R109).

**Completion bar.** Every Q has a surviving formulation, a rejected alternative
where one was considered, and a pass/kill test executed in the coding loop.

## Phase 2 - Evidence

| Source | Used for |
|---|---|
| Dossier I (1.2), (1.5)-(1.7), (1.14), (1.23)-(1.27) | commutators, curvature, Codazzi, Gauss with Lambda, evolution, congruence invariance of type and h |
| Dossier II ii:commutator, ii:connection_divergences, canonical table | all eleven types from (N, a) with N a = 0 |
| Dossier II ii:photon_characteristic, ii:screen_generator, ii:coherency_transport | photon characteristic R, V, screen generator g |
| Dossier II ii:hodge_potentials | V = grad U + J grad Z, degree <= 2 potentials |
| Dossier II ii:gaunt_prefactor, ii:gaunt_gradient, ii:gaunt_rotation, ii:spectral_hierarchy | exact spin-harmonic kernels |
| Dossier II ii:kernel_parity, ii:rigid_rotation_limit, ii:isotropic_curvature_phase, type-V example | parity and three closed-form limits |
| Dossier II ii:thomson_pstf, ii:boosted_thomson, ii:thomson_carrier, ii:weighted_thomson | rest and moving-electron Thomson operators, rank-9 carrier |
| Dossier II ii:bolometric_PSTF_moments, ii:pstf_harmonics | rho, q, pi from I_0, I_a, I_ab; PSTF <-> harmonic maps |
| R109-R112 BASS | `advance_ray`, `scatter_kernel` (BE/SDIRK2), `recoil`, `replay`, `radiation_feedback::advance_mixture_with_options`, `tilted_dust`, `sky_spectrum` |
| R112 REC | `anisotropic_two_temperature_source`, `matched_hydrogen_rhs` |
| Literature | Goldberg et al. 1967 (spin harmonics); Varshalovich et al. 1988 (3j, Racah formula); Hu & White 1997 and Challinor 2000 (total-angular-momentum and covariant polarized hierarchies); Pontzen & Challinor 2007 (Bianchi polarization); Ellis & MacCallum 1969, Wainwright & Ellis 1997 (orthonormal frames, types); Misner 1968 and Stewart 1969 (collisionless neutrino stress in anisotropic expansion) |

## Phase 3 - Claim-source audit

| Claim | Source | Status |
|---|---|---|
| Free photon transport has coupling width abs(l-l') <= 2 in the normal frame | ii:hodge_potentials | SUPPORTED |
| The kernels G, K_grad, K_J reproduce the characteristic | ii:gaunt_* | SUPPORTED as derivation; R113 adds an independent numerical generator check (V3) |
| Type and h are invariant along the exact evolution | I-(1.26)-(1.27) | SUPPORTED; R110 certificate |
| Rest-electron BE closure equals the PSTF Thomson matrix on l<=2 | ii:thomson_pstf, R109 `implicit_stage` | INFERENCE, derived in D5, tested V6 |
| Collisionless radiation gives pi/rho = -(8/15) int Sigma d eta at first order in Bianchi I | derived D7 | INFERENCE, tested V9 |
| The radiation energy frame nulls the bolometric dipole exactly | derived D8 | INFERENCE, tested V10 |

## Phase 4 - Hypothesis space

| Gap | Candidates |
|---|---|
| G1 type constants (Q1) | H1a per-type closed forms (status quo of the original code); **H1b** Lie data (Sigma, N, A, Omega) and their degree-<=2 potentials as the only type input |
| G2 radiation representation (Q2) | H2a Lagrangian rays only (R109); **H2b** Galerkin spin-harmonic hierarchy with Lie-generated Gaunt coefficients; H2c Cartesian-component scalar expansion of the 3x3 coherency |
| G3 collisions (Q3) | H3a exact Gaunt expansion of the boosted operator; **H3b** pseudo-spectral: synthesize on a Gauss-Legendre grid, apply the R109/R110 electron-rest closure (BE/SDIRK2, recoil), project back |
| G4 neutrinos (Q4) | H4a viscous-fluid closure; **H4b** kinetic collisionless massless species in the same representation |
| G5 high l (Q4) | H5a raise the hierarchy L; **H5b** record the rest-frame collision sources of either route and replay along exact backward characteristics (R110) |
| G6 boost/tilt split (Q5) | H6a numerical dipole-nulling root; **H6b** radiation energy frame from the T^ab eigenproblem |
| G7 recombination (Q6) | H7a absolute Peebles integration; **H7b** matched differential step on top of a reference history, implicit in x_p |

## Phase 5 - Adversarial review

- H1a. The original per-class charts are gauge fixed (Wainwright-Hsu, Hewitt-
  Wainwright kappa, Hervik variables); every new physical sector needs a new
  derivation per chart, and the exceptional VI*_-1/9 branch and the tilted class
  B charts have different variable sets. Rejected for new physics; retained as
  legacy oracles.
- H2a alone cannot certify itself: the replay, the forward solve and the
  analysis share the characteristic integrator. An Eulerian discretization with
  an independent error structure is needed for cross-validation. Kept as route 1.
- H2b attack: kernel sign conventions (spin phase, eth sign, dyad orientation)
  are easy to get wrong and would still conserve energy. Answer: the kernel matrix
  is tested against a finite-difference generator built from `advance_ray`
  (exact R109 characteristic, independent code) on a random band-limited polarized
  field for random Lie data (V3); a sign error fails at O(1).
- H2b attack: Galerkin truncation at L is not positivity preserving and loses
  focused structure (VII_h at late times). Answer: truncation error is measured by
  L refinement and by the replay comparison (H5b) at l <= L/2; positivity of the
  synthesized grid sky is checked at every collision.
- H2c needs six scalar fields and does not preserve transversality e.F = 0 under
  truncation. Rejected.
- H3a needs the Gaunt expansion of D^-3 J^-1 S M S J^-T: infinitely many terms
  for finite beta. Rejected.
- H3b attack: projection after each collision step leaks power above L.
  Answer: at beta = 0 the gain is band-limited to l <= 2 and the step is exact
  (D5); at finite beta the leak is the Galerkin error, measured. l = 0,1 are
  analyzed by the same quadrature that defines energy and momentum, so the
  host recoil balance is exact.
- H4a cannot represent the free-streaming anisotropic stress of collisionless
  radiation (it has memory, D7). Rejected.
- H5a costs O(L^2) states per step; the observed l is limited by the state.
  Kept only for low-l cross checks.
- H6a depends on the observable definition (T = I^(1/4) vs I) and needs a root
  search. H6b is exact for the bolometric I dipole and independent of l. H6a is
  kept as a diagnostic.
- H7a inherits the percent-level Peebles-vs-HYREC difference into the absolute
  history. H7b attack: the reference and anisotropic states must be matched in
  clock and density. Answer: both are evaluated on the same BASS step, and the
  FLRW identity is exact by construction (D9).

## Phase 6 - Physics and mathematics validation

### D1 - Type constants from the Lie algebra

With [e_i, e_j] = C^k_ij e_k (I-(1.2)), the Jacobi identity reduces to N A = 0.
The Koszul formula ii:spatial_connection gives the spatial connection
Gamma^k_ij = (C^k_ij - C^i_jk + C^j_ki)/2, the Ricci tensor and the Codazzi map
D_j sigma^j_i = -3 Sigma_ij A_j - epsilon_imn N_mb Sigma_bn (ii:connection_divergences).
Under the exact evolution N -> P N P^T, A -> det(P) P^-T A with
P = exp[d eta (Sigma + W + q I/2)] (I-(1.26)); rank and inertia of N, the vanishing of A
and h = A^2/(n_2 n_3) are invariant (I-(1.27)). Hence a Bianchi type is a choice
of initial (N, A) up to rotation, and every operator below is a polynomial in
(Sigma, N, A, Omega) and matter moments. The canonical representatives
(Dossier II table; III = VI_-1, VI* = VI_-1/9) are multiplied by a scale and
rotated by an arbitrary SO(3) matrix; rotations act covariantly (R110 V11).

The *type constants* of the photon sector are the spherical-harmonic
coefficients of four degree-<=2 potentials (next section). They are the only
place where the algebra enters the radiation equations.

### D2 - Potentials of the photon generator

From ii:photon_characteristic and ii:screen_generator in the Hubble-normalized
e-fold clock,

    R(e) = d ln E/d eta = -1 - Sigma:ee,
    g(e) = Omega + A x e + N e - (tr N/2) e - e x (Sigma e),   V = g x e,
    V = grad U + J grad Z,  J X = e x X,
    U = -(1/2) Sigma:ee - A.e,     Z = -(1/2) N_TF:ee - Omega.e,
    omega = g.e = Omega.e + N_TF:ee - (tr N)/6.

Direct check: grad(Sigma:ee) = 2[Sigma e - (Sigma:ee) e], grad(A.e) = A - (A.e)e, and
e x grad Z = -e x N_TF e + Omega x e, so grad U + J grad Z = V term by term
(this is also the R109 `liouville_coefficients` vector field, which is the
truth used in V3). The harmonic content is

| potential | L = 0 | L = 1 | L = 2 |
|---|---|---|---|
| R | -sqrt(4 pi) | 0 | -Sigma_2M |
| U | 0 | -A_1M | -(1/2) Sigma_2M |
| Z | 0 | -Omega_1M | -(1/2) N_TF,2M |
| omega | -sqrt(4 pi) tr N/6 | Omega_1M | N_TF,2M |

where v_1M and X_2M denote the Y_LM coefficients of v.e and X:ee. Class A
algebras differ only through tr N (an isotropic screen phase) and N_TF (a
divergence-free twist of order 2 plus a screen phase); class B adds the order-1
gradient potential -A.e, i.e. a dipolar flow towards -A that focuses rays
(divergence 2A.e, ii:angular_jacobian). The exceptional VI*_-1/9 branch has no
special term: the potentials are regular for every h.

### D3 - Exact spin-harmonic hierarchy

For the bolometric (k = 4) carrier, integrating ii:spectral_hierarchy against
E^3 dE replaces -R E d_E by +4R (boundary terms vanish for finite moments).
With p_0 = I, p_+-2 = Q +- iU in the propagation-direction dyad and
p_h = sum a^h_lm _hY_lm,

    d_eta a^h_lm = sum_{LM, l'm'} [ 4 R_LM G^h - U_LM K_grad^h - Z_LM K_J^h
                                    + i h omega_LM G^h ]_{lm,LM,l'm'} a^h_l'm' + c^h_lm,

with G, K_grad, K_J from ii:gaunt_prefactor-ii:gaunt_rotation. Selection rules:
abs(l - l') <= L <= 2, m' = m - M, so each row has at most 25 entries. The
isotropic part 4 R_00 G = -4 is integrated exactly as a factor exp(-4 d eta).
Parity (ii:kernel_parity, eta_p = (-1)^(l+L+l')) fixes the E/B structure: the
class-B dipole (L = 1) converts E <-> B at equal l (eta_p = -1) and couples
E->E, B->B at l' = l +- 1; the N_TF twist (L = 2) converts E <-> B at l' = l +- 1.
Exact limits: Omega = Omega_z z: d_eta a = -i m Omega_z a (ii:rigid_rotation_limit);
N = n_c I: d_eta a^h = -i h n_c a^h/2 (ii:isotropic_curvature_phase); type V
a = A z: same-mode advection +-A/3 at (l,m) = (2,1) for h = +-2 (Dossier II).
The truncated system sets a_l'm' = 0 for l' > L (Galerkin).

The internal analysis/synthesis uses the R109 `sky_spectrum` Wigner columns
_sY_lm = (-1)^s sqrt((2l+1)/4pi) d^l_{m,-s}(theta) e^{i m phi} (Goldberg) with the
same E/B combination, so a^+-2 = -(E +- iB); the observed sky is produced by
the same `observed_sky` and analysis code as the ray route.

### D4 - Representation-independent quantities

ii:bolometric_PSTF_moments: rho = 4 pi I_0, q_a = (4pi/3) I_a, pi_ab = (8pi/15) I_ab.
In harmonic coefficients these are the l <= 2 scalar coefficients; on the
Gauss-Legendre grid they are the quadrature sums that also define the ray
route's moments, so the Einstein source is the same functional of the field.

### D5 - Collisions in the harmonic basis

The pseudo-spectral collision synthesizes the coherency on an N_theta x N_phi
Gauss-Legendre grid (weights w_i, sum 4 pi), applies the R109/R110 electron-rest
cell (BE or SDIRK2 closure of the six-component source S, optional gain map,
recoil iteration on the host stream) and analyzes back to l <= L.

*Lemma (rest electrons).* For beta = 0 and a band-limited input (l <= L) on a grid
exact for polynomials of degree L+2 (N_theta >= L+3, N_phi >= 2L+6), the step is
exact: the closure integrals are exact, the gain P(e) S P(e) has scalar part
tr S - e.Se (l <= 2) and tensor part TT_e S (l = 2), and the projection returns
the BE solution of ii:thomson_pstf:
I_0 unchanged, I_l -> I_l/(1+tau) (l = 1, l >= 3), (I_2, E_2) -> (1 - tau A_2)^-1 (I_2, E_2),
E_l, B_l -> /(1+tau) otherwise, with A_2 = [[-9/10, -3/5],[-1/10, -2/5]] in the
Dossier E sign. Tested in V6.

*Moving electrons.* D^-3 J^-1 S M S J^-T is not band-limited; the projection is the
Galerkin error. The l = 0,1 coefficients are the same quadrature sums that the
recoil step uses for the photon energy and momentum change, so the host kick and
the energy defect ledger are unchanged.

*Stiffness.* The cell is the same L-stable implicit closure as the ray route;
the encounter invariant (R110 D5) holds on the grid.

### D6 - Time splitting and records

Each e-fold step is C(1/2) S(1) C(1/2): collision half steps at the left and right
nodes and free streaming between them. Streaming integrates D3 with classical RK4
on substeps with linearly interpolated potentials, after the exact isotropic
factor. With SDIRK2 every part is second order. Every collision cell emits the
R110 `CollisionEvent` (depth, beta, gain map, stage sources); the replay theorem
(R110 D1) applies unchanged because a recorded cell acts on a single ray through
its rest-frame source tensor only. Hence the harmonic route also yields all l by
backward characteristics, and its replay at l <= L/2 measures the hierarchy
truncation (V8).

### D7 - Collisionless neutrinos

A massless collisionless species obeys the same characteristic with c = 0 and
p_+-2 = 0. It carries energy fraction f_nu of the initial radiation and enters
Einstein through its own E, q, P. In Bianchi I at first order in Sigma, with an
initially isotropic distribution, I(e) = I_0 exp(-4 eta)[1 - 4 e.Psi.e],
Psi = int_0^eta Sigma, since direction drift is second order. With
<e_i e_j e_k e_l> = (delta_ij delta_kl + 2 delta_i(k delta_l)j)/15,

    pi/rho = -(8/15) Psi,
    Sigma' = (q - 2) Sigma - (8/5) Omega_coll Psi,   Psi' = Sigma.

In radiation domination (q = 1) with all radiation collisionless (Omega_coll = 1),
Sigma'' + Sigma' + (8/5) Sigma = 0: oscillatory decay ~ exp(-eta/2), not the
fluid law exp(-eta). The free-streaming stress is a restoring force with memory
(H4a cannot represent it). Tested in V9 against the active solver with and
without neutrinos.

### D8 - Energy frame, local boost and global tilt

For a radiation stress tensor with normal-frame (rho, q, P) the energy frame
u_E = gamma(n + beta) solves T^a_b u^b = -rho_E u^a, i.e.

    rho_E = rho - q.beta,   beta = (q - P beta)/(rho - q.beta).

For a boosted isotropic sky (rho = rho'(4 gamma^2 - 1)/3, q = (4/3) rho' gamma^2 beta,
P = rho'[(4/3) gamma^2 beta beta + I/3]) the root is the boost itself. In u_E the
bolometric flux, hence the I dipole, vanishes exactly. For an observer with velocity
beta_o (normal frame), the *local boost* is the relative velocity of beta_o with
respect to u_E (Einstein subtraction); the *global tilt* is the velocity of each
matter stream relative to the normal congruence and to u_E. These are exact,
l-independent and computed from the final state of either route.

### D9 - Matched recombination step (REC)

With a reference hydrogen history x_ref(eta) on the same clock and the pointwise
REC rate r(x; sky, H, n_H, T_m) per proper second,

    x_{n+1} - x_n = [x_ref,n+1 - x_ref,n]
                  + d eta [ r_ani(x_{n+1}) / (gamma H) - r_iso(x_ref,n+1) / H_ref ].

In FLRW (isotropic sky at the reference temperature, gamma = 1, H = H_ref, matched
n_H) the root is x_{n+1} = x_ref,n+1 exactly, for every step size. The equation is
monotone in x_{n+1} in the stiff Saha regime and is solved by safeguarded
Newton-bisection on [0, 1]. This is the R112 `matched_hydrogen_rhs` made implicit.

## Phase 7 - Verification design

| ID | Test | Pass | Kill |
|---|---|---|---|
| V1 | R112 defaults unchanged (CLI cases incl. LoS, tracer, ionization) | byte-identical TSV | any diff |
| V2 | Lie constants: classification and h of rotated canonical data for all 12 families; potentials reproduce R, U, Z, omega pointwise | type equal; pointwise <= 1e-13 | any mismatch |
| V3 | Hierarchy matrix vs finite-difference generator of `advance_ray` on a random band-limited polarized field, random class A and class B Lie data with rotation | relative <= 1e-6 | > 1e-3 |
| V4 | Closed limits: rigid rotation, N = n_c I phase, type V +-A/3 | <= 1e-12 | > 1e-8 |
| V5 | Spin SHT round trip and agreement with `sky_spectrum::analyze_rings` | <= 1e-12 | > 1e-9 |
| V6 | Rest-electron harmonic collision vs PSTF BE closed form | <= 1e-12 | > 1e-9 |
| V7 | Harmonic route vs ray route, same physics, 12 families + FLRW, l <= 4 | difference decreases with L and mesh | grows |
| V8 | Harmonic-route replay vs direct harmonic output at l <= L/2 | decreases with L | grows |
| V9 | Bianchi I collisionless stress vs D7 ODE | relative <= 1e-2 at Sigma ~ 1e-3 | sign or rate wrong |
| V10 | Energy frame of a boosted isotropic sky; I dipole zero in u_E | <= 1e-12 / <= 1e-10 | larger |
| V11 | Neutrinos conserve energy; FLRW H = exp(-2 eta) with f_nu | <= 1e-12 | larger |
| V12 | REC matched step: FLRW identity for any step | <= 1e-14 | larger |
| V13 | REC matched step with anisotropic sky: finite, in [0,1], converges first order in d eta | ratio ~2 | nonmonotone |

## Phase 8 - Decision gate

| Candidate | Decision | Reason |
|---|---|---|
| H1b Lie type constants | PROMOTE | D1-D2; V2 |
| H2b spin-harmonic hierarchy | PROMOTE (route 2) | D3; V3-V5, V7 |
| H2a ray route | KEEP (route 1, default) | R109-R112 evidence |
| H2c Cartesian components | REJECT | transversality, cost |
| H3b pseudo-spectral collisions | PROMOTE | D5; V6 |
| H3a Gaunt boosted collisions | REJECT | non-polynomial kernel |
| H4b kinetic neutrinos | PROMOTE | D7; V9, V11 |
| H5b replay for both routes | PROMOTE | D6 |
| H6b energy frame | PROMOTE | D8; V10 |
| H7b matched REC step | PROMOTE as REC library + BASS opt-in | D9; V12-V13 |

## Phase 9 - Implementation contract

1. `geom::lie`: canonical algebras (all families, scale, rotation), invariants,
   `photon_potentials(node) -> [R, U, Z, omega]_LM` (complex, L <= 2).
2. `kinetic::wigner`: Wigner 3j (Racah, log-factorial), Gaunt kernels of D3.
3. `kinetic::spin_sht`: Gauss-Legendre ring synthesis/analysis for s = 0, +-2 with
   the `sky_spectrum` columns.
4. `kinetic::lie_hierarchy`: kernel table for (L, spins), RHS from potentials,
   exact isotropic factor, RK4 substeps with interpolated potentials.
5. `homogeneous_sky::field`: radiation representation (rays | harmonic), synthesis to
   grid photons for collisions/observation, moments; neutrinos as a second
   collisionless field; general solver `solve::solve_general` with
   `SolveOptions {route, neutrino_fraction}`; legacy entry points delegate with
   defaults and keep their floating-point operation order.
6. `homogeneous_sky::frames`: energy frame, relative velocities, frame report.
7. CLI: `--route rays|harmonic --harmonic-lmax L [--harmonic-ntheta --harmonic-nphi]`,
   `--neutrino-fraction f`, `--observer-frame normal|host|spectator|radiation`.
8. REC: `rec_microphysics::matched_history::implicit_step` (D9).

## Phase 10 - Closeout

Filled in `README_KO.md` with the measured V1-V13 outcomes and the remaining
open items after the coding loop.

### Closeout record (appended after the coding loop)

Implementation against the Phase 9 contract. Items 1-7 are implemented as
specified (`geom::lie`, `kinetic::{wigner, spin_sht, lie_hierarchy}`,
`homogeneous_sky::{field, frames}`, `solve::solve_general` with `SolveOptions`,
CLI). Three deviations are recorded here rather than silently absorbed:

1. REC item 8 is `rec_microphysics::matched_history::implicit_matched_step` (REC
   commit `05db545`), with `anisotropic_peebles_rate` / `isotropic_peebles_rate`
   wrapping the R112 collapsed-Peebles closure. The root is found by a bracketed
   Illinois regula falsi on [0, 1 - 1e-12], not by Newton-bisection: G(x) =
   x - base - d eta (r(x)/(gamma H) - r_ref/H_ref) is increasing because the net
   Peebles rate decreases with x, so the bracket is valid and the TLA closure need
   not be differentiated. The REC-level FLRW identity of D9 is exact (V12: <= 1e-14
   for d eta = 1e-4 ... 50).
2. The BASS coupling goes beyond item 8: `SolveOptions::recombination:
   Option<MatchedRecombination {t_unit_k, n_h_emit_m3, h_emit_s}>`. The reference
   is the flat FLRW model with the run's initial Lambda fraction and matter fraction
   (T_ref = t_unit e^-eta, n_H,ref = n_H,emit e^-3eta, H_ref from the Friedmann
   constraint); the anisotropic side uses the transported sky in the Thomson host
   rest frame (`rec_bridge::material_directional_sky`, beta' by a one-step
   difference), the host proper density and the normal H of the evolved Einstein
   background. The hydrogen fraction is min(x_e,table, 1 - 1e-12) (helium electrons stay as
   tabulated; while the reference hydrogen is fully ionized the response is zero) and the matter temperature is the Compton temperature of the material
   sky. delta_x_e enters the Thomson cells of the next step through
   `Ionization::cells_with_offset` (first-order splitting); delta_x_e = 0 reproduces
   the table cells bit for bit (V1).
3. Because H and n_H of the BASS side come from the integrated background, the
   BASS FLRW gate is not the exact D9 identity: the offset is the response to the
   background truncation error and vanishes at second order in d eta (V12-BASS).
   The exact identity holds where the inputs are exact (REC test).

Decisions of Phase 8 stand. H7b is promoted as an REC library plus an opt-in BASS
coupling; its validity statement is the hydrogen-only collapsed-Peebles TLA with a
Compton matter temperature, matched to an FLRW HYREC table, at first order in the
coupling step.

Open items carried forward (not claims of this round): helium and matter
temperature as evolved variables in the matched step; second-order (Strang)
coupling of delta_x_e; spectral (non-bolometric) transport, which the bolometric
temperature of the material sky approximates once spectra mix; reionization
through REI rather than through the supplied table; a Gaunt-exact moving-electron
collision on the harmonic route (currently pseudo-spectral on the collision grid);
cost of the matched step (about 5x the table run on 576 directions, dominated by the
directional REC rate).

## References

- Dossier I-II (BASS, 14 Oct 2026), `htt_base/docs/solver_free_research_20261014/sources/dossier/`.
- J. N. Goldberg et al., J. Math. Phys. 8, 2155 (1967).
- D. A. Varshalovich, A. N. Moskalev, V. K. Khersonskii, Quantum Theory of Angular Momentum (1988).
- W. Hu and M. White, Phys. Rev. D 56, 596 (1997), arXiv:astro-ph/9702170.
- A. Challinor, Phys. Rev. D 62, 043004 (2000), arXiv:astro-ph/9911481.
- A. Pontzen and A. Challinor, MNRAS 380, 1387 (2007), arXiv:0706.2075.
- G. F. R. Ellis and M. A. H. MacCallum, Commun. Math. Phys. 12, 108 (1969).
- J. Wainwright and G. F. R. Ellis (eds.), Dynamical Systems in Cosmology (1997).
- C. W. Misner, Astrophys. J. 151, 431 (1968); J. M. Stewart, Astrophys. J. 157, 1 (1969).
