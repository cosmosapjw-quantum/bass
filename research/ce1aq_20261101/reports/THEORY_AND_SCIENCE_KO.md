# CE1AQ | Exact Bianchi I null optical-beam Jacobi, fifth-order source-to-distance jet, 9,888 real physical observables

**Immutable parent:** BASS CE1AP Draft PR #301 at exact HEAD \`baef3a4b5a556703f2e2feb93b57da6b364d29fd\`; original massless collisionless reflection-even *diagonal Bianchi I* six-cell binary64 source SHA256 \`022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035\`. Signature (-,+,+,+), Λ=0, normalized Einstein 8πG=1, proper u∈[0,.08]. All parent, source, production and root \`DAG.json\` unmodified.

## Original physical ray-screen construction

Fix observer at u_o=.08 and source at eight **fixed proper times** u_e=0,.008,.016,.024,.032,.04,.048,.064 (NOT fixed observed redshift). Rescale spatial observer coordinates so a_i°(u_o)=1. For observed unit direction n_i, Bianchi I translation Killing fields imply conserved k_i=n_i and normal-frame photon energy E(u)=sqrt(Σ_i n_i²/a_i°(u)²). The exact comoving ray derivative is

\`\`\`
J_ij = ∫[u_e,u_o] du (δ_ij/(a_i°² E) − n_i n_j/(a_i°² a_j°² E³)).
\`\`\`

For observer sky basis b^j_A, emission physical projected beam B_iA=a_i°(u_e)J_ij b^j_A, source photon unit vector s_i=n_i/(a_i° E), screen P=I−s s^T and G=B^T P B, the **area distance** is D_A/(cT*) = det(G)^(1/4). Positive sqrt eigenvalues of G give the two accumulated beam semiaxes; report ellipticity (smax−smin)/(smax+smin). This finite-beam ellipticity is **not** the local optical shear scalar and no Sachs screen rotation is inferred.

**Independent exact Bianchi I Sachs/Saunders determinant**: geometric mean a=(Πa_i°)^(1/3), E as above, I_i=∫du a_i°²/(a^6 E³), Δ=n_x² I_y I_z+n_y² I_x I_z+n_z² I_x I_y. Then D_A/(cT*)=a(u_e)sqrt(a(u_e)E(u_e) Δ). This agrees with P. Fleury, C. Pitrou, J.-P. Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D 91, 043511 (2015), [DOI 10.1103/PhysRevD.91.043511](https://doi.org/10.1103/PhysRevD.91.043511), Eqs. (7.14)–(7.17) converted from conformal η. Wolfram evaluated all 3×3 components of the Jacobian derivative difference to **0**. For FLRW D_A=a_e∫du/a and for Minkowski D_A=u_o−u_e.

## New exact time-T fifth-order source physics

CE1AP exact original source-dark initial metric response is ∂ε ℓ_i(u)=(A_i/8)u⁴+O(u⁵), where A_i=Σ_jkσ_jσ_kδT_ijk(0), Σ_i A_i=0. For source at u_e=0 and observer T→0, observer-normalized f_i(u)=A_i(u⁴−T⁴)/8 and S_f=Σ_i n_i²f_i. The first variation of screen area gives

\`\`\`
∂ε ln D_A = −S_f(0)/2 + (2/T)∫_0^T S_f(u)du + O(T⁵)
          = −(11/80)T⁴ Σ_i n_i²A_i+O(T⁵),
∂ε [D_A/(cT*)] = −(11/80)T⁵ Σ_i n_i² A_i + O(T⁶).
\`\`\`

Wolfram symbolic residual for the exact −11/80 coefficient is **0**. An independent zero-background synthetic test verified the coefficient, and the original GL24 x-axis Einstein–Vlasov response ratio (numeric central source secant)/(exact leading jet) approaches unity as T→0: ~.974 at T=.008 vs ~.775 at T=.08. No uniform bound for the O(T⁶) remainder has been proven.

## Executed physical sky and self-hostile validation

From the existing **nine** source-owned self-consistent original CE1AP Einstein–Vlasov IVPs (GL8/16/24; ε=0,±.035), construct 103 physically observed directions per sky (7 anchors + 96 independent full-sky samples), eight emission times and 3 GL orders: **7,416 new** optical beam records plus **2,472 new** source-dependent distance-response records = **9,888** *new physical observational-function records*, **zero new Einstein IVPs**. These are conditional geometric optics, not observational Planck/CMB data. At GL24 and u_e=0, baseline (x,y,z) D_A/(cT*)≈(0.077725208, 0.078675568, 0.078490957). ε=+.035 relative source (x,y,z) shifts≈(−1.82907e−11, +2.10022e−12, +1.65532e−11). Optical beam ellipse in 96 sampled directions is nonzero.

**Local 14/14 pytest PASS** with FLRW, Minkowski, axis independent scalar quadrature, screen basis rotations, GL comparison, source sign/regularity and exact jet weak-background tests. Full original 7,416 physical beam records have max direct-Jacobi / independent Saunders relative residual **1.33023e−15**, all sampled screen determinants positive. A separately implemented *same-author* finite-angle ray-displacement adversarial test on 36 independent physical beams had max abs D_A difference **1.56567e−9** and detected an intentionally swapped-axis false source control (difference 0.000950360). Same-author is NOT distinct-author R6/C9. No claim of continuum in-sky no-caustic proof or rigorous time-integrator enclosure.

**Primary background:** Ho Lee, Ernesto Nungesser, Paul Tod, *On the future of solutions to the massless Einstein-Vlasov system in a Bianchi I cosmology*, Gen. Relativ. Gravit. 52, 48 (2020), [DOI 10.1007/s10714-020-02699-7](https://doi.org/10.1007/s10714-020-02699-7). First-party [CLASS](https://github.com/lesgourg/class_public), [CAMB](https://github.com/cmbant/CAMB), [ESA Planck PR3](https://pla.esac.esa.int/) remain mainstream FLRW and public observation authorities but are **not owner source substitutions**.

**DAG and gates:** CE1 upper 9/15 (21 edges), CE1 PARTIAL, new upper completed 0; CE1AQ scoped 3/3 exact Jacobian+fifth jet+real sky. VigilODE 7/23 separate source; VigilODE PR165 newer *different* full-Stokes result not imported. No CMB likelihood, fixed-observed-redshift source modeling, polarized collision, or Sachs rotation. Production HOLD, Merge HOLD, AUTO_NEXT=false, native subagent NOT_RUN, distinct-author R6/C9 NOT_RUN. Root \`DAG.json\` is ACCEL02 other-lane and remains unchanged.

## Evidence and source publication
- S0 = 13,663 B SHA256 \`91ee289b9efbb26281c40bd5a459457b4a7320e2449bfaab09acf2fa80d8c69b\` (theory + portable code and source lock)
- S1 = 1,159,415 B SHA256 \`3d7b69ea6738918526812d162ba4034e070cd3de9f5d0614de60a3a2f2c479e9\` (real physics and adversarial results)
- S2 = 2,645,530 B SHA256 \`7b9836e71674f5a9af26dde12094ecbca5724da7f738c699de2b7ee138d9575d\` (complete standalone, including ancestor 16,842-row CE1AP physics and plots)
- Exact immutable S0/S1/S2 ZIPs each CRC and 6/20/24 member SHA manifest verified locally; provider readback is separately checked and recorded, NOT implied by this text.
- The clean-checkout GitHub CI independently regenerates PR301 nine original IVPs using the parent source, then computes the new Jacobi/Saunders atlas; this is a different but scientifically equivalent implementation to local S2, *not byte-identical*.
