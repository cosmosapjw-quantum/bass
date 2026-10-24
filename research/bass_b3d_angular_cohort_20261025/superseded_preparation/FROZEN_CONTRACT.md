# BASS_B3C1_EMISSION_SPLIT_20261025 — frozen research contract v1

## Authority, admission and intended result

Use the explicitly selected physmath-research-loop **1.0.0**. Parent BASS
PR187 remains Draft/open/unmerged at 0a088e1f8fca6618107525e687f930406ca32d18;
its scientific snapshot is 03101fd962ad2ce81195a2fcd3fae57834c80bd6. Central
fixed authority is rei_bianchi 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17;
current observation 6de537660df51101c68c7adf18a697d1aae1cceb preserves AGENTS
429a5a13ee75b1222bc50627f8d5973d01dd21c4 and BASS handoff
55c86aabe97702d6b64631c5f24a9d1a9563820e. No merge or production activation.

The actual REC source audit leaves finite absorption open: a saved scalar
blue-edge occupation is not a receiver cell/face trace with a finite donor.
The selected fallback is a **bounded, self-consistent diagonal Bianchi-I,
zero-incident, cold two-level emission plus collisionless photon model**.
It supplies one narrow B3c path. It does not replace the actual REC35x26
bootstrap or its Bianchi-II initial-data qualification. New initial populations
and geometry below are explicitly synthetic diagnostics; source card, source
map, physical units and Einstein/kinetic operators are actual pinned code.
No empirical recombination or full kinetic-atomic closure accuracy is claimed.

## Frozen initial state and physical approximations

Metric (-,+,+,+); c,hbar,k_B retained. Normal and hydrogen tetrads coincide;
no tilt, rotation, cosmological constant or spatial curvature: n=a=0. Let
tau=c*t/L, alpha'=h, beta_i'=sigma_i with sum beta=sum sigma=0.
Use H=c*h/L and S=diag(sigma_i)/h only in the source (which requires H>0).
The Einstein operator itself is unchanged and does not divide by H.

Use existing H_LYA_EFFECTIVE_2P / collapsed_2p card, g=3,
E=10.198714553953742 eV converted by source EV_J, lambda=h_P*c/E,
and source A21 unchanged. Its coincident-line/statistical-sublevel closure
and frozen whole-path thick gate remain explicit model assumptions.

Main diagnostic: N0=8*pi/(g*lambda^3), x0=0.1, S0=diag(-0.4,0.1,0.3),
initial photons exactly empty, alpha0=beta0=0. These intentionally selected
stocks make source and expansion changes resolvable; they are not the native
z1100 populations. The finite atomic donor is N0*x0, specified before a run.
No ambient bath, fictitious incoming donor, bandwidth or positivity clipping.

Ground rest-mass approximation M0=mp+me with CODATA2022 values
mp=1.67262192595e-27 kg and me=9.1093837139e-31 kg. This fixes the constant
ground-energy zero to this approximate mass; binding corrections to that
constant are not part of the numerical claim. The transition increment E is
the actual line-card energy. Cold, recoil-free atoms have p=pi=0. Thermal,
ionization, electron and collisional yields are absent by the selected model.
The high-density diagnostic is not a validity assertion for collision-free
real hydrogen at that density.

Use three **accounting sectors for one physical atom population plus photons**:
  0: rho_exc = alphaL*E*N*x, pressure=0, pi=0;
  1: rho_rest = alphaL*M0*c^2*N, pressure=0, pi=0;
  2: photon moments from actual positive massless packets.
Here alphaL=8*pi*G*L^2/c^4. The ground and excited sectors count the same N
atoms, not two distinct atom gases. This separation preserves resolved source
increments without subtracting tiny excitation from the much larger rest mass.
It adds no energy reservoir or process. The reaction changes only sectors0/2.

Set physical rho0=N0*(M0*c^2+E*x0), then
H0=sqrt[(8*pi*G/c^2)*rho0/(3-tr(S0*S0)/2)], L=c/H0, h0=1,
sigma0=S0, Pstar=E/c. Initial Hamiltonian and momentum constraints must pass.
Use core's G=6.67430e-11 unchanged. Time interval tau=[0,0.02].

## Subflows and state representation

Drift A evolves Einstein geometry and collisionless radiation with the source
reaction disabled. x remains constant; N=N0*exp(-3*alpha). For a cohort born
at alpha_b,beta_b with k_b,w_b,
  k_i=k_bi*exp[-(alpha-alpha_b)-(beta_i-beta_bi)],
  w=w_b*exp[-3*(alpha-alpha_b)].
These are the exact diagonal Bianchi-I characteristic maps conditional on the
geometry solution. No packet projection, merging, clipping, rebinning or
renormalization. Vacuum uses the inherited explicit empty-stock branch.

Construct core.State/core.Source from these exact stock formulas at each RHS
evaluation, call unchanged core.rhs, and evolve only h, sigma_xx, sigma_yy,
alpha, beta_xx, beta_yy (sigma_zz=-sigma_xx-sigma_yy). Source.pi contains
state STF stress. Reconstructed sector densities are not separately integrated
in this client; document that choice instead of claiming an independent
rho-ledger evolution. Flux vanishes by the actual sign-symmetric packet set.

Reaction C freezes geometry, N and current photons. Rebuild actual owner
LineState from current N,x,H,S with f_plus=0, standalone_detached and
native_line_owner_active=False. Use unchanged parent gross_counts and
commit_emission, atomic_sector=0, photon_sector=2. The source's finite
exposure and opacity-domain checks remain active; use the exact source map.
Every finite transaction must be bound to the current epoch/scale/stock and a
unique transfer id. Source duration dt=(L/c)*Delta_tau_substep. Global tau is
advanced by A only: splitting subflow clocks are not added twice.

C injects fourteen positive rays at the outgoing line face with energy E;
they represent escaped photons immediately redward of the unresolved line,
not a blue incident occupation. Each ray's actual birth geometry and weight
are saved for later drift. Rest sector1 remains unchanged under C. The updated
source has U=J=0 because the finite exchange was already charged.

Strang step: C(hstep/2) -> A(hstep) -> C(hstep/2).
Lie control: C(hstep) -> A(hstep). A uses scipy DOP853 with rtol=2e-12,
atol=2e-14, and max_step=outer step. No adaptive adjustment of frozen acceptance.
The source14-ray angular model is the finite discrete model under test;
continuum angular convergence is not claimed by time refinement.

## Zero-blue-trace support and conservation

All initial photon support is empty. In diagonal Bianchi I, define m_i=h+sigma_i.
For positive dust/excitation and photons on the Hamiltonian constraint,
  m_i' + 3*h*m_i = (rho_rest+rho_exc)/2 + P_gamma,ii >= 0.
Off constraint, the exact extra term is (2/3)*C_H. Local C preserves geometry
and total rho/flux, hence C_H. Thus strictly positive m_i initially remain
positive along the continuum split subflows. Since h'<=-h^2,
  m_i(tau) >= m_i(0)/(1+h0*tau)^3 > 0.
The actual initial minimum is0.6; at tau0.02 the bound exceeds0.565.
Photon energy obeys d log E_gamma/dtau=-sum m_i*n_i^2<0. Outgoing line
photons move redward and cannot supply the blue face in this model. This
conditional support proof does not apply to the pre-existing REC bootstrap
or an added blue-side background. Record numerical constraint and m_i minima
as separate numerical checks, not an interval proof from samples.

Invariant atom count: exp(3alpha)*N=N0.
Invariant excitation plus photon count:
  exp(3alpha)*(N*x+n_gamma)=N0*x0.
Source conserves rho_exc+rho_gamma instantaneously and preserves total
constraints. During drift, for u=rho_exc+rho_gamma,
  u'=-3h*(u+p_gamma)-sigma:pi_gamma.
Integrate the positive/anisotropic-work expression along A as a separate
scalar ledger; compare u(t)+W(t)=u(0). It is an energy-work check including
expansion, not constant physical energy in an expanding volume. Ground mass
has its independently exact dust dilution. Use source original256eps gates.

## Independent checks and numerical acceptance

Reproduce no parent campaign or completed parent tests. New checks cover:
1. Initial constraints, exactly empty photons, source injection/owner/gross
   down with up=0, current geometry/stock binding, three-sector accounting.
2. A drift's exact diagonal momentum and density scaling, redward support,
   nucleus/excitation-photon conservation and state-pressure/STF consistency.
3. Rejection of added f_plus, a blue-side initial stock, nonpositive directional
   expansion, incompatible frame/owner and failed thick domain; no mutation.
4. Prescribed constant H,S diagnostic using the same source14 rays: independent
   exact exposure K(t)=8*pi*expm1(3Ht)/(3*N0*lambda^3), log-map equation
   g*v-(g+1)*x0*(1-exp(-v))=K(t), x=x0*exp(-v). Obtain photon final moments
   by one-dimensional emission-time quadrature, separate from split stepping.
   This is an oracle for source/transport composition, not the coupled metric.
5. Self-consistent Strang grid steps[16,32,64,128] on tau[0,.02]. Compare final
   geometry, relative x, photon number and photon spatial tensor normalized
   by finest nonzero photon rho. Final64/128 discrepancy <=2e-8 and relative
   constraint <=2e-8. Retain every coarse result/failure. Require asymptotic
   observed order in[1.8,2.2] for resolved source/radiation differences; report
   roundoff-dominated components separately rather than inventing slopes.
6. One finer A-control at128 with rtol=2e-13,atol=2e-15; change must be below
   2e-10 on the same normalized outputs. It resolves time-solver contamination.
7. Lie versus Strang on the prescribed oracle at steps[16,32,64], demonstrating
   first versus second order for resolved radiation moments. Oracle quadrature
   uses independent scalar root residual and epsabs/epsrel small enough for
   numerical reference; report its estimated quadrature error, not certification.

All invariant floating errors must be reported with denominators. Atom and
excitation/photon number target5e-12; energy-work target2e-10 normalized to
initial excitation; positive-domain and support gates are strict. No hidden
H rescaling, constraint projection, or source-time adjustment to pass a gate.
A failure receives diagnosis and one bounded targeted correction; freeze
scope/tolerances and retain original raw evidence.

## Implementation, review, resource and delivery

Only new lane research/bass_b3c1_emission_split_20261025 is writable for this
unit. Copy the parent actual finite_exchange.py, core.py, kinetic.py,
rec_line_source/code/{line_source,escape_moments}.py and required unchanged
dependencies into this lane; bind exact original blob/SHA256. Parent files
and production dispatch are unchanged. Keep code small, and add provenance
only for scientific ownership, execution and recovery.

Lower-tier implementation uses the frozen contract; independent Astra review
of actual source, results and figure precedes scientific admission/publication.
Root controls all Git/Drive/Dropbox writes. New stacked Draft branch only,
fresh actual expected SHA, force=false. No other owner repository writes.

New scientific process guard:120 wall seconds aggregate,60 CPU seconds
aggregate; implementation allocation60wall/40CPU; individual process<=30wall/
20CPU. Reviewer allowance20wall/10CPU; symbolic allowance20wall/10CPU. Preserve
all starts/argv/cwd/exit/stdout/stderr/sourcehash/environment/resource receipts.
Use one thread and writable MPLCONFIGDIR. Record actual scientific spend;
I/O/review/orchestration wall is separate or unmeasured. Existing historical
remaining wall/CPU=null and budget_reset=false. Prior34.1262904040002seconds
is a partial subtotal, not a balance. Prior B3b2 subtotal11.957513821989018wall/
11.935948999999999CPU is retained separately. No old archive/NPZ downloads or
campaign replays. Number new bounded IVP trajectories honestly.

Create real CSV/JSON results and a figure of refinement, energy/count ledgers,
and directional-expansion support. Preserve exact zero values. Each R/C stage
links its scientific evidence and earliest cumulative S0/S1/S2 receipt; twenty
stage labels do not imply twenty independent uploads. Overall BASS physical
completion remains null. Finite absorption, broad B3c domains, B4 restart and
B5 domain validation remain distinct obligations.
