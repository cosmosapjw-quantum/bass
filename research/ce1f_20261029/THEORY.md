# Positive angular-cell stress certificate

Let a table contain exact nonnegative total cell energies w_C, with positive sum. In each first-octant solid-angle cell C=[mu_a,mu_b]x[phi_a,phi_b], put F0=w_C/(8 Delta mu Delta phi) and reflect in all coordinates. This defines a nonnegative integrable angular function; jumps on cell boundaries are admissible for the source integrals. Let x_i=q_i^2, x in the probability simplex, and m_C=cell-average x. Every original cell can be subdivided while dividing its energy by exact area fractions; this changes the quadrature, not F0.

For u=t/Tstar and ell_i=log a_i, define b_i=exp(-2ell_i), v=exp(-sum ell), r=sqrt(b dot x). Continuum energy and pressures are E=v sum_C w_C <r>_C and P_i=v sum_C w_C <b_i x_i/r>_C. Exact symmetry makes flux/offdiagonals vanish; sum_i P_i=E. Differentiation gives partial_ell_j E=-E-P_j and sum_j |partial_ell_j P_i|=4P_i<=4E0 in the expanding octant. The diagonal Einstein evolution is ell_i'=h_i and h_i'=-theta h_i+P_i, theta=sum h. Hamiltonian H=h_x h_y+h_x h_z+h_y h_z-E satisfies H'=-2theta H. All h_i>=0 is forward invariant since h_i'=P_i>=0 on h_i=0, and E<=E0.

Means are analytic: m_z=(mu_a^2+mu_a mu_b+mu_b^2)/3; c=1/2+[sin(2phi_b)-sin(2phi_a)]/[4Delta phi]; m_x=(1-m_z)c,m_y=(1-m_z)(1-c). Define exact coordinate ranges [l_i,u_i] by endpoint products of mu^2,cos^2phi,sin^2phi. Popoviciu gives sigma_i^2<=w_i^2/4 for widths w_i=u_i-l_i, and V=sum sigma_i^2<=sum w_i^2/4.

For a uniform geometry box 0<=ell_i<=L, put d=1-exp(-2L), r_min=exp(-L), Q=(3/4)d^2 V. For Delta=x-m, sum Delta=0, hence E[(b dot Delta)^2]<=Q by subtracting (max b+min b)/2 from all b_i and using ||Delta||_1^2<=3||Delta||_2^2. For f_i=b_i x_i/sqrt(b dot x), along x(t)=m+tDelta,

f_i''(t)=-b_i Delta_i(b dot Delta)/(b dot x(t))^(3/2)+(3/4)b_i x_i(t)(b dot Delta)^2/(b dot x(t))^(5/2).

The first Taylor term averages to zero, and integral_0^1(1-t)dt=1/2. Thus the cell pressure bias is bounded by

|<f_i>-f_i(m)| <= (1/2)r_min^-3 sqrt((w_i^2/4)Q)+(3/8)u_i r_min^-5 Q.

We used b_i<=1 and v<=1 for a uniform bound. This bound is second order in cell diameter and vanishes at L=0. It does not truncate the physical angular field or dynamics. Direct range/Lipschitz and geometric-midpoint rules were considered; the centered mean rule gives a genuinely smaller uniform-cell error and preserves the initial second moments.

Stored numerical rays n are binary64 square roots of interval-enclosed means; X_i=n_i^2 is treated as an exact rational product, not a rounded numpy square. Set epsilon_i>=|X_i-m_i|, epsilon_1=sum epsilon_i, s_min=min(1,sum X), and r0^2=exp(-2L)s_min. For the straight segment between m and X, the mean-value theorem bounds the stored correction by epsilon_i/r0+(1/2)M_i epsilon_1/r0^3, with M_i=max(m_i upper,X_i). A separate |w_C-w_C,stored| sqrt(sum X) term accounts for mass conversion. This includes nonunit stored rays and all actual stored masses. MPFR192 outward operations and rational-to-interval conversion evaluate each positive bound. Cell mean trig values use directed pi and sin/cos with explicit extrema handling, not a globally monotone sine assumption.

Initial continuum E0=sum w_C is exact. Exact-real discrete E0Q=sum w_stored sqrt(sum X) is enclosed independently of float64 summation. Continuum shear uses exact binary sx,sy and sz=-(sx+sy); each mean expansion follows sqrt((E0+sum s_i^2/2)/3)+s_i. Compare those intervals against the stored floating initial h, including stored trace and root error. Both continuum and exact discrete data must be all-expanding. Set Emax>=max(E0,E0Q), not just the rounded numerical energy. With h_i'<=Emax, ell_i<=max(h_i(0))*u+Emax*u^2/2 for both models.

On that shared box let eta bound the pressure-source discrepancy. The geometry difference obeys Dini e_ell'<=e_h and e_h'<=4Emax e_ell+eta because the logarithmic infinity norm of the h-Jacobian is max_i(h_i-theta)<=0. For k=2sqrt(Emax), initial e_ell=0 and e_h=d0, e_h(u)<=d0 cosh(ku)+eta sinh(ku)/k and e_ell(u)<=d0 sinh(ku)/k+eta(cosh(ku)-1)/k^2. The discrete ODE initial condition is the actual stored floating h. A claim about the computed numerical trajectory additionally needs its time-error contribution; this unit reports that contribution as excluded.

Independent validation: symbolic Wolfram second derivative residual0; separate-agent proof rederivation; 96 independently integrated cells with no violations, maximum sampled ratio0.192238694. A geometric-midpoint substitution fails already for the isotropic full-octant z pressure (1/4 versus exact1/3 while centered bound0). The numerical validation tests the construction; the universal bound follows the preceding analytic inequalities. No new no-go is submitted, so NG1-NG7 admission is not invoked.
