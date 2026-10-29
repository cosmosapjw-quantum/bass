# CE1-K: canonical safe-source + panel-local source-pressure enclosure

## Authority and provenance

Canonical base PR246, head `4474f8acb13614ffda7a30524a815976e306efc9` (parent PR245); numerical source/time modules exactly taken from its archived S2 immutable source files. Donor mathematical result PR247, head `bd94bf270dcbf3bf140ac6cf7a7caf7e72532ac0` (parent PR242). Current work is an additive synthesis, never a merge of these branches or an update to original parents. Upper DAG is 9/15; CE-1 remains partial.

## Frozen model

Signature (-,+,+,+), Lambda=0, massless collisionless reflection-even diagonal expanding Bianchi I. Proper dimensionless u=t/Tstar, ell_i=ln a_i and h_i=Tstar H_i. Positive finite continuum original-cell angular-energy measure M, exact stored binary64 ray/mass discrete measure Q. Original mu=[0,.5,1], phi_fraction=[0,.25,.75,1], energies=[[.1,.25,.05],[.2,.15,.15]], shear=(.2,-.13,-.07), u in [0,.08], 4 RK4 panels and original fixed target max|Delta h|<1e-5. No collisions, tilt, polarization, spatial hierarchy or measured sky.

## Derivation

For arbitrary positive finite measure X in {M,Q}, put b_i=e^(-2ell_i), Z=sum b_i n_i^2, V^-1=e^(-sum ell_i). For each i,

  P_i^X(ell) = e^(-sum ell) int (b_i n_i^2/sqrt(Z)) dX.

For s>=0, P_i^X(ell+s 1)=e^(-4s)P_i^X(ell), since the volume factor contributes e^(-3s), numerator e^(-2s), sqrt(Z)^-1 e^(s). Thus D_i=P_i^M-P_i^Q obeys the same identity exactly. This identity needs *fixed comoving ray and mass measure* (not adaptive reweighting); the outward pressure-difference certificate also needs positivity and a valid current-source snapshot.

On panel j, suppose the exact and the stored exact-binary Hermite paths satisfy m_j<=min_i ell_i(u) for all u in [u_j,u_{j+1}], and known common global geometry upper B_i>=ell_i(u) applies to both. Then for ell in this region x=ell-m_j 1 belongs to product box [0,B_i-m_j]. The inherited CE1-F certificate E_Q(B-m_j1) implies

  |D_i(ell)|<=exp(-4m_j) E_Q(B-m_j1).

A second valid bound is the prior uniform eta_global, hence the minimum is also sound:

  eta_j=min(eta_global, exp(-4m_j) E_Q(B-m_j1)).

The canonical CE1-I ancestor certifies each m_j by (1) exact Einstein-flow positive h_i, theta<=theta0 and h_i'>=-theta h_i, providing an exact-flow lower at panel start, (2) the whole exact-binary Hermite cubic Bernstein hull on that panel, with explicit stored left-knot identity. Their smaller certified lower is valid throughout the panel. The exact flow h_i>0 ensures ell_i monotone. All shifts, exponents, interval radii and enclosure propagations are outward rounded under MPFR192. Reject inconsistent boxes B_i<m_j; do not clamp a failed proof premise to zero.

Let e_ell/e_h be nonnegative infinity error envelopes. Using exact Jacobian row sum 4P_i, panel L_j=4max_i P_i(0)e^(-4m_j) or canonical CE1-I's already checked upper, and original residuals rho,

  D+ e_ell<= e_h+rho_ell,
  D+ e_h <= L_j e_ell+eta_j+rho_h.

Within each panel, use the same positive 2x2 propagator as original CE1-I and add exact stored binary Hermite knot jumps at boundaries. The source term can be propagated separately. The canonical initial/time components are inherited unchanged; only source contribution is recertified and repropagated. This cannot increase the bound because eta_j<=eta_global, provided exactly the same L_j and residual carriers are used.

## Known limits and destructive checks

- m_j=0 recovers prior global/source bounding, as long as its source box is exactly inherited.
- All eta_j are nonnegative and eta_j<=eta_global by construction.
- M=Q gives actual source difference zero but the certificate need not be zero.
- A mutated source ray/mass or changed Hermite origin invalidates a previously recorded certificate unless the *current* data are recertified; the canonical PR244 code has current-source majorant recomputation and left-knot identity.
- A box with B_i<m_j is a proof-premise failure. Rejection is mandatory, not silent clamping.
- A single numerical sample is not an exact real or code-formal certificate.
- Even passing the fixed original target only supports this frozen pilot Einstein-Vlasov model; production/merge/statistics gates remain held.

## Related literature (methodology, not source of this lemma)

A. Neumaier, *Global, rigorous and realistic bounds for the solution of dissipative differential equations, Part I* (logarithmic norms, differential inequalities); Heinzle and Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations* (CQG 2006, DOI 10.1088/0264-9381/23/10/016). The e^(-4s) source discrepancy law is directly derived here from the frozen pressure definition, not attributed to these papers.