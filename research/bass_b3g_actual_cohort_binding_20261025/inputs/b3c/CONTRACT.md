# BASS B3c frozen contract — bounded f-plus-zero background coupling

Unit: BASS_B3C_BOUNDED_F0_BACKGROUND_20261024
Status at freeze: PRE_EXECUTION; R6 final review required; no numerical admission.
Parent BASS: cosmosapjw-quantum/bass@0a088e1f8fca6618107525e687f930406ca32d18
Parent branch: research/bass-b3b2-locked-cell-bridge-20261024 (PR187, Draft/open/unmerged).
New lane: research/bass_b3c_bounded_f0_background_20261024
Proposed branch: research/bass-b3c-bounded-f0-background-20261024
Fixed central authority: rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17,
research/orchestration_longterm_20261023/assembly/HANDOFF_bass_KO.md.
Current central observed: 79c042a15e7e29b894dadc32188e286dade73aad.
AGENTS blob 429a5a13ee75b1222bc50627f8d5973d01dd21c4 and BASS handoff blob
55c86aabe97702d6b64631c5f24a9d1a9563820e are unchanged.
PhysMath 1.0.0 supplied workflow governs R1–R10/C1–C10.

## 1. Scientific question and admission

Does the actual detached REC LINE01 finite f_plus=0 emission operator, composed
with the actual fixed-scale BASS Einstein/packet operator, produce a bounded,
positive, source-owned cold-atom Bianchi-I evolution that converges to its
declared continuous finite-angular model and independent isotropic reference?

A PASS is only for the declared manufactured model, tau in [0,0.1], and
fourteen rays per emission cohort. It is not calibrated recombination,
finite absorption, angular-continuum accuracy, arbitrary Bianchi families,
a restart certificate, a full B1–B5 result, or production authorization.
The original B1/B2 narrow admissions and missing old pytest argv/cwd remain
unchanged. Historical replay=0; recovered old archives are not downloaded.

## 2. Pinned actual owners

Use unchanged copies, with exact source identities in intake/B3B_SOURCE_IDENTITY.json:
- B3b code/finite_exchange.py, blob b4b29110771b335a22efe854f092a6438bab88fa.
- LINE01 code/line_source.py, blob 5ac2a3107b80710504e63705ff16562131b5d1cf.
- escape_moments.py, blob 599a6c6f70ae07a6e79623db65eacf3d00c44e36.
- hyrec_spike_transfer.py, blob ade2cc6d3da852f444289d7c6f2e9132c8ca7c90.
- BASS core.py, blob 3e95a652715b346a47f097fde2131540237390a4.
- BASS kinetic.py, blob 1fef508f01479508e5489cf8a167d2aff8184a81.

Actual REC scientific pin ae189694c15e09c6f96c44ef6b74b48afc2632ac remains
byte-valid at current PR133 c5394eccf6ff45f134e396c549844af91988aeb7:
28 source files plus 3 NPZ inputs match. Finite absorption is still
OPEN_INPUT_OWNERSHIP. The PR187 locked spectrum is bootstrap INITIAL-DATA,
not a LINE01 incident blue-side trace.

Source card: actual H_LYA_EFFECTIVE_2P, g=3, b=4,
A=(626490000+2*626480000)/3 per second,
E=10.198714553953742 eV, eV_J=1.602176634e-19,
lambda=h_P*c/E with h_P=6.62607015e-34.
Use the actual card values, not separately rounded reconstructions.
Source frame: non-tilted matter rest tetrad.
Rate measure: local proper time per proper physical volume.
Source mode: standalone_detached; native_line_owner_active=false.
Effective downward escape and net transfer coincide here; effective upward
transfer is exactly zero because f_plus=0. This is not a count of every
trapped microscopic emission. No finite bath, bandwidth, clipping, or donor
other than the owned atomic excitation is introduced.

## 3. Equations, clocks and units

Metric (-,+,+,+). tau=c*t/L, alpha'=h=HL/c, sigma=(L/c)*sigma_phys.
alphaL=kappa*L^2=8*pi*G*L^2/c^4.
Use G=6.67430e-11 SI and c=299792458 m/s as declared model constants.

Cold common-frame atoms have N=n_l+n_u, x=n_u/N, d=g-b*x>0.
Their SAME atom energy is represented by sectors R=0 and X=1:
rho_R=alphaL*M_lower*c^2*N; rho_X=alphaL*E*n_u.
Both have pressure, flux, pi equal to zero. Photon sector gamma=2.
M_lower=1.6735e-27 kg is a chosen hydrogen-scale MODEL input, not a new
calibrated NIST measurement. Recoil/thermal yield is zero in this closure.
Only X is debited. R and X are energy terms of the same atoms, not distinct
number reservoirs. Pass atomic_sector=1, photon_sector=2 explicitly.

Ndot=-3*H*N; xdot=-(8*pi*H/(N*lambda^3))*x/(g-b*x).
Effective photon production R_line=(8*pi*H/lambda^3)*x/(g-b*x).
Continuous U_gamma=kappa*L^3*E*R_line/c=-U_X, U_R=0, J=0.
The finite transaction already applies this exchange and must return/use
zero U/J afterwards. Source.pi is accumulated state stress, never PiRate_hat.
Injection pressure-rate tensor is U_gamma*(I/3+2*S/15), S=sigma/h.

Bianchi I: n=a=0, Lambda=0, frame rotation=0, diagonal STF sigma.
h'=-h^2-sigma:sigma/3-(rho_R+rho_X+2*rho_gamma)/6.
sigma'=-3*h*sigma+pi_gamma; alpha'=h; beta_i'=sigma_i.
Photon p=rho/3 and pi come from actual kinetic.moments.
The unchanged core.rhs must supply geometry derivatives.
Evolve h; never re-solve it from the Hamiltonian after initialization.

During each collisionless transport half:
N=N_start*exp(-3*Delta_alpha), x fixed,
k_i=k_i,start*exp(-Delta_alpha-Delta_beta_i),
w=w_start*exp(-3*Delta_alpha).
Keep beta_3=-beta_1-beta_2 and sigma_3=-sigma_1-sigma_2.
These are exact characteristic representations of the declared reduced ODE,
not positivity or Hamiltonian projections. An empty initial photon stock
has exact zero moments; never replace it with epsilon photons.

## 4. Frozen fixtures

Both controls use nu=N0*lambda^3/(8*pi)=1, x0=0.3,
alpha0=beta0=0, h0=1, initial photon vacuum.
- ISO: S0=0.
- ANISO: S0=diag(0.15,-0.05,-0.10).

For each separate fixture define fixed
L^2=(3-S0:S0/2)*c^4/[8*pi*G*N0*(M_lower*c^2+E*x0)].
Thus physical H0=c/L is determined by that fixture. Their physical H0 and
endpoint times need not coincide. Set Pstar=E/c for packet normalization.
No atom/source card is calibrated by the comparable-rate choice nu=1.
This dense manufactured fixture deliberately tests expansion and source on
comparable clocks. It is not the native z~1100 snapshot.

Run tau_end=0.1, nsteps=32,64,128,256 for each ISO/ANISO.
Initial and intermediate states must be finite, h>0, N>0,
0<=x<g/b, positive photon weights and energies, nonnegative owned sectors.

## 5. Composition and exact ownership

Use T(Delta_tau/2) -> actual commit_emission(Delta_tau) -> T(Delta_tau/2).
T is RK4 for the six geometry/shape variables with moments rebuilt from
characteristics at every stage. Source physical dt=(L/c)*Delta_tau,
using midpoint N,H,S. Global time advances once by Delta_tau.
Old packets travel both halves; new packets are born at the midpoint and
travel only the second half. Distinguish interval endpoints, midpoint
deposition epoch, source-subflow duration, and global time in the receipts.
Use a unique transfer ID for every committed interval; preserve histories.

Construct X at source entry using the SAME operation as its owner:
scale.density_factor * card.energy_J * population.n_u_m3.
Do not change the source's strict stock or 256-eps moment agreement gates.
After each transaction derive new x from its actual endpoint populations,
retain returned packet arrays and ledger identities, and verify zero U/J.
Rebuild physical moment closure from the same population/packet state.
Transport's core energy-row integral is a diagnostic only and never
overwrites this closure. Use source kicks in its separate monitor.

## 6. Independent identities and references

For x0>0 the exact thick-model oracle is
g*log(x/x0)-b*(x-x0)=-(K0/3)*expm1(3*Delta_alpha),
K0=8*pi/(N0*lambda^3)=1.
u=log(x/x0) solves u+z0*expm1(u)+Omega=0,
z0=-b*x0/g, Omega=K0*expm1(3*Delta_alpha)/(3*g).
Use a monotone scalar solve with an independent bracketing implementation,
not the same finite interval source integrator. x0=0 is exact vacuum.

Independent ISO fluid reference (DOP853, rtol=2e-12, atol=2e-14):
r=rho_gamma/(alphaL*E*N0), x'=-K0*h*exp(3*alpha)*x/(g-b*x),
r'=-4*h*r+K0*h*x/(g-b*x), alpha'=h,
h'=-h^2-(rho_R+rho_X+2*rho_gamma)/6,
rho_R=R0*exp(-3*alpha), rho_X=Escale*x*exp(-3*alpha).
Record solver status, evaluation count, clocks and actual options.

C=3*h^2-sigma:sigma/2-sum(rho), C'=-2*h*C.
Source at fixed geometry has Delta h'=-Delta rho_gamma/6,
Delta sigma'=2*S*Delta rho_gamma/15.
Comoving atom count and upper-plus-photon count are conserved:
exp(3*alpha)*N=N0,
exp(3*alpha)*(N*x+n_gamma)=N0*x0.
The nontrivial comoving work ledger is
d[exp(3*alpha)*(rho_X+rho_gamma)]/dtau
=-exp(3*alpha)*(h*rho_gamma+sigma:pi_gamma).
Integrate its RHS as a diagnostic, not an energy correction.

Twelve exact algebraic residuals and physical-root monotonicity have been
checked through actual Wolfram calls. Preserve first pre-call syntax error,
the first actual initialization/export failure, the subsequent mathematical
PASS with uppercase-symbol linter warning, and final clean PASS; never mark
all attempts first-run PASS. Raw calls/responses are the evidence.

## 7. Frozen scientific gates and normalizers

Define X0=alphaL*E*N0*x0, Escale=alphaL*E*N0 and R0=initial rho_R.
All listed reference/refinement gates are for the finest n=256 result.
Keep all coarser errors even when they exceed the gate.

| Observable | Gate / normalizer |
|---|---|
| x vs exact x(alpha), maximum over saved path | abs(x-x_exact)/x0 <=2e-8 |
| ISO x vs DOP853 endpoint | abs(dx)/x0 <=2e-8 |
| ISO radiation energy vs DOP853 | abs(drho_gamma)/X0 <=2e-8 |
| ISO geometry h,alpha vs DOP853 | infinity norm absolute <=2e-8 |
| ANISO fine temporal error estimate x | abs(x256-x128)/(3*x0) <=2e-8 |
| ANISO rho_gamma and pi time error estimate | abs(delta rho)/(3*X0), Frobenius(delta pi)/(3*X0) <=2e-8 |
| ANISO geometry h,sigma1,sigma2,alpha,beta1,beta2 | infinity norm difference/3 <=2e-8 |
| Observed temporal order | 1.7..2.3 for non-floor x and photon-energy errors/differences using available refinements; <=1e-13 normalized error is ROUND_OFF_FLOOR, not a fitted order |
| Comoving atom count | relative to N0 <=5e-12 |
| Comoving upper-plus-photon count | relative to N0*x0 <=5e-12 |
| Comoving excitation+radiation work balance | relative to X0 <=2e-8 |
| Independent core-energy transport monitor | R/R0 and X,gamma/X0 <=2e-8 |
| Hamiltonian | abs(C)/max(1,sum(abs(rho))) <=2e-8 |
| Photon zero-flux symmetry | norm(flux_gamma)/X0 <=5e-12 |
| Finite source/domain/identity guards | actual unchanged guards at each source call; fail closed |
| Immediate h feedback | exact Wolfram coefficient plus floating absolute residual <=32*eps*max(1,abs(hprime)); no tiny-backreaction relative claim |
| Immediate sigma feedback | norm(residual)/X0 <=2e-8, with actual 14-node injection |

For vector/matrix quantities use ordinary Euclidean/Frobenius norms as
specified. A radiation/source error divided by total rest energy is not an
admissible substitute. Do not label a successful Hamiltonian test as a
successful trajectory accuracy test.

Useful discriminating controls (bounded):
- exact x0=0 one short transport run: no source packets and no fake vacuum;
- one source application exercises actual X-only debit, finite number/energy
  ownership and geometric feedback; duplicate-transfer refusal if already
  available cheaply; no replay of the prior B3b whole suite;
- deliberately wrong newborn age/start placement ISO n=32,64: record
  independently referenced radiation errors; expect visible first-order bias.
  It is labelled a negative control, never an admitted production path.
  Acceptance: wrong n=64 radiation error exceeds correct n=64 by >5 and
  exceeds 2e-8, demonstrating sensitivity. Report actual order.
No extra test campaign or arbitrary variants are required.

## 8. Whole-window domain and angular limitations

Let chi=tau_end=0.1, s0=||S0||F. Positive cold matter/radiation on C=0 gives
h0/(1+3*h0*tau)<=h<=h0 and
qmin>=1-(1+3*chi)*(s0+sqrt(6)*chi)>0.
A lower whole-window optical-depth bound is
A*lambda^3*N0*exp(-3*chi)*(g-b*x0)/
[8*pi*H0*(1+s0+sqrt(6)*chi)].
Evaluate and report it once against actual log1p(1e8).
These are model bounds, not interval-enclosed floating trajectories.
Retain actual RK/source finite-domain tests and the source's local whole-path
opacity gate. Refused source/stage domains stop execution.

All line photons begin at E and H*q>0 thereafter. With no diffusion,
upscattering or line re-entry in the declared closure, they redshift below
the line while the incident blue-side f_plus remains zero.

Actual fourteen-node quadrature has axes weights1/15, corners weights3/40.
It is exact for source-required low moments, but <nx^6>=7/45 differs from
the spherical1/7 by4/315. ANISO is a finite-angular model. Time refinement
does not establish continuous angular convergence; ISO has a true isotropic
fluid comparator because all rays redshift equally.

## 9. Execution, repair and preservation

Astra owns this contract and science decision. The existing requested
lower-tier implementer owns code, tests, bounded runs and targeted repairs.
A separate Astra-role reviewer inspects actual code, raw outputs and figure.
Do not claim observed runtime model identity from requested routing alone.

New scoped local guard=120 wall seconds, one execution child/thread.
Historical remaining wall/CPU=null, budget_reset=false.
The first failed Wolfram kernel time is unknown, so charge a conservative
20 wall seconds for planning; subsequent measured kernel wall is recorded.
Provisional lower-tier allowance70 wall seconds INCLUDING tests/reference/
negative controls/plot; independent diagnostic reserve15 wall seconds.
Do not start a command whose guarded allocation would exceed the current
unit's ledger. Stop on the guard and preserve partial outcomes.
Environment/intake/I/O tool latency is reported separately from science.

Set OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1 and
MPLCONFIGDIR to a writable task-local directory. Python runtime has NumPy,
SciPy and matplotlib. SymPy and Rust on PATH were absent at fresh probe;
neither is required for this experiment. Record actual argv, cwd, env,
exit, wall/CPU, inputs/source hashes and original stdout/stderr.

S0: frozen source/theory/intake/R6 contract, Git readback + Drive + Dropbox.
S1: actual implementation/raw/science review and figure, same three receipts.
S2: final DAG/20-stage ledger/resource limits/copyable handoff and receipts.
Provider ACK != local hash validation != remote byte restore != scientific
admission. Full external restore is not automatically rerun.
Fresh actual expected branch SHA and policy/source checks precede each push.
Keep Draft/open/unmerged. No merge, production activation, archive replay,
donor invention, positivity clipping, or post hoc gate relaxation.

