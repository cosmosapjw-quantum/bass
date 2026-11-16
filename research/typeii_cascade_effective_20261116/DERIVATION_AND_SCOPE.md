# Bound-bound cascade and conservative effective interface

## Assumptions, units and input authority
All microscopic rates use proper atomic/electron-rest seconds. Metric convention(-,+,+,+), h=2pi hbar, energies in J, cross sections in m^2, electron density in m^-3, capture coefficients in m^3/s. The prescribed source BASS fields use mean label1+z_mean=1701 exp(-tau_H), not observed photon redshift. No new cosmological population evolution is performed; parent Tm and ne are fixed at each local state. A later Hubble-time evolution would require division by Gamma H_n, without conflating photon line escape with this time conversion.

Bound levels are 1s,2s,2p,3s,3p,3d and the seventh state is an ion tracer exchanging electrons with a prescribed reservoir. Unaligned substates, nonrelativistic infinite-mass hydrogen convention, unpolarized external radiation, isotropic Maxwellian relative electrons, no collisional excitation or line profile, no self-consistent field evolution. The finite-band Milne kernels are reused unchanged from parent PR337. The statistical weight is g_nl=2(2l+1), with electron spin normalization inherited from that parent.

## Exact Coulomb E1 construction
With x=r/a0, the radial wavefunction is
R_nl(r)=a0^(-3/2)(2/n)^(3/2)[(n-l-1)!/(2n(n+l)!)]^(1/2) exp(-x/n)(2x/n)^l L_(n-l-1)^(2l+1)(2x/n).
The dimensionless radial matrix element I_ul=integral x^3 Rtilde_u Rtilde_l dx is evaluated by expanding the finite Laguerre polynomial and integrating each monomial against exp[-(1/nu+1/nl)x]. Independent infinite-interval numerical quadrature checks the result.

For |lu-ll|=1, unaligned upper substates and summed photon polarization,
A_ul=e^2 omega_ul^3/(3 pi epsilon0 hbar c^3) [max(lu,ll)/(2lu+1)] a0^2 |I_ul|^2.
The dimensions are s^-1. Upper/lower transition energy is Delta=chi_lower-chi_upper from the unchanged parent binding convention, so every loop energy closes. The n3 source binding is rounded to0.111111Ry; its radial integral is still the exact integer-n Coulomb expression, a stated approximation rather than precision spectroscopy.
R_ul=A_ul(1+nbar(Delta)), R_lu=(g_u/g_l)A_ul nbar(Delta).
For an isotropic common-temperature Planck field, R_lu/R_ul=(g_u/g_l)exp[-Delta/(kBT)]. For a BE field with n=[exp(E/kBT+eta)-1]^-1, one-photon absorption introduces an additional exp(-eta).

NIST persistent-line values provide an external scale check, not the code's authoritative constants. The2p scale6.26485e8 is the midpoint of NIST's6.2648e8 and6.2649e8 fine-structure values, not a separately tabulated multiplet average. The3p1s scale1.6725e8 is a tabulated unresolved entry. Infinite mass and neglected fine structure explain why no machine precision equality is demanded. The initially attempted NIST HTML download failed; the values were verified through retrieved official NIST page text, and are not claimed byte-archived.

## Two-photon kernel and normalization
Original source HYREC hydrogen.c sums A2s weights over NSUBLYA and rescales them to L2s1s=8.2206 s^-1. Its sub-Lyman-alpha entries represent the larger photon of an unordered pair: y=Ehigh/E21 >1/2, y<1. Use this half-spectrum ONCE. Higher-n resonant two-photon additions are excluded because their sequential resonances are already represented by the E1 cascade network.

Source photon-sharing fractions y are mapped to the parent Delta_(2s1s). Original source E21=10.198714553953742eV is reduced-mass, whereas the parent model gap is10.204269842245498eV. Retaining source weights and amplitude while mapping sharing is an explicit hybrid energy-convention choice. It ensures detailed balance/energy closure for this chosen model; it does not establish exact isotope physics.

Leading spin-independent nonrelativistic E1E1 emission has the normalized unpolarized angular factor W(c)=3(1+c^2)/4=1+P2(c)/2. For an axisymmetric prescribed occupation define n_l(E)=1/2 integral[-1,1] n(E,mu)P_l(mu)dmu. The pair average is
B(E1,E2)=n0(E1)n0(E2)+(1/2)n2(E1)n2(E2).
Consequently the higher-photon quadrature weights w_b give
D_2gamma=sum_b w_b[1+n0(E1b)+n0(E2b)+B(E1b,E2b)],
U_2gamma=(g2s/g1s)sum_b w_b B(E1b,E2b),
with E1b+E2b=Delta and g2s/g1s=1. Literal pair-angle and azimuth integrations independently verify this reduction. Vacuum D=sum w=8.2206. At beta=0 and eta=0, U/D=exp(-Delta/kBT), bin by bin. With BE eta, U/D=exp(-Delta/kBT-2eta). For beta!=0 the atom sees a prescribed anisotropic Planck transform, not a scalar blackbody.

The loop3p->2s->1s->3p emits two net photons. Its log product of forward/reverse rates is2eta at beta=0: energy sums telescope, but photon number does not. Hence channelwise BE relations from the bound-free-only parent do NOT guarantee global equilibrium after number-changing cascades are included. A maintained nonthermal bath can drive stationary cycle currents. No full-bath H-theorem is claimed.

## Positive conservative stationary elimination
Let Q be a finite column generator with Qij>=0 (i!=j), 1^T Q=0. The bound-free columns are Q_(ion,i)=beta_i and Q_(i,ion)=ne alpha_i. Partition R=(1s,2s,2p,ion), F=(3s,3p,3d). Assume every eliminated state reaches retained states with probability one (transience). Then
N=(-Q_FF)^(-1)=integral[0,infinity] exp(Q_FF t)dt >=0.
For this finite model Q_FF is diagonal with strictly negative outgoing rates, so the condition is directly inspectable.
Set L=N Q_FR, P=Q_RF N, S=Q_RR+Q_RF L.
Offdiagonal entries of S are nonnegative. The original F-column identity1_R^T Q_RF=-1_F^T Q_FF gives1_R^T P=1_F^T, i.e. exit probabilities normalize. Combining the R-column identity with this gives1_R^T S=0. S has units s^-1; N has seconds; L,P are dimensionless.

For stationary Qp*=0, p_F*=Lp_R*. Conversely any Sr=0 lifts to a full stationary vector. If r is normalized on retained states, the physical normalized full vector is [r,Lr]/[1+1_F^T Lr]. The stored fast population must not be discarded. If Q is reversible with a positive thermal vector pi, the similarity D^(-1/2)QD^(1/2), D=diag(pi), is symmetric. Its Schur complement is symmetric too, proving retained thermal reversibility. This proof does not assume nonthermal cycles are reversible.

For retained bound state i the finite-network effective capture is alpha_eff_i=S_(i,ion)/ne; photoionization beta_eff_i=S_(ion,i). These already contain eliminated-state paths. Adding direct coefficients again double counts microscopic channels. They are not complete high-n HYREC coefficients, and no such replacement is made.

## Exact dynamic elimination and storage
For a constant local generator and proper time t,
p_F(t)=exp(Q_FF t)p_F(0)+integral_0^t exp[Q_FF(t-u)]Q_FR p_R(u)du.
Substitution into the retained equation gives the memory kernel plus an initial fast-state forcing. In Laplace frequency s,
K(s)=Q_RR+Q_RF(sI-Q_FF)^(-1)Q_FR,
[sI-K(s)]p_R(s)=p_R(0)+Q_RF(sI-Q_FF)^(-1)p_F(0).
The retained block of the full resolvent and this expression are algebraically identical. S=K(0) is a stationary/zero-frequency limit, not the entire chronological generator. Ignoring the forcing for initially occupied F loses that population outright.

At low frequency, (sI-Q_FF)^(-1)=N-sN^2+O(s^2), giving storage matrix C=I+Q_RF N^2 Q_FR. The exact identity
1_R^T C=1_R^T+1_F^T L
shows how fast-state occupancy contributes to total storage. C^-1 S is NOT asserted to be a positive Markov generator for arbitrary rates. Source frequency/time tests measure, rather than assume, a validity interval.

## Particle and energy readouts
Assign bound atomic energies epsilon_i=-chi_i, epsilon_ion=0. Each bound-free event has photon energy chi_i+K, electron kinetic energy K and bound/ionization energy chi_i. Each downward E1 or2gamma event emits totalDelta and lowers bound energy byDelta; photon multiplicity is respectively one or two. Thus explicit channel readouts obey J_photon+J_electron_kinetic+epsilon^T Qp=0 for any positive tracer population. The electron reservoir receives the appropriate charge flux; a self-consistent evolving electron density is a separate nonlinear closure.

At the stationary lift p_F=Lp_R, fast derivatives vanish, and epsilon^T Qp=epsilon_R^T S p_R. Therefore the reduced energy balance is obtained by lifting and evaluating the ORIGINAL channel readouts. S alone does not encode how many cascade photons, their energies, or their frequency distribution were emitted. For time-dependent populations, the memory-state reconstruction is needed; one must not differentiate Lp_R and simultaneously pretend Q_FF p_F+Q_FR p_R stays zero without approximation.

## Validation and interpretation
Exact radial formulas, scalar thermal ratios, pair-angle quadrature, exit normalization, stationary reconstruction, block resolvents, initial fast-state memory and source energy ledgers were actually checked. A diagnostic matrix max error and a slow-column conservation admission defect were observed and repaired with retained failing logs and regression tests. Conservation now uses each column's own outgoing/incoming scale, not the largest rate in the entire matrix.

The model intentionally omits line trapping/escape, solved radiative transfer, nonlinear electron feedback, high-n completion, helium excited states, spectral profile broadening, sublevel alignment and Einstein/thermal backreaction. It is a source-conditioned finite microscopic interface. Next positive construction: LYMAN_LINE_TRANSPORT_AND_CONSERVATIVE_ESCAPE_INTERFACE, with optically-thin and thermal limits and no unqualified Sobolev substitution in a nonmonotone directional frequency flow.

Primary references: https://arxiv.org/abs/1006.1355 ; https://arxiv.org/abs/1011.3758 ; https://arxiv.org/abs/0705.3033 ; https://arxiv.org/abs/1203.6601 ; https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable3_a.htm . Original code/atomic table bytes are under sources/ and bound by PROVENANCE.json.
