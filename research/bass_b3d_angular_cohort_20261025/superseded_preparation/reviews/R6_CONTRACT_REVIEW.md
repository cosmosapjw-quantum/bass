# R6 independent contract review — B3C1 emission/streaming

Reviewer: independent rec_source_audit agent. This agent did not author the
contract. This is a same-model independent derivation/source review; different-
model review is NOT_RUN. No scientific execution or remote write was performed.
The exact five reviewed inputs are recorded in R6_INPUT_IDENTITIES.json.

## Scoped decision

The proposed synthetic, non-tilted diagonal Bianchi-I zero-incident model has a
consistent source/transport/Einstein composition and correctly delimited physical
scope. The source card, three accounting sectors, proper-clock conversion,
Hamiltonian initial data, and zero-blue-support argument are accepted as derived
within the stated recoil-free/thick/finite-angular model.

Scientific contract: **PASS_SCOPED**. One small numerical acceptance
clarification below should be frozen in the implementation or an addendum before
its first scientific call. This does not reopen the accepted physical equations
or require a new source campaign.

## Independent derivation and source comparison

### Units, initial geometry and accounting

The physical energy density is N(M0 c²+E x), in J m^-3. Multiplication by
alphaL=8 pi G L²/c⁴ gives the dimensionless densities used by core.State.
With L=c/H0, h0=1 and sigma0=S0,

    C_H = 3 - (S0:S0)/2 - (8 pi G/(c² H0²))*rho_phys,0 = 0

for the stated H0. Momentum constraints vanish for n=a=flux=0. The three
sectors are a linear decomposition of the same atomic stress plus photons,
not a second atom population: ground mass and excitation both dilute with N,
while only excitation is debited by the line transition. Their pressure is
zero under the explicitly cold/no-recoil closure.

The pinned finite_exchange.commit_emission changes only chosen atomic/photon
sector indices, recomputes the actual source14 packet moments, returns a copied
state/source, and enforces duplicate transfer keys. Setting atomic_sector=0 and
photon_sector=2 therefore retains sector1 exactly during C. U=J=0 is correct
after a finite transaction: adding a rate after the state increment would charge
the same event twice. Source.pi is a stored STF stress, as the parent code states.

N0=8 pi/(g lambda³) has units m^-3. The source proper duration is
(L/c)*Delta_tau. The autonomous Strang composition uses C(Delta_tau/2),
A(Delta_tau),C(Delta_tau/2); only A advances the reported physical clock.
The summed reaction exposure is one Delta_tau, so this is ordinary operator
splitting rather than a doubled elapsed time.

### Diagonal streaming and conservation

For n=a=rotation=0, the pinned kinetic.flow reduces to
k_i'=-(h+sigma_i)k_i and (log w)'=-3h. The cohort exponentials in the contract
are their exact solutions conditional on alpha and beta. Opposite sign rays
have identical energies and weights throughout diagonal drift; odd moments
cancel and spatial off-diagonal moments cancel by coordinate reflections.
The fixed14-ray representation is therefore closed under this diagonal geometry.
It is still a finite angular model, as the contract explicitly says.

With no reaction during A, both N and the photon number density scale as
exp(-3alpha). During C, Delta(Nx)=-Delta n_gamma. Thus
exp(3alpha)(Nx+n_gamma)=N0*x0. Combining photon moment conservation with cold
excitation gives

    (rho_exc+rho_gamma)' = -3h(rho_exc+rho_gamma+p_gamma)-sigma:pi_gamma.

The separate W integral has the correct sign in u+W=u0 and dimensionless energy
normalization. Ground rest energy satisfies its own exact dust dilution.
This uses the reconstructed stock formulas; it is not independent integration
of the inherited core's rho equations. The contract accurately states that limit.

### Directional expansion and zero-blue support

Write s²=sigma:sigma, rho_d=rho_rest+rho_exc and
C_H=3h²-s²/2-rho_d-rho_gamma. The actual core equations imply

    m_i' + 3h m_i
    = 2h²-s²/3-(rho+3p)/6+pi_i
    = rho_d/2+P_gamma,ii+(2/3) C_H.

This verifies the coefficient and sign of the off-constraint term. On C_H=0,
positive dust and positive photon packets give a nonnegative right side.
The integrating-factor formula preserves m_i>0 from m_i(0)>0. It also implies
h=(m_x+m_y+m_z)/3>0. Raychaudhuri gives h'<=-h², hence
alpha(tau)<=log(1+h0*tau), and therefore

    m_i(tau)>=m_i(0) exp[-3alpha(tau)]
             >=m_i(0)/(1+h0*tau)^3.

C keeps h,sigma and total rho fixed, so it keeps C_H and all m_i fixed. The
argument applies through all continuum split stages. Empty initial photon
support and injection on the outgoing red side then give E_gamma'<0 after
birth, excluding an incoming blue trace within this declared model.

This proof is conditional on the stated physical model and exact constrained
flow. Numerical m_i samples and constraint residuals are separate diagnostics;
they cannot become an interval certification. A pre-existing blue background
would invalidate the premise, which is why the planned rejection matters.

### Prescribed-geometry oracle

For f_plus=0, N=N0 exp(-3Ht) and fixed H,S,

    dx/dt = -[8 pi H/(N lambda³)] x/[g-(g+1)x].

With x=x0 exp(-v), direct integration gives

    g v-(g+1)x0(1-exp(-v))
    =8 pi expm1(3Ht)/(3 N0 lambda³).

The stated oracle equation is correct. Integrating each cohort's emission time
against the independent diagonal redshift/dilution map is an appropriate
continuous-time reference for source/streaming composition. It is independent
of split-step placement but shares the deliberately fixed14-ray angular model.
It does not establish continuous-angular convergence or coupled-metric error.

## Finding R6-N1 — freeze the exact output-distance formulas before execution

**Object:** numerical acceptance items5–7, specifically “final geometry” and
“observed order for resolved source/radiation differences.”

**Observed issue:** the contract fixes thresholds and several denominators, but
does not yet write the geometry norm/component scales, the precise multi-output
comparison vector, or the rule that classifies a difference as roundoff-dominated.
Different plausible choices can change reported slopes without changing the
scientific output.

**Impact:** acceptance/rejection must be reproducible from saved rows before
results are seen. This is a numerical-reporting ambiguity, not a physical error.

**Minimal correction:** before the first scientific call, record exact formulas
for each output distance (geometry, relative x, photon number, spatial tensor),
which distances enter the order gate, and the fixed numerical resolution rule.
Use the existing frozen thresholds. For example, h/sigma may use fixed h0=1 and
alpha/beta a stated dimensionless scale; x and photon number may use explicitly
named reference endpoints; tensor uses the already frozen finest photon rho.
Specify whether each p=log2(d_N,d_2N) is per-output or an aggregate. Preserve all
coarse distances and raw values. Root may choose the actual formulas; the reviewer
is not prescribing an alternative physical tolerance.

Status: **OPEN preexecution clarification**, to be closed by root's exact
implementation/addendum. No further independent review pass is needed solely
for this clarification.

## Implementation cautions tied to actual parent code

- The source checks state.rho[atomic_sector] >= alphaL*E*n_u literally. Construct
  rho_exc from the exact same stored n_u product, avoiding a false rejection from
  a different floating multiplication order of N*x. The scientific contract is
  unchanged; do not loosen this source gate.
- Give each birth cohort its actual accepted alpha_b,beta_b and preserve its
  canonical weights. Reconstructing old cohorts with a new source epoch must not
  replay applied physical transfer IDs or change the event identity.
- Normalize the new energy-work test to initial excitation as specified. The
  parent's total-energy gross denominator contains the large ground rest sector;
  that inherited check alone would be insensitive to an excitation-scale error.
  The new ledger closes that particular gap without changing parent tolerances.
- Backreaction is present by construction through core.rhs and packet stresses.
  Any claim that the small geometry response itself is numerically resolved must
  use an observed comparison; successful source/radiation refinement alone does
  not measure its amplitude. No extra simulation is required for the current
  bounded-path claim.

## Review boundary

Accepted here: equations, source/code correspondence, units, clock, accounting,
continuum zero-blue-support proof and the purpose of the planned finite tests.
Not reviewed here: new client code, actual trajectories, numerical gate outcomes,
figure interpretation or publication/backup ACKs. Those remain actual later-stage
obligations. This review preserves finite absorption open, overall physical
completion null, and B4/B5 NOT_RUN.
