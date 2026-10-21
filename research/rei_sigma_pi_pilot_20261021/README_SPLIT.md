# Independent matter and radiation stress pilot

This additive unit implements `SPLIT_CONTRACT.json`. It retains the completed
81-case common-alpha pilot and does not edit its source, results or provenance.
The immutable owner remains REI PR141 at
`80825585f9fe31d2ee0d5af545ada3fa1f52be72`.

## Scientific inputs and component definitions

The new input chart is the full signed 9×9×9 grid in initial half-contraction
`Sigma`, matter `Pi_m`, and radiation `Pi_r`, for 729 distinct cases. Zero
magnitudes have sign zero; all nonzero magnitudes have both signs.

Matter stress means **the collisionless massive nonbaryonic Vlasov component**:
`D_m = Pi_massive`. Under the existing owner closure the baryonic gas and
remaining cold matter have zero anisotropic stress. Radiation stress means
`D_r = Pi_gamma + Pi_nu + Pi_UV`, with the owner's massless neutrino component.
These physical components are read from every actual evolved owner row. UV is
initially empty and subsequently evolves through the unchanged native source
and gas model.

The initial source calibration uses the original isotropic initial H and the
original finite-mass J01 quadrature. It sets
`W_m = mass_ref_density*J01/5` and
`W_r = (rho_gamma + rho_nu)/5`.
Each independently requested signed component maps to its own positive P2
coefficient through `sigma_pi_map.initial_seed`. Gamma and nu share alpha_r;
massive particles use alpha_m. Every coefficient must remain in [-1,2], and
no weights, stresses or cancellation residuals are clipped. The actual owner
initial state must achieve each requested signed component and shear to
absolute 3e-13.

The dimensionless normalization uses `kappa_time = 3*owner.KAPPA`:

- `Pi_m_half = kappa_time*abs(D_m)/(sqrt(3)*H^2)`.
- `Pi_r_half = kappa_time*abs(D_r)/(sqrt(3)*H^2)`.
- `Pi_total_half = kappa_time*abs(D_m+D_r)/(sqrt(3)*H^2)`.

The tensor sum is formed **before** its norm. `Pi_component_norm_sum` is a
separately named diagnostic upper bound, never the total stress norm. Results
retain the component/total signed contractions, half and Frobenius norms,
`2*s*D_m`, `2*s*D_r`, `2*s*(D_m+D_r)`, their floating-point work-sum residual,
and `cancellation_fraction = 1-|D_m+D_r|/(|D_m|+|D_r|)` (zero for a zero
denominator). Each component and total has its own unresolved status below
3e-13, while its raw value and sign remain intact.

The nominal input cancellation plane contains 81 cases: 72 with nonzero
opposing components plus nine component-zero cases. Its physical total can
have a nonzero roundoff residual. Independently evolving components need not
continue to cancel.

## Execution

The actual run is **COMPLETE**: 729 cases, 243 successful groups, 47,385 history
rows, and 5,832 stored gates passing. The first group was reused after changing
worker width from one to eight. Execution source is
`82372ed8db68085868603d4267a630ed9cde6abb`; figures have separate plot provenance.
Do not repeat the completed sweep to populate additional CPU cores. The following
commands only rebuild aggregates and figures from the saved verified outputs.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 split_sweep.py aggregate --manifest results/split729/inputs_manifest/manifest.json --scope results/split729/scope --out results/split729/aggregate
python3 split_plot.py --aggregate results/split729/aggregate --out results/split729/aggregate/sigma_pi_split
```

The default groups contain three sequential cases, giving 243 independent
jobs. One context per group shares the readonly native source, cosmology,
rate-PCHIP, radial grid and angular operators from the prior preparation.
The split-specific guard admits independent alpha_m/alpha_r while keeping all
other parameters and switches fixed. Every case owns its own massive weights,
state, gas, photons, proxy, counters and integration results. No owner dynamics
method is overridden, and there is no multiprocessing within a case.

Each successful case flushes a group checkpoint. A failure writes the traceback
and completed case IDs, returns nonzero, and retains raw outputs. The executor
can reuse verified complete whole jobs; partial-case or cross-group reuse is
not implemented. Resource settings and worker counts remain outside science
identity. Prepare on the execution host to bind that host's exact executable
and paths. NCP resource limits are controlled by the existing executor profile.

Science binding includes the new split adapter and contract, the prior sweep
and map dependency, the immutable source package, exact inputs and observed
Python/NumPy/SciPy versions. Plot scripts are recorded as figure provenance
and are not part of the scientific solver identity. Preparation refuses to
overwrite a differing immutable input or manifest.

Aggregation accepts successful receipt-referenced results, verifies receipt
output hashes, science binding, owner ref and step count, and checks complete
history length and final a. It rejects conflicting duplicate cases and
preserves deterministic order. `cases.csv`, `history.csv` including step zero,
and `summary.json` retain the component data, original errors, raw owner
history values and flattened nested owner energy columns. Partial aggregates
explicitly list missing case IDs and are labelled PARTIAL. The group JSON
remains the full raw-plus-derived owner result.

## Targeted verification and figures

`test_split.py` checks all 729 actual initial mappings and both positive seed
families, including the 72 nonzero-component cancellation states. Two opposite
seed inputs compare prepared and original owner initial states and the first
two nsteps=64 short steps, with fresh-state isolation and unchanged original
ledger gates. The export check serializes those actual opposite-alpha states
and every owner row field through both canonical JSON and file output,
including NumPy booleans, while rejecting nonfinite and unsupported values.
No timing or speedup claim is made. The tests do not execute the 729-case sweep.

`split_plot.py` writes two 2×2 PNG/PDF figures and corresponding provenance:

1. `_slices`: actual signed endpoint shear minus the actual endpoint of the
   same-initial-Sigma, zero-initial-matter-and-radiation-stress control, at Sigma 0, +.004 and
   -.004 on the nonuniform matter/radiation grid, with the exact cancellation
   diagonal marked; a fourth panel shows that same paired response along the input
   cancellation plane for each initial shear.
2. `_components`: separate matter and radiation stress changes at zero initial
   shear, actual-minus-initial component trajectories for opposing initial stresses, and the
   total stress norm generated from initial cancellation.

Component changes subtract actual initial states; shear panels subtract the
actual matching control endpoint. Raw initial and final values are preserved.
Meshes use physical midpoint
edges from the full contract grid, masked missing cells and a zero-centered
diverging color scale for signed changes. No fit, smoothing or interpolation
is used. Separate component evolution and total-norm generation are labelled
explicitly. Input hashes, source identity, script/helper hashes, closure scope
and the warm near-z4 interval accompany the figures.

## Claim boundary

This remains a warm a=.1999 to .2, near-z4, non-tilted LRS Bianchi I
conditional pilot. The owner uses external MD14 stellar production, Grackle
Case-A chemistry/escape and its existing positive compression/feedback scheme.
Full donor/escape Q^a closure, cold z20-to4 histories, arbitrary higher initial
moments, general tensor orientations and angular/spectral convergence remain
open. Independent matter/radiation inputs and successful numerical gates do
not establish those broader claims.
