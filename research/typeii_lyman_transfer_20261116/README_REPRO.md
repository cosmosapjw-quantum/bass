# BASS TypeII Lyman transfer: reproducible scoped interface

Current Draft PR339, immutable parent PR338/232c033cb961fc3d4f5a98760ea27c834b8b0b55. Run from the exact repository checkout with Git, Python3, NumPy, SciPy and SymPy. No external atomic downloads or native production source changes are needed; original parent cascade and source photon/geometry data are identity checked in Git.

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
p=research/typeii_lyman_transfer_20261116
python3 "$p/test_line.py"
python3 "$p/verify_kernels.py"
python3 "$p/run_line_sources.py"
python3 "$p/source_resonance_fates.py"
python3 "$p/verify_final.py"
```

`verify_final.py` executes14 contracts normally and optimized, rejects14 malformed inputs, replays three scientific programs under -O and verifies seven source outputs byte-exact. The native branch status is NOT a Rust production build or hosted-CI pass. The exact meanings and limitations are in `DERIVATION_AND_SCOPE.md` and `FINAL_REPORT.md`.

## Outputs
- `DIRECTIONAL_LINE_DIAGNOSTICS.csv`:358x26 source atom-frame drift and formal escape/wing/variation diagnostics. Mean redshift is not observed redshift.
- `FINITE_LINE_BAND_FLUXES.csv`:390 frozen local line-band solutions. Directional4pi-equivalent fluxes are not an angular integral. Boundary exit is not global escape.
- `CLOSED_ATOM_PHOTON_TRACE.csv`:physical local two-level/32-bin collision test with a fixed thermal reservoir, no expansion.
- `RESONANCE_FATES.csv`:358 finite n<=3 tagged-excitation fates from the actual parent generator. Not high-n recombination feedback or a universal photon-death coefficient.
- `SOURCE_LINE_RESULTS.json`, `KERNEL_VERIFICATION.json`, `RESONANCE_FATE_RESULTS.json`, `VERIFICATION_AND_HOSTILE.json`:actual results and independent checks.

The fixed-ne parent stationary tracer is scaled by a conserved hydrogen-density reference for the opacity scenario. It is not a newly solved neutral/electron abundance. Equal-profile Sobolev and symmetric-Voigt wing continuations are diagnostic controls; the actual bin interface includes the thermal absorption correction. No correction of high-frequency/line-wing physics is inferred by extending an invalid local model. Full evolving phase-space dilution, angular focusing, partial redistribution and atomic feedback are the next unit.

## Preservation
`publish.sh` commits only this folder, pushes and verifies remote HEAD, then creates/checks a host Git ZIP. L1 external copy is verified. L2 external copy failed ENOSPC twice despite reported free space; the failure is saved. Since then the script skips unchanged external writes rather than deleting user data or retrying indefinitely. Current host archives are complete; extra external archives are not. Do not remove `BACKUP_COPY_FAILURE.json` merely to bypass the issue. A separately diagnosed storage repair or authorized alternative destination is needed before external completion can be claimed.

Stage receipts reside outside Git under `/home/cosmosapjw/research_backups/bass_typeii_lyman_transfer_20261116/STAGE_RECEIPTS.tsv` to avoid self-referential commit identity. `NEXT_THREAD_HANDOFF.txt` requires live HEAD first. No automatic merge.
