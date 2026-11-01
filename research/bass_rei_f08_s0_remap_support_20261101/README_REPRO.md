# Reproduction | source-locked original REI F08 S0

This is an additive BASS-only science branch based on immutable BASS PR317. Its original H/He proper material history and original source code are present in the parent research directory.

Run from the repository root:
1. python3 -m unittest discover -s research/bass_rei_f08_s0_remap_support_20261101/tests -v
2. python3 -O -m unittest discover -s research/bass_rei_f08_s0_remap_support_20261101/tests -v
3. python3 research/bass_rei_f08_s0_remap_support_20261101/spectral_support.py --out /tmp/rei_s0_hat_replay
4. python3 research/bass_rei_f08_s0_remap_support_20261101/audit_support.py

Python 3.12 and NumPy 2.4.2 recommended. The actual Git-source owner files are saved under original local REI runs/rei_fastest_v1/paired/receipts, and copied byte-exact in source_inputs; check LOCKED_CHECKPOINT_SHA256SUMS.txt. The inherited parent source_inputs has ORIGIN_SHA256SUMS.txt with 12 byte locks.

Three new physical data files in results:
- SOURCE_MATCHED_F08_S0_SPECTRAL_SUPPORT_TIMELINE.csv.gz (60 rows).
- ORIGINAL_AND_REMAPPED_F08_S0_FINAL_SPECTRUM.csv.gz (108 rows).
- ORIGINAL_AND_REMAPPED_F08_S0_ANGULAR_SUPPORT.csv.gz (768 rows).

All three are generated from original real source qhat/energy nodes, original 16000 physical proper-time steps and physical original H/He matter snapshots. Passive=redshift/hat/injection only, frozen HI=Verner H I absorption on frozen original matter; original checkpoint is original native reference. This is one physics unit, not a complete REI original full coupled solver reproduction. Results/RESULT.json contains SHA and original science status.

Critical record semantics: source F08 original photon_n already includes guard. Any CSV under source support includes original below-10-eV guard only ONCE. First step exact physical null support excludes the lower 13.675-eV node while the original source hat interpolation assigns it positive number. Production HOLD, original REI 28/88 unchanged, BASS upper 9/15 scoped unchanged.
