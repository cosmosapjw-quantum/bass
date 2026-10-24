# Actual REC finite occupation to BASS snapshot bridge

## Scientific decision and evidence boundary

The next admitted unit should map the actual REC finite occupation inventory to
a BASS photon snapshot. Its inputs are the stored mode measures `G_i`, the
stored photon momentum scales `p_i = CollisionNetwork.momentum_scale`, the
actual angular weights and directions `(A_j,n_j)`, and the actual occupation
array `f_ij`. This is a constructive bridge between two existing state
representations. It does not require an incoming radiation boundary, an atomic
donor, a spectral line profile, or a time integration.

This note is an independent source inspection and algebraic derivation under
the parent's frozen snapshot scope and the user's explicitly supplied
PhysMath 1.0 instructions. No scientific program, numerical IVP, old campaign,
or symbolic kernel was executed by this child. The parent owns subsequent
symbolic/numerical validation and scientific admission. All formulas below
are derived statements, not a report of tests that have already passed.

The pre-existing B3b finite-emission derivation and its admitted validation are
reused unchanged. B1/B2 historical evidence gaps and their qualifications are
unchanged. Remaining budget is `null`; `budget_reset=false`.

## 1. Actual source authority

The current REC source copies have exact Git-blob identities recorded by the
intake agent in `../rec_intake/SOURCE_COPIES.json`. Relevant actual code:

| Object | Source file / authority | Meaning used here |
|---|---|---|
| Finite state | `recoil/nonlinear_bose_runtime.py`, blob `67c39313fdaf29100296ba1381293f2478107e09` | Positive `mode_measure`, `momentum_scale`; indexed frequency states |
| Number moment | `recoil/nonlinear_bose_release.py`, blob `df06f46252b44ad6d169cb95e7c0f8b551ae4a25` | Occupation times mode measure and normalized angular quadrature |
| Physical energy | REC PR43, head `37a943347bf319af998230bb77c6f89827feddff` | `momentum_scale*c` is the sole locked energy authority |
| Interface bookkeeping | `recoil/coupled_interface.py`, blob `b7274ebbfd2900a18b674a12068092c6680ccb56` | Integrated number packet and exact face energy have separate meanings |
| Frequency transport | `recoil/frequency_liouville.py`, blob `95ad73d8095e5b5c19667661e1680a48bd6a5765` | Cell/face energy difference and redshift work are explicit |
| Unfinished atomic ownership | `trajectory/dynamic_macro_ownership.py`, blob `a196840d164aa7497b27178c1a38ca0f9627c426` | Current COM atomic source is disabled; split-domain replacement is incomplete |
| BASS state moments | B3b `vendor/kinetic.py`, blob `1fef508f01479508e5489cf8a167d2aff8184a81` | `moments`, `tensor`, and state boost |
| BASS geometry convention | B3b `vendor/core.py`, blob `3e95a652715b346a47f097fde2131540237390a4` | Fixed physical scale and `Source.pi` as state stress |

Targeted intake has now obtained the three actual, fixed-hash inputs, without
replaying their generating campaign:

| Input | Shape/use | SHA-256 |
|---|---|---|
| `data/z1100_direct_network_node.npz` | 35 locked mode measures/momentum scales | `e6a28194d183658a87f0974afe3f46323106382970a85338f9ce94c20c7b5736` |
| `data/pr01c_background_snapshots_v048.npz` | 26 directions and positive angular weights | `df136bca7c120054cc45cf2b4fc2bd52acc3d60e6159b0f63c2622de03f2f03c` |
| `data/pr05c2c1b2b1e0_source_derived_parent_v073.npz` | Actual positive 35 by 26 occupation | `c74a2a0e69d6d34c338d19af2f123d1eb32130ac103a68e4494a2c9542eaa958` |

The saved occupation is scalar-history, unpolarized isotropic bootstrap
INITIAL-DATA in the hydrogen tetrad. Its actual builder is restricted to the
validated Bianchi-II background and records `coupled_macro_endpoint=false`.
It restores Planck plus distortion at arithmetic COM centres and repeats the
scalar state over the angular grid. General anisotropic test occupations in
this bridge are synthetic diagnostics on the actual grid; they do not recover
missing native angular information.

Full acquisition and byte identity are in
`../rec_intake/NPZ_INPUT_IDENTITY.json`. These are source-state inputs, not new
dynamic physical-split evidence.

### A correction that must remain visible

My initial exploration suggested reconstructing each photon energy from the
geometric centroid

\[
\bar\nu_i=\frac34\frac{\nu_{i,+}^4-\nu_{i,-}^4}
                         {\nu_{i,+}^3-\nu_{i,-}^3}.
\]

Fresh PR43 intake showed that this repeats a previously repaired owner error:
the tracked network energy is **the stored** `c*momentum_scale`, not this
reconstruction. PR42's full-array discrepancy was reported as
`5.5440192880951145e-08 eV`; PR43's selected RED witness missed the locked moment
by `5.540597669551062e-08 eV`. These are inherited receipt values, not new
measurements. The corrected bridge below uses only stored `p_i`. Geometric
centroids can be diagnostics, with their discrepancy reported explicitly.
The relevant fresh PR43 body is preserved in
`../rec_intake/PARALLEL_PR_READBACK.json`.

## 2. Definitions, units, and physical domain

Use signature `(-,+,+,+)`, photon momentum
\(p^a=(E/c,\mathbf p)\), and the hydrogen-rest snapshot frame supplied by the
REC state. Let

\[
G_i>0\quad[\mathrm{m}^{-3}],\qquad A_j>0,\quad
\sum_jA_j=1,\qquad |\mathbf n_j|=1,\qquad f_{ij}\ge0,
\]

\[
p_i>0\quad[\mathrm{kg\,m\,s}^{-1}],\qquad E_i=cp_i,
\qquad C_{ij}=G_i A_j,\qquad n_{ij}=C_{ij}f_{ij},
\qquad \ell_j^a=(1,\mathbf n_j).
\]

`G_i` already contains the source's polarization and radial phase-volume
normalization. No extra factor of two or `4*pi` is introduced. The actual
full-sphere continuum formula `8*pi*(nu_hi^3-nu_lo^3)/(3*c^3)` explains the
measure convention, but recomputing a different-temperature grid is not a way
to replace the locked array. All arrays, their labels, frame, and epoch are
bound together.

For the **actual locked discrete REC state**, its number current and stress
tensor are

\[
N^a=c\sum_{ij}n_{ij}\ell_j^a,
\qquad
T^{ab}=\sum_{ij}E_i n_{ij}\ell_j^a\ell_j^b.
\tag{1}
\]

Thus `N^0/c` is photon number density, `T^00` is energy density, and `c*T^0i`
is physical energy flux. These are moments of the provided finite state; a
new continuum angular/radial accuracy claim is not needed for this identity.

## 3. Constructive forward map

Let the existing BASS fixed scale supply
\(\alpha_L=\kappa_{\rm grav}L^2\) and let \(P_*>0\) be the momentum scale.
Create a massless packet for each occupied source index:

\[
\mathbf k_{ij}=\frac{p_i}{P_*}\mathbf n_j,
\qquad w_{ij}=\alpha_L cP_*G_iA_jf_{ij},
\qquad m_{ij}=0.
\tag{2}
\]

The actual kinetic routine uses \(e_{ij}=|\mathbf k_{ij}|=p_i/P_*\).
Substituting (2) into that routine gives, without approximation,

\[
\rho_\gamma=\alpha_L T^{00},\qquad
F_\gamma^a=\alpha_L T^{0a},\qquad
p_\gamma=\frac{\rho_\gamma}{3},
\tag{3}
\]

\[
\pi_\gamma^{ab}=\alpha_L\sum_{ij}E_iG_iA_jf_{ij}
  \left(n_j^a n_j^b-\frac{\delta^{ab}}3\right).
\tag{4}
\]

In (3) and (4), Latin spatial indices run from 1 to 3. The source index `i`
elsewhere still labels frequency cells. No isotropy is assumed. In particular,
the actual 26-direction grid must not be silently replaced by the B3b
14-direction emission cubature.

Number can be recovered from the BASS packets independently of energy:

\[
N^a=\frac{1}{\alpha_LP_*}\sum_{ij}w_{ij}\ell_j^a.
\tag{5}
\]

The Minkowski trace is

\[
\eta_{ab}T^{ab}
=\sum_{ij}E_i n_{ij}(-1+|\mathbf n_j|^2)=0.
\tag{6}
\]

Equation (4) identifies the state-stress quantity used by `Source.pi` in the
existing BASS convention. This adapter constructs no `Source` and writes no
source fields. It returns packet/state moments only; no `U`, `J`, or
`PiRate_hat` is inferred from a snapshot.

## 4. Exact inverse on the declared representation

Retain each packet's original `(frequency_label, angular_index)` together with
the immutable source grid and frame binding. On that fixed representation,

\[
f_{ij}=\frac{w_{ij}}{\alpha_L cP_*G_iA_j}.
\tag{7}
\]

The inverse first verifies that the packet is massless and that its momentum
equals `p_i*n_j/Pstar` in the declared source frame. It then applies (7).
Equation (7) is a genuine left and right inverse of (2) on this labeled state
space. It is not a rebinning rule for arbitrary BASS packets. Duplicate
labels, off-grid momenta, mismatched frame/epoch/scale, or a changed energy
owner are a different state and require an explicit transformation.

Zero entries can be retained with zero weight or omitted with an explicit
full-grid index map. The all-zero array has the true empty-photon-stock
representation; no positive seed is needed. An omitted index reconstructs
zero only because the grid manifest makes that omission unambiguous. Negative
occupations are rejected, not clipped. Positive values whose packet weight
underflows, and nonfinite inputs, must be reported as unrepresentable.

Finite-precision tests should compare forward/inverse values and moments at
their stated conditioning scales. Algebraic invertibility does not mean
every mathematically positive input is representable in binary64.

## 5. Snapshot Lorentz covariance and the event-rate distinction

For a proper Lorentz transformation `Lambda`, define

\[
p_{ij}^{\prime a}=\Lambda^a{}_b p_{ij}^b,
\qquad D_j=E'_{ij}/E_i>0,
\qquad \ell_j^{\prime a}=\Lambda^a{}_b\ell_j^b/D_j.
\]

The state number-density weight on the new observer's simultaneity slice is

\[
n'_{ij}=D_jn_{ij},\qquad w'_{ij}=D_jw_{ij}.
\tag{8}
\]

The factor is independent of radial energy for massless packets at a fixed
direction. Equations (1) and (8) prove

\[
N^{\prime a}
=c\sum D_jn_{ij}\frac{\Lambda^a{}_b\ell_j^b}{D_j}
=\Lambda^a{}_bN^b,
\tag{9}
\]

\[
T^{\prime ab}
=\sum (D_jE_i)(D_jn_{ij})
 \frac{\Lambda^a{}_c\ell_j^c\Lambda^b{}_d\ell_j^d}{D_j^2}
=\Lambda^a{}_c\Lambda^b{}_dT^{cd}.
\tag{10}
\]

This is exactly the circumstance in which BASS's existing state rule
`w_new=w*E_new/E` is correct. The inverse bridge for a boosted stock either
returns it through the explicit inverse boost and rechecks the canonical
grid, or retains a complete transformed-cell binding. It must not divide
boosted weights by untransformed `G_i*A_j` and call that the canonical `f_ij`.

For the B3a invariant local spacetime event measure `dR`, an event source
instead obeys

\[
Q^a=\int p^a\,dR,
\qquad
K^{ab}(u)=c\int \frac{p^ap^b}{-u\cdot p}\,dR.
\]

There is no simultaneity-slice number-density factor to append to the
invariant event measure. Applying (8) to `dR` would introduce an extra Doppler
factor and reproduce the error isolated in B3a. The present state derivation
therefore complements, rather than changes, that event-rate result.

## 6. Energy-owner and information-loss witnesses

If a candidate bridge replaces the stored energy `E_i=cp_i` by a reconstructed
energy `Etilde_i`, it can pass photon number and the massless trace tests while
shifting the energy density by

\[
\Delta\rho_\gamma
=\alpha_L\sum_{ij}G_iA_jf_{ij}(\widetilde E_i-E_i).
\tag{11}
\]

A snapshot supported on one cell with unequal energies makes (11) nonzero.
This is why locked-energy comparison is an independent required check.
Trace-zero and positivity cannot establish correct physical energy ownership.

The bridge preserves the actual discrete `N` and `T` in (1). It neither adds
nor reconstructs unresolved radial information. For example, a packet of
number `n` at energy `E` and two half-number packets at `E-delta,E+delta`
have the same number and first energy moment, whereas their second energy
moments are `n*E^2` and `n*(E^2+delta^2)`. Higher spectral moments, line-profile
occupations, and a unique incoming line-boundary trace cannot be deduced from
`N` and `T`, nor from a centroid packet alone. This elementary constructive
witness is not a new strong no-go or a novelty claim.

Likewise, a COM interface crossing carries the exact face energy, which may
differ from a stored cell's energy. The existing REC code keeps that
representation correction separate from cosmological redshift work and sets
its interface atomic source to zero. A future finite transfer must reuse that
ownership; a mismatch is not automatically atomic heat.

## 7. What this closes and the next physical dependency

This unit closes an actual finite-inventory representation link, including
number/energy/flux/stress, labeled roundtrip, vacuum, and observer covariance.
It does not make the LINE01 input `f_plus` a cell average. Current source
inspection identifies the narrower remaining tasks:

1. Bind the physically relevant boundary/history value to the finite receiver
   and its clock. The outer blue face at `x=+21.25` is not automatically the
   LINE01 line-side trace.
2. Resolve native/COM atomic and diffusion ownership before combining their
   source actions. The current source explicitly declares
   `replacement_complete=False`, `com_atomic_source_support="disabled"`.
3. If finite atomic emission/absorption is then introduced, identify its actual
   donor/receiver energy and distinguish gross paired channels from their net.

These are local coupling obligations, not absence of all finite spectral
capacity and not an impossibility theorem. The adopted snapshot bridge needs
none of those unresolved inputs and is therefore a productive next research
and coding unit now.

## 8. Conditional closed-cell construction retained from exploration

This subsection records a new constructive option for later work; it is not
part of the frozen snapshot implementation or a claim about LINE01 admission.

The actual `IsotropicEinsteinLineSource` has a positive paired action

\[
\dot f=a\{x(1+f)-g(1-x)f\},\quad
a=\frac{c^3NA_{ul}\phi}{8\pi\nu^2}>0,
\]

when its two populations are normalized to a paired density `N`. If an actual
finite capacity `C` is supplied, photon and atomic energy per excitation both
equal the same specified `E0`, and the source is admitted as their sole owner,
set `chi=C/N` and `dot x=-chi dot f`. Then

\[
m=x+\chi f,\quad b=g+1,\quad A=g+\chi+bm,
\quad P(x)=bx^2-Ax+gm,
\quad \dot x=aP(x).
\]

With `Delta=A^2-4bgm`, the stable root is
`r_minus=2gm/(A+sqrt(Delta))` and the other root is
`r_plus=(A+sqrt(Delta))/(2b)`. Set `R=r_plus-r_minus` and
`y0=x0-r_minus`. The exact finite map is

\[
x(t)=r_-+
\frac{y_0e^{-abRt}}{1-(y_0/R)(1-e^{-abRt})},\qquad
f(t)=\frac{m-x(t)}\chi.
\tag{12}
\]

The domain `0<=x<=min(1,m), f>=0` is invariant: at `f=0` the photon source is
nonnegative, at `x=0` atomic absorption is nonnegative, and at `x=1` atomic
emission is nonnegative. `N*x+C*f` and `E0*(N*x+C*f)` are conserved. Gross
up/down counts remain separate time integrals and can both grow at equilibrium.
They are not each bounded by the *initial* photon stock because emission can
replenish that stock during the same evolution.

The entropy per paired atom

\[
s=-x\log(x/g)-(1-x)\log(1-x)
 +\chi[(1+f)\log(1+f)-f\log f]
\]

satisfies

\[
\dot s=\frac{R_\uparrow-R_\downarrow}{N}
                 \log\frac{R_\uparrow}{R_\downarrow}\ge0,
\]

with the continuous boundary interpretation. At equilibrium,
`x*(1+f)=g*(1-x)*f`. This proves positivity, conservation, and detailed balance
for the explicitly closed conditional model without clipping.

Here `R_down=C*a*x*(1+f)` and `R_up=C*a*g*(1-x)*f` are number rates per
physical volume. The discriminant is strictly positive because
`Delta=(bm-g)^2+2*chi*(g+bm)+chi^2`. The stable root lies in the physical
interval, while `r_plus>min(1,m)` for nontrivial positive data; consequently
the denominator in (12) remains positive for finite positive time. This
establishes that the displayed finite map uses the physical solution branch.

For several actual cells with energy `E_i`, let `q_i` be their net photon
production. Charging each event to a fixed atomic excitation `E0` leaves
`dot E_total=sum_i (E_i-E0)*q_i`. That term requires a real recoil/thermal
energy owner or a justified spectral approximation. Declaring it a new donor
reservoir would not close the physical model. Also, actual LINE01 `f_plus` is
a boundary trace, so substituting a COM cell occupation into its escape map
does not implement (12) or establish a physical source link.

## 9. Following alternative: B3c source/transport composition

If selected in a later unit, actual B3b `f_plus=0` finite emission can be
composed with actual BASS collisionless Einstein/packet transport and atomic
dilution on expanding Bianchi I. In that restriction `n=a=0`,

\[
\mathbf k'=-(hI+\sigma)\mathbf k,\quad
(\log w)'=-3h,\quad N'=-3hN,
\]

and an atomic dust/excitation sector has `rho_atom'=-3h*rho_atom` between
collisions. The finite source substep holds geometry fixed, conserves total
rho/flux, and therefore preserves the *existing* Hamiltonian/Codazzi residual.
The changed photon pressure and stress then enter the actual geometry RHS.

With positive directional expansion `h+n.sigma.n>0`, emitted photons starting
at the line or below it redshift away, which can support a zero incoming blue
trace when the boundary orientation and absence of other upscattering are
explicit. A symmetric source/transport/source composition is locally second
order on a compact smooth physical domain with admissible substeps. This is
not a long-time error certificate. Each source entry must still satisfy the
whole-path optical-depth and continuum positivity gates.

The actual `CoupledPackets` class has fixed, nonempty packet count and log
weights. A new wrapper would be required for true vacuum plus finite source
injection, and a constraint-satisfying initial fixture would have to be built
explicitly. Thus this alternative requires a new bounded IVP contract. It is
not part of the currently chosen snapshot bridge.
