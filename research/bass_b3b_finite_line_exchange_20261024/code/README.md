# B3b implementation

`finite_exchange.py` evaluates the frozen thick LINE01 integrated gross ledger
and commits canonical-rest emission into actual BASS `core.State`, `core.Source`
and `kinetic.moments` stocks. This is an opt-in research module. Every numerical
fixture in this unit is synthetic; the owner, cards and BASS receiver are actual
unchanged source copies, identified in `../vendor/SOURCE_SHA_MAP.json`.

## Interface and physical preconditions

`gross_counts(LineState, dt_s)` calls the unchanged `thick_local_step` for its
stable population increment, net count, whole-path opacity gate and original
finite-opacity error envelopes. It interprets the owner's exact-LTE `u=0`
shortcut using the continuous gross clock `v=omega`. Its positive gross formulas
use a bounded alternating series for `v-a(v)` at `v<=1/2`. The reported next term
is a truncation bound; it is not an interval enclosure of floating evaluation.
The gross counts compute the reduced thick model and receive no new relative
finite-opacity certificate.

`commit_emission(**kwargs)` takes a validated LINE01 `LineState`, explicit
`source_identity` and `state_identity`, an actual `core.State` and `core.Source`,
`PopulationStock`, `PhotonStock`, actual `FixedScale`, SI momentum scale
`Pstar`, proper duration `dt_s` and a concrete `transfer_id`. Its return contains
copied updated state, source, stocks and line plus the analytic ledger and
reported conservation tolerances/residuals. Callers should use the returned
stocks for subsequent intervals. Rejections leave supplied objects unchanged.

The identity binds source owner, source card/population scope, stock epoch,
fixed scale and momentum unit. The required frame is `rest`; the required clock
is `proper_time_dt_dV_invariant`. Source and state geometry must obey
`h=H*L/c` and `sigma=h*S`. The actual detached owner validator remains
authoritative, including `native_line_owner_active=False`. The physical transfer
key is `(owner, epoch, transfer_id)`, independent of `representation` labels.
The source/state/population/photon bindings must agree before a commit.

Only `f_plus==0` commits are admitted. General-f gross counts remain valid as a
prescribed-boundary ledger; no finite incoming photon reservoir is inferred.
The atomic sector must already contain its excitation energy
`FixedScale.density_factor * E * n_u`; additional constant caller-owned energy
is preserved. Atomic pressure/pi and all other sectors remain unchanged.
Incoming `core.Source` energy and momentum transfer fields must be zero. This
explicit local-substep precondition prevents an already applied interval from
discarding unrelated source rates. Returned interval U/J are zero, while the
new photon pressure and state pi remain present for subsequent evolution.

An empty photon stock uses a true vacuum branch with empty arrays and exactly
zero sector moments. It does not create an epsilon bath. Nonempty stocks use
the actual kinetic packet moments. Massless zero-weight packets are compatible
with those underlying moments; this is not admission to the strict-positive
`CoupledPackets` logarithmic IVP, which is not executed here.

The 14 positive source directions are six signed axes (weight 1/15 each) and
eight signed cube corners (weight 3/40 each). Finite packet state weights scale
with L squared. The interval-average source rate instead scales with L cubed
over c; integration with `Delta_tau=c*dt/L` gives the same finite increment.
Source pi is a state stress, never an interval-average PiRate.

## Numerical checks and resolution policy

The source population/net map is not reconstructed by subtracting rounded gross
channels. Nonzero requested changes that do not advance a floating population
or either affected sector energy are rejected explicitly. No populations or
packets are clipped, projected for positivity, renormalized or silently removed.
The code retains the core five-component STF encoding for analytic STF tensors.
The committed upper density is constructed from the actual owner's endpoint
`N*x1`; it is not obtained by subtracting a nearly exhausted gross donor.
Atomic energy is reconstructed as the caller's unchanged constant component
plus the excitation of that endpoint. A positive endpoint or remaining
excitation that underflows, or cannot be represented alongside the constant
atomic energy, causes explicit rejection. A zero source update preserves its
original stocks and energy exactly. The wrapper also checks every physical
State scalar/array and Source array for finite real values before invoking the
unchanged core validators; complex values are rejected without casting warnings.

Photon sector rho/flux/p/pi must match its actual packet moments within
`256*eps*rho_gamma`, with exactly zero tolerance in true vacuum. Emitted packet
moments are checked against analytic increments within `256*eps*abs(Delta_rho)`.
The reported gross scales for conservation are total atom population N, sum of
absolute pre-step sector energies plus the emitted energy magnitude, and that
energy scale plus geometry magnitudes for the constraints. These are ordinary
floating consistency checks; they do not certify interval arithmetic or an
initially constraint-satisfying state. In particular the synthetic initial
constraint residual is generally nonzero and is preserved by the substep.

## Reproduction and bounded execution

From this unit's root run:

```sh
python code/run_bounded.py python code/reference_runner.py
```

The wrapper enforces a 30-second child-process ceiling and a cumulative
60-second implementation-science wall allocation. It records every attempted
scientific command with argv, working directory, exit code, raw stdout/stderr,
measured wall time and child CPU time in `results/EXECUTION_LEDGER.json`.
Orchestration and backup time are not measured as science. Historical remaining
campaign budgets remain null and `budget_reset` remains false.

The current suite independently integrates the original positive rates in v,
uses Decimal cancellation oracles and exact rational angular moments, tests
full/half population and count composition, checks actual core/kinetic finite
conservation and constraint preservation, and exercises the physical admission
and floating-resolution failures. No old campaign, cosmological IVP or coupled
packet evolution is run. `reference_runner.py` writes actual curve data and one
current two-panel figure only after the current validation succeeds.

Raw command outputs preserve observed failures. Any repairs are recorded in
`results/REPAIR_HISTORY.json`; a later passing run does not imply a first-pass
success. Independent code/physics/figure acceptance belongs to the separate
reviewer and is not asserted by this implementation.
