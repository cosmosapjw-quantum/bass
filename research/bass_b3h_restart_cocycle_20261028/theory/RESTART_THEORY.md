# Closed-cut restart for affine population and reward systems

## Scope and source
This is a derived companion to the pinned B3h endpoint transaction, not a new atomic source, physical error calibration, B4 production restart, or new B3i consumption. Proper time t is in seconds, u=log(a/a0) and theta=t/T are dimensionless; p is a two-component abundance fraction. Source maps have inverse-second units. Counts and energies use the common V0=1 m3. The inherited scalar FLRW, effective-H and zero direct Ly-alpha recoil conventions remain. Metric (-,+,+,+), x0=ct. No new natural-unit convention is introduced.

## T1. Affine reward composition
Let b,M,a,L be continuous on a finite interval, p'=b-Mp and z'=a+Lp. The units of each row of z are fixed independently (count or J per V0); L has that row's units per second per fraction. Put X=(p,z,1). Its generator is [[-M,0,b],[L,0,a],[0,0,0]]. A transition has the form

    p_b=P_ba p_a+q_ba,
    z_b=z_a+R_ba p_a+r_ba.

Substituting the first interval into the second proves

    P_ca=P_cb P_ba; q_ca=P_cb q_ba+q_cb;
    R_ca=R_ba+R_cb P_ba; r_ca=r_ba+R_cb q_ba+r_cb.

The identity is (I,0,0,0); associativity follows either by substitution or block-matrix multiplication. Existence and uniqueness follow from the standard fundamental matrix and variation-of-constants theorem. The nonautonomous flow property is Eq.(7) of Baake and Schlaegel, The Peano-Baker series, https://arxiv.org/html/1011.1775, read through Exa. No commutativity of M at different times is assumed. exp(-integral M) is not a general substitute. This is a standard linear-systems identity specialized to source-owned atomic rewards, not a new general theorem claim.

## T2. State contraction does not erase accumulated reward error
Assume -M is Metzler and every column sum of M is at least gamma>0. Then mu_1(-M)=max_j[-M_jj+sum_(i!=j)|M_ij|]<=-gamma. For a represented path p_hat with residual r=p_hat'-b+M p_hat, e=p_hat-p obeys e'=-M e+r. Variation of constants and the induced one-norm give

    ||e(t)||_1 <= exp[-gamma(t-c)] eps_c
                  + integral_c^t exp[-gamma(t-s)] ||r(s)||_1 ds.

For one unchanged reward row L, |delta z(t)| is bounded by its preserved prefix error plus integral ||L(s)||_infinity ||e(s)||_1 ds. If ||L||_infinity<=ell and ||r||_1<=rho, this yields

    |delta z| <= eps_z + ell eps_c phi_gamma(D)
               + ell rho [D/gamma-phi_gamma(D)/gamma],
    phi_gamma(D)=(1-exp(-gamma D))/gamma.

For gamma=0 the limits are D and D^2/2. This follows directly by exchanging two nonnegative integrals. A scalar homogeneous reset error e(c)=delta, e'=-gamma e, and z'=ell e attains the first term exactly. Thus e(t) tends to zero while the integrated error tends to ell*delta/gamma. The augmented population-plus-reward system is not itself strictly contracting because accumulated rewards persist. For coefficient changes include delta b-delta M*p in the forcing; do not silently apply the same-law bound across a model change. A variable gamma(t) replaces each exponential by exp(-integral gamma), with no positive constant required if the actual integral is retained.

## T3. Global-clock and expansion rebasing
For a suffix beginning at t_c,u_c, define theta'=(t-t_c)/(T-t_c), beta=1-theta_c, theta_c=t_c/T. The identities theta=theta_c+beta theta' and u=u_c+u' imply, for integer j>=0,

    I_kj_global = exp(k u_c) sum_(r=0)^j binom(j,r)
                 theta_c^(j-r) beta^r I_kr_local,
    I_kj=integral exp(k u) theta^j p(t) dt.

The same relation holds for scalar F with p replaced by1. This is a binomial change of origin, not permission to reset the physical coefficients to the left endpoint. In the implementation all saved native moments stay in the original common-volume/global-clock basis. If densities were instead re-normalized to V_c, the additional V_c/V0 factor must be included once. It is NOT included for already common-V0 inputs.

For endpoint-tagged maps f_c^r=a_c^r+ell_c^r p with r=0,1, the nonnegative proper-time mixture is j_c=(1-theta)f_c^0+theta f_c^1. Each endpoint energy owner stays attached: Q_cs=(1-theta)e_cs^0 f_c^0+theta e_cs^1 f_c^1. Multiplying separately interpolated energy and rate changes the model. The weighted count of each tag on a panel is

    C_c,k^0=NH[a_c^0(F_k0-F_k1)+ell_c^0 dot(I_k0-I_k1)],
    C_c,k^1=NH[a_c^1 F_k1+ell_c^1 dot I_k1].

Add only disjoint panel increments; cumulative prefixes are not additive disjoint bins.

## T4. Separate physical exchange and geometric work
Let U_s=V*rho_s be sector energy per reference cell with a prescribed constant w_s. Homogeneous expansion gives U_s'=-3w_s H U_s+V*cQ_s^0. Consequently Z_s=exp(3w_s u)U_s has additive event increments. Here k=0 for rest/internal energy, k=2 for nonrelativistic monatomic gas, and k=1 for radiation. Density at an endpoint is rho_s=exp[-(3+k)u] Z_s/V0. These factors preserve the source's finite-volume ownership; geometric dilution/work is not collision heating. A finite-interval average Q is not a pointwise source for arbitrary later intervals. General anisotropic stress or changing EOS needs the corresponding work law and is not inferred from this scalar certificate.

## T5. Closed-form new prefix incoming moment
The represented incoming occupation is f_in(u)=d0+s*u+exp(-A exp(u)) within a native linear segment. For integer k>0 a primitive of its departure contribution is

    exp(k u)*[(d0+s u)/k-s/k^2].

The Wien integral from a to b is A^(-k)[Gamma(k,A exp(a))-Gamma(k,A exp(b))], with Gamma(k,x)=(k-1)! exp(-x) sum_(m=0)^(k-1) x^m/m!. Thus one new prefix count uses G*integral exp(3u)f_in du; weighted energy uses G*E21_J*integral exp(4u)f_in du. Differentiate the primitive to check the sign. The suffix is defined as the saved whole incoming value minus this prefix, so the old whole incoming data and its unknown quadrature remainder are preserved. This does not certify the old physical incoming history.

## Stored scalar F recovery without old quadrature
The archived certified_quad.integrate computes an ordered sum of positive Gauss-weighted scalar values and a gross_scale=sum(abs(term)). For the scalar integrands exp(k*u)*theta^j/H, H>0 and 0<theta<1 at every interior Gauss node; hence gross_scale equals that same positive sum. The two stored scalar F1j/F2j gross_scale rows therefore recover their per-panel scalar values, under this specific source-code and positivity argument. This is not valid for arbitrary signed quadrature. F00 is duration; F01 is (t_b^2-t_a^2)/(2T). Preserve the saved MP70 rounding/conditional bounds; summing stored decimal strings can differ in their last printed places from the original sum before printing.

## Restart packet, validation and boundaries
A closed-cut packet must retain source/model/frame/clock/V0 identities, absolute time and step index, p, all accumulated count/energy moments, finite stocks, work/counter totals and committed transaction status. Pending transactions are rejected by this narrow interface, not silently discarded. This study tests exact float-hex roundtrip for a fixed global RK4 schedule; it does not implement FSAL, variable-step controller, error estimator, solver epochs or B4's full pending-transaction journal. The native result applies only at the existing two-panel boundary, not arbitrary newly sampled cuts. No native ODE, B3i RHS, old quadrature or prior test campaign is run.

## Literature and review status
Baake/Schlaegel Eq.(7) and Theorem2 support the standard flow construction. Soederlind2006, BIT46,631-652, DOI10.1007/s10543-006-0069-9 supplies logarithmic-norm context; the inequalities above are derived here. SciSpace returned reset-control and reaction-count papers but no exact BASS-specific source; none supplies missing native data. Wolfram independently evaluated finite algebra identities, not the full numerical implementation. Native subagent dispatch and distinct-author R6/C9 reviews are NOT_RUN; serial self-check is not independent admission. Physical radii and global completion remain null, L4=false; canonical DAG28/88 delta0.
