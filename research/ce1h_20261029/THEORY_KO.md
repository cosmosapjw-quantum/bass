# BASS CE1-H: 초기 방향별 압력으로 제한하는 Bianchi-I 비교정리

Parent CE1-G PR #240 HEAD `0fd95e4baadf8982cdb1f9f81725b7b8e8fd0aa1`; CE1-F PR #239. PR #238 and corrected alternative PR #241 are independent evidence, not merged. Upper DAG 9/15, CE-1 PARTIAL.

## Definition and conventions

Signature (-,+,+,+). Diagonal reflection-even massless collisionless Bianchi I, Lambda=0, normal proper clock u=t/T_*, ell_i=ln a_i, h_i=T_* H_i, E,P_i=(8 pi G T_*^2/c^2)*(physical energy density,directional pressure). No collisions, polarization, tilt, spatial gradients, low-l closure, native production, or measured-sky acquisition.

For a positive finite angular-energy measure mu on S^2, put b_i=exp(-2ell_i), V^-1=exp(-sum ell), Z=sum b_j n_j^2. Then E=V^-1 int sqrt(Z) dmu and P_i=V^-1 int b_i n_i^2/sqrt(Z) dmu. The exact Einstein-Vlasov ODE is ell_i'=h_i, h_i'=-theta h_i+P_i, theta=sum h_i. The Hamiltonian constraint is sum_{i<j} h_i h_j=E.

## Lemma (derived): monotone pressure Jacobian

Define R_ij=V^-1 int b_i b_j n_i^2 n_j^2/Z^(3/2) dmu. Direct differentiation gives

    partial_(ell_j) P_i=-(1+2 delta_ij)P_i+R_ij.

Positivity gives 0<=R_ij<=P_i and sum_j R_ij=P_i. Therefore every Jacobian entry is nonpositive and the exact absolute row sum is

    sum_j |partial_(ell_j)P_i|=4P_i.

Consequently P_i(ell)<=P_i(0) for ell>=0. Integrating the Jacobian along the straight segment between two nonnegative ell vectors yields

    ||P(ell)-P(ell_tilde)||_infty <= L_P ||ell-ell_tilde||_infty,
    L_P=4 max_i P_i(0).

This follows constructively from CE1-G's existing Jacobian identities; no global novelty claim. It replaces CE1-G's conservative 4 Emax Lipschitz coefficient without changing the source, physical input or recorded path. P_i(0)<=E_cont(0)<=Emax ensures L_P<=4 Emax. The minimum of two independent outward upper bounds remains a valid upper bound.

## Exact original-cell initial pressure

The physical input is six first-octant cells with exact stored binary64 endpoints and cell energies E_C. Integer subdivision preserves the physical continuum. At ell=0,

    P_i(0)=sum_C E_C m_i,C,   m_i,C=mean_C[n_i^2].

For a cell [mu_a,mu_b] x [t_a,t_b] with t=2phi/pi,

    m_z=(mu_a^2+mu_a mu_b+mu_b^2)/3,
    C=1/2+(sin(pi t_b)-sin(pi t_a))/(2 pi (t_b-t_a)),
    m_x=(1-m_z)C, m_y=(1-m_z)(1-C).

The CE1-F `_cell_geometry` computes outward MPFR192 enclosures from exact rational edges; `initial_continuum_pressure_cap` accumulates exact binary cell energies with directed rounding. Sum_i m_i=1 and sum_i P_i(0)=E_cont(0) are exact identities. No nearest-rounded NumPy pressure replaces the continuum moment.

For mu=[0,.5,1], t=[0,.25,.75,1], E=[[.1,.25,.05],[.2,.15,.15]], the upper initial pressures are (0.3175105438719036,0.25748945612809654,0.32500000000000007), Emax=0.9, Pmax=0.32500000000000007. The Lipschitz coefficient drops from 3.6 to 1.3000000000000003, a 63.8889% coefficient reduction, not a 63.9% reduction of final error.

## Nonlinear error comparison (derived)

Let z solve the exact continuum ODE and z_tilde be CE1-G's piecewise exact-real stored binary Hermite cubic. Define r_ell=ell_tilde'-h_tilde and r_h=h_tilde'+theta_tilde h_tilde-P_Q(ell_tilde). CE1-G MPFR192 Taylor3 + analytic fourth-derivative remainder encloses whole-panel residuals; exact-binary knot jumps are added at each endpoint.

For expanding histories, the infinity logarithmic norm of D_h(-theta h) is max_i(h_i-theta)<=0. The new pressure lemma yields

    D+e_ell <= e_h+rho_ell,
    D+e_h <= L_P e_ell+eta_Q+rho_h,

where eta_Q is unchanged CE1-F continuum-vs-stored source error and rho are unchanged CE1-G panel residuals. With k=sqrt(L_P)=2sqrt(Pmax), the positive propagator is

    Phi(t)=[[cosh(kt),sinh(kt)/k],[k sinh(kt),cosh(kt)]].

Initial Hamiltonian mismatch, source error, and time residual plus binary knot jumps propagate separately and add by positivity. Emax remains unchanged in the exact-solution geometry box and source certification. Only the comparison coefficient is sharpened; substituting Pmax into the source box would be invalid.

## Verification and scope

Wolfram single-ray symbolic differentiation gave exact row-sum identity residual 0. Independent mpmath100 integration of the six rational cells returned P0=(0.317510543871903543737151...,0.257489456128096463895632...,0.325000000000000000693889...), inside MPFR192 intervals. Forty-eight high-precision positive-ray Jacobian probes gave no positive derivative and maximum row-sum identity residual ~1.43e-101. These checks are not a distinct-author R6/C9 review or formal MPFR program proof.

The lemma applies to positive cell-defined continuum measures and nonnegative expanding exact/reconstructed paths. It does not certify arbitrary unmeasured sky subcell content, generic Bianchi families, collisions, polarization, global tilt, native solver, or floating RHS independently of recorded binary paths.

Primary context: Lee, Nungesser & Tod, GRG 52,48 (2020), DOI 10.1007/s10714-020-02699-7 (small-anisotropy asymptotics, not this error theorem); Wu & Yang arXiv:1804.03363 (linear ODE Hermite residual method); Neumaier DOI 10.1016/S0168-9274(01)00155-6 (validated ODE/logarithmic norms). The present scoped comparison is directly derived, not attributed to those works.
