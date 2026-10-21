# Independent matter–radiation anisotropic-stress pilot

Date: 2026-10-21 UTC. This is a new three-coordinate initial-data family. The completed common-amplitude 81-case pilot, its contract, and its outputs remain unchanged. This note derives the split and records **729 original-owner initializations only**; it does not report a new evolution or convergence result.

Owner: `cosmosapjw-quantum/rei_bianchi`, PR141, commit `80825585f9fe31d2ee0d5af545ada3fa1f52be72`. Source authority is the vendored C15 [`coupled.py`](../vendor/rei_c15/research/rei_c15_sigma_pi_feedback_20261015/coupled.py), specifically `Parameters`, `initial_moments`, `initial`, `massive_source_3moments`, `_physical`, and `rhs`. Exact source hashes, all 729 achieved initial states, and numerical checks are in [`SPLIT_INITIAL_REVIEW.json`](SPLIT_INITIAL_REVIEW.json).

## 1. Species ownership is part of the definition

For this model define pressure differences, in Pa = J m⁻³,

\[
D_m = \texttt{Pi_massive},\qquad
D_r = \texttt{Pi_gamma}+\texttt{Pi_nu}+\texttt{Pi_UV},\qquad
D_{\rm tot}=D_m+D_r.
\]

| Split | Included C15 components | Meaning and limitation |
|---|---|---|
| Matter | Independent collisionless massive nonbaryonic species | The modeled H/He baryon gas and remaining ideal cold matter are isotropic, so their anisotropic stresses are zero. This does not supply a general closure for every matter species. |
| Radiation | Primordial photons, massless neutrinos, tracked ionizing UV photons | Neutrinos in this owner lane are massless and belong here. Newly born and surviving tracked UV photons belong here at every evolved state. |
| Outside closed inventory | Full stellar/emitter donor and escaped-radiation energy–momentum reservoirs | Their full covariant closure remains open in C15. Splitting the plotted stress does not create a missing reservoir. |

`Pi_UV` is initially zero because the owner initializes an empty ionizing-photon cloud. It must nevertheless be included in radiation after evolution. Do not move a massive-neutrino species into radiation merely because it is called a neutrino; no such additional species is introduced by this adapter. The existing massive model remains the same source-defined component with fraction 0.1 and m/T = 30.

## 2. Tensor sum precedes the norm

Use the same non-tilted LRS Bianchi I geometry as the completed pilot,

\[
a_\perp=a e^{-b},\quad a_\parallel=a e^{2b},\quad
s=\dot b,\quad
\sigma^i{}_j=\operatorname{diag}(-s,-s,2s).
\]

Both matter and radiation stresses share this model's symmetry axis:

\[
\pi_A{}^i{}_j=\operatorname{diag}(-D_A/3,-D_A/3,2D_A/3),
\qquad A\in\{m,r\}.
\]

Write Kt = 8πG/c² = 3 × C15.KAPPA. The half-contraction convention gives

\[
\Sigma_h=\sqrt3\,|s|/H,\qquad
\Pi_{A,h}=\frac{K_t|D_A|}{\sqrt3H^2},\qquad
\widetilde\Pi_{A,h}=\frac{K_tD_A}{\sqrt3H^2}.
\]

The tilde denotes a signed coordinate; it is not a norm. Define signed shear similarly by \(\widetilde\Sigma_h=\sqrt3s/H\). The correct total is

\[
\boxed{\Pi_{{\rm tot},h}=|\widetilde\Pi_{m,h}+\widetilde\Pi_{r,h}|}
\]

and therefore

\[
\Pi_{{\rm tot},h}^2=\Pi_{m,h}^2+\Pi_{r,h}^2
+2\epsilon_m\epsilon_r\Pi_{m,h}\Pi_{r,h}.
\]

Adding the two nonnegative component norms gives an upper bound, not the total in opposite-sign cases. This exact signed-scalar rule uses the shared LRS axis; for arbitrary differently oriented tensors one must sum the actual tensors before contracting.

The work terms and Einstein source are

\[
\sigma_{ab}\pi_A^{ab}=2sD_A,\quad
\dot s+3Hs=\frac{K_t}{3}(D_m+D_r).
\]

With all physical stress switches on and the manufactured multiplier equal to one, the C15 RHS source is the physical total. Retain the source and physical sums separately in output so a future switched or manufactured lane cannot silently change this meaning. Frobenius norms of each component and of the tensor total are individually √2 times their half-contraction norms. The SI convention uses H in s⁻¹; if κ is written as 8πG/c⁴, the normalized stress contains κc².

## 3. Two independent positive angular seeds

At b = 0, use

\[
f_m(q,\mu)=f_{m0}(q)[1+\alpha_m P_2(\mu)],
\]
\[
f_\gamma(q,\mu)=f_{\gamma0}(q)[1+\alpha_r P_2(\mu)],\qquad
f_\nu(q,\mu)=f_{\nu0}(q)[1+\alpha_r P_2(\mu)].
\]

Here αm and αr are independent. Photons and massless neutrinos share αr, so this pilot does not independently scan the two radiation species' angular shapes. The even P₂ family has zero flux/odd angular moments and remains non-tilted initially. For each family,

\[
-1\le\alpha_A\le2,\qquad
\langle P_2\rangle=\alpha_A/5,\quad
\langle\mu^2\rangle=1/3+2\alpha_A/15.
\]

The monopole is unchanged, so the zero-shear initial energy and Hbase do not depend on the two amplitudes, apart from recorded floating-point quadrature residuals. Let

\[
W_m=\rho_{m,\mathrm{ref}}J_{0,m}^{(1)}/5,\qquad
W_r=(\rho_{\gamma,i}+\rho_{\nu,i})/5.
\]

The massive moment \(J_{0,m}^{(1)}\) is evaluated from the original finite Fermi–Dirac momentum quadrature at x = b = 0. It contains the kinetic pressure factor; replacing it by unity would substantially miscalibrate the matter axis. Direct angular integration gives

\[
D_{m,i}=\alpha_m W_m,\qquad D_{r,i}=\alpha_r W_r.
\]

For either component put K = ρ for radiation or K = ρm,ref J01 for massive matter. Then its initial principal pressures are

\[
P_\parallel=K(1/3+2\alpha/15),\qquad
P_\perp=K(1/3-\alpha/15).
\]

These are positive throughout the stated angular family. The distribution condition, rather than pressure positivity alone, is the relevant seed restriction. The family is a restricted choice of higher moments and does not parameterize every admissible distribution with the same stress norm.

## 4. Exact inverse and sign-dependent caps

For requested magnitudes and signs \((\Sigma_h,\epsilon_s;\Pi_{m,h},\epsilon_m;\Pi_{r,h},\epsilon_r)\),

\[
H_i=\frac{H_{\rm base}}{\sqrt{1-\Sigma_h^2/3}},\qquad
s_i=\epsilon_s\frac{\Sigma_h H_i}{\sqrt3},\qquad 0\le\Sigma_h<\sqrt3,
\]

\[
\boxed{\alpha_A=\epsilon_A\frac{\sqrt3H_i^2\Pi_{A,h}}{K_tW_A},\quad A=m,r.}
\]

A coordinate of zero has requested sign zero; a nonzero magnitude has sign ±1. Never clip an inadmissible α and retain the original requested coordinate. For each component,

\[
\Pi_{A,h}^{(-)}\le C_A(\Sigma_h),\qquad
\Pi_{A,h}^{(+)}\le2C_A(\Sigma_h),\qquad
C_A=\frac{K_tW_A}{\sqrt3H_i^2}.
\]

The actual pinned-owner calibration is:

| Quantity | Value |
|---|---:|
| Hbase [s⁻¹] | 1.3845102779768001 × 10⁻¹⁷ |
| Kt | 1.866397643667488 × 10⁻²⁶ |
| J01 massive | 0.014042977688245464 |
| Wm [Pa] | 8.493704601357930 × 10⁻¹² |
| Wr [Pa] | 8.836950583153555 × 10⁻¹² |
| Matter negative cap at Σh = 0.004 | 0.0004774699218655195 |
| Radiation negative cap at Σh = 0.004 | 0.0004967653459237577 |

Each positive cap is twice its negative cap. These are the smallest caps over the proposed shear grid. Thus component magnitudes {0, 0.00005, 0.0001, 0.0002, 0.0004} are admissible with both signs, independently for matter and radiation. The resulting maxima are |αm| = 0.837749105613109 and |αr| = 0.8052091460932763. The minimum continuous angular factors are respectively **0.162250894386891** and **0.19479085390672368**.

## 5. Cancellation is a distinct physical family

The signed axes have 9 shear values and 9 values for each component, giving 9³ = **729 initial cases**. The plane \(\widetilde\Pi_m=-\widetilde\Pi_r\) has **81 cases**: 72 with nonzero opposing component stresses and 9 with both component amplitudes zero. At the maximum opposing amplitudes the sum of component norms is 0.0008 while the total norm is zero up to measured roundoff.

Store each component's signed pressure, norm, sign and resolved/unresolved status independently. A total below the invariant floor 3 × 10⁻¹³ has unresolved total orientation even when the individual components are well resolved. Preserve the raw residual; do not force a tiny total to an exact zero inside the equations.

Initial cancellation need not persist. Collisionless radiation pressure redshifts as a⁻⁴ in isotropic expansion, while a nonrelativistic massive pressure approaches a⁻⁵; the exact finite-mass C15 integrals lie between the relativistic and nonrelativistic behavior. Photon scattering, UV births, and anisotropic expansion also distinguish the channels. Consequently an initially cancelling pair can source later total stress. This statement motivates retaining the cancellation family; no evolved cancellation result is claimed by the initial-only probe.

## 6. Independent initialization result

Every one of the 729 cases used a fresh original `EinsteinBoltzmann` constructor and original `initial()`. The source snapshot was hash-verified before import. Calls to `_physical` and `massive_source_3moments` read the achieved initial moments. All model RHS and geometry counters remained zero; no ODE or step/run call was made.

All **7,290 initial gates passed**, with maximum absolute coordinate residuals:

| Coordinate/check | Maximum residual |
|---|---:|
| Σh | 0 |
| Signed Πm,h | 3.361026734705064 × 10⁻¹⁸ |
| Signed Πr,h | 3.252606517456513 × 10⁻¹⁹ |
| Total Πh versus absolute requested signed sum | 3.632781212868302 × 10⁻¹⁸ |
| H versus common isotropic calibration, relative | 1.1128440 × 10⁻¹⁶ |
| Massive monopole J00 minus one | 8.881784197001252 × 10⁻¹⁶ |
| Massive quadrature weight reflection asymmetry | 0 |

All 81 nominal total-cancellation cases have achieved total Πh below 3.633 × 10⁻¹⁸. The raw residuals are preserved in the JSON. Nonnegative massive quadrature weights, positive continuous seed factors, finite states, empty initial UV, physical stress-cone checks and the initial Hamiltonian relation all passed.

These checks validate the inverse map and admissibility. They do not validate a forthcoming split evolution implementation. A dedicated split prepared-context guard must accept independent αm/αr while keeping the frozen source, fraction, mass, L and grids. The old common-amplitude guard correctly rejects this family and should remain unchanged for the completed pilot.

## 7. Scope, outputs and reused evidence

Retain the original warm a = 0.1999 → 0.2 interval, Tinitial = 12000 K, xHII = 0.4, xHeII = 0.5, L = 8, native source 8×8, fraction 0.1, m/T = 30 and the original 64 steps. Species splitting changes the initial-data family and reporting, not the kinetic or thermochemical evolution equations. Gas nonrest energy remains included in the owner Hamiltonian. Full donor/escape Qᵃ closure, full EoR history and temporal/angular/spectral convergence remain open.

Each evolved record should retain Dm, Dr, Dtotal, the three normalized stress magnitudes and signed counterparts, component work terms, the raw owner channels, and actual achieved initial coordinates. Three-dimensional parameter data can be presented as fixed-shear component-plane slices and representative pure-matter, pure-radiation, aligned and cancelling trajectories. Labels must distinguish component norms from signed coordinates and total tensor norm.

The metric/tensor algebra and positive P₂ integrals reuse the independently derived, Wolfram-checked evidence in [`THEORY.md`](THEORY.md) and [`EVIDENCE.json`](EVIDENCE.json). Primary literature support already read for the owner bridge is Lee–Nungesser–Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, [arXiv:1911.04937](https://arxiv.org/abs/1911.04937), and Heinzle–Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, [arXiv:gr-qc/0512031](https://arxiv.org/abs/gr-qc/0512031). Their collisionless results do not establish reionization or convergence for this pilot. The source-specific numerical claims in this note come exclusively from the recorded original-owner initialization probe.
