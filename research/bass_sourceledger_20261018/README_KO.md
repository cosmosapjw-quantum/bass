# BASS SourceLedger: verified source publication retry

2026-10-18. Base BASS commit `9c264c0a21fbc4d0c3d111ed83bf0ad826a2a904`; immutable REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177`. This publication recovers the complete runnable source/test dependency set from `BASS_SOURCELEDGER_READY_20261018.zip`. It adds no new physics and does not execute NCP.

## Run from Git, with no external package transfer

In this directory, prepare a Python 3.11+ environment with `python -m pip install -r requirements.txt`. On a fresh worktree run:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python generate_fixtures.py --out fixtures
bash RUN_LOCAL.sh
bash RUN_NATIVE.sh /absolute/path/to/rei_bianchi_git /absolute/new/output/path
```

The first command creates the full 58-case input, 1090 birth records, five negative controls and matched Python oracle data locally. The generator is create-only: do not delete or silently replace an existing fixture directory. The two preparation/test commands were actually replayed from a fresh directory containing only the 22 exact published runtime/source/test files, and 51 tests passed. No ZIP, attachment, `/mnt/data` dependency or 60k-character source capsule is needed.

`RUN_NATIVE.sh` calls `native_runner.py`, which reads committed upstream blobs, stages literal include dependencies, builds the external probe and invokes actual `CovariantTransport::inject`, `inventory`, and `validate_state`. It must record all 58 result rows, the completion marker, compiled owner/probe identities, per-ray moments and the five negative controls. This native compilation/measurement remains NOT_RUN. Synthetic validator tests are not native evidence.

## Scientific boundary

Non-tilted axisymmetric Bianchi I, signature (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b). Retain signed s=dot b and Sigma=sqrt(3)|s|/H separately. Native stocks are photons/H-nucleus and eV/H-nucleus; only conversion to proper volume introduces n_H=n_H0/a^3. A locally isotropic source uses one solid-angle Jacobian. Monopole normalization alone does not force exact discrete quadrupole isotropy.

The source-only positive GL2 birth-time quadrature and its Python tests are not a reactive H/He integrator, an Einstein feedback callback, a new source-bound restart, or an EoR prediction. No original REI production state or checkpoint is modified.

## Actual verification and backup

The original archive is unchanged: 646321 bytes, SHA256 `022af5cf56958c371e4d4154c785780952ccd9a5e0d38b390f603c96e67f13de`. All 83 manifest payloads passed. New Dropbox and Google Drive copies were each downloaded independently and passed the same archive and 83-payload hashes.

- Dropbox: `/BASS_BACKUPS/BASS_SOURCELEDGER_READY_20261018_RETRY.zip`.
- Google Drive: `/Google Drive/BASS_BACKUPS/BASS_SOURCELEDGER_READY_20261018_RETRY.zip`.
- Full original results, generated fixtures, earlier failures, local Git bundle and historical delivery files remain in that archive.
- This Git branch exposes the runtime Python/Rust code, tests, pinned reference sources and generator as regular files. Generated 58-case fixtures are deliberately regenerated rather than transcribed through a CSV-to-text connector.
- The archived standalone local Git commits are NOT BASS upstream commits. The new repository commit is rooted in the real BASS parent named above.
- Remote Desktop Commander was retried once and returned a monthly usage pause. It was not retried or reconnected. GitHub connector writes and cloud uploads succeeded independently.

Read `DAG.json`, `RETURN_TO_CHATGPT.json` and `CODEX_HANDOFF_KO.md`. Original stage theory remains in `S1_THEORY.md`; the source-only finite-time derivation is `S2_THEORY.md`. No automatic merge or CI PASS claim.
