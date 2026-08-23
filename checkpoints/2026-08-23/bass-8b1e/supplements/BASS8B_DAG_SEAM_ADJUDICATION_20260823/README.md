# BASS-8B DAG-seam adjudication — preservation supplement

This directory preserves the bounded decision that reconciles the two durable
next-node labels after BASS-8B.1:

- E4: `BASS-8B.1E.5`, direction-dependent local Q-time Thomson-rate binding;
- BASS-8B.1: `BASS-8B.2A`, typed electron-state binding, then `2B` projector/left-functional work.

## Exact decision

```text
CRITICAL_PATH_NEXT_BASS_8B_2A__E5_DEFERRED_RATE_SUBNODE
```

Status:

```text
PASS_DECISION_ONLY__NO_AUTHORITY_ROW_PROMOTION
```

The exact package is:

```text
BASS8B_DAG_SEAM_ADJUDICATION_20260823.zip
SHA-256 beb0b30f22e3a7bd601a3e24ea57e45258cfaeb57fe633794513bac7a0ad2b8f
```

It is stored as three lossless binary parts. Run `./restore_archive.sh` from
this directory to verify the parts, reconstruct the ZIP, verify its outer
SHA-256, and test its ZIP CRC.

`DECISION.md` and `DECISION.json` are duplicated outside the ZIP for direct
review. The ZIP remains the complete manifest-bound artifact.

## Ordering

```text
BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING          CRITICAL PATH / NEXT
  -> BASS-8B.2B_FINITE_CARRIER_PROJECTOR_LEFT_FUNCTIONAL
  -> BASS-8B.3_ROWS7_8_READJUDICATION

BASS-8B.1E.5_DIRECTION_DEPENDENT_LOCAL_RATE      SIDE SUBNODE
```

For nonzero scalar rate, multiplying the collision shape does not change its
right/left kernel, rank, nullity, equilibrium carrier, or normalized projector.
At zero rate, the entire carrier becomes a kernel, so collision-off cannot
identify a nontrivial projector. Consequently E5 is required before claiming a
complete direction-dependent collision generator, but it is not a prerequisite
for rows 7–8 projector/left-functional authority.

## Non-claims

This preservation checkpoint is not an authority-row promotion, VI0 classifier,
solver/runtime implementation, production migration, merge candidate, or PR.
