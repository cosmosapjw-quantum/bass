# BASS CE1-OBS | Conserved-momentum → normal-frame bolometric angular sky

## Contract / provenance

Parent: cosmosapjw-quantum/bass PR #258, HEAD `0656e98989750de4ea19c510ff2052654aaa3eda`; parent of PR #258: PR #253 HEAD `e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0`. Original physical-history ZIP SHA256: `162097533f0bc88ec5ddee8f10edcc08aaf4b81cbf2e4c14c42982dbf73ca6b7`. Original binary64 six-cell angular input SHA256: `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. All original six cell masses, edges and the initial shear are immutable. We use saved DOP853 41-time histories, not a new closure or dynamic integration.

Signature (-,+,+,+), positive reflection-even massless collisionless source, expanding diagonal Bianchi I, Λ=0, a_i(0)=1, u=t/Tstar ∈ [0,0.08]. Matter normalization E=8πG Tstar² ρ_energy/c², and P_i in the same unit. The local observer is comoving normal, orthonormal tetrad e_(0)=c⁻¹∂t, e_(i)=a_i⁻¹∂_(x^i) (where coordinate choices set spatial dimensions consistent with original metric). Propagation vector `e` is *photon momentum direction*, not the opposite incoming line of sight. With full inversion symmetry all nonzero even multipoles are unchanged by the antipodal convention change.

## Phase-space and angular map (derived)

The three translational Killing fields conserve q_i=p_i. At u=0, define q_i=q n_i with n·n=1 and q>0. The physical tetrad spatial momenta are q n_i / a_i, and energy is `epsilon(u)=c q r`, with `r = sqrt(sum_i a_i^-2 n_i²)` and `epsilon(0)=c q`. The observed propagation direction is `e_i=a_i^-1 n_i/r`. It is an orientation-preserving bijection S²→S², with inverse `n_i=a_i e_i/s`, `s=sqrt(sum_j a_j² e_j²)` and `r=1/s`.

For A=diag(a_i⁻¹), the normalized-direction map e=An/|An| has solid-angle Jacobian `J=|det A|/|An|³=V⁻¹ r⁻³`, where V=a1 a2 a3. Proof: the oriented area three-form satisfies det(e, de, de)=det(A) det(n,dn,dn)/r³. A Wolfram symbolic determinant ratio returned 1; a separate finite-difference differential-area computation checked the formula at four general angles.

Let dW₀(n)=J₀(n)dΩ₀ denote the **original normalized initial bolometric energy measure** integrated over canonical momentum magnitude. The six physical cell values W_ij are *total full-sphere energy including eight octants*, with μ=n_z∈[0,1], t=2φ/π∈[0,1] in the positive octant. Since `dΩ₀=(π/2)dμ dt` in each positive octant, eight octants cover `4π dμ dt`. Thus `J₀(n)=W_ij/(4π Δμ_i Δt_j)` for all eight sign copies of any (μ,t) cell. No artificial isotropy or spectrum is assumed.

Collisionless transport fixes the canonical momentum distribution. The physical angular energy pushforward is `dW_u(e)=V⁻¹ r(n) dW₀(n)`. Dividing by `dΩ_u=V⁻¹ r⁻³dΩ₀` gives the **observer-frame angular energy density** `J_u(e)=r⁴ J₀(n(e))`. All equalities are bolometric; this source has no specified photon spectral function and cannot determine a unique temperature field. If an external spectral intensity were provided, its frequency transformation would require the independent invariance `I_ν/ν³`, which is NOT assumed or evaluated here.

Observable moments: `E(u)=∫ J_u dΩ_u=V⁻¹∫r dW₀`; `T^hat(i)hat(j)=∫J_u e_i e_j dΩ_u=V⁻¹∫(a_i⁻¹n_i)(a_j⁻¹n_j)/r dW₀`. Independent coordinate sign reflection makes all off-diagonal terms zero; `P_i=T^hat(i)hat(i)`, `sum_i P_i=E`. The bolometric energy flux also vanishes for this normal observer. The full angular measure, not a fluid closure, is retained.

## Harmonics and pressure inversion (derived)

Take Condon–Shortley complex harmonics with ∫Y_lm Y_l'm'*dΩ=δ_ll'δ_mm'. Define `a_lm(u)=∫ J_u(e) conj(Y_lm(e)) dΩ_u = V⁻¹∫r J₀(n) conj(Y_lm(e(n))) dΩ₀`. Then:

- `a00=E/sqrt(4π)`;
- `a20=sqrt(5/(16π)) (3P3-E)`;
- `a2,2=a2,-2=sqrt(15/(32π)) (P1-P2)` (real);
- `a_lm=0` for odd l or odd m, all sine modes vanish; `a_l,-m=(-1)^m conj(a_lm)`.

Conversely, setting `d=a20/sqrt(5/(16π))`, `z=a22/sqrt(15/(32π))`, recover `E=sqrt(4π)a00`, `P3=(E+d)/3`, `P1=(E-P3+z)/2`, `P2=(E-P3-z)/2`. Thus the normal-frame quadrupole reproduces the *entire diagonal pressure tensor*, while l=4 probes genuinely additional angular information. Explicit polynomial Y40,Y42,Y44 are implemented in the generator; SciPy sph_harm_y independently checks all l≤4 including vanishing parities on eight full sign octants.

For one deterministic sky define `C_l=(2l+1)⁻¹∑_{m=-l}^l|a_lm|²`. No ensemble average, thermodynamic temperature interpretation, observational likelihood, or statistical isotropy is implied.

## Discretization semantics

- Original continuum six-cell J₀ is positive, piecewise constant in μ,t (full sphere by eight reflections). GL24 and GL40 approximate its integrals with tensor-product Gauss–Legendre points *inside each original cell*. In each positive octant, `dΩ0_node=(π/2)(ΔμΔt/4)w_i w_j`, total all-eight energy mass `W_ij w_i w_j/4`.
- Original `stored_ref{1,4,8,16}` are atomistic approximations: one quadrature ray for each refined cell with components equal to square roots of the analytic cell means of n_i² (source's MPFR-directed midpoint construction up to binary64 rounding), and mass W_ij/f². They have a discrete angular-energy pushforward; they do NOT define a pointwise intensity J_u and are NOT used to render a smooth sky.
- Recomputing e, r and J on the parent physical ell_i time arrays does not evolve or modify the Einstein–Vlasov state. GL40 is a numerical comparison, never a rigorous enclosure or replacement for the independent CE1-N RK4/Hermite MPFR certificate.

## Literature and applicability

- Lee, Nungesser & Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, GRG **52**, 48 (2020), DOI 10.1007/s10714-020-02699-7; conservation of Bianchi I covariant momenta. Its late-time perturbative isotropization theorem is NOT imported to this short-time simulation.
- Fleury, Pitrou & Uzan, *Light propagation in a homogeneous and anisotropic universe*, PRD **91**, 043511 (2015), DOI 10.1103/PhysRevD.91.043511; independent geometrical treatment of Bianchi-I photon redshift and directional transport, distinct from the present kinetic initial angular measure.
- Pitrou, *Radiative transport of relativistic species in cosmology*, Astropart. Phys. **125**, 102494 (2021), DOI 10.1016/j.astropartphys.2020.102494; distinction between angular radiation moments, polarization, and spectral distortions. Neither collision nor polarized transport is introduced here.

**Claim boundary:** Exact algebraic map and sky moment identities derived for the specified source; numerical checks are binary64, GL comparisons noncertified. No blackbody CMB temperature, no Thomson source, no general Bianchi-family support, no production-ready or merge-ready status.
