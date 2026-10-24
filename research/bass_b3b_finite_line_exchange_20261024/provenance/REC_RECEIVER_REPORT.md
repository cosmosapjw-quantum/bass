# REC current receiver/source intake for BASS B3b

## Decision from the inspected sources

The current REC lineage supplies an actual **finite atomic-population map** that
can advance the selected LINE01 state under its frozen local assumptions. It does
not supply a generic closed finite-photon bath for the same detached gross
channels. The appropriate next BASS construction can reuse that atomic map and
derive its integrated gross counts. It must identify any photon receiver and its
domain explicitly, or retain the source's prescribed incident boundary.

No scientific runtime, source test, IVP, old campaign replay, remote mutation or
archive download was performed by this intake. New formulas below are analytic
derivations for the parent to verify under a frozen bounded contract.

## 1. Current census, identity and parallel work

The actual current latest REC PR inspected is
[PR131](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/131),
`research/rec-history-input-admission-20261024` at
`c7cdabd871ab2ef6f722594ff063b8ce8550e6b4`, Draft/open/unmerged.
It descends from PR130 at `93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa`.

The metadata census exhausted two pages each:

| Object | Page counts | Total | Meaning |
|---|---:|---:|---|
| Current branches | 100,49 | 149 | Names and HEADs enumerated |
| All-state PRs, sorted by update | 100,31 | 131 | Metadata enumerated |
| Selected current tree | one untruncated recursive tree | 5,924 entries | Path/blob inventory |
| Selected source/contract contents | 14 files | 188,705 bytes | Actual contents read and saved |

`REC_METADATA_CENSUS.json` retains the complete enumerated branch/PR metadata.
This is not a claim that every file of every branch was read.
`SOURCE_OWNER_INTAKE.json` and `SOURCE_COPIES.json` bind selected source bytes.
All 14 saved files match their immutable Git blob identity. Six unchanged files
were rebound to the current tree using their already available exact local bytes;
eight newly selected files were fetched. No serialization repair was needed.

Root `AGENTS.md` returns404. The complete selected tree has no ancestor AGENTS
for the selected research/source paths. Its three `AGENTS.md` files are archived
other-repository survey copies. The parent retains the explicitly assigned
central AGENTS authority from the B3a intake.

PR131's current `CLAIM_GATES.json` records
`parallel_HISTORY02=OWNER_RESERVED_STAGE_A_OBSERVED_ONLY`.
The parent additionally reports cross-conversation GO_IMPLEMENT activity for
REC-HISTORY-02R at2026-10-24T02:49Z. This intake does not enter that reserved
characteristic/Wien-reference lane.

## 2. What changed in PR131

The actual new `admit_history.py` performs source/clock/coverage admission. Its
module says “No integrator, native runtime or solve.” It is not a new finite
photon/atomic transaction.

At the fixed native face z=1099.9986525171403, the retained report finds313
retarded queries covering source z=1100.092189396162..1133.87330719964.
h2U5 covers313/313 with its causal prefix, while the other three candidates
cover0/313. Source and energy grid match, but physical parameters do not:

| Parameter | Target | Actual h2U5 producer |
|---|---:|---:|
| T0 [K] | 2.728 | 2.7255 |
| nH0 [m^-3] | 0.18745798773143102 | 0.18971712352134673 |

Endpoint error, independent-reference uncertainty and justified curvature bound
remain null. Therefore H5 remains `INPUT_DEPENDENT_UNCALIBRATED`, and the parent
REC-HISTORY remains `PARTIAL`. The current source lists386 original primary
checks and3 original independent probes; none was repeated here.

The current delivery records preserve a workspace-reset loss: exact SUMMARY
recovered, original1,252 detailed candidate rows,313-query table, checks,
controller files and old figures not recovered. The new SUMMARY-only figure is
not the recovered original. These provenance limitations remain distinct from
the narrow observed scientific result. See the copied
`research/rec_history_input_admission_20261024/{HANDOFF_KO.md,NEXT_INPUT_CONTRACT.md,CLAIM_GATES.json,delivery/RECOVERY_STATUS.json}`.

## 3. Actual selected LINE01 finite-population receiver

Source:
[line_source.py at current REC HEAD](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/c7cdabd871ab2ef6f722594ff063b8ce8550e6b4/research/rec_line_source_20261023/code/line_source.py).
Git blob `5ac2a3107b80710504e63705ff16562131b5d1cf` is unchanged from the B3a source.

`LineState` owns the finite physical populations:

```text
card_id, population_scope,
n_l_m3, n_u_m3, H_s_inv, f_plus, S,
state_provenance, angular_provenance,
owner_mode='standalone_detached', native_line_owner_active=False
```

Its properties are `N=n_l+n_u` and `x=n_u/N`. It enforces a positive finite N,
nonnegative populations and incident occupation, strictly positive opacity
`g*n_l-n_u`, positive H and every-ray expansion. The selected effective2p card
uses g=3, the pinned native E21, SI lambda=hc/E and NIST A coefficients under a
statistical1:2 coincident-line closure. A whole-n=2 population cannot be substituted.

The actual finite update API is:

```text
thick_local_step(
  card_id, population_scope, N_m3, x0, H_s_inv, f_plus, S, omega,
  owner_mode='standalone_detached', native_line_owner_active=False)
```

It is a pure algebraic local map, returning x1 and integrated signed count,
energy and STF packets. It does not mutate a cosmological trajectory. A caller
can form the subsequent `LineState` from the actual returned populations while
retaining the selected frozen coefficients.

### Frame, clock and frozen quantities

The frame is matter-comoving, local orthonormal and non-tilted. Time is proper
seconds and volume is the physical local volume. During the source substep,
N,H,S,f_plus and line constants are frozen. S=sigma/H is trace-free and
q(n)=1+n·S·n>0. H supplies the frequency drift; cosmological density dilution and
background/shear evolution are separate operators. f_plus is direction-independent.

Write

\[
b=g+1,\quad F=1+bf,\quad x_{eq}=gf/F,\quad
d(x)=g-bx,\quad d_0=g/F,
\]
\[
k_\ell=\frac{8\pi H}{N\lambda^3},\qquad
\eta=\frac{k_\ell F}{d_0},\qquad T=\frac{\omega}{\eta}.
\]

Here k_ell has units s^-1 and is distinct from BASS's gravitational kappa.
The upstream exact thick reduced equation is

\[
\dot x=-k_\ell\frac{F(x-x_{eq})}{d(x)}.
\]

For y0=x0-xeq and z0=-b*y0/d0>-1, its principal solution is encoded by

\[
u+z_0\operatorname{expm1}(u)=-\omega,
\quad x_1=x_{eq}+y_0e^u,
\quad \Delta x=y_0\operatorname{expm1}(u).
\]

The source implements a bracketed scalar root and exact zero-time/equilibrium
branches. The solution is monotone between x0 and xeq; it preserves nonnegative
atomic levels and positive opacity without clipping.

The source gates the entire interval through

\[
\frac{t_{min}}{q_{max}}\geq\log(1+10^8)
=18.420680753952364,
\quad
t_{min}=\frac{A\lambda^3N[g-b\max(x_0,x_{eq})]}{8\pi H}.
\]

It returns the full-path depth, delta=exp(-tmin/qmax), log-domain representations,
an endpoint bracket and analytic model-truncation estimates. Its float
evaluation is explicitly not interval arithmetic.

### Existing finite ledgers

The same stable signed increment gives

\[
P_\gamma=-N\Delta x,\quad
\Delta n_u=-P_\gamma,\quad\Delta n_l=P_\gamma,
\]
\[
\Delta u_{\gamma}=E_\ell P_\gamma,
\quad\Delta u_{atomic,int}=-E_\ell P_\gamma,
\quad\Delta u_{thermal}=0.
\]

Ionic and free-electron yields are zero for this selected bound-bound process.
The actual internal energy partner is E_line*n_u relative to the chosen lower
level. No new reservoir definition is required to identify this atomic partner.

The thick angular shape is q(n), normalized by its mean1, and the source returns

\[
\Delta\Pi_\gamma=\frac{2S}{15}E_\ell P_\gamma,
\qquad
\Delta T_{\gamma,spatial}=E_\ell P_\gamma(I/3+2S/15).
\]

These are integrated source packets under the selected rest-frame source-step
contract. They do not automatically define a boosted finite-volume state update
or replace BASS's current state stress.

## 4. Integrated gross counts: constructive extension to verify

The upstream local map returns a signed net packet; it does not yet return the
two integrated gross counts. Those counts follow from the actual thick gross
rates without declaring the net to be an emission measure:

\[
\dot D=N k_\ell\frac{x(1+f)}{d(x)},\qquad
\dot A=N k_\ell\frac{g(1-x)f}{d(x)}.
\]

The ODE gives the pointwise identities

\[
\dot D=N(1+f)(k_\ell f-\dot x),\qquad
\dot A=Nf[k_\ell(1+f)-\dot x].
\]

Therefore, for the same frozen step,

\[
\boxed{D=N(1+f)[k_\ell fT-\Delta x]},
\qquad
\boxed{A=Nf[k_\ell(1+f)T-\Delta x]}.
\]

Both counts are nonnegative as integrals of the original gross rates, and
`D-A=-N*Delta_x`. The normalized angular measure q(n) is common and constant
through the thick step.

Three essential limits are:

- T=0: D=A=0.
- f=0: A=0 and D=-N*Delta_x; the photons come from the actual finite excited
  atomic population.
- LTE x0=xeq with f>0: Delta_x=0 but
  `D=A=N*k_line*f*(1+f)*T>0`. The source map returns u=0 on that exact branch;
  using that special u to set all gross events to zero would be incorrect.

**Numerical boundary:** for very short absorption steps starting near x0=0,
`k_line*f*T-Delta_x` is a small difference of nearly equal terms. Stable
evaluation or a positive integral/series reference is needed. A clipped
negative rounded count would hide the conditioning problem.

### Separate finite-opacity gross bound

Let B(x) be the actual finite-opacity mean and let
`r(x)=t(x)*B(x)=<q[1-exp(-t/q)]>`. On the source's whole-path gate,
`1-delta <= r <= 1`. The finite flow is the thick flow with the effective clock

\[
\theta(T)=\int_0^T r(x_f(t))dt\in[(1-\delta)T,T].
\]

The two gross identities remain valid with T replaced by theta and Delta_x by
Delta_x_f. If upstream w bounds `abs(x_thick-x_finite)`, then

\[
|D_t-D_f|\leq N(1+f)[k_\ell f\delta T+w],
\]
\[
|A_t-A_f|\leq Nf[k_\ell(1+f)\delta T+w].
\]

This explicitly accounts for gross activity at LTE, where the population bound
w can vanish while the gross finite-opacity difference remains nonzero. It
does not establish a finite-opacity angular gross-packet bound by itself;
that requires its own angular argument. These formulas were derived here but
not numerically or CAS-verified by this intake.

## 5. Actual receiver APIs that cannot be silently substituted

### Existing native accepted-step transaction

`src/full_bianchi_hyrec/trajectory/history_ownership.py`, blob
`b3cdc80c0b9cb5c1e189e8fddc84eca275d70029`, already has
`AcceptedStepTransaction.commit/discard/rollback_for_event`.
It is bound to a `ScalarHistoryOwnerSwapProblem`, a complete
`SourceIdentifiableOriginalHyRecDAE`, full local state/derivative, restart payload
and a native `HistoryAppendCandidate`. Only scalar Dfplus feedback ownership is
swapped; canonical Sobolev escape, A1s diffusion and Tvv remain with the native
operator. It does not accept detached LINE01 D/A counts as an interchangeable
argument. A new native mapping would change the source/owner contract and belongs
to a separately scoped native coupling task.

### Existing owned FLRW history

`OwnedFLRWHistory` in `owned_flrw_history.py`, blob
`3106859a178b16e05b549f941b96a59e58ff7430`, owns 311 virtual outgoing/average and
3 Lyman outgoing sample arrays on a native ln-a grid. `append` validates all
candidate arrays before adding a whole column. These are retarded radiation
history samples, not a generic finite photon-count bath charged by detached
emission/absorption events.

### Existing finite boundary ledger

`research/rec_history_boundary_20261023/code/history_boundary.py`, blob
`1aa7f134c332bc4596372df18c7c47306260ecfc`, exposes `line_ledger` with exclusive
`owner='boundary'` or `owner='event'`. It returns a signed net source,
`occupation_is_boundary_encoding=True` and `extra_radiation_source=0.0`.
Adding a second radiation event source to that outgoing boundary would duplicate
the transfer. The boundary code's native Wien departure convention is not the
detached full-Planck/stimulated LINE01 convention.

## 6. Scope of the next safe executable unit

The available source supports a bounded **frozen-background finite atomic step**
and its corresponding signed radiation packet. Constructing and validating its
integrated gross channels is a concrete next mathematical/code result. An
emission-only f_plus=0 transaction can draw from the real supplied excited
population. With absorption, the actual f_plus provider and selected radiation
receiver must be explicit: the existing source treats f_plus as a prescribed
incident reservoir and its own THEORY says a negative packet does not guarantee
positivity of an arbitrary closed photon bath.

Do not infer source populations from aggregate ionic fractions, append a native
history sample from a detached gross count without a source-qualified map, or
invent a missing donor. Preserve BASS Source.pi versus PiRate_hat, event-rate
versus finite-state weights, single physical transfer charge, and the original
B1/B2 claim boundaries. Historical remaining campaign wall/CPU remain null,
budget_reset=false. No merge or production activation follows this intake.

The current sources and new algebra are now concrete enough for the parent to
freeze the next bounded contract and proceed to implementation and independent
review. No additional census/audit is requested here.
