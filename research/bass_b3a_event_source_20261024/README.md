# BASS B3a detached REC event adapter

Implementation unit: `BASS_B3A_REC_EVENT_ADAPTER_20261024`.
The frozen preparatory contract remains `BASS_B3A_EVENT_SOURCE_20261024` in
`CONTRACT.md`. This source-only local reference received `PASS_SCOPED` from the final
independent physics and code reviewers; F1/F2/PHY findings are closed.
Controller publication acknowledgement is a separate delivery event, with
controller delivery receipts authoritative for its current status.

## Run the current bounded checks

From a fresh checkout of the BASS repository, use this repository-relative
working directory:

```bash
cd research/bass_b3a_event_source_20261024
```

The actual absolute cwd for this validation was:

```text
/workspace/scratch/fe69646d3c76/bass_source/research/bass_b3a_event_source_20261024
```

From the unit directory, run:

```bash
python3 code/run_bounded.py tests
python3 code/run_bounded.py reference_plot
```

The harness records exact child argv, cwd, environment overrides, stdout,
stderr, exit status, timeout status, wall time and separately user/system CPU.
It retains failures and accumulates every invocation in
`results/VALIDATION_RECEIPT.json`. Each scientific child has a 30 s ceiling;
the cumulative new tests/reference/plot wall ceiling is 60 s. Re-running
appends cost and uses only the remaining new local ceiling.
The historical campaign remaining wall/CPU stay null and `budget_reset=false`.
These local limits do not create a historical campaign balance.

The observed environment supplied NumPy, SciPy and Matplotlib. This unit uses
stdlib `unittest`; no pytest or SymPy is required. The controller actual probes from this turn in `provenance/INTAKE.json`
record Python and C++ runtimes available and successfully executed, with only
the optional pytest/SymPy packages absent in default Python. This is not a
runtime-availability blocker. This unit needs neither absent package; no
original missing-package command or exit status is invented here.

## Public API and scientific conventions

Add `code/` to your Python import path. `event_measure.py` exposes typed
`Identity`, `PhotonEventMeasure`, `GrossEventBundle` and `MomentResult`.
An identity explicitly records owner, epoch, frame, clock and provenance.
The event constructor accepts positive energy in joules, unit direction
vectors and nonnegative gross rates in m^-3 s^-1. Emission and absorption
remain separate measures. `GrossEventBundle.net_moments()` subtracts their
moments without clipping the signed result.

For `r=c*p=(E,E*n)`, `moments` computes

```text
cQ = sum(rate * r)
K(u) = sum(rate * outer(r,r) / (u0*r0 - u_spatial.r_spatial))
```

`K` has units J m^-3 s^-1. Its denominator changes with the observer.
`PhotonEventMeasure.boosted(beta, frame=...)` uses the positive off-diagonal
Lorentz convention and keeps invariant event-rate weights unchanged.
It never invokes kinetic density-weight transformations.

`PiRate_J_m3_s` is the spatial STF of `K` only for the exact target observer
`(1,0,0,0)`. For a generic future unit observer, `moments` returns the generic
`K(u)` and sets this 3D PiRate field to `None`; a coordinate spatial subblock
is not passed off as that observer's physical PSTF tensor. The tests verify
`K'(Lambda*u)=Lambda*K(u)*Lambda.T`, `K(u)*u_flat=-cQ` and the differing result
when the target observer is changed.

`rec_adapter.event_bundle(state, identity, n_mu=12, n_phi=20)` invokes the
unchanged selected REC owner domain and quadrature helpers. It restores all
eight signs of each principal-octant square-root node, rotates with the owner
eigenvectors and allocates weight/8 to each sign. It never renormalizes the
weights to force agreement. It requires the explicit pinned `OWNER` identity, canonical origin
`frame='rest'`, clock `proper_time_dt_dV_invariant`,
`owner_mode='standalone_detached'` and `native_line_owner_active=False`.

The gross channels are the effective escaping-reservoir channels
`A*n_u*(1+f_plus)*beta` and `A*g*n_l*f_plus*beta`, not every microscopic
trapped-line event. The native scalar reconstruction uses the small frozen
extract to restore `x2p=xr[1]+3*x1s*exp(-E21/TR)`, the full Planck contribution
to `f_plus`, SI number densities and stored `H`. It makes no native solver
call. The angular `S` is explicitly constructed, including in the native
scalar reference. This is a detached full-Planck/stimulated reference from
native scalar inputs, not native LINE02 or history parity.

### BASS attachment

`bass_binding.bass_rate_pair(bundle, length_m=...)` returns `BassRatePair`.
The sector order is radiation, atomic internal excitation energy. The two
sector transfers are equal and opposite in both energy and momentum:

```text
U = (kappa*L^3/c) * cQ[0]
J = (kappa*L^3/c) * cQ[1:]
PiRate_hat_radiation = (kappa*L^3/c) * PiRate_phys
kappa = 8*pi*G/c^4
```

`attach_source` takes explicit current state pressure and pi for the two
sectors. It copies these unchanged into the actual vendored BASS `Source`;
only the balanced U/J pair enters the transfer fields. PiRate stays a
separate result. The function does not determine the matter's pressure-rate
tensor. The atomic partner is internal excitation energy; thermal rate,
ionization yield and free-electron yield are zero. There is no recoil source,
new donor bath, integration, packet injection or state-stock advancement.

For example, a synthetic callback fixture can inspect a proposed rate pair:

```python
from rec_adapter import OWNER, owner, native_scalar_state, event_bundle
from event_measure import Identity
from bass_binding import attach_source
import numpy as np

state, provenance = native_scalar_state(owner.shear_fixtures()['rotated'])
identity = Identity(OWNER, 'example_epoch', 'rest', 'proper_time_dt_dV_invariant',
                    'NATIVE_SCALAR_EXTRACT; CONSTRUCTED_ANGULAR_FIXTURE')
bundle = event_bundle(state, identity)
attached = attach_source(
    bundle, length_m=1e12,
    pressure=np.zeros(2), pi=np.zeros((2, 3, 3)),
    expected_identity=identity, transfer_id='example_transfer',
    positive_domain=lambda rates: True,  # SYNTHETIC TEST ONLY
)
source = attached.source
separate_pi_rate = attached.rates.PiRate_hat_radiation
# Persist/pass the returned set when composing another pure attachment:
applied_keys = attached.applied_transfer_keys
```

A nonzero binding with a missing or false callback is refused. The example
callback certifies no physical finite reservoir; a real owner must provide
its actual positive-domain check. The returned key set is explicit caller
state for duplicate refusal, keyed by `(owner, epoch, transfer_id)` independent
of frame. It must be passed into a later attachment to preserve that refusal,
including when the same event has been genuinely boosted to another frame. Expected identity mismatch (including epoch, frame or
clock) is refused. No callback clips density, populations or signed rates.

## Current observed results

The initial 12 stdlib tests passed, exit status 0; independent review later
found missing F1/F2 guards that these tests did not cover. The authorized
repair added three regression/zero-source tests. Their initial run retained
six guard failures across F1/F2, while the exact-zero test passed. After the
minimal repair, the targeted 3/3 and final full 15/15 suites passed, exit 0.
See `REPAIR_ADDENDUM.md` for the unchanged RED log and full repair timeline.

The initial test invocation used the following measured resources. It used
0.7295351350 s wall and 0.728739 s CPU (user 0.663727 s, system 0.065012 s).
The reference/plot process exited 0 with 2.0566071320 s wall and 2.052599 s CPU
(user 1.966444 s, system 0.086155 s). The initial validation subtotal
was 2.7861422670 s wall and 2.781338 s CPU. Including the authorized RED/GREEN
and final suite runs, the current implementation subtotal is 5.1271016830 s
wall and 5.119500 s CPU. The independent reviewer initial-plus-final probe cost, recorded in
`reviews/CODE_REVIEW_FINAL.json`, was 1.2357569410087308 s wall and
1.2340099999999998 s CPU. `RESOURCE_LEDGER.json` separately aggregates measured
implementation, reviewer and internal Fraction-check costs; the current
Wolfram kernel actual elapsed time remains unmeasured. These are measured child-process
costs, not estimates of model inference or editing time.

The current native scalar actual-owner call at the identical quadrature has
energy discrepancy 1.9453006649e-16 and PiRate maximum-entry discrepancy
4.0704039246e-16, both normalized by the gross energy source. The local gate
is 5e-12. Constructed emission, absorption and LTE cases are separately
reported in the reference JSON. Same-grid parity does not establish angular
continuum convergence. The historical B2 2e-8 gate is untouched.

A/B uses six equally weighted axis directions and eight equally weighted cube
corners, unit energy and unit total gross event rate. Both have the same rest
first/second moments. At beta=(3/5,0,0), both have
`cQ=(5/4,3/4,0,0)`, but their PiRate diagonal entries are
`A=(3/10,-3/20,-3/20)` and `B=(5/22,-5/44,-5/44)`. The exact axis formula
for A-B xx is `2*b^2*sqrt(1-b^2)/(3*(3-b^2))`. This formula is for scalar
axis boosts only. The oblique counterexample beta=(1/5,2/5,2/5) instead has
A-B xx `-286408/10384605 = -0.02758005720968687`.

The new diagnostic plot samples beta=0..0.95 and has maximum absolute numeric
minus exact residual 4.4408920985e-16. Its PNG was visually inspected: both
axis curves, a distinct oblique point below zero, and a linear residual panel
with the zero baseline are visible. It is a new adapter diagnostic; no
historical figure was regenerated.

## Files and review boundary

- `code/event_measure.py`: event representation, boosts and observer moments.
- `code/rec_adapter.py`: detached owner bridge, all-eight-sign restoration,
  native scalar reconstruction.
- `code/bass_binding.py`: pure balanced transfer attachment using actual BASS
  `Source`; separate PiRate.
- `code/run_bounded.py`: cumulative measured subprocess receipts.
- `code/reference_runner.py`: current references, CSV and new diagnostic.
- `tests/test_adapter.py`: 12 initial tests, including wrong-density-weight
  control; `tests/test_repairs.py`: three canonical-identity, cross-frame
  duplicate and exact-zero-source regression tests.
- `results/01_tests.log`, `results/02_reference_plot.log`: raw stdout/stderr.
- `results/VALIDATION_RECEIPT.json`: exact commands and measured resources.
- `results/CURRENT_REFERENCE.json`, `results/AB_EXACT_BOOST.csv`,
  `results/AB_EXACT_BOOST.png`: small current scientific outputs.
- `SOURCE_INDEX.json`: pinned owner/base and individual immutable source bytes.

The minimal REC files are copied unchanged with their original layout and
license. The BASS core copy matches true Git blob
`3e95a652715b346a47f097fde2131540237390a4`; the materialized source had one
serialization newline, repaired only in the owned copy by finding the exact
blob match. Original sources were not modified. Code and evidence remain
inside the task-owned directory. At the implementation-agent checkpoint, this agent had performed no external
Git/Drive/Dropbox calls, merges or publication. This is not a current global
delivery-status assertion: controller delivery receipts are authoritative. The intentionally failing targeted RED run is preserved; the authorized
identity/key repair and final 15/15 PASS are described in
`REPAIR_ADDENDUM.md`. No child timed out. Requested model: `gpt-6.1-sol`;
observed runtime model is not inferable from tool/process evidence.

## Documentation closeout

After both final reviewers returned `PASS_SCOPED`, this closeout updated only
review/delivery wording and resource aggregation. No kernel, test, reference
output or figure was changed, and no scientific process was rerun.
