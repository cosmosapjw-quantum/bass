# PR170 S4 interruption recovery, 2026-10-18

Scope: complete the interrupted BASS non-tilted LRS photon source-age research; no new REI production or NCP run. The branch was still at S3 `a923b568ed91f4dbfa10c02baa35725060ab74d5`; no pull request existed for this branch at recovery start.

The immutable 2026-10-16 ZIP was recovered (330800 bytes; SHA256 `2b462b77bcca8257431a026928c06dadee31d5178a4925d3520189ca7c437274`). All 40 manifest payloads matched. This commit publishes the exact missing S4 physics sources and the three pinned PR169/PR164 local dependencies. The standalone archived physics sources were not rewritten or assigned a new scientific authority.

Actual replay on 2026-10-18: 36/36 scientific Python tests; original RUN_LOCAL.sh exit 0; independent campaign regeneration exactly matched HISTORY.csv and RESULTS.json bytes; MP70 oracle PASS. The earlier chat count of 35 is corrected to 36. Python 3.13.5 / NumPy 2.3.5 / SciPy 1.17.0 / mpmath 1.3.0.

For a Git-only checkout, run `bash RUN_GIT_REPLAY.sh`. It reconstructs the original raw CSV from the already-published HISTORY.csv.gz and verifies the gzip Git blob and raw SHA256 before writing. It rejects any changed existing CSV. No ZIP download, absolute /mnt/data source path or manual transfer is needed. Three additional packaging tests were observed RED then GREEN; they are separate from the 36 scientific tests. Run them with `python -m unittest -v test_prepare_git` after the replay script.

The earlier stage ZIPs, original archive manifests and historical full test logs remain preserved in the immutable archive. The repository stores HISTORY.csv compressed; references to raw HISTORY.csv become readable after the verified prepare step. The recovery delivery package additionally contains fresh raw test and execution logs.

Dropbox original-archive upload and independent Files raw readback passed at `/BASS_BACKUPS/BASS_PR170_SOURCE_AGE_PHOTON_STRESS_20261016_RECOVERED_20261018.zip`; original Google Drive file `1CWOYmmsukkk1QQb2TaCZDemi3ZgoMB68` was independently restored with the same SHA256. Direct sandbox URL download was blocked and direct HTTP DNS failed; Files materialization succeeded. These are transport failures, not physical or numerical failures.

The photon birth source S(x) is manufactured bolometric injection, not native MD14. Two-moment compression is first-order in b(x)-b(u), not a finite-anisotropy closure. Native REI H/He, opacity, Q^a reservoir closure, polarization, new photons in the Einstein source and NCP remain NOT_RUN/HOLD. Native subagents were not exposed; no independent external scientific review was performed in this closeout.
