# B3c1 implementation notes

The new client implements the frozen contract and R6-N1 addendum. The unchanged
parent source and its required dependencies are copied under this lane;
`results/SOURCE_COPIES.json` records original and copied SHA256 values.

`emission_split.py` reconstructs `core.State` and `core.Source` from six geometry
coordinates, the current upper fraction, and immutable photon birth data at each
RHS. It integrates only `h,sigma_xx,sigma_yy,alpha,beta_xx,beta_yy` plus the
expansion-work ledger divided by initial excitation. The sector densities are
reconstructed rather than independently integrated. Ground rest mass and
excitation are accounting sectors of the same atom population. The actual
`core.rhs` supplies geometry derivatives; there is no constraint projection.

A reaction rebuilds the actual `LineState` from current geometry and stock,
constructs excitation from `scale.density_factor * E * line.n_u_m3` in that
multiplication order, and calls unchanged `commit_emission` with sectors0/2.
Every call has a unique transfer id and current epoch. Old cohort birth
coordinates remain unchanged when the current transaction's identity is rebound.
The source's original opacity, positivity and 256-epsilon checks remain active.
Global time advances only in A. Photon moment evaluation uses the actual packet
moment routines, including the explicit inherited vacuum branch.

`prescribed_oracle` uses `brentq` on its own monotone scalar residual and four
one-dimensional quadratures in the exact exposure variable. Its angular sums
are the independently reduced 14-ray formulas in the derivation, rather than a
time-stepping replay. Quadrature errors are estimates. Distance/order formulas
follow the addendum; orders below 4096 machine-epsilon resolution are null.

After preservation S0 ACK, exact new execution commands from this lane are:

```
python code/metered_run.py tests/test_split.py
python code/metered_run.py code/run_case.py controls
python code/metered_run.py code/run_case.py coupled 16
python code/metered_run.py code/run_case.py coupled 32
python code/metered_run.py code/run_case.py coupled 64
python code/metered_run.py code/run_case.py coupled 128
python code/metered_run.py code/run_case.py tight 128
python code/metered_run.py code/summarize.py
```

Every child is metered with one thread, 30-second wall timeout and 20-second CPU
hard limit (reduced to the whole CPU seconds remaining when necessary).
Each start receipt is saved before child dispatch. Receipts are additive and preserve all raw stdout/stderr, exit
codes, source hashes, package versions, UTC timestamps, argv and cwd. The
implementation allocation is 60 wall / 40 CPU seconds across scientific
children; historical budget reset is false. `summarize.py` converts only the new
raw results into final CSVs, frozen numerical gates and the requested figure.
Independent Astra review and root admission are separate from mechanical gates.
