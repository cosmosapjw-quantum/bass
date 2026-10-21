# ACCEL03 stored-result figures

Status: **PENDING_INDEPENDENT_REVIEW**. Both rendering commands exited 0,
and the focused source-point equality checks passed. The controller and
independent reviewer retain scientific admission and final visual review.

## Portable interface

```sh
python -B research/rei_sigma_pi_sweep_analysis_20261021/plot_sweep.py --aggregate AGGREGATE_DIR --out OUTPUT_DIR [--signed-sigma 0] [--title TITLE]
```

The script consumes only `cases.csv`, `history.csv`, `summary.json`, and
`provenance.json` in the supplied aggregate directory. It creates PNG and
PDF figures, `source_points.csv`, and `plot_provenance.json`. It imports no
owner, preparation context, native backend, or solver. Numerical threads are
fixed to one and process affinity is restricted to at most two CPUs before
NumPy and Matplotlib imports. No dependencies were installed.

Cases are split by exact `cohort_id` before plotting. A cohort with stored
history produces the actual-sample history summary. A cohort without stored
history produces endpoint scatter panels at exactly the requested
`--signed-sigma`; selection uses equality, not nearest matching. No archived
64-step endpoint is treated as part of the native 2-step cohort.

## Actual products

### Native NCP five-case cohort

`results/ncp5/plots/actual_samples_4ff69a0d5fef.png` and its PDF show six
panels: signed matter stress, radiation stress, total stress, shear,
matched-control final shear, and the residual fraction for the opposite
requested stress case. History lines join actual saved samples and mark
every sample. The title block reports five cases, two steps, backend,
origin, source, cohort, and 15 saved samples. The footer states the original
half-contraction convention.

The 15 input history rows appear in each of four history panels. Five
matched-control endpoints and three cancellation-history samples give
**68 plotted points** in the long-format source table. All five controls
were available. The cancellation case is `native_check_4`; its three
stored residual fractions are approximately 8.81e-16, 1.19950645e-4, and
2.39895553e-4. The plot uses those values directly without clipping the
small initial residual.

### Archived 729-case cohort

`results/baseline729/plots/endpoint_slice_caed0ccd4a58.png` and its PDF
show four scatter panels at exact requested signed Sigma=0: final signed
shear, final signed total stress, final residual fraction, and final
normalized total shear work. The actual requested signed matter/radiation
coordinates are scatter positions. Color represents the corresponding
stored endpoint value. Signed fields use symmetric diverging color scales;
the residual fraction uses the physical 0-to-1 display scale.

The selected exact slice contains **81 actual coordinates** out of 729
endpoints, giving **324 plotted points** across four panels. The title block
reports the archived owner backend, 64 steps, reused-completion origin,
source and cohort. It explicitly states that intermediate history is not
loaded in this endpoint projection; this does not deny the original stored
history. A ring marks the requested (Pi_m, Pi_r)=(0,0) coordinate in the q
panel, and a footnote identifies its q as a nominal-zero floating-point
residual diagnostic without physical cancellation interpretation. Its raw
numeric value and source table row are retained unchanged. No threshold or
clipping is introduced. No interpolation, grid filling, smoothing, fitting, or
history reconstruction occurs.

## Source-point checks and provenance

Every plotted series has a long-format table row containing the exact
source CSV name, zero-based row index, source field, source value, plotted
value, case/science/source/backend/toolchain/cohort metadata, and explicit
availability status. Endpoint scatter records both requested coordinate
fields. History horizontal coordinates are the actual saved scale factors.
The matched-control panel uses categorical case positions; its source
requested-shear coordinate is separately retained.

The plotter checks every plotted y value and every stored source x value
against the original CSV row using exact float equality. Scatter y
coordinates receive the same check. Values unavailable in CSV remain
empty in the point table with `UNAVAILABLE` status, rather than becoming
zero. No undefined values occurred in the two actual products. The
provenance JSON uses strict JSON serialization, with absent metadata as
null where applicable, and records all source file hashes, output hashes,
counts, cohorts, argv and script hash.

Actual commands, combined stdout/stderr and exit statuses are preserved in
`evidence/PLOT_RUN.log`; `evidence/PLOT_RUN_STATUS.json` records both exits.
`evidence/PLOT_POINT_TABLE_CHECKS.json` records a focused reread of the
serialized point tables against source CSV values. Both PNGs were visually
inspected by the implementation executor: headings, axes, color bars,
legends and footnotes were readable and unclipped. This does not substitute
for the controller and fresh reviewer's required PNG inspection.

After the controller accepted the initial layout, two requested semantic
clarifications changed only the projection wording and nominal-zero q
annotation. The same two products were regenerated with one built-in
source-value equality pass per aggregate. Both commands again exited 0,
and both complete source-point table hashes remained identical. Updated
figure hashes, argv and raw output are retained in
`evidence/PLOT_CLARIFICATION_RUN.log` and
`evidence/PLOT_CLARIFICATION_STATUS.json`.

Requested execution model: `gpt-6.1-sol`. Observed runtime model: `null`
(the execution interface did not expose it). Solver calls, native builds,
and benchmarks: zero.
