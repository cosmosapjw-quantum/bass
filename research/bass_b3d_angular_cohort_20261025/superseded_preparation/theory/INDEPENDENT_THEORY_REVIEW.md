# Independent theory contribution — BASS zero-incident source/transport coupling

Workflow: physmath-research-loop 1.0.0, inherited policy/R1–R10/C1–C10 read in this turn. Reviewer is a separate native agent with inherited model; this is not different-model review. No scientific campaign or historical test was rerun. This note distinguishes new derivations, owner-code reading, literature support and open input obligations.

## 1. Source reading and literature checks

Read current local exact-source copies:

- `bass_source/research/bass_b3b_finite_line_exchange_20261024/code/finite_exchange.py`
- `.../vendor/rec_line_source/code/line_source.py`
- `.../vendor/core.py`, `.../vendor/kinetic.py`
- Existing B3b `CONTRACT.md`, `REPORT_KO.md`, `HANDOFF_KO.md` at BASS final parent `0a088e1f8fca6618107525e687f930406ca32d18`.

SciSpace was actually called with a natural-language question about HyRec/Sobolev blue-side incident occupation and cell averages. It returned ten papers, including duplicate arXiv/journal records and incorrect repository-year metadata; use original papers for publication dates and equations. Raw response: `scispace_initial.json`.

Primary literature opened:

1. Ali-Haïmoud and Hirata, *HyRec: A fast and highly accurate primordial hydrogen and helium recombination code*, Phys. Rev. D **83**, 043513 (2011), DOI `10.1103/PhysRevD.83.043513`, arXiv `1011.3758v2`, https://arxiv.org/html/1011.3758v2 . Equations (73)–(78) distinguish the line/spike-profile average, incoming blue edge and outgoing red edge; (94) transports outgoing data to the next incident edge with retarded free streaming.
2. Ali-Haïmoud, Grin and Hirata, *Radiative transfer effects in primordial hydrogen recombination*, Phys. Rev. D **82**, 123502 (2010), DOI `10.1103/PhysRevD.82.123502`, arXiv `1009.4697`, https://arxiv.org/pdf/1009.4697 . Equations (43)–(49) give the boundary solution, Sobolev escape factor and thick net line-crossing flux under the paper's stated approximations.
3. Strang, *On the Construction and Comparison of Difference Schemes*, SIAM J. Numer. Anal. **5**, 506–517 (1968), DOI `10.1137/0705041`. Publisher metadata and author's bibliography were retrieved. Publisher full-text open timed out; no unobserved full-text reading is claimed. The local second-order argument below is by direct flow expansion.

Web source refs available to the parent after its own open/find: `turn2view0` (HyRec HTML), `turn2view4` and `turn1view1` (Sobolev paper PDF), `turn0search0`/`turn0search11` (Strang publisher metadata). Raw web outputs are saved separately. Retrieval date: 2026-10-25 KST.

## 2. Incident trace remains a separate input

For constant source function and optical depth across a resolved line profile, write P=(1-exp(-tau))/tau. The literature-supported boundary relation is

    f_minus = exp(-tau)*f_plus + (1-exp(-tau))*f_eq,
    f_profile_average = P*f_plus + (1-P)*f_eq.

The REC locked momentum-cell average uses a different weight, G = integral phase-space measure over the cell. The profile relation does not identify that average with f_plus. Even a reconstruction from a true profile average requires f_eq and tau and amplifies errors by 1/P; the thick limit is poorly conditioned.

An explicit identifiability example uses s=(p^3-pL^3)/(pR^3-pL^3). With phase-space measure proportional to p^2 dp, both f0(p)=fbar and fa(p)=fbar[1+a(2s-1)] have the same cell occupation for |a|<1, while their upper-face traces differ by a*fbar. Thus the bridge's exact stored cell inventory does not close the face contract. This is a simple reconstruction ambiguity, not a new strong no-go claim.

For the existing thick owner let d=g-(g+1)x, f_eq=x/d and F0=8*pi*H/lambda^3. The positive channels used by B3b have

    R_down=F0*x*(1+f_plus)/d,
    R_up=F0*g*(1-x)*f_plus/d,
    R_net=F0*(f_eq-f_plus).

Since g*(1-x)=d+x, R_down=F0*f_eq*(1+f_plus) and R_up=F0*f_plus*(1+f_eq). The incident face flux is F0*f_plus (with the corresponding directional q weighting), and R_up can exceed it. These are owner-defined positive channels with a shared induced/recycled term F0*f_eq*f_plus. A finite receiver must either explicitly own that local process or implement the correct conservative net boundary flux. Simply withdrawing the gross R_up from independent blue-face photons would add a new, unjustified donor model. At f_plus=0 this distinction disappears: only the source's actual upper atomic population supplies emitted photons.

Missing real-input obligations remain face ID/orientation and trace reconstruction, spectral measure and support, time interpolation/retardation, source frame and hydrogen proper clock, treatment of line-internal radiation, and exclusive owner of internal energy and native atomic terms. They must be resolved in the actual REC provider, not filled with this diagnostic initial state.

## 3. Full coupled Bianchi-I diagnostic is a closed conditional model

Suggested narrow model: diagonal Bianchi I, no curvature or rotation, comoving cold recoil-free two-level atoms, scalar unpolarized photons represented by the admitted source's finite positive 14-ray emission cohorts. Atoms are split into three **accounting** sectors:

    rho_exc = alphaL*E_line*N*x,
    rho_ground = alphaL*M_ground*c^2*N,
    rho_gamma = sum(packet energy weights).

The first two belong to the same atoms and both have p=pi=0. N is one physical number density. Separating the two energies prevents loss of resolved excitation when adding it to ground rest energy; it does not create a reservoir. Specify M_ground explicitly and state any approximation to its binding energy. The exact source card, collapsed-level closure, recoil omission and physical coefficient uncertainty remain inherited.

Initial photons are exactly empty; this is a new declared diagnostic initial state. It is not the real REC35x26 bootstrap and is not obtained by changing that bootstrap's f_plus. Initial x in [0,g/(g+1)), N>0, directional expansion positive and whole-interval opacity are required.

Let prime denote tau=c*t/L, h=HL/c, sigma=(L/c)*sigma_phys, alpha'=h and beta_i'=sigma_i. The collisionless/Einstein subflow A has x'=0 and

    N(tau1)=N(tau0)*exp(-3*Delta alpha),
    k_i(tau1)=k_i(tau0)*exp(-Delta alpha-Delta beta_i),
    w(tau1)=w(tau0)*exp(-3*Delta alpha).

These are exact diagonal Bianchi-I characteristic formulas. Integrate h,sigma,alpha,beta with the current core RHS and reconstruct all stresses from the actual cohorts. This avoids pretending that an independently accumulated floating photon rho is exact to the parent's 256eps transaction threshold.

The source subflow C freezes geometry and N by definition; H,S=sigma/h are consequently constant within that subflow. Apply the existing f_plus=0 finite source map with dt_s=(L/c)*Delta tau, atomic sector0 and photon sector2. Ground sector1 is unchanged during C. Recompute the owner from the actual stage state before each source call. The finite transaction itself preserves total instantaneous rho and flux, and therefore the instantaneous constraints. It returns state stress pi, not PiRate, and already-applied U/J remain zero.

The actual physical clocks are unchanged. Artificial effective exposure, if ever used as an analytic oracle, must not be reported as an elapsed proper-time source interval.

## 4. Directional-redshift support theorem

This is a new direct derivation using the exact imported core equations; it is not a literature-novel theorem claim. Let m_i=h+sigma_i, P_i=T_gamma^{ii}>=0, rho_d=rho_ground+rho_exc>=0. In diagonal Bianchi I the Hamiltonian residual is

    C = 3*h^2 - (sum sigma_i^2)/2 - rho_d - rho_gamma.

The core equations imply exactly

    m_i' + 3*h*m_i = rho_d/2 + P_i + (2/3)*C.

On C=0,

    m_i(tau)=exp(-3*Delta alpha)*[m_i(0)+integral_0^tau exp(3*Delta alpha(s))*(rho_d(s)/2+P_i(s)) ds].

Thus m_i(0)>0 implies m_i(tau)>0 throughout every regular exact solution. The source subflow changes no m_i or alpha, conserves C, and preserves nonnegative energies. It therefore preserves this cone too. Diagonal stress and paired directions preserve the diagonal/zero-flux subspace.

For all photon directions, d ln E/dtau = -(h+n.sigma.n)<=-min_i(m_i)<0. Initial vacuum has no blue-side support; source output is assigned to the outgoing red side E_line-minus-zero. Every emitted photon then moves strictly to lower energy. The full coupled selected model therefore maintains f_plus=0 without inventing a bath or bandwidth. The outgoing orientation is necessary; it is not a finite band. This uses the inherited unresolved-line/Sobolev-escape closure: the packet is already outside the resolved resonance. It is not a theorem that a photon just redward of the line center cannot be reabsorbed by a resolved finite-width line profile, nor does it cover frequency redistribution or thermal scattering.

For h0>0, h'<=-h^2 gives h<=h0/(1+h0*tau), Delta alpha<=log(1+h0*tau), and

    min_i(m_i(tau)) >= min_i(m_i(0))/(1+h0*tau)^3.

With h0=1, initial S=diag(-0.4,0.1,0.3), tau<=0.02, this lower bound is 0.6/(1.02)^3. It is an analytic exact-model bound; the numerical solution must separately control C and integration errors. Off-constraint the explicit 2*C/3 term provides the relevant defect mechanism.

There is also a conservative whole-interval opacity bound. STF plus C=0 and positive rho gives |sigma_i|<=2h and hence q_max<=3. Since x is nonincreasing, d>=d0; N/H >=(N0/H0)/(1+h0*tau)^2. Therefore the Sobolev depth t_Sob satisfies

    t_Sob/q_max >= t_Sob(0)/[3*(1+h0*T)^2]   for 0<=tau<=T.

This is sufficient to check the inherited source thick threshold without turning sampled minima into interval claims.

## 5. Splitting order and required discriminants

For the autonomous full vector field A+C, the compositions C(h/2) A(h) C(h/2) or A(h/2) C(h) A(h/2) are symmetric. Direct Taylor expansion through h^2 agrees with the full flow; the first defect is h^3 when the solution and subflows are sufficiently smooth inside the frozen domain. Global second order additionally requires a stable evolution and an A approximation whose accumulated error is smaller than the splitting error. Recomputing geometry-dependent source coefficients at each C is essential. Holding the initial H,N,S through the entire macro interval would define a different model.

Finite 14-ray source cohorts form the angular model. Time refinement checks time splitting of that model; it does not independently establish continuum angular convergence. Further angular order and full native inputs remain separate.

Useful discriminants:

- Source-off recovery of exact Bianchi-I packet redshift/dilution.
- Zero-duration/zero-upper-population/vacuum handling and existing parent source transaction reuse.
- Hamiltonian and zero-flux constraints, no projection or clipping.
- e^(3alpha)*N and e^(3alpha)*(N*x+n_gamma) conservation.
- Separate excitation+photon energy-work residual: d(rho_exc+rho_gamma)/dt +3H(rho_exc+rho_gamma+p_gamma)+sigma_phys:pi_gamma =0. Rest-mass dilution is checked separately so it cannot hide a reaction-energy error.
- Direct source exchange conservation and attribution, keeping U/J zero for finite increments.
- Monotone photon energy relative to E_line, paired-direction flux, source q positivity, analytic global opacity lower bound.
- Successive step ratios and a tighter A solve on the finest step, reporting denominators and keeping the inherited2e-8 selected gate.
- A fractional error normalized only to total ground rest energy would conceal the small radiation/excitation dynamics; use each relevant sector's nonzero scale and a gross emission scale near vacuum.

The proposed coupled unit can be admitted only after actual current execution and independent code checks. This theory review does not claim those runs. Finite real REC absorption remains input-dependent regardless of success here.

## 6. Prescribed-background oracle (a distinct check)

For constant H>0 and fixed diagonal S, N=N0*exp(-3Ht). With b=g+1, z=b*x0/g and eta0=8*pi*H/(g*N0*lambda^3), define

    F(v)=v-z*(1-exp(-v)),
    omega(T)=eta0*expm1(3HT)/(3H),
    F(vT)=omega(T), x(T)=x0*exp(-vT),
    s(v)=log1p[(3H/eta0)*F(v)]/(3H).

F'(v)=1-z*exp(-v)>0 for x0<g/(g+1), so there is exactly one nonnegative root. The independent exact comoving count is

    n_gamma(T)=N0*exp(-3HT)*x0*(1-exp(-vT)).

For a cohort direction n_j set r_j(d)=sqrt(sum_i n_ji^2*exp[-2H(1+Sii)*d]). Then the energy and spatial tensor follow bounded one-dimensional quadrature:

    rho_gamma(T)=E*N0*exp(-3HT)*x0 * integral_0^vT exp(-v)*sum_j A_j*q_j*r_j(T-s(v)) dv,

    T_ii(T)=E*N0*exp(-3HT)*x0 * integral_0^vT exp(-v)*sum_j A_j*q_j*n_ji^2*exp[-2H(1+Sii)*(T-s(v))]/r_j(T-s(v)) dv.

For the actual14ray rule, the angular energy sum reduces to three axis terms with weights2(1+Sii)/15 plus one cube term with weight3/5. This avoids a repeated time ODE in the oracle. It checks source/transport coupling on a prescribed background and must not be reported as an Einstein-coupled reference. The root's subsequently frozen B3c1 contract selects this oracle as a required discriminant.

## Provisional result

Theory: PASS_SCOPED for the conditional diagonal Bianchi-I, f_plus=0, two-level source/packet construction and the support/opacity bounds. Real receiver finite absorption: input obligations remain open. Numerical coupled execution and code verification: not performed by this reviewer. New strong no-go: none claimed. Root owns final scientific admission and publication.
