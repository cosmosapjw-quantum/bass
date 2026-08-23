# BASS-8B.1E checkpoint backup — 2026-08-23

This is a preservation-only backup of the bounded BASS-8B.1 electron-frame
authority sequence.  It is not an authority-row promotion, a production
runtime integration, or a merge candidate.

## Git lineage

- Repository: `cosmosapjw-quantum/bass`
- Backup branch: `agent/backup/bass-8b1e1-e4-checkpoints-20260823`
- Explicit base: `main@d9e5ba7577ccb05b648b11ea7ac991bf6e09d8b9`
- Local source lineage: `LOCAL_GIT_LINEAGE_UNAVAILABLE`; the recovered working
  tree contains no Git metadata, so the explicit base is only the storage
  branch parent and is not claimed as the scientific source parent.
- Existing recovery, research-snapshot, B1-authority, and DAG-realignment refs
  were not moved or combined.

## Preserved checkpoints

| Sequence | Artifact | SHA-256 | Recorded status |
|---|---|---|---|
| Owner decision gate | `BASS8B1_MODEL_OWNER_DECISION_REQUIRED_20260823.zip` | `d18d922e941c9b5e7b18f3801c2711f29694205068fe69ed54c8ebbf830a4778` | historical blocked decision checkpoint; later resolved by the H2-with-comoving-restriction route |
| E1 | `BASS8B1E_ELECTRON_TEST_FIELD_FRAME_ADAPTER_IMPLEMENTED_20260823.zip` | `054d85e0e2f900162dfb58e42ec953c1de45b9ba636cfadbcdaf5ba667596544` | implemented bounded; partially confirmed because full JAX/Rust integration was unavailable |
| E2 | `BASS8B1E2_ELECTRON_COLLISION_RATE_AUTHORITY_IMPLEMENTED_20260823.zip` | `75c137d897d37e327aeb23c5352f547deed474401a25673a72681351e6e4e750` | bounded implementation; independently confirmed; not production-wired |
| E3 | `BASS8B1E3_COLD_THOMSON_VALIDITY_AUTHORITY_20260823.zip` | `bc10633dbab0e8beb401badc8270988af41ba4fae5ea47fcb35c4f38942defc1` | bounded implemented and verified; not promoted |
| E4 | `BASS8B1E4_TRAJECTORY_ORIENTATION_AUTHORITY_20260823.zip` | `d7590182b52d7bb30f537232993f2bb954a049d530138b0325474633926ec766` | confirmed bounded Python authority; not promoted |

E1-E3 and the decision artifact are stored byte-for-byte as single ZIP files.
The 2,627,127-byte E4 ZIP is stored as six lossless binary parts because the
connector used for this backup has a smaller single-payload boundary.  Run
`./restore_e4.sh` from this directory to reconstruct it, verify the original
SHA-256, and test its ZIP CRC.

`latest/` exposes the E4 state, verification report, next action, manifest,
and the high-value authority source/test/audit files for direct browsing.  The
complete source snapshot and every predecessor dependency remain inside the
reconstructed E4 ZIP.

`post-seal/` preserves the two append-only E1/E2 working-state receipts that
sit outside their immutable ZIPs to avoid a circular archive hash:

- E1 post-seal state SHA-256:
  `e3c22ab30dac8faf56f8499cc40777d5329033341d778f1b9437ba1d43bfbc71`;
- E2 post-seal state SHA-256:
  `a81c4922ca1241718713d23e06a79f6d2e18de8c432ac339821011511f78da30`.

## Fresh pre-upload verification

- all five outer SHA-256 sidecars: pass;
- all five ZIP CRC checks: pass;
- E4 internal manifest: `9/9` hashes pass;
- clean-extracted E4 focused gate: `28/28` pass;
- E1/E2/E3 regression gates: `13/13 + 13/13 + 20/20` pass;
- E4 hostile audit, electron audits, P9, compilation, and contract JSON: pass.

From the repository root, `sha256sum -c
checkpoints/2026-08-23/bass-8b1e/BACKUP_CONTENT.sha256` verifies every
payload file except the manifest itself.

The next bounded node recorded by E4 is `BASS-8B.1E.5`, the
direction-dependent Q local-rate binding authority.  Scalar-Q averaging,
production solver/JAX/Rust wiring, and authority-row promotion remain out of
scope.
