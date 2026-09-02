# Plot-driven CRAG audit — SYNC-MAP-02C R3

## Evidence surfaces

- `R3_SOURCE_COVERAGE_SUMMARY.csv`
- `R3_SOURCE_COVERAGE_SUMMARY.svg`
- `R3_SHARED_FORMULA_CONSUMERS.csv`
- `R3_FEDERATION_GATE.svg`
- `scripts/render_sync_map02c_r3_plots.py`

The current chat-local Python runtime returned a client error and is not
relabeled as a plot pass. The repository path instead regenerates both SVGs
with standard Python in GitHub Actions and byte-compares them with the
committed evidence.

## Direct plot reading

### Exact-source coverage plot

The four bars read `7 + 8 + 4 + 3 = 22`:

- seven files carry one or more named R3 relations;
- eight are REI-owned numerical/closure surfaces with no new shared Formula ID;
- four are nonformula protocol or typed-absence surfaces;
- three are runner/local-stage surfaces delegating to classified operators.

The dominant bar is an adjudicated REI numerical/closure class, not an
uninspected remainder. The plot therefore supports complete path disposition,
not complete line-by-line formal proof.

### Federation-gate plot

Two independent arrows enter 02E:

```text
02C REI ─┐
         ├─> 02E six-record shared export ─> 02F
02D HTT ─┘
```

The 02E box is visibly marked `HELD`, and the figure separately states that it
contains no background provider. This prevents the stale visual narrative
`02B REC -> four-formula export`.

## CRAG

### Correctness

The source-coverage totals agree with the exact 22-row CSV and the production
verifier. The six-row consumer matrix agrees with the R3 JSON. The DAG plot
agrees with the required predecessor set `{02C,02D}`.

### Retrieval

The SciSpace lock supports the distinction between the full-sky physical
Lorentz pullback and mask/frequency/estimator response. It does not determine
project signs. The exact code supplies the project adapter `n=-e`.

### Augmented checks

The verifier and tests are augmented with mutations for a compound owner,
stale four-formula union, missing source row, source-blob drift and premature
02E activation. The Wolfram oracle adds Jacobian-power, Doppler-weight and
sphere-tangency mutations.

### Generation

The surviving prediction is narrow:

1. the next shared Formula-ID export contains exactly six records;
2. REI contributes no new unique frame/photon Formula ID;
3. the export does not unlock the BASS background provider, anisotropic REI
   group-redshift evolution, finite-electron-tilt collision or fitting.

## Adversarial interpretation

A reader could incorrectly treat the fifteen exclusion rows as weak or absent
review. The matrix prevents that interpretation by binding every row to an
exact blob, semantic disposition and exclusion reason. Conversely, the chart
must not be cited as proof that every numerical REI formula is correct; it is a
coverage/ownership figure only.

The gate figure could be misread as saying 02E is implemented. The explicit
`HELD` label and downstream 02F/consumer/manual gates prevent that reading.

## Verdict

`SURVIVING_NARROWED_CLAIM`

Allowed claim:

```text
The active REI source tree is completely classified at path level, its
relations have atomic owners, and the next shared export scope is the six-item
REC+REI+HTT union, still held behind 02C/02D frozen readback.
```

Rejected claim:

```text
The shared export, background coupling, provider path, first canonical
interval, or observational/statistical pipeline is complete.
```
