# Units, coupled support derivation, and independent prescribed oracle

This is a direct derivation for the frozen BASS B3c1 contract, not an empirical recombination claim. Signature is (-,+,+,+). All sums below are over i=1,2,3 or the actual admitted finite photon rays. Quantities without SI subscripts in the Einstein equations use the fixed BASS scale. The literature/owner distinctions and unresolved real REC receiver contract are in `INDEPENDENT_THEORY_REVIEW.md`.

## 1. Fixed scale and clocks

Take the diagonal Bianchi-I metric

    ds^2 = -c^2 dt^2 + sum_i a_i(t)^2 (dx^i)^2,
    a_i(t)/a_i(0) = exp[alpha(t)+beta_i(t)],  sum_i beta_i=0.

The comoving hydrogen proper clock is t. With one constant L,

    tau=c*t/L, h=H*L/c, sigma_i=(L/c)*sigma_phys,i,
    alpha'=h, beta_i'=sigma_i, alphaL=(8*pi*G/c^4)*L^2.

Here H=(1/3)sum_i(dot a_i/a_i), and directional expansion is H_i=H+sigma_phys,i. A prime is d/dtau and a dot is d/dt. alphaL has dimensions m^3/J, while h,sigma_i,tau,alpha,beta_i are dimensionless. The source uses S_i=sigma_i/h and requires H>0; the imported Einstein RHS contains no division by H.

| Quantity | Definition | SI dimension |
|---|---|---|
| N,n_u,n_gamma | proper number densities | m^-3 |
| x | n_u/N | 1 |
| E_line | h_P*c/lambda=2*pi*hbar*c/lambda | J |
| Pstar | fixed momentum scale, selected E_line/c | kg m s^-1 |
| k_i | p_phys,i/Pstar | 1 |
| w | alphaL*c*Pstar*proper packet number density | 1 |
| rho,p,pi | alphaL times corresponding SI energy density/stress | 1 |
| k_line | 8*pi*H/(N*lambda^3) | s^-1 |
| finite D_down,D_up | integrated event count per proper volume during frozen source step | m^-3 |
| U | kappa*L^3*E_dot/c | 1, rate in dimensionless tau equation |

The last row concerns an unapplied rate. A committed finite source step has already changed state rho; its outgoing U,J are zero. State pi is never replaced by PiRate. During split composition a source substep of length delta_tau uses dt=(L/c)*delta_tau in the exact owner. The outer time is advanced once, not by summing the durations of all split subflows.

The physical photon number is n_gamma=sum_j w_j/(alphaL*c*Pstar). The dimensionless energy and spatial stresses are

    rho_gamma=sum_j w_j*|k_j|,
    P_ij=sum_a w_a*k_ai*k_aj/|k_a|,
    p_gamma=tr(P)/3=rho_gamma/3,
    pi_ij=P_ij-delta_ij*rho_gamma/3.

The photon energy owner remains E=c*|p|. These are state weights; none of the formulas applies a state Doppler weight to invariant event rates.

## 2. Exact source map reused in a changing background

For f_plus=0 write b=g+1, d(x)=g-b*x and k=8*pi*H/(N*lambda^3). The inherited source ODE in proper time is

    dot x = -k*x/d(x),   0<=x<g/(g+1).

During source subflow C, H,N,S are frozen by the definition of C. Let z=b*x0/g, omega=k*dt/g and x1=x0*exp(-v). Integrating (g/x-b)dx=-k dt gives

    F(v) := v-z*(1-exp(-v)) = omega.

For 0<=z<1, F'(v)=1-z*exp(-v)>0 and F(0)=0. Hence every finite omega>=0 has one v>=0. For z>0 the root satisfies omega<=v<=omega+z; z=0 is the vacuum-upper-population endpoint. The existing owner evaluates stable endpoints and net increments. The positive count is D_down=N*x0*(1-exp(-v)), D_up=0, and the atomic endpoint is N*x1.

In the full coupled system H,N,S vary under A. Rebuilding their values before every C is exactly what the split flow requires. Calling C with the initial coefficients for all macro steps would integrate a different vector field. The emitted angular measure A_j*(1+n_j.S.n_j) is positive on the frozen source domain and has the admitted14ray second/fourth moments.

## 3. Characteristic reconstruction and physical counts

In diagonal Bianchi I, n=a=rotation=0, so the imported kinetic equations reduce to

    k_i'=-(h+sigma_i)*k_i,   (log w)'=-3h.

Therefore a cohort born at alpha_b,beta_b obeys

    k_i=k_bi*exp[-(alpha-alpha_b)-(beta_i-beta_bi)],
    w=w_b*exp[-3*(alpha-alpha_b)].

The comoving atom number density N*exp(3alpha)=N0 is constant under A and C. A has x'=0 and n_gamma'=-3h*n_gamma. C transfers exactly one upper excitation into one escaped photon, so N*x+n_gamma is unchanged at fixed alpha. Consequently

    exp(3alpha)*(N*x+n_gamma)=N0*x0

for the exact combined and exact split model. No finite spectral bandwidth enters this count. The initial photon state is the declared vacuum, not the previous REC bootstrap.

## 4. Directional expansion and support

Let rho_d=rho_exc+rho_rest. The imported diagonal Einstein equations are

    h'=-h^2-(sum sigma_i^2)/3-(rho_d+rho_gamma+3*p_gamma)/6,
    sigma_i'=-3h*sigma_i+P_i-p_gamma,
    C_H=3h^2-(sum sigma_i^2)/2-rho_d-rho_gamma.

Set m_i=h+sigma_i. Adding the first two equations and 3h*m_i yields

    m_i'+3h*m_i
      = 2h^2-(sum sigma_i^2)/3-(rho_d+rho_gamma)/6-3p_gamma/2+P_i
      = (rho_d+rho_gamma)/2-3p_gamma/2+P_i+(2/3)C_H
      = rho_d/2+P_i+(2/3)C_H.

The second equality uses 3h^2-(sum sigma_i^2)/2=rho_d+rho_gamma+C_H. The last uses 3p_gamma=rho_gamma. On C_H=0 this is a scalar linear equation with positive forcing, giving

    exp(3alpha(tau))*m_i(tau)
      = exp(3alpha0)*m_i0
        + integral_0^tau exp(3alpha(s))*(rho_d(s)/2+P_i(s)) ds.

The packet measure is positive and both atomic accounting energies are nonnegative. Thus initial m_i>0 stays positive. C changes neither geometry nor alpha and conserves total rho/flux, so it also preserves C_H and m_i. Opposite-ray symmetry preserves zero flux; diagonal stress preserves the selected diagonal metric subspace.

Photon energies satisfy

    (log E_gamma)' = -sum_i m_i*n_i^2 < 0.

The selected escaped-line source is placed on the **outgoing** side of the unresolved line. Vacuum initial support plus strict redshifting leaves no incoming blue trace. This conclusion uses the unresolved Sobolev-escape closure; a resolved line-wing/diffusion model would need its own support analysis.

On the selected regular interval, h'<=-h^2 and h>0 imply

    h(tau)<=h0/(1+h0*tau),
    alpha-alpha0<=log(1+h0*tau),
    m_i(tau)>=m_i0/(1+h0*tau)^3.

The displayed inequalities, not a sampled trajectory, establish the exact-model bound. With h0=1, m_min,0=0.6, T=0.02 the lower bound is 0.6/(1.02)^3>0.565. Numerically C_H is nonzero and contributes 2*C_H/3; the numerical residual must be reported independently.

For a whole-interval thick bound, tracefree sigma implies sigma_i^2 <= (2/3)sum_j sigma_j^2. On C_H=0 and nonnegative rho, sum sigma^2<=6h^2, hence sigma_i<=2h and q_max<=3. Since x cannot increase, d(x)>=d(x0), and

    N/H >= (N0/H0)/(1+h0*tau)^2,
    t_Sob/q_max >= t_Sob,0/[3*(1+h0*T)^2].

The source's inherited finite-opacity gate can use this conservative lower bound. It is a sufficient condition; no sharpness or new no-go result is claimed.

## 5. Energy work without the large ground-energy denominator

Let u=rho_exc+rho_gamma. The source exchanges these energies exactly and the ground sector does not participate. Under A,

    u'=-3h*(u+p_gamma)-sum_i sigma_i*pi_i.

Define W'=3h*(u+p_gamma)+sum_i sigma_i*pi_i, W(0)=0. Then u+W=u0. With diagonal photon stress and positive m_i,

    W'=3h*rho_exc+3h*rho_gamma+sum_i m_i*P_i >=0.

This is the expansion/shear-work ledger of the excitation plus radiation subsystem. It is normalized to its own initial excitation and cannot be hidden under the much larger ground rest energy. Ground rest energy separately dilutes as exp(-3alpha). The ledger is a numerical consistency check, not an exact interval enclosure or a second independent implementation of Einstein evolution.

## 6. Independent prescribed-H oracle

This diagnostic holds H>0 and S fixed and is therefore distinct from the coupled Einstein test. Let theta=H*t, N=N0*exp(-3theta), eta0=8*pi*H/(g*N0*lambda^3), z=(g+1)x0/g. Integrating the varying-density source equation gives

    g*v-(g+1)*x0*(1-exp(-v)) = K(t),
    K(t)=8*pi*expm1(3H*t)/(3*N0*lambda^3),
    x(t)=x0*exp(-v).

This is dimensionless K. Write F(v)=v-z*(1-exp(-v)); then F(vT)=eta0*expm1(3H*T)/(3H). The inverse emission-time map is

    s(v)=log1p[(3H/eta0)*F(v)]/(3H).

The exact infinitesimal emission count at s is R(s)ds=N(s)*x0*exp(-v)dv. Transport dilution from s to T cancels N(s)'s exp(-3Hs), so

    dn_gamma(T)=N0*exp(-3H*T)*x0*exp(-v)dv,
    n_gamma(T)=N0*exp(-3H*T)*x0*(1-exp(-vT)).

Set a_i(d)=exp[-H*(1+S_i)*d], r_j(d)=sqrt(sum_i n_ji^2*a_i(d)^2), q_j=1+sum_i S_i*n_ji^2. The final physical energy and principal stress are

    rho_gamma,SI = E*N0*exp(-3HT)*x0
                  * integral_0^vT exp(-v)*sum_j A_j*q_j*r_j(T-s(v)) dv,
    P_i,SI = E*N0*exp(-3HT)*x0
             * integral_0^vT exp(-v)*sum_j A_j*q_j*n_ji^2*a_i(T-s(v))^2/r_j(T-s(v)) dv.

For the exact14ray source rule define r_c(d)=sqrt[(a_1^2+a_2^2+a_3^2)/3]. The angular sums simplify to

    R(d)=sum_i [2*(1+S_i)/15]*a_i(d) + (3/5)*r_c(d),
    Q_i(d)=[2*(1+S_i)/15]*a_i(d) + a_i(d)^2/[5*r_c(d)].

Their trace identity sum_i Q_i=R supplies a useful independent check. A single monotone scalar solve plus these four bounded one-dimensional quadratures provides the reference, without replaying a time-stepping trajectory. Quadrature error estimates are numerical estimates, not certified bounds. For H*dt small, use expm1/log1p and an accurately resolved F(v); small-v cancellation must not be mistaken for splitting failure.

## 7. Direct order statement

Let L_A,L_C be Lie derivatives of the smooth autonomous vector fields on the admitted finite model. Expanding

    exp(hL_C/2) exp(hL_A) exp(hL_C/2)

through h^2 yields I+h(L_A+L_C)+(h^2/2)(L_A+L_C)^2. The defect starts at order h^3; on a regular compact admitted domain, stable iteration yields order2. The analogous Lie product has a local commutator defect at h^2 and global order1. This derivation assumes the exact subflow interpretation and sufficiently accurate A integration. The actual observed orders and gate results must come from the new run, not this formal expansion. Angular discretization is held fixed by this statement.
