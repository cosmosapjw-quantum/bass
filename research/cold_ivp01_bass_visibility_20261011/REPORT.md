# Finite stored rest-frame visibility implementation

The new wrapper evaluates existing BASS directional scattering rates at zero
material velocity and a fixed unit direction, averages adjacent edge rates,
and actually calls `integrate_visibility`. It returns both edge rates and cell
averages with the finite visibility result. A linear rate schedule has exactly
these edge depths and cell probabilities. No within-cell visibility profile,
chemistry evolution, continuum result, or physical late-time certificate is
asserted. Tail zero supplies no additional depth after the stored interval.

The campaign consumes REI109 stored physical N32 histories, IDs 0 through 3,
on five proper/normal second edges from 0 to 1e14. PR138 snapshot guards and
density/fraction mapping are retained. Decimal80 computes the same schedule
from actual binary mapping inputs and binary physical constants. The stored
producer Decimal histories are checked separately at the stated 1e-10 electron
density criterion. N8/N16 and three-edge schedule differences are reported as
diagnostics without a convergence claim.

One offline locked build took 37.05 seconds, one targeted test took 0.35
seconds, and one campaign took 0.04 seconds. No solver was launched. All
prescribed thresholds, controls, actual opacity comparison arithmetic, observed
survival/cell probability bounds, and finite mass conservation passed.
The read-only closeout checks source receipt stability and `git diff --check`.
Raw inputs, stdout, stderr, actual binary identity, and receipts are preserved
in `evidence/`. Independent Astra review approved `PASS_SCOPED` for the finite
stored schedules (see `REVIEW.json`). Continuum/convergence, physical late-time
visibility, chemistry evolution, within-cell peak and broader admission remain
`HOLD`. The first mechanical closeout failure is retained; its correction did
not rerun the build, test or campaign.

`HARNESS_UNAVAILABLE`: the configured bounded-work RULES path was absent;
the parent-supplied task contract and finite hard maxima govern this unit.
Requested lower-tier execution was supplied by the parent; runtime model
identity was not independently observed. Original dirty checkouts were
preserved. Scoped recovery backup and draft publication are authorized.

The task's contract was recorded before build/campaign; initial wrapper edits
preceded the parent's clarification that no on-disk Astra contract existed.
