# Standalone ACCEL02 restoration

This checkpoint preserves the original pilot, current BASS ACCEL01 base
documentation/source, the scoped native implementation, raw local verification,
independent review, and handoffs. The package inventory gives every included
relative path, byte count and SHA256. The root CHECKPOINT_FILES.json describes
the immutable packaged snapshot.

The source layout is directly runnable after extraction into a new task-owned
directory. It contains three research directories under a common root; keep that
layout. No Git worktree/clone is required to run an extracted source snapshot.
Use the existing Python environment with NumPy/SciPy and a Linux C++17 compiler
for native execution. Generated binaries and Python caches are not packaged.

## Scope of the snapshot

- Original pilot:112 files, completed729 endpoint/review/plot evidence and its
  pinned owner source. Original physical model and64-step completion unchanged.
- ACCEL01:current pinned BASS base including the eight later Drive/documentation
  changes, plus the reviewed optional backend dispatcher introduced here. The
  matching native execution source exists in both BASS PR178 and REI PR215.
  Historical repository-specific handoff wording can differ; this archive's
  canonical old-document base is BASS. See delivery/BASE_DOC_SYNC.json.
- ACCEL02:source, original140-point and3-derivative raw checks, five paired
  two-step trajectories, worker solve/reuse artifacts and read-only C9 review.

The original47,385-row history (70,618,848 bytes) is NOT included. Its SHA256 is
`139f3f75f535116483ff05dd96933611ac15896ce125c78d9394eb983bb58332`.
Its prior restored backup index remains
`/BASS_BACKUPS/BASS_REI_PILOT_STAGE5_SPLIT729_DATA_20261021_INDEX.json`,
SHA256`df7ddc6648b06b775c105c7c85cd7ccc4f5827284eb95b7f631d91cd79b13340`.
Refer to the original pilot delivery and handoff for its18 parts; there is no
need to fetch that history for endpoint reuse or native compilation.

## Minimal restored-source use

From the extracted root, without compilation:

```bash
python research/rei_sigma_pi_native_moments_20261021/native_worker.py plan --out /tmp/accel02-restored-plan.json
python research/rei_sigma_pi_native_moments_20261021/native_worker.py prepare --plan /tmp/accel02-restored-plan.json --out /tmp/accel02-restored-prepared --case-store /tmp/accel02-restored-store
```

The default plan must report completed729/pending0; no manifest or native job is
needed. Use fresh output paths if those examples already exist. For an explicit
pending task, follow CODEX_HANDOFF.md from its environment/planning/build
sections, pointing variables at the extracted root and a new run-output folder.

Saved worker manifests and build receipts under evidence/ document the original
sandbox paths. They are historical evidence, not portable NCP manifests. Generate
a new target plan/manifest and build receipt. Compiler/library/platform changes
produce a legitimate different backend identity; compare physical/numerical
outputs under the declared criteria instead of requiring binary equality.

## Publication and backup receipts

This immutable ZIP is assembled before its own final provider acknowledgement.
It therefore contains the Stage C delivery-in-progress snapshot. The subsequent
Git closeout records actual publication, full-GET verification and final DAG
delivery state without trying to place a ZIP's own hash recursively inside it.
Read delivery/FINAL_PUBLICATION.json and delivery/STAGEC_BACKUP_VERIFIED.json
from PR178/PR215 for the actual final provider results. StageA/B receipts in the
archive already describe their acknowledged provider objects and byte sizes.
The final verification checks the complete downloaded ZIP's SHA256/size,
Dropbox block content hash, CRC and exact members.

Scientific admission is only PASS_SCOPED_LOCAL_NUMERICAL_EQUIVALENCE. This is not
fullEoR/non-LRS/fullQ^a, convergence, measured speedup, or NCP target-run evidence.
