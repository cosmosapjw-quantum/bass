# RF-04 LOCAL-01 telemetry parity checkpoint

This directory is a durable partial checkpoint for
`BASS-LOCAL-01_NATIVE_TELEMETRY_PARITY`. It records successful exact R5 intake,
genuine RED reproduction, the byte-frozen telemetry delta, a separate bounded
nonfinite safety repair, focused Rust donor tests, validator hardening, a pinned
production wheel build, and the measured public-route blocker.

The checkpoint does **not** claim LOCAL-01 completion. The rebuilt wheel retains
the three scalar/raw v1 symbols but has no authorized polarized v2 result
carrier, serialization contract, registration, or PyO3 success/error mapping.
The controlling handoff forbids inventing those interfaces. Therefore:

```text
PASS_RF04_SCALAR_RAW_SLICE_PROOF retained
BLOCKED_BY_MISSING_AUTHORIZED_V2_PUBLIC_MAPPING
LOCAL-01 NOT_PASS
LOCAL-02 NOT_RUN
NO_PASS_RF04
```

`LOCAL01_VALIDATION.json` is the machine-readable acceptance matrix.
`RAW_MANIFEST.sha256` binds the retained raw logs below `raw/`. The two audit
reports record the single permitted PHYS-MATH and PHYS-MATH-CODE review round.
