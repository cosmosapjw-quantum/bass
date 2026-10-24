# B3d angular-cohort implementation

This compact client implements the frozen B3d contract with float64 arrays.
The actual parent `finite_exchange.cubature14`, `core.FixedScale`, and
`kinetic.moments/tensor` are called unchanged. Their seven source/dependency
copies are bound in `results/SOURCE_COPIES.json`; computed Git blob identities
identify file content and do not substitute for an independent remote readback.

`angular_cohort.py` integrates over birth directions. The number measure has
only the cosmological dilution D. It creates no atomic source transaction,
event rate, duration, IVP, or REC trajectory. A current-direction change would
instead use dOmega'=det(R)/|R*n|^3 dOmega; no extra Jacobian is applied to these
birth-label sums. `Q26` is the canonical positive rule defined in the contract,
not an observed actual REC26 inventory.

The continuum uses independent Gauss-Legendre mu and uniform azimuth grids.
The octant cross-check explicitly reflects its positive-octant nodes over all
eight octants and is restricted to diagonal S,C. The K40 tails are ideal-node
analytic truncation bounds; floating nodes and summation are not interval
certified. Raw small differences are retained even when unresolved below
4096 eps; such values cannot support a reported order or leading-coefficient
claim. Only plotting masks true zeros and eta=0 in logarithmic panels.

The tests cover monomials through degrees5/7, the actual14-rule degree-six
defects, birth/trace/flux identities, co-rotation, actual physical packets,
isotropic limit, immutable source copies, and the frozen invalid input classes.
The sweep writes after each fixture to preserve partial output on failure.
Summary gates use the exact rational coefficients supplied by root's frozen
theory, fixed error denominators, and the finest resolved consecutive triplet.
Q26 coefficients/orders are diagnostic; benchmark2e-8 failures are retained
and are not admission failures for this angular-quantification unit.

After root confirms R6 and actual S0 preservation, exact commands from this
lane are:

```
python code/metered_run.py tests/test_angular_cohort.py
python code/metered_run.py code/run_sweep.py
python code/metered_run.py code/summarize.py
```

Each child runs with one thread and at most30wall/20CPU seconds; cumulative
implementation allocation is60wall/40CPU seconds, budget_reset=false. The
CPU hard limit is reduced to the remaining whole CPU seconds if necessary.
Every start is saved before dispatch and all raw stdout/stderr, exit status,
argv/cwd/UTC, package versions, source hashes, and actual wall/CPU are retained.
The first substantive failure stops execution for root's targeted disposition.
These mechanical gates do not grant scientific admission; C9 is independent.
