# SYNC-MAP-02D Plot-Driven CRAG Audit

## Generated figures

### Connected-Wolfram renders

- relation-class bar chart:
  `https://www.wolframcloud.com/obj/44ba6567-a562-44ed-b05b-bb1e9d3e47f9`
- R2 prerequisite graph:
  `https://www.wolframcloud.com/obj/0f82ed96-1e05-460e-90f8-4b5280112091`

### Deterministic repository figures

- `HTT_RELATION_CLASSES.svg`
- `R2_FEDERATION_DAG.svg`

The repository SVGs are text-deterministic summaries of the same relation
counts and required graph edges. They are evidence visualizations, not
scientific observable plots.

## Plot reading

The relation chart has one immediately dominant class: five HTT-owned
processed extensions. Four relations are pending common BASS imports, while
only one adapter and two independent oracles remain. The visual balance rules
out the misleading narrative that the entire HTT WU-010/WU-011 surface is a
single common Lorentz formula. Most of WU-011 is observation-side processing.

The DAG render has one load-bearing diamond-shaped join in substance, even
though rectangular nodes are used visually: `02C_REI` and `02D_HTT` are
parallel prerequisites of `02E_SHARED_EXPORT`. The graph then places the
cross-repository semantic graph after the exact export and before the three
repository sync nodes. The final gate is visually dashed to mark manual
activation.

## C — Correctness

- Bar counts are `4+1+2+5=12`, equal to the JSON and CSV relation count.
- The graph has ten unique nodes and twelve directed edges.
- Both `02C_REI -> 02E_SHARED_EXPORT` and
  `02D_HTT -> 02E_SHARED_EXPORT` are visible and machine-required.
- `02E_SHARED_EXPORT -> 02F_SEMANTIC_GRAPH` is explicit.
- Three sync nodes, not the relation maps themselves, feed the manual gate.
- Local observer boost and global matter tilt never share a node or edge.

No semantic mismatch was found between the plotted labels and the committed
classification.

## R — Retrieval

The SciSpace literature check supports two visually separated layers:

1. exact full-sky Doppler/aberration transformation;
2. realistic masked/beam/noise/estimator response.

Dai–Chluba supports the first layer; Ferreira–Quartin, Pereira et al., and
Gruetjen–Shellard support the need for a distinct processed response layer.
The plots therefore agree with the literature-role lock and do not infer
repository ownership from literature.

## A — Augmented adversarial checks

The exact Wolfram oracle was mutated in five ways:

```text
wrong boosted-chart Doppler sign        detected
wrong solid-angle Jacobian power        detected
omit induced l=1 quadrupole response    detected
omit induced l=3 quadrupole response    detected
remove 02D_HTT -> 02E_SHARED_EXPORT     detected
```

The final mutation remains an acyclic graph. This is the key adversarial
result: a visually tidy DAG and a successful acyclicity test could still omit
a mandatory consumer-classification prerequisite. Required-edge checks are
therefore retained as separate machine gates.

## G — Generated predictions

The combined 02B+02D gap set predicts six candidate BASS records before REI is
mapped:

```text
BASS.FRAME.ABERRATED_DIRECTION.001
BASS.FRAME.DOPPLER_FACTOR.001
BASS.FRAME.SOLID_ANGLE_JACOBIAN.001
BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001
BASS.PHOTON.DIRECTION_FLOW.001
BASS.PHOTON.ENERGY_DRIFT.001
```

This is not yet the final 02E input. `02C_REI` may add, narrow, or split
records. The plot predicts only that 02E cannot validly start from the REC map
alone or from the HTT map alone.

## Print-size and legibility audit

### `HTT_RELATION_CLASSES.svg`

- 960×540 view box;
- 24–30 px primary type and direct numeric labels;
- four non-overlapping horizontal bars;
- safe for single-column or double-column use;
- no legend is required because labels are inline.

### `R2_FEDERATION_DAG.svg`

- 1400×930 view box;
- 20–31 px type;
- branch join and manual gate are spatially separated;
- safe as a double-column figure;
- not recommended at single-column width because node subtitles would become
  the first elements to lose legibility.

No clipping or coordinate overlap is present in the SVG primitive layout. A
rasterized hostile visual inspection in an independent image runtime was not
available in this connector session; that non-load-bearing publication-quality
check remains `PENDING_EXTERNAL_VISUAL_READBACK`.

## Adversarial claim disposition

```text
SURVIVING
  exact HTT relations can be classified without duplicate common authority
  full-sky common formulas and processed HTT extensions are distinct
  02C and 02D are both required before 02E

NARROWED
  Wolfram result is a stateless exact oracle, not a native repository replay
  SVG layout is structurally audited; external raster visual readback pending

REJECTED
  acyclicity alone closes the federation DAG
  HTT local boost constitutes BASS global tilt
  Task-7B synthetic processing licenses data fitting or Bianchi attribution
```

## Final CRAG verdict

`PASS_FOR_RELATION_CLASSIFICATION / NOT_A_SHARED_EXPORT_OR_PUBLICATION_FIGURE_CLOSEOUT`
