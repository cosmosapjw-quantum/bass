# Signed Sigma/Pi pilot implementation

This adapter loads the immutable REI C15 snapshot at
`80825585f9fe31d2ee0d5af545ada3fa1f52be72`. It verifies every fetched source
file against `vendor/rei_c15/SOURCE_FETCH_MANIFEST.json` **before importing
owner code**. It does not edit that snapshot, replace any physical kernel,
change the owner solver tolerances, or change source/rate ownership.

## Commands

Run with one numerical library thread per worker; `shared_executor.py` sets
worker thread variables itself. For standalone commands use:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 -m unittest -v test_pilot.py
python3 sweep.py prepare --out runs/pilot81 --nsteps 64 --group-size 1
python3 shared_executor.py runs/pilot81/manifest.json --scope runs/pilot81_scope --profile sandbox --max-workers 8
python3 sweep.py aggregate --scope runs/pilot81_scope --manifest runs/pilot81/manifest.json --out results/pilot81
python3 plot_pilot.py --aggregate results/pilot81 --out results/pilot81/sigma_pi_pilot
```

For NCP prepare the manifest from the exact copied local package **on the
execution host**, so absolute paths and Python executable resolve there. Use
`--profile ncp --max-workers 64` under the executor's available-capacity caps.
Grouping is configurable with `--group-size`; default 1 creates 81 independent
jobs. A larger group reuses one prepared context for several sequential cases.
Each group writes `result.checkpoint.json` after every successful case, and
`result.failure.json` with the traceback if a case fails. Group failures return
nonzero. A checkpoint preserves raw work for diagnosis; automatic cross-group
or partial-group case reuse is not implemented. The executor reuses verified
successful **whole jobs**. Do not change grouping in an existing scope expecting
completed individual cases to transfer automatically.

Preparation refuses to overwrite an existing scientifically different input
or manifest. Scientific input identity contains the contract, 81 ordered cases,
step count, compression and feedback choices. Source identity includes all
snapshot Python/CSV/JSON files, the adapter, map, contract and fetch manifest.
Toolchain identity records the actual Python, NumPy and SciPy versions.
Concurrency is absent from scientific case identity. Run paths are exact and
must remain unchanged for a given manifest.

`aggregate` accepts successful executor receipt referenced results. It checks
their recorded output SHA256 and science binding and rejects conflicting
copies of one case. For explicit result files use `--result-files 'path/*.json'`
instead of `--scope`; these must be successful group result JSONs. It writes
ordered `cases.csv`, `history.csv` (including step zero), and `summary.json`.
Nested owner energy dictionaries are flattened into clearly prefixed CSV columns,
for example `Hamiltonian_source_J_m3.gamma`; raw result JSON stays intact.
Partial aggregates explicitly list missing case IDs and are labelled PARTIAL.
No failed history is treated as a successful result.

## Prepared immutable context

The original isotropic `EinsteinBoltzmann` constructor creates the cosmology,
native stellar source, Case-A log-PCHIP rate table, angular matrices and
finite-mass radial grid once per group. Their numerical arrays are marked
readonly. Models share only the explicitly enumerated fixed constructor
fields. Each model gets its own Parameters, alpha-dependent massive weights,
zeroed counters, fresh gas/photon/multipole state and fresh proxy. Every owner
evolution method, RHS, reduction order, compression call and gate is used
without override. No per-case inner multiprocessing exists.

The numerical calibration uses the original initial H and original radial
`massive_source_3moments(0,0)` J01. The common alpha is mapped through
`sigma_pi_map.initial_seed`. Initial requested and achieved invariants must
agree to absolute 3e-13; weights and stress are never clipped. Unresolved
near-zero values retain their signed raw values and receive a status label.
The adapter emits both half-contraction and Frobenius norms, continuous signed
contractions, physical `D_physical_Pa=sum(Pi_gamma,Pi_nu,Pi_massive,Pi_UV)`, and
`2*s*D` shear work. Original `Pi_total_source` remains separate. All physical
feedback switches are enabled with manufactured multiplier one.

## Targeted verification

`test_pilot.py` tests 81 distinct signed coordinates, admissible positive P2
weights, actual owner initial values, the factor-three KAPPA normalization,
signed contractions, an inadmissible request, and fresh-state isolation. One
fixed actual extremal input compares original versus prepared initial data and
the first two nsteps=64 short steps. It checks unchanged original ledger gates,
rows, multipoles and geometry. This is an optimization-equivalence check, not
a timing or speedup benchmark. Successful group JSON rejects NaN/Infinity.
The owner additionally enforces per-step number 5e-12, energy 5e-11 and
gamma/neutrino number-monopole 3e-9 gates; these appear in every result.

## Figure and claim boundary

The figure shows signed initial/final stress response, signed initial/final
shear, representative actual trajectories, and endpoint physical stress norm.
Every axis uses the half-contraction convention. The endpoint grid shows
actual sampled cells; no interpolation, fit or smoothing is performed.
The plot includes the near-z4 interval and warm initial gas, and writes PNG,
PDF and full data/plot provenance JSON. Small thermochemical changes remain
in the CSV but are not presented as converged differences.

This is a conditional warm short interval near z=4 with original external MD14
stellar production, Grackle Case-A chemistry and escape ledger. Full
stellar/emitter and escaped-radiation Q^a closure, a cold z20-to4 history and
global angular/spectral convergence remain open. Source-equivalent preparation
and successful numerical gates do not establish those broader claims.
