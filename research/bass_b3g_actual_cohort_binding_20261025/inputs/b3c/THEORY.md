# BASS next physical unit: bounded cold-atom source/background coupling

## Decision

The smallest useful next physical experiment is an opt-in, finite-duration
Bianchi-I coupling of the actual B3b `f_plus=0` emission transaction to the
actual fixed-scale Einstein and collisionless-packet operators. The parent has
proposed an isotropic control and a diagonal anisotropic fixture, both with
explicit cold two-level matter, a true initial photon vacuum, and a midpoint
source composition. That selection is coherent with the current source.

This note supplies source inspection, mathematical derivations and a bounded
experiment proposal. It executes no scientific program, IVP, historical
campaign, build, or test. Numerical tolerances and final admission remain the
parent's frozen-contract responsibility.

## 1. Current authority and attachment intake

Current parent BASS is PR187 at
`0a088e1f8fca6618107525e687f930406ca32d18`. The actual PR187 frozen contract,
handoff, fixed-scale `core.py`, and `kinetic.py` were read locally. The central
AGENTS text was read from `../CENTRAL_AGENTS.md`, with unchanged blob
`429a5a13ee75b1222bc50627f8d5973d01dd21c4`; the parent reports current central
HEAD `cdba5c98819ea615c32c4d7cea2c613a737e9eb1`.

The user-supplied PhysMath 1.0 workflow and current central policy govern this
work. Old attachment instructions are historical source/workflow material.
Their owner-decision, dual-audit, toolchain and repeated-runtime gates do not
create new barriers for this already authorized narrow research unit.

| Attachment | Actual inspection | Relevance |
|---|---|---|
| 01 low-ell audit text | Complete text | Distinguishes implemented physics, family claims, local boost, output and statistical claims; no all-family audit is launched here |
| 04 adaptive protocol | Complete text | Useful equation/code/observable mapping and narrow repair discipline |
| 05 DAG research executor | Complete text | Useful dependency selection and explicit evidence; legacy repeated audits are not a new mandate |
| 07/08 figure review texts | Complete texts | Figure semantic accuracy, legibility and exact-zero interpretation are appropriate later checks |
| 12 background/high-ell harness ZIP | 103-member inventory; four selected small documents | Its own first-read document says it is a harness baseline, not solver/science evidence. Old pending OD decisions do not override current authorization |
| 10 Rust-core archive | 18-member inventory; README/conventions and selected PR-status excerpts | Historical backend claims and conventions; no Rust installation/build is needed for this Python experiment |
| 14 review archive | 434-member inventory; selected exchange and kinetic-Einstein source | Existing momentum-only exchange is not a line-energy donor. Its old constraint-solved-H method motivates an independent Raychaudhuri/constraint check |
| 17 locked Rust archive | 8451-member inventory; first 100 lines of coupled kinetic source | Existing hierarchy backend is separate from current finite LINE01 emission and does not supply its missing atomic source |

`ATTACHMENT_INDEX.json` records the 20 attached files and hashes of the five
read texts and four inspected archives. Full archive member-name/size lists
are in the four `ARCHIVE_*_INVENTORY.tsv` files. No attached archive was bulk
extracted or executed. `INSPECTED_ARCHIVE_SOURCE_IDENTITY.json` records only
the ten small selected members copied for provenance. The other attachment
files were inventoried by filename and size, not represented as fully read.

## 2. What the existing scientific units actually provide

PR187 admits a reversible mapping of an actual 35-by-26 REC photon inventory
to a BASS snapshot. That saved inventory is scalar-history, unpolarized,
isotropic bootstrap INITIAL-DATA in the hydrogen tetrad, not a coupled
macro endpoint or a LINE01 incoming blue-side trace. Current REC intake still
finds the incident-trace/atomic-ownership link open. Consequently it cannot
be inserted as an unqualified finite absorption bath for this experiment.

The B3b finite emission transaction and its source dependencies were fetched
read-only at the exact PR187 pin. All nine fetched source/doc/fixture files
match their Git blobs; paths and SHA-256 hashes are in
`B3B_SOURCE_IDENTITY.json`. The critical files are:

| File under `b3b_source/` | Exact Git blob | Role |
|---|---|---|
| `code/finite_exchange.py` | `b4b29110771b335a22efe854f092a6438bab88fa` | Gross ledger and finite source transaction |
| `vendor/rec_line_source/code/line_source.py` | `5ac2a3107b80710504e63705ff16562131b5d1cf` | Actual source card, whole-path gate and monotone finite population map |
| `vendor/rec_line_source/code/escape_moments.py` | `599a6c6f70ae07a6e79623db65eacf3d00c44e36` | Required unchanged import and angular domain validation |
| `vendor/rec_line_source/vendor/hyrec_spike_transfer.py` | `ade2cc6d3da852f444289d7c6f2e9132c8ca7c90` | Transitive source import |
| `tests/test_finite_exchange.py` | `45d4d0006af7f7cbc53c6e6272a06a13ae97a786` | Actual old synthetic fixture; read, not executed |

The source card remains the declared effective coincident collapsed 2p model:
`g=3`, `E=10.198714553953742 eV`, `lambda=h_P*c/E`, and the existing weighted
spontaneous rate. Statistical 1:2 sublevel occupation and common frequency,
profile and incident occupation are inherited model assumptions. The source
is `standalone_detached`, with `native_line_owner_active=False`, matter-rest
frame, local proper time and proper volume. Thermal recoil, ionization and
free-electron yields remain zero in this model.

### The old transaction fixture is not a dynamic matter closure

Actual B3b tests use `N=1e9`, `x=.3`, `H=1e-18`, `L=1e25`, and synthetic
atomic `rho=alphaL*E*n_u+.003`, pressure `.0002`, nonzero atomic stress, an
extra density `.007`, nonzero extra flux and nonzero curvature. The source
transaction was required to preserve those supplied fields while geometry
was held fixed. It did not derive their equations of state or solve the
initial Einstein constraints. They cannot silently become the evolving
matter/background of B3c.

## 3. Explicit new cold-matter closure

Use signature `(-,+,+,+)` and retain physical `c`, Planck's `h_P`, and `G`.
Let the lower-state rest mass be a specified positive MODEL parameter
`M_l=1.6735e-27 kg`, as proposed by the parent. This is a hydrogen-scale model
input, not a newly calibrated atomic-mass determination. Let the paired
physical density be `N=n_l+n_u` and the upper fraction `x=n_u/N`.

The same atoms have total energy density

\[
u_{\rm at}=M_lc^2N+ENx.
\]

Represent its two terms as separate co-moving dust ledger sectors:

\[
\rho_R=\alpha_LM_lc^2N,\quad
\rho_X=\alpha_LENx,\qquad
p_R=p_X=0,\quad F_R=F_X=0,\quad\pi_R=\pi_X=0,
\tag{1}
\]

where `alphaL=8*pi*G*L^2/c^4`. The split is an algebraic decomposition of the
same atoms' rest and excitation energy. It does not add another donor. Only
sector X is debited by LINE01; sector R follows the conserved atomic number.
This avoids erasing a small, representable excitation by adding/subtracting
it from roughly 10^8 times larger hydrogen-scale rest energy.

Cold atoms, non-tilted common rest frame, negligible thermal/recoil pressure,
and a detached two-level source are explicit NEW closure assumptions for
this model fixture. They are not established by the saved native thermal
snapshot, whose nonzero temperature and incoming occupation must remain
separate. The experiment is not a recombination-history reconstruction.

## 4. Actual continuous equations and clocks

Let `tau=c*t_proper/L`, `h=H*L/c`, `sigma=(L/c)*sigma_phys`, and
`alpha'=h`. Primes below mean `d/dtau`. Choose Bianchi I, zero frame rotation,
zero cosmological constant, `n=a=0`, and initially diagonal STF shear.

For the optically thick f-plus-zero source, with `b=g+1` and `d=g-b*x>0`,

\[
R=\frac{8\pi H}{\lambda^3}\frac{x}{d},\qquad
\dot N=-3HN,\qquad
\dot x=-\frac{8\pi H}{N\lambda^3}\frac{x}{d}.
\tag{2}
\]

`R` is the effective escaping downward number rate per proper volume, not
the gross count of every trapped microscopic emission/reabsorption. Here the
effective upward channel is zero and the effective downward/net channels
coincide. The full source/population equations are

\[
\dot n_u=-3Hn_u-R,\quad \dot n_l=-3Hn_l+R,
\quad \dot n_\gamma=-3Hn_\gamma+R.
\tag{3}
\]

The continuous dimensionless source transfer is

\[
U_\gamma=\frac{\kappa_{\rm grav}L^3}{c}ER,
\quad U_X=-U_\gamma,\quad U_R=0,\quad J_i=0.
\tag{4}
\]

It is used to identify the continuous model. A committed finite B3b interval
returns zero already-applied `U/J`; it must not be integrated again. The
injected spatial stress RATE is `U_gamma*(I/3+2*S/15)`, with `S=sigma/h`.
`Source.pi` always holds the actual accumulated photon state stress.

The actual core reduces to

\[
h'=-h^2-\frac{\sigma:\sigma}{3}
       -\frac{\rho_R+\rho_X+2\rho_\gamma}{6},
\qquad \sigma'=-3h\sigma+\pi_\gamma,
\tag{5}
\]

\[
\rho_R'=-3h\rho_R,\quad
\rho_X'=-3h\rho_X-U_\gamma,\quad
\rho_\gamma'=-4h\rho_\gamma-\sigma:\pi_\gamma+U_\gamma.
\tag{6}
\]

For each massless packet during collisionless transport,

\[
\mathbf k'=-(hI+\sigma)\mathbf k,\qquad
(\log w)'=-3h.
\tag{7}
\]

For diagonal shear introduce `beta_i'=sigma_i`, `sum beta_i=0`. Each cohort
has the exact characteristic representation

\[
k_i(\tau)=k_{i,b}\exp[-(\alpha-\alpha_b)-(\beta_i-\beta_{i,b})],
\quad w(\tau)=w_b\exp[-3(\alpha-\alpha_b)],
\quad N=N_0e^{-3(\alpha-\alpha_0)}.
\tag{8}
\]

The finite source leaves geometry unchanged and adds 14 actual B3b packets
at exactly the source card energy E. These are a new line-photon sector;
no locked COM cell energy or bandwidth is substituted.

## 5. Constraints and conservation observables

The Hamiltonian and momentum constraints become

\[
C=3h^2-\tfrac12\sigma:\sigma-\rho_R-\rho_X-\rho_\gamma,
\quad C_i=F_{\gamma i}.
\tag{9}
\]

Antipodal source pairs and the linear Bianchi-I momentum flow preserve zero
flux. The Jacobi constraints vanish because `n=a=0`. The actual core's
off-surface constraint equation gives

\[
C'=-2hC
\tag{10}
\]

for balanced sources. Initialize C=0 by constructing h0 once, then evolve h
with the actual RHS. Re-solving h from the constraint at every step would
make the principal constraint check vacuous and is not the selected method.

A finite source conserves total rho/flux at fixed geometry, hence preserves
the existing constraint residual. Its immediate geometry-RHS changes are

\[
\Delta h'=-\Delta\rho_\gamma/6,\qquad
\Delta\sigma'=\frac{2S}{15}\Delta\rho_\gamma.
\tag{11}
\]

Useful independent ledgers are

\[
e^{3\alpha}N=\mathrm{constant},\qquad
e^{3\alpha}(Nx+n_\gamma)=\mathrm{constant}.
\tag{12}
\]

Total physical energy is not constant during expansion. In fixed-scale units,

\[
\frac{d}{d\tau}\{e^{3\alpha}(\rho_R+\rho_X+\rho_\gamma)\}
=-e^{3\alpha}(h\rho_\gamma+\sigma:\pi_\gamma).
\tag{13}
\]

The rest term on the left is independently constant in comoving volume.
Therefore an excitation-plus-radiation work ledger can avoid subtracting a
large rest-mass contribution while testing the same nontrivial physics.

## 6. New exact dilution/population oracle

Equation (2) admits an exact relation even when H and shear evolve. Define
`K0=8*pi/(N0*lambda^3)`. Using `dalpha/dt=H` gives

\[
\frac{dx}{d\alpha}
=-K_0e^{3(\alpha-\alpha_0)}\frac{x}{g-bx}.
\]

For `x0>0`, integrate directly:

\[
g\log\frac{x}{x_0}-b(x-x_0)
=-\frac{K_0}{3}\operatorname{expm1}[3(\alpha-\alpha_0)]
=-\frac{8\pi}{3\lambda^3}\left(\frac1N-\frac1{N_0}\right).
\tag{14}
\]

Let `u=log(x/x0)<=0`, `z0=-b*x0/g`, and

\[
\Omega=\frac{K_0}{3g}\operatorname{expm1}[3(\alpha-\alpha_0)].
\]

Then the same source-owned monotone scalar root solves

\[
u+z_0\operatorname{expm1}(u)+\Omega=0,
\qquad x=x_0e^u.
\tag{15}
\]

Its derivative `1+z0*exp(u)>0` on the non-inverted domain gives the physical
unique root. `x0=0` is the exact no-emission branch and must be handled before
forming a logarithm. This relation was derived independently here before the
REC intake sibling sent the same identity. It has not been numerically or
symbolically executed by this child. It is an oracle for the THICK coupled
model; it does not promote its finite-opacity approximation into equality.

## 7. The parent-proposed manufactured fixture

Adopt, subject to parent freeze:

| Quantity | Proposed value/definition |
|---|---|
| Atomic card | Actual B3b effective collapsed 2p card, unchanged A and E |
| Density parameter | `nu=N0*lambda^3/(8*pi)=1`, hence K0=1 |
| Upper fraction | x0=0.3 |
| Lower rest mass parameter | M_l=1.6735e-27 kg, explicitly a hydrogen-scale model input |
| Background | Bianchi I; Lambda=0; rotation=0; alpha0=beta0=0 |
| Shear control | S0=0 |
| Anisotropic case | `S0=diag(.15,-.05,-.10)` |
| Radiation | True initial photon vacuum |
| Normalization | h0=1 by fixed L determined from the physical Hamiltonian |
| Duration | tau in [0,.1] |
| Refinement | 32,64,128,256 macrosteps, if confirmed by parent |

The physical H0 is determined from the declared matter:

\[
H_0^2\left(3-\frac12S_0:S_0\right)
=\frac{8\pi G}{c^2}N_0(M_lc^2+Ex_0),
\qquad L=c/H_0.
\tag{16}
\]

The denominator is positive for both proposed S0. This gives the same h0=1
convention with source-consistent physical H0, rather than setting H from an
unrelated frozen opacity fixture.

This density choice is scientifically material. The actual ratio

\[
k_{\rm line}/H=8\pi/(N\lambda^3)
\tag{17}
\]

is independent of H. At inherited N=1e9 m^-3 and Ly-alpha wavelength it is
of order 10^13, so a reaction-time experiment would have almost stationary
geometry and a Hubble-time calculation would exhaust representable excited
stock. Setting nu=1 is a NEW manufactured model fixture with comparable
expansion/reaction rates. It is not native z~1100 data and does not establish
accuracy of all neglected dense-gas, overlapping-line or thermal physics.

## 8. Whole-interval positivity and thick-domain bounds

For the exact continuous cold-matter/radiation model on C=0, positive rho and
`p_gamma=rho_gamma/3` give

\[
-3h^2\le h'\le-\tfrac32h^2,
\quad \frac{h_0}{1+3h_0\tau}\le h\le h_0.
\tag{18}
\]

For any positive photon measure,
`||pi_gamma||F <= sqrt(2/3)*rho_gamma`. Therefore, with
`s0=||S0||F` and `chi=h0*tau`,

\[
\|\sigma\|_F\le h_0(s_0+\sqrt6\,\chi),\qquad
q_{\min}\ge1-(1+3\chi)(s_0+\sqrt6\,\chi).
\tag{19}
\]

For the proposed anisotropic S0, `s0=sqrt(14)/20`; at chi<=.1 the right side
is positive with a substantial margin. This supplies a conservative
whole-interval expansion argument for every direction, not only the 14 rays.
During the model evolution `N>=N0*exp(-3*chi)` and `x<=x0`, so

\[
\frac{\tau_{\rm line}}{q_{\max}}
\ge
\frac{A\lambda^3N_0e^{-3\chi}(g-bx_0)}
 {8\pi H_0(1+s_0+\sqrt6\,\chi)}.
\tag{20}
\]

The parent can evaluate this fixed expression once and compare it to the
actual source threshold `log1p(1e8)`. Source calls must retain the unchanged
local whole-path gate as well. Equations (18)-(20) are model-level analytic
bounds, not interval enclosures of a floating trajectory. Numerical stages
still need finite/domain checks and an explicit failure if a gate fails.

Since each emitted photon starts at E and subsequently has
`dot E/E=-(H+sigma_phys:nn)<0`, the escaped radiation can accumulate redward
while the incoming blue trace remains zero. This construction assumes no
frequency diffusion, upscattering or re-entry, consistent with the selected
detached closure. Zero incoming occupation does not mean zero total photon
stock after emission.

## 9. Finite event placement and transport algorithm

Let T denote source-free transport/background evolution and C the actual
frozen B3b source transaction. Use

\[
T_{\Delta\tau/2}\ C_{\Delta\tau}\ T_{\Delta\tau/2}.
\tag{21}
\]

The reaction duration passed to B3b is `dt_s=L*Delta_tau/c`, with H, S and N
from the midpoint transport state. Geometry does not advance inside C. This
is a splitting subflow, so the elapsed physical macrostep is Delta_tau; one
must not add the reaction's fictitious subflow duration to that clock again.

Old cohorts traverse both transport halves. The newly generated 14-packet
cohort is assigned the midpoint birth epoch and traverses only the second
half. Source interval identity and deposition epoch are recorded separately.
Depositing all interval emission at its start would give those photons a
full-step redshift age and generically reduce the source/transport accuracy
to first order.

During each T half, the proposed RK4 integration evolves h, the two independent
diagonal shear entries, alpha and beta using the actual `core.rhs`. At every
stage, (8) gives N and all packet momenta/weights, and actual kinetic moments
give radiation rho/flux/p/pi. Sector X has its post-reaction x held fixed in
T. Sector state rho is this physical moment closure; refreshing it from the
declared state variables is not a constraint or positivity projection.

An independently integrated core energy-row ledger can monitor transport
error, with its exact meaning documented. It is not fed back into B3b as an
inconsistent photon stock: B3b's existing 256-eps moment matching is a
representation contract, not an adjustable RK4 truncation-error threshold.
Keep h as an evolved variable, without Hamiltonian reprojection.

Symmetry of (21) and sufficiently accurate subflows gives second-order local
composition on a smooth admitted domain. RK4 transport has higher local order
and should become subdominant under the proposed refinement. The actual
observed order must be reported from the new outputs; it is not presumed
passed from this derivation.

## 10. Independent isotropic reference and discriminating observables

In the isotropic control define
`r=rho_gamma/(alphaL*E*N0)`, with alpha0=0. An independent continuous fluid
reference is

\[
x'=-K_0he^{3\alpha}\frac{x}{g-bx},\qquad
r'=-4hr+K_0h\frac{x}{g-bx},\qquad \alpha'=h,
\tag{22}
\]

with

\[
\rho_R=\alpha_LM_lc^2N_0e^{-3\alpha},\quad
\rho_X=\alpha_LEN_0xe^{-3\alpha},\quad
\rho_\gamma=\alpha_LEN_0r,
\quad h'=-h^2-(\rho_R+\rho_X+2\rho_\gamma)/6.
\tag{23}
\]

The parent's proposed DOP853 reference integrates these few fluid variables,
not cohorts or the same Strang implementation. Equation (14) supplies a
further exact population-vs-alpha reference. Neither is a replay of an old
campaign.

Meaningful acceptance data include source/radiation/population differences
under timestep refinement, the two comoving count invariants, excitation plus
radiation work balance, positivity, whole-path source gates, packet/core
moment consistency, Hamiltonian propagation, and the immediate feedback (11).
Source and radiation errors must use source/radiation scales, not a large
rest-mass denominator. A proposed `2e-8` gate can be judged only against the
parent's explicitly defined nonzero norm and the actual observed outputs.

Because `E/(M_l*c^2)` is of order 1e-8, source-induced changes of h are much
smaller than h itself. Subtracting two binary64 h trajectories or two full
geometry RHS values has a cancellation floor relative to that small effect.
The exact coefficient/sign test (11), a separately reported absolute
geometry error and a well-scaled source/radiation test should remain distinct.
Do not present a source-normalized small-Delta-h relative tolerance that the
floating representation cannot resolve, or change M merely to hide it.

## 11. Angular claim boundary and a concrete witness

The actual B3b cubature has six axes of weight1/15 and eight corners of
weight3/40. It exactly represents the required second/fourth moments at
injection, but

\[
\langle n_x^6\rangle_{14}=\frac2{15}+\frac{3/5}{27}
=\frac7{45},\qquad
\langle n_x^6\rangle_{S^2}=\frac17,
\quad\hbox{difference}=\frac4{315}.
\tag{24}
\]

Later anisotropic transport probes angular moments beyond the degree-5
injection rule. Therefore the anisotropic experiment tests the actual
inherited finite 14-ray source model, with its timestep convergence and
Einstein coupling. It does not certify continuum angular convergence.
The isotropic control avoids this angular distortion because every ray has
the same redshift factor. This is a finite-model scope qualification, not a
new strong no-go theorem or a reason to stop the bounded experiment.

## 12. Alternatives and recommended edge

| Candidate | Constructive value | Current disposition |
|---|---|---|
| Selected B3c cold f-plus-zero source/background experiment | Tests a real finite donor, proper-volume dilution, photon age/redshift and actual Einstein feedback with independent references | Recommended now with the explicit new fixture and scope above |
| Use native-density N~1e9 with the same detached source | Short reaction-time test is valid, but expansion is nearly frozen and long-time endpoint underflow is material | Separate stiff-regime work; not silently substituted for the comparable-timescale fixture |
| Closed finite-f absorption from PR187 spectral inventory | Would advance incident-photon ownership if boundary and atomic source maps were supplied | Incident-trace/native-COM atomic ownership remains open; do not invent it |

Recommended DAG edge: completed B3a event measure + B3b finite emission +
G1B/core packet transport + PR187 state representation -> current B3c declared
model and bounded coupled evolution -> independent numerical/physical review.
Restart, arbitrary Bianchi families, finite-opacity coupled errors, angular
continuum refinement, real recombination history, absorption ownership and
production activation remain distinct later dependencies.

## Execution and preservation status

- Scientific runs by this intake child: 0; new IVPs: 0; old replay: 0.
- Read-only current-source fetches: nine small files, all exact at PR187 pin.
- Attached files downloaded: 0; Library calls: 0; archive bulk extraction: 0.
- Remote mutations: 0. The source copies and reports are local preparation.
- Historical remaining budget remains null; `budget_reset=false`.
- Any backup/publication ACK and scientific PASS belong to the parent's later
  stages and are not inferred from this report or source-copy hashes.
