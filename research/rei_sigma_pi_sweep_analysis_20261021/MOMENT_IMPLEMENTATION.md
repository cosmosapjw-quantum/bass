# ACCEL03 massive stress response implementation

Status: **PENDING_INDEPENDENT_REVIEW**. The prescribed bounded numerical
checks passed; scientific admission belongs to the controller and fresh
independent reviewer.

## Implementation

`moment_response.py` exposes
`moment_response(qbar2, mu2, weights, mass, x, b)`. Its arguments are existing
dimensionless owner quadrature arrays and fixed distribution weights. It
returns `J0`, `J2`, `J4`, `G`, `J2_x=-5*J2+J4`, `J2_b=-G`, and the absolute
stress-kernel sum. All sums use NumPy binary64 arrays. It imports no owner
model, native backend, preparation context, or evolution machinery. It
validates the finite, nonnegative quadrature domain and energy before
evaluation. It permits negative local x values so the prescribed centered
stencil at x=0 can evaluate the exact finite-sum formula.

`verify_moment_response.py` reuses the original split pilot's
`PreparedContext` and `parameters(alpha_m=...)` to prepare the unchanged
96 by 32 quadrature at mass/T=30. That preparation includes the existing
initial calibration; it runs no trajectory, time step, RHS, solver, native
backend, build, or benchmark. The pure diagnostic consumes
`model.massive_q2`, `model.massive.mu2`, `model.massive_weight`, and
`model.massive.mass` directly. No production source was edited.

The verifier uses exactly the frozen 27 central points:

- alpha_m = -0.9, 0, 1.8;
- x = 0, ln(0.2/0.1999), 0.1;
- b = -0.1, 0, 0.1.

Each derivative uses the five-point formula with h=2^-15. Every residual is
normalized by the positive central energy J0; none is divided by a possibly
cancelled stress. Both frozen derivative limits remain 2e-9, and the G
criterion remains G >= -128*eps64*J0. There are 216 stencil evaluations in
addition to the 27 central evaluations.

## Observed bounded result

The saved command exited with status 0. Maximum energy-normalized derivative
residuals were:

| Quantity | Maximum | Frozen limit |
| --- | ---: | ---: |
| x derivative | 1.0715866992998556e-13 | 2e-9 |
| b derivative | 3.6901037780978584e-14 | 2e-9 |

All 27 G checks passed; the smallest central G was
0.012992574995213354. Numerical threads were fixed to one, process affinity
was restricted to CPUs 0 and 1, and no worker processes were created.
Observed toolchain: Python 3.12.14, NumPy 2.3.5.

Two separate one-node computational illustrations use qbar^2=1, mu^2=1,
weight=1, x=b=0. The massless illustration uses mass=0 and returns
J4/J2=1 and J2_x/J2=-4. The nonrelativistic illustration uses mass=10^6;
its exact v^2 is 1/(10^12+1), so J4/J2=v^2 and J2_x/J2=-5+v^2.
These are illustrative limits, not C15 parameter checks and not radiation
evolution comparisons.

## Evidence and identities

- `evidence/MOMENT_RESPONSE_INPUTS.json`: all three complete quadrature
  inputs, full parameter records, owner ref, source file bindings, contract,
  theory, implementation and verifier SHA256 values.
- `evidence/MOMENT_RESPONSE_RAW.json`: every central moment and all eight
  stencil diagnostics for each point, signed differences, normalized
  residuals and positivity results.
- `evidence/MOMENT_RESPONSE_ILLUSTRATIVE_LIMITS.json`: the distinct one-node
  examples and their analytic ratios.
- `evidence/MOMENT_RESPONSE_STATUS.json`: bounded numerical summary and
  pending review status.
- `evidence/MOMENT_RESPONSE_RUN.log`: actual argv, thread environment,
  combined stdout/stderr, and exit status.

Original owner ref: `80825585f9fe31d2ee0d5af545ada3fa1f52be72`.
Validated pilot source binding:
`9a3a36bf03885245e6910f2d544d13634fb1b82dac45ddcb484efc7ecdb91334`.
Requested execution model: `gpt-6.1-sol`. Observed runtime model: `null`
(not exposed by the execution interface). The request is not treated as
evidence of actual runtime identity.

Reproduce from the checkout root with:

```sh
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 BLIS_NUM_THREADS=1 python -B research/rei_sigma_pi_sweep_analysis_20261021/verify_moment_response.py
```

For this sandbox's outer workspace layout, prefix the script path with
`bass_work/`, as shown by the actual saved command. The script also enforces
the numerical thread environment and at most two CPUs before importing
NumPy.
