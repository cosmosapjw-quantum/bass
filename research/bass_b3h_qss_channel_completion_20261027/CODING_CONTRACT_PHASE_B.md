# Phase B: finite native-source channel transaction in the actual Ly-alpha clock

Root scientific contract, 2026-10-27. Original DAG27/88. This is a selected,
explicit finite completion of the actual effective source, with physical
radii eS/en/eE/geometry/temporal/total null. It does not assert that an original
QSS history endpoint already solves a finite two-interface evolution.

## 1. Identity, execution, and scope

Read the admitted Phase A SOURCE_OPERANDS.json (SHA256
179784a094091324dd85ba727fddca1a592178099e9067ff254d6c44c60dd7bd),
the immutable source/input packet, and saved old photon/tube result. Do not
execute Phase A, the original native history, previous inverse/result/plot,
512 cohort reconstruction/transport, or either previous B3i consumer.

One new `phase_b` metered invocation is authorized after code/input freeze,
latest AGENTS/HEAD/parallel preflight and root execution message. Cumulative
allocation includes Phase A, Phase B and one saved-result plot: CPU60s,
wall180s, RSS768MiB, one thread. Phase A already used CPU1.129564s and
wall1.245074523s. A failed invocation is preserved and returned to root;
no automatic replay, tolerance change or model substitution is permitted.

Use mpmath at 70 decimal digits for new maps, finite counts and energy sums.
Binary64 source numbers are represented exactly via mp.mpf(float), with
their identities retained. This precision is needed to resolve excited
storage in the difference of much larger gross event counts. Build new
controls and the result in this one invocation. Only if transaction checks
pass, call the preserved B3i core.rhs exactly once for the new sector packet.
Implementation belongs to the delegated lower-tier worker; independent
Astra review and root admission follow actual output.

## 2. Explicit finite model

At the LEFT actual endpoint, construct all positive gross affine channel
maps after virtual-state elimination. Divide every non-Ly-alpha rate map by
the actual left Ralpha0. Freeze those ratios through the cell. At time u,
multiply them by the actual Ly-alpha activity Ralpha(u). This freezes source
ratios in activity time; it does not match the right source operator.
The separately admitted right operator is a source-variation diagnostic.

u ranges from0 to h=8.49e-5. Use the preserved strict-past incoming history
and its actual split knot; do not replace it by two endpoint interpolation.
The effective opacity g(u) is linear between the two actual x1s values.
nH(u)=nHref_cm3 exp(-3u), dt=du/H(u),
Ralpha(u)=LYA_FACT H(u)/(nH(u) g(u)). Define

 s(u)=integral_0^u Ralpha dt,
 ds/du=LYA_FACT exp(3u)/(nHref_cm3 g(u)),
 D(u)=du/ds=nHref_cm3 g(u) exp(-3u)/LYA_FACT.

Use nHref from the existing common-volume tube consistently in this clock,
not a slightly different rounded reconstruction of the same density.
H and proper duration are the preserved native geometry/tube values.
The actual incoming absolute occupation is departure+exp(-A exp(u)), using
the old tube's A and strict-past interpolation convention. New outgoing is
p_p/(3g). Direct Ly-alpha atomic current is Ralpha[p_p-3g fin]. Therefore

 NHref Ralpha dt[p_p-3g fin] = G exp(3u)du[fout-fin],
 G=3e6 LYA_FACT.

This exact clock identity is mandatory. Source g=1-xHII remains a prepared
opacity parameter; finite ground inventory is a separate count below.

## 3. Absolute physical gross maps

Use pre-diffusion radiation arrays for two-photon/Raman. A_i,b=-Tvr_pre[i,b]
and B_i,b=-Trv_pre[i,b] are nonnegative gross emission/absorption coefficients.
Diffusion edges are added exactly once: core-to139 A2p_dn and reverse Aup139;
core-to140 A2p_up and reverse Adn140; virtual b-to-b+1 Aup_b and reverse
Adn_(b+1), for100..138 and140..178. The virtual unknown X_b is absolute
g*fbar, not an atomic population.

For each virtual bin set C_b=Tvv_diag_b-Gamma_b from the saved source;
C_b must be positive. Form the physical virtual generator from those gross
coefficients (diagonal = C + all outgoing radiation/diffusion coefficients,
offdiagonal = negative incoming neighbor coefficients). This conservative
reassembly may differ from a saved rounded diagonal by arithmetic ulps only;
report its entry/gross discrepancy, requiring <=5e-14. Its positive source
is C_b*g0*(fin_departure_b+exp(-E_b/TR0)). Solve the tridiagonal system for

 X=a+B p, a=V^-1(source), B=V^-1(real-emission coefficients).

This is the absolute diffusion completion. Compare it with the native
departure form and explicitly record d=-T_diff q and
c_diff=d_r-Trv V^-1 d_v; do not call the known Wien-drive restoration an
unchanged native result. The full affine Wien shift and this correction are
different terms. The tiny source small-tau approximations remain identified.

Non-Ly-alpha gross atomic channels per proper second at left are:

* bound-free i: R_i=nH0 xe0 xHII0 Alpha_i, I_i=Beta_i p_i;
* real mixing: 2s->2p 3R2p2s p_s, 2p->2s R2p2s p_p;
* each radiative real/virtual bin: downward A_i,b p_i, upward B_i,b X_b;
* two core diffusion edges: downward A2p_edge p_p, upward reverse_edge X_b;
* Ly-beta and gamma effective real2s/ground channels: k_beta p_s,
  k_gamma p_s, k_l=3Ralpha0 c_l exp(-(E_l-E21)/TR0),
  c_beta=1.664786871919931, c_gamma=1.953125;
  upward beta=3Ralpha0 c_beta g0*(stored f_beta_in departure+exp(-E31/TR0));
  upward gamma=3Ralpha0 c_gamma g0 exp(-E41/TR0) (source background only).

Divide the above maps by Ralpha0. Sum their stoichiometries first to define
b_nL and M_nL in activity time. Add Ly-alpha downward p_p and upward
3g(u)fin(u). The resulting M=M_nL+e_p e_p^T is constant and

 dp/ds=b(s)-M p, b(s)=b_nL+3g fin e_p.

Require nonnegative gross maps/propensities, positive virtual Thomas
denominators, M offdiagonal nonpositive, positive column sums and eigenvalues.
Let gamma=min column sums of M>0. Let K=M^-1. M and source identities are
defined from the same gross maps, avoiding a tiny independent rounded
matrix inconsistency that could obscure finite storage.

Boundary C_b X_b and C_b g fin are algebraic loss/source, not literal gross
face crossing counts. If reported, actual virtual face gross uses
kappa_b=Gamma_b/tau_b and fout=fin+(C_b/kappa_b)(X_b/g-fin).
Use this only as a separate face diagnostic, never as an additional energy
credit on top of the same radiative events.

## 4. Constant-matrix finite solution and moments

Initialize p0 with the actual left absolute 2s/2p source populations. On each
smooth incoming segment use the three-term particular approximation

 p_a_part=K b-K^2 b_s+K^3 b_ss.

Carry a homogeneous layer exp(-M(s-s_j)) times the difference between the
incoming population and this particular solution. The residual is K^3 b_sss.
For a segment length L and carry-in state error E_j, the endpoint bound is

 E_end <= exp(-gamma L) E_j
          +(1-exp(-gamma L))*||K^3||_1 sup||b_sss||_1/gamma.

Include any explicitly omitted homogeneous tail bound. A homogeneous term
may be set to zero only when its norm bound is below the declared arithmetic
allowance; retain its bound and log exponent. The population is continuous
across the actual incoming-history knot, including the jump in derivatives.
Do not insert the approximation residual as a physical source.

Compute b derivatives analytically through D=d/ds relative to d/du.
For F=fin, g'=constant, W=exp(-A exp(u)), bound |W^(k)| using z=A exp(h):
Wmax=exp(-A), W1<=z Wmax, W2<=(z^2+z)Wmax,
W3<=(z^3+3z^2+z)Wmax. Include each actual departure slope in F1.
Define Bu1=3(|g'|Fmax+gmax F1),
Bu2=3(2|g'|F1+gmax F2), Bu3=3(3|g'|F2+gmax F3).
With c=nHref_cm3/LYA_FACT, use
Dmax=c*gmax, D1max=c*(|g'|+3gmax), D2max=c*(6|g'|+9gmax),
and bsss_bound=Dmax^3 Bu3+3Dmax^2 D1max Bu2
 +(Dmax D1max^2+Dmax^2 D2max)Bu1.
These are absolute bounds on the represented smooth segments, not sampling
estimates. A global population norm bound is
Pmax=max(||p0||_1, sup||b||_1/gamma).

Do not integrate a cosmological-width explicit stiff ODE. All unweighted
population integrals, including the fast initial layers, follow instead from

 Ip=integral p ds = K[b_nL*S+e_p*Nin_saved/NHref-(p1-p0)].

Use the saved independent incoming count if supplied with its actual
precision; keep its inherited numerical uncertainty separate. An error in
p1 gives an Ip error bounded by ||K||_1 E_end. The very small excited storage
must be resolved by the same MP event counts, not by a gross-only tolerance.

For energy propagation need weighted moments I_k=integral exp(k u) p ds,
k=1 for radiation and k=2 for nonrelativistic thermal energy. Define
w=exp(k u), w_s=k exp(k u)D and
w_ss=k exp(k u)D(kD+D'). Then

 I_k = K[B_k-w(h)p1+w(0)p0]
       +K^2[B'_k-w_s(h)p1+w_s(0)p0]+R_k,
 B_k=integral w b ds, B'_k=integral w_s b ds=k integral exp(k u)b du,
 ||R_k||_1 <= ||K^2||_1 Pmax*S*k exp(kh)Dmax*(kDmax+D1max).

Use the saved incoming pulled-back energy for the forcing part of B_1;
only the newly needed k=2 forcing moment is integrated. B'_k and clock
moments are new integrals, so their calculation does not replay the old tube.
These formulas include narrow initial layers through the boundary terms.

Evaluate the smooth, short-u integrals at MP70. Use independent16/24-point
MP Gauss-Legendre on each actual segment with relative agreement <=1e-40
(absolute scale based on integral of absolute terms). For exp/quadratic
polynomial/Wien terms a Cauchy circle radius0.01 around each segment midpoint
gives an analytic sup M_f; require hseg/(2r)<1 and attach the conservative
positive-quadrature Taylor remainder bound
2*hseg*M_f*(hseg/(2r))^(2n)/(1-hseg/(2r)).
For exp((3+k)u)/g(u), either the same pole-free Cauchy bound with
|g(z)|>=g(center)-|g'|r>0, or the geometric/exponential series bound is allowed.
Record a separate conservative MP arithmetic allowance of1e-55 times each
gross scale; it is an assumed arithmetic allowance, not a physical radius.

Controls: exact constant-M affine-forcing solution/integral identity,
known diagonal two-state case including finite layer, invalid negative
propensity and mismatched clock rejected; no old controls are replayed.

## 5. Finite stocks and actual energy owners

All counts are per common reference V0=1m^3. Initial
Nc=NHref*xHII0, Ns=NHref*p_s0, Np=NHref*p_p0,
Ng=NHref-Nc-Ns-Np. Initial electron count equals Nc. The small interface
stock is therefore included exactly rather than hidden in g=1-xHII.
Integrated gross event counts are NHref*(a*S+ell.Ip) for each activity map.
Update continuum/electron, ground and interface inventories using actual
stoichiometry. Finite continuum and ground reservoirs must remain positive;
their full gross debit bounds may certify this. Interface positivity follows
from the positive M-matrix system and nonnegative source, with numerical
error margins. Require endpoint storage sum vs event count identity to agree
within the derived truncation/quadrature/arithmetic bounds and <=1e-8 of its
own nonzero storage change. Do not clip a stock or invent a refill.

Energies use the saved native EI,E21 and bin energies, and exact eV_J.
Atom internal energies: continuum EI, interfaces E21, ground0.
Bound-free successful event owners are exactly the admitted Phase A moments:
recombination atom -chi, gas -Krec, radiation +(chi+Krec);
photoionization opposite with Kion. Do not additionally subtract3Tm/2.
Mixing2s/2p energy0. Direct Ly-alpha downward atom-E21, photon+E21,
gas/recoil0 (chosen native resonant model). For non-diffusive real->virtual,
observed radiation Eb and companion radiation E21-Eb; gas0.
For core->virtual diffusion, observed radiation Eb and gas E21-Eb.
For virtual b->c, radiation Ec-Eb and gas Eb-Ec, atom0.
For Ly-beta/gamma, observed E31/E41 and companion E21-E31/E41, atom-E21.
Every orientation reverses these energy signs. Each event energy sum is0.
Radiation observed/companion subledgers may be combined into ambient total;
virtual boundary bookkeeping must not credit the same energy a second time.

The finite ambient initial radiation stock is a declared spectral completion
from actual left stored data: use the native Planck bath outside the actual
311-bin energy range; inside, use the piecewise-linear stored mean departure
plus the source Wien background. This is an explicit represented spectrum,
not a new physical-error certificate. Test its positivity analytically in
each bin (linear+exp has endpoint or one interior minimum). Remove the
selected Ly-alpha incoming characteristic shell [E21,E21 exp(h)] from this
ambient spectrum and replace it with the separately preserved actual
incoming Ly-alpha tube. This prevents counting its background twice.
Use the common phase normalization Kgamma=G/E21^3, so
Uambient0=Kgamma*eV_J*integral E^3 f_ambient(E)dE. The Planck total is
Kgamma*eV_J*pi^4*TR0^4/15; the linear departure moments are polynomial;
Wien-minus-Planck and shell terms are bounded short integrals. No arbitrary
zero-energy bath or residual-defined stock is supplied.

Initial gas thermal energy is (3/2)NHref*(1+fHe+xe0)*Tm0*eV_J;
inert He uses the actual source fHe. Initial cold rest-energy carrier may be
NHref*mH*(1+3.97153*fHe)*eV_J, a distinct source-free dust sector.
Every energy owner must remain positive through the finite selected step.
Where a gross energy debit bound is too conservative, report it and use the
positive rate maps plus bounded partial moments; do not equate an overly
conservative debit test failure with physical negativity.

## 6. Transport, T and four-force, one new B3i call

Reuse the old completed Ly-alpha photon calculation as an immutable baseline:
Nout_new=NHref*Ip_p, Uout0_new=NHref*E21_J*I1_p.
DeltaN_correction=Nout_new-Nout_old;
DeltaU_correction=Uout0_new-Uout0_old.
Add only these corrections to the saved baseline. Preserve actual baseline
and new model values separately. Nout1=exp(-3h)Nout_new,
Uout1=exp(-4h)Uout0_new using the existing B3g map convention.
Event Ly-alpha energy is E21_J*(Nout_new-Nin_saved); pulled-back energy and
redshift work are separate expressions of that same exchange.

For ambient radiation use its event energy affine maps weighted by I1 and
S1: Uamb1=exp(-4h)*(Uamb0+Qamb_pullback).
For gas use I2,S2: Ugas1=exp(-5h)*(Ugas0+Qgas_adiabatic_pullback).
Internal atom energy is exp(-3h)*[EI*Nc1+E21*(Ns1+Np1)]*eV_J.
Rest carrier is dust exp(-3h). Report each geometry-work term separately so
the total finite energy change equals event exchange(sum0)+geometry work.

At the right endpoint, build separate sector T for rest dust, atomic internal
energy, gas thermal energy, ambient radiation, and outgoing Ly-alpha.
For each isotropic sector T00=U, Tii=p, T0i=0:
p_rest=p_internal=0, p_gas=2Ugas/3, p_radiation=U/3.
The transfer source is the finite event energy / saved proper duration /
exp(3h), per right proper volume; use cQ0 in J m^-3 s^-1 and
Q0=cQ0/c in J m^-4. Spatial Q=0 does not mean spatial T=0.
The source is an explicitly selected finite-step average applied at the
right geometry, not a pointwise original native history export.

Reuse the preserved si_to_core/FixedScale and original core implementation.
One actual core.rhs invocation uses these sector tensors, five-sector
four-force, the saved isotropic H/right geometry and zero shear/structure.
Compare the one result to independently written algebraic isotropic core
identities with source terms, relative <=5e-12 on each own nonzero scale.
Verify sum sector Q=0 to MP conservation allowance before conversion, and
conversion roundoff separately. Do not demand Friedmann closure from a
selected component packet or call this L4/global BASS completion.

## 7. Required output and stopping rule

Save endpoint maps, chosen model, all gross counts, exact finite inventory
and energy ledgers, numerical error bounds, source/right comparison,
baseline correction, propagated sector T, Q, actual core RHS and checks.
All raw failures and partial results survive. Require positivity, count and
event-energy identities, source conservative reassembly, native clock,
weighted transport/work identities and one new RHS algebraic comparison.
No additional future supplier is a prerequisite for this selected model.
Physical radii and prior unknown remaining budgets remain null.

After successful result, one saved-result-only plot may use the remaining
cumulative allocation following separate root authorization. Final independent
review admits only this frozen finite model, then source publication,
actual Drive/Dropbox ACKs, additive latest-central update and handoff follow.
