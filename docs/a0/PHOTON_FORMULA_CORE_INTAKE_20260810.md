# BASS Route A — photon formula-core intake

**Intake status:** `A0A_OWNER_REVIEW_CANDIDATE`

**Intake date:** 2026-08-10

**Purpose:** bind the newly supplied homogeneous polarized-photon formula package to the
Route A design without promoting formula evidence to solver, numerical, finite-tilt, or
observable-output readiness.

**Normative machine companion:** `contracts/a0/photon_formula_core_v1.json`

## 1. Exact received artifacts

| Artifact | Bytes | SHA-256 | Intake role |
|---|---:|---|---|
| `FORMULA_ATLAS_11_BRANCHES_FINAL.pdf` | 674218 | `93934e5ce714295d48e2f22d56fb7a05006038dceb54329123288a750b3f54b6` | Compact visual review surface only |
| `Bianchi_Polarized_Boltzmann_Core_SSOT_FINAL.pdf` | 577544 | `cd9b4e8e092faf9de580c7949ab5af296ed9449af112e01c0f4785ff9ed8045e` | Visual review surface only; not an equation carrier |
| `Bianchi_Core_Closure_Final.zip` | 40842695 | `5909b3cd5632245ecc794532c0f569a59c6ee5a0e741bb307001f1c4e3087a0e` | Full supplied closure/provenance package |
| `Bianchi_Core_Closure_Formula_Artifacts.bundle` | 1437849 | `de34f9b643e117f1f1078ce94a8c433d5e33f743a9daa856484c6c6ee537662e` | Durable formula-source snapshot used by this candidate |

The last artifact is preserved in this repository as
`artifacts/formula_core/Bianchi_Core_Closure_Formula_Artifacts_f63d5ae.bundle`.
`git bundle verify` reports a complete, prerequisite-free bundle history for its advertised
ref, with
`refs/heads/core-closure-final` at commit
`f63d5ae8faa2ea0c9afd2fee37fe2e7051cf16b0`, tree
`c2b9e910f4b2a9c0be726059e32cc8411f65cced`. A clean clone of that exact ref passes
`git fsck --full` and has no working-tree changes. The two received PDFs are byte-identical
to the corresponding release PDFs in the supplied ZIP.

“Complete” is restricted to that advertised bundled ref: it does not prove that the bundle
contains every ref or every object from the producer's original repository.

The full ZIP passed path-containment and CRC checks. Its own replay verifier reports 21
passing gates and 179 valid manifest rows. Those are package-integrity and internal replay
facts, not independent scientific reproduction.

The outer-ZIP SHA-256 above was computed at intake; no separate producer-signed or
producer-detached outer-ZIP hash accompanied the upload. A0B approval of the exact candidate
therefore explicitly adopts this intake-computed identity. It does not represent a producer
signature.

## 2. Exact scope accepted for planning

Subject to owner approval of the exact A0A candidate commit, the formula bundle is a
governed **project-derived formula input** for:

- homogeneous distribution-level photon Liouville transport in the normal frame;
- spectral and bolometric scalar PSTF hierarchies for Stokes `I` and `V`, all ranks
  `ell>=0`;
- spectral and bolometric polarized PSTF hierarchies for `E` and `B`, all ranks
  `ell>=2`;
- cold, non-tilted, elastic electron-rest Thomson collision multipoles;
- the PSTF/project-spin-Wigner dictionary;
- literal formula specialization to the eleven public Bianchi rows
  `I, II, III, IV, V, VI_0, VI_h, VII_0, VII_h, VIII, IX`;
- the exceptional `VI_-1/9` dynamical supplement, which is not a twelfth algebra type.

The package registry records 96 explicit equations and 824 atomic term/source rows. That
coverage specifies an infinite all-rank formula operator. It is not an `ell_max`
closure, finite state layout, numerical solver, Einstein-background module, line-of-sight
pipeline, or release claim.

The machine registry's generic text domain `VI_h: h<0` is not sufficient runtime dispatch.
Public `III` and public `VI_h` with exact `h=-1` use the same computational algebra but
must each round-trip with the originally requested label. Neither input canonicalizes the
other public label away. Exact `h=-1` therefore uses a label-preserving shared-kernel
dispatch, not the generic `VI_h` path.

Exact `h=-1/9` identity selection must route to the exceptional handler with
`registry_only=true`, never the generic `VI_h` path. A separate activation validator must
then enforce

\[
9A_1^2-N_{23}^2+N_{22}N_{33}=0,\qquad
N_{22}\Sigma_{12}+(N_{23}-3A_1)\Sigma_{13}=0.
\]

`Sigma13` and `Sigma23` remain independent where the constraint permits; diagonalizing
`n_B` does not authorize diagonal shear. The packaged witness gauge is a test fixture, not
the full exceptional branch. Algebraic-constraint and momentum-constraint failures require
independent negative tests, and a nonzero off-diagonal-shear fixture must be accepted.

The exact nonlinear polarized coefficients, the Bianchi-specific screen reduction, and the
all-rank Wigner equivalence have no single primary-source formula. They remain
`PROJECT_DERIVED` inputs that require independent reproduction from the primitive
screen-tensor operator before production promotion. [Challinor](https://arxiv.org/abs/astro-ph/9911481)
supplies the general-spacetime polarization tensor, exact electron-rest Thomson source, and
frame transformation, but its displayed multipole hierarchy is almost-FRW.
[Pontzen--Challinor](https://arxiv.org/abs/0706.2075) is a nearly-FRW Bianchi regression.
[Maartens--Gebbie--Ellis](https://arxiv.org/abs/astro-ph/9808163) anchors the exact nonlinear
scalar-intensity lane, not the completed polarized hierarchy.

## 3. Equation-carrier precedence and document defect

For implementation and review, formula bytes are read in this order:

1. checksum-addressed JSON equation/term registries in the formula bundle;
2. formula-source TeX/Markdown and theorem sources at bundle commit `f63d5ae8...`;
3. compact formula atlas for human cross-checking;
4. PDFs for visual review only.

The 45-page SSOT PDF is materially clipped at the right media edge on literal branch
equation pages, including PDF pages 17, 20, 43, and 44. A clean rebuild reports 83 overfull
boxes, with a maximum overflow of about 325.68 pt. Therefore the PDF must not be parsed,
copied, or cited as the coefficient authority. A later documentation gate must repair and
re-render it before it can be called a reliable formula deliverable. The compact atlas does
not remove the need to use checksum-addressed source for code generation.

## 4. Required convention and unit adapter

The formula core uses ray-length rates:

\[
\frac{1}{c}\partial_t X+\mathscr O_{L^{-1}}[X]=C_{L^{-1}}[X],
\qquad
[H_{\rm core}]=[\sigma_{\rm core}]=[\Omega_{\rm core}]
=[a^{\rm B}]=[n^{\rm B}]=[\kappa]=L^{-1}.
\]

The A0 background convention instead stores physical proper-time kinematic rates
`H_A0`, `sigma_A0`, and future `Omega_A0` in `s^-1`. The only permitted adapter is

\[
H_{\rm core}=\frac{H_{\rm A0}}{c},\qquad
\sigma^{\rm core}_{ab}=\frac{\sigma^{\rm A0}_{ab}}{c},\qquad
\Omega^a_{\rm core}=\frac{\Omega^a_{\rm A0}}{c}.
\]

The physical orthonormal-frame structure magnitudes `a_B`, `n_B` and opacity
`kappa=n_e sigma_T` remain in `m^-1`. Multiplying the hierarchy by `c` gives the
proper-time rates `c a_B`, `c n_B`, and `c kappa` in `s^-1`. A registry's dimensionless
canonical Lie-algebra fingerprint must never be substituted for these physical inverse-
length magnitudes.

The bolometric map is applied exactly once and only under the declared endpoint condition:

\[
[\epsilon_\gamma X_{A_\ell}]_0^\infty=0,
\qquad \mathcal D_\epsilon\mapsto-1,
\qquad H_{\rm core}(3-\mathcal D_\epsilon)\mapsto4H_{\rm core}.
\]

This gives the low-rank scalar shear coefficient
`(ell+1-D_epsilon) -> +(ell+2)`. The package's `CC12-SA-001` amendment of the printed
final sign in MGE Eq. (71) stays explicit in every ledger and negative test; it is never
silently normalized away.

That coefficient map is not yet the physical-moment adapter. The hatted hierarchy
variables are bare energy integrals. A5A must freeze
`Delta_ell=4*pi*2^ell*(ell!)^2/(2*ell+1)!` and
`mathscr X_Aell=Delta_ell*Xhat_Aell/c`. For intensity this gives
`rho_gamma=mathscr I_0`, `q_gamma_a=mathscr I_a`, and
`pi_gamma_ab=mathscr I_ab`, while physical SI energy flux is `F_a=c*q_gamma_a`.
`q_gamma_a` and `F_a` must never share a unit/type. Temperature multipoles require an
explicitly declared blackbody or perturbative spectral submanifold.

## 5. Photon V decision

Photon `V` is restored to `IN_V1_REQUIRED` as a scalar PSTF radiation sector. In
particular, the Bianchi V specialization has `a_B=A u_(1)`, `n_B=0` and the exact linear
equation

\[
\frac1c\partial_t V_{A_\ell}
+H_{\rm geom}(3-\mathcal D_\epsilon)V_{A_\ell}
+\mathcal S^{[\epsilon]}_{A_\ell}[V]
+\mathcal A^{(\mathrm B)}_{A_\ell}[V]
+\mathcal O_{A_\ell}[V]
=\kappa\left[-V_{A_\ell}+\frac12\delta_{\ell1}V_{A_1}\right].
\]

Thus nonzero initial or externally produced circular polarization can evolve and its
multipoles can be remapped by anisotropic redshift, shear, class-B direction flow, triad
choice, and a finite observer/electron-frame boost. A boost mixes angular ranks and energy
dependence but does not mix `V` with `I,Q,U`: the invariant spectral variables transform
within their own Stokes sectors in Challinor's exact frame law.

Under the Route A baseline assumptions--metric geometric optics plus cold,
unmagnetized/unpolarized-electron Thomson scattering--the operator is homogeneous in `V`.
It therefore does not generate `V` from `I/E/B`, and `V=0` is an exact invariant subspace
in every Bianchi branch, including tilted Bianchi V after the exact Lorentz pullback. Both
paths are required:

- a full `V` evolution lane for physically allowed nonzero initial/source data;
- an exact `V=0` invariant fast path and negative control for the standard baseline.

No claim that Bianchi geometry or tilt alone creates circular polarization is permitted.
Magnetized plasma, birefringence, parity-violating interactions, generalized Compton terms,
or other genuine `I/Q/U -> V` source physics requires a separate future scope decision.

## 6. Required downstream gates

The later implementation plan must preserve this sequence; A0B itself authorizes planning
only.

| Gate | Required result | Explicitly still absent |
|---|---|---|
| `A5A_FORMULA_INTAKE_ADAPTERS` | Clone/verify bundle; parse registries; freeze signs, spin, energy variable, ray-length/time and sky-direction adapters; type the occupation/radiance/bare-integral/normalized-PSTF/stress-energy chain including `Delta_ell/c` and `F_a=c q_a` | Production source |
| `A5B_DISTRIBUTION_PSTF_REPRODUCTION` | Independently project the primitive screen-tensor equation; reproduce scalar and polarized coefficients; check PSTF/Wigner equivalence | Finite hierarchy |
| `A5C_RADIATION_TRUNCATION_CONVERGENCE` | Choose spectral versus bolometric authority state, memory layout, `ell_max`, closure/guard band, endpoint conditions, stability and three-level convergence | Collision history and observables |
| `A6A_ELECTRON_REST_THOMSON` | Reproduce cold zero-tilt collision kernel, conserved/null sectors, `I_2 -> E_2`, no direct `B` gain, and exact `V=0` invariance | Finite electron tilt |
| `A6B_FINITE_TILT_PULLBACK` | Freeze `u_e=gamma_e(n+v_e)`, proper electron density, `epsilon_e=gamma_e epsilon_n(1-v_e dot e)`, relative-flux collision prefactor, aberration, screen/spin phase, invariant measure/Jacobian, and the energy-nonlocal electron-frame pullback; pass finite-, zero-, and independently derived small-tilt tests | Recombination/reionization |
| `A6C_VISIBILITY_HISTORY` | Couple validated recombination/reionization and freeze `tau_dot<=0`, `kappa_dot>=0`, `g=-tau_dot exp(-tau)` conventions | Line-of-sight/output readiness |
| `A7_DETERMINISTIC_OUTPUT` | Output-only local observer boost and sky-direction adapter | Statistics or inference readiness |

Minimum characterization includes Minkowski, FLRW, Bianchi I, Bianchi V class-B
direction flow, all eleven public rows plus `VI_-1/9`, collision conservation/nullspaces,
parity/reality, screen-gauge covariance, spectral/bolometric commutativity, exact `V=0`,
and a nonzero-`V` evolution witness.

`A5A` must also choose whether runtime input is a proper diagonal/branch-aligned chart or a
full-symmetric chart. Any proper rotation must act on `a_B`, `n_B`, `sigma`,
`Omega_triad`, and every PSTF multipole together. Improper frames fail closed unless an
explicit parity adapter for all affected quantities, including `B`, is implemented.

At A6B the boosted collision operator must not be treated as local in normal-frame photon
energy, and conservation may not be asserted shell by shell in that frame. The global
matter/electron tilt supplies `v_e`; a local observer output boost is a different adapter and
cannot substitute for the collision pullback.

## 7. Claims that remain forbidden

This intake does not authorize any of the following descriptions:

- full Einstein--Boltzmann solver or solver-ready;
- finite hierarchy closure or numerically mature;
- finite-electron-tilt complete;
- recombination/reionization, line-of-sight, or observable-output complete;
- full Compton, thermal/recoil, or Klein--Nishina complete;
- perturbation-, statistics-, likelihood-, or inference-ready;
- native end-to-end Wolfram replay completed in this environment.

The package reports hybrid plugin-assisted clean orchestration. It explicitly says that a
native `wolframscript` end-to-end replay was not executed there and that direct
`MakeTraceless` output was not the authority witness. Those qualifications propagate into
all future BASS receipts.
