# Independent std-only Rust P2/P4 implementation

Source: `../balance_p24.rs`.
Algorithm ID: `BASS_LRS_SOURCE_KL_P24_V1`.
Source SHA256 at the recorded run:
`ad88b0902207747c61145b65d60818efa567999daaf5715dfed7d8352b7f4f14`.

## Scope and API

This module adjusts angular birth weights of a declared locally isotropic source.
The caller owns that declaration, the birth frame, and the fixed spectral owner.
Directions, spectrum, surviving photon weights and native defaults are not changed
by this module. Native integration and finite-bin ledgers have separate receipts.

```rust
pub const ID: &str = "BASS_LRS_SOURCE_KL_P24_V1";
pub struct Projection {
    pub weights: Vec<f64>,
    pub multipliers: [f64; 2], // lambda2, lambda4
    pub residuals: [f64; 2],   // mean(P2), mean(P4)
    pub iterations: usize,    // evaluated nested distributions, incl brackets
}
pub fn project(mu: &[f64], prior: &[f64], tol: f64)
    -> Result<Projection, &'static str>;
```

The input has 2–4096 strictly sorted finite directions in `[-1,1]`, finite
positive prior weights, reflection-paired directions and an even normalized prior.
The reflection tolerance is the inherited `5e-14`. Prior normalization scales by
the largest weight before summing. The default moment tolerance is `3e-15`;
only tightening within `[1e-16,3e-15]` is accepted.

The exact support theorem is in `../S3_THEORY_KO.md`. Float geometry uses a fixed
`64*f64::EPSILON` uncertainty guard. This guard never enlarges a feasible set:
ambiguous cases are returned unresolved. A rank1 target compatible in exact
arithmetic can have full-positive weights, but this f64-only entry point does not
certify a near-zero affine defect. It returns `FEASIBILITY_UNRESOLVED_RANK1`.
The sharp exact support `z={0,3/5}` is tested specifically to preserve this
distinction from mathematical infeasibility.

On certified full-dimensional interior supports, the nested dual solve fixes
lambda4 and brackets the unique P2 root in lambda2; the outer P4 residual is
monotone with derivative equal to the covariance Schur complement. Each bracket
has at most 60 doublings and each bisection at most 200 steps. The inner tolerance
is `tol/8`. Log-sum-exp and compensated summation are used. Both moment residuals,
normalization, reflection parity, finiteness and strictly positive final weights
are checked before returning a result. Numerical zero weights at bracket probes
are permitted; zero weights in returned results are rejected.

## Failure classes

| Category | Returned labels |
|---|---|
| Invalid input | `ANGULAR_INPUT_DOMAIN`, `ANGULAR_TOLERANCE_DOMAIN`, `REFLECTION_SOURCE_REQUIRED` |
| Clear fixed-support infeasibility | `INFEASIBLE_P24_RANK0`, `INFEASIBLE_P24_MEAN`, `INFEASIBLE_P24_RANK1`, `INFEASIBLE_P24_LOWER`, `INFEASIBLE_P24_UPPER` |
| Geometry unresolved in f64 | `FEASIBILITY_UNRESOLVED_RANK1`, `FEASIBILITY_UNRESOLVED_NEAR_BOUNDARY` |
| Numerical support/domain loss | `NUMERIC_POSITIVE_SUPPORT_LOSS`, `NUMERIC_EXPONENTIAL_DOMAIN`, `NUMERIC_NORMALIZATION_DOMAIN`, `NUMERIC_MOMENT_DOMAIN`, `NUMERIC_REFLECTION_LOSS` |
| Numerical solve failure | `INNER_P2_LOWER_BRACKET`, `INNER_P2_UPPER_BRACKET`, `INNER_P2_PRECISION_LIMIT`, `INNER_P2_NOT_CONVERGED`, corresponding `OUTER_P4_*` labels |
| Failed output contract | `MOMENT_TOLERANCE`, `NORMALIZATION_TOLERANCE` |

An exact boundary requires dropping some support weights; it is not accepted
under the full-positive contract. Float ambiguity is not asserted to prove a
boundary or no-positive result. Solver failures do not establish infeasibility.

## CLI format

Compile and run from the research directory:

```bash
rustc --edition=2021 -O balance_p24.rs -o balance_p24_probe
./balance_p24_probe INPUT.txt OUTPUT.csv
```

Input uses the old whitespace token structure with the new ID:

```text
BASS_LRS_SOURCE_KL_P24_V1 CASE_COUNT
CASE_ID RAY_COUNT
mu_0 prior_0
mu_1 prior_1
...
```

There are 1–512 cases and at most 2,000,000 input bytes. IDs must be unique and
contain no comma. Extra tokens, missing values and rejected cases are errors.

Output is:

```text
BASS_LRS_SOURCE_KL_P24_V1 CASE_COUNT
id,nrays,lambda2,lambda4,residualP2,residualP4,evaluations,w0,...,w[n-1]
...
END CASE_COUNT
```

CSV weights start at field index 7. Floats have 17 digits after the decimal in
scientific notation. The CLI uses the fixed default `3e-15`. It validates every
case before creating output and uses `create_new(true)` to forbid overwrite.
Success exits 0 with `BALANCE_P24_PASS`; errors exit 3 with `BALANCE_P24_ERROR`.

## Executed checks

Actual compiler: `rustc 1.94.1 (e408947bf 2026-03-25)`,
`x86_64-unknown-linux-gnu`; see `rust_p24_version.log`.

Sixteen unit tests passed. They include an analytic unique three-group solution,
an independently manufactured exponential-family KL minimizer on four groups,
idempotence, extreme positive common prior scaling, full positivity and parity,
the sharp lower/upper/mean/rank failures, compatible rank1 unresolved status,
near-boundary ambiguity, invalid input and refusal to relax tolerance. Actual
native GL8 source-frame supports at birth `b=-0.3,+0.3` passed the default moment
tolerance. Commands, exit statuses and source identity are recorded in
`rust_p24_execution.json`; compiler/test logs are adjacent.

`rust_p24_cli_checks.py` executed the compiled CLI. One valid analytic case and
seven negative controls passed. The controls cover preservation of an existing
output's SHA256 under a repeated invocation, trailing tokens, wrong schema,
truncation, duplicate case IDs, infeasibility in a later case before any output
is created, and the mathematically feasible rank1 example returned unresolved.
Actual inputs, outputs, logs and `RETURN.json` are in `rust_p24_cli_artifacts/`.

No external Rust crate or scientific runtime is required by this module. No
native photon/energy conservation claim is made by these algorithm tests.
