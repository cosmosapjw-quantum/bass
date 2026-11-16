# Reproduce the level-resolved bound-free bridge

Current Draft PR337, immutable parent PR336/ad4bda34a833d215aa49037d7cb4d609e5cee04b. Run from this checkout. Original BASS9/9 protected source blobs and parent atomic/field tables are not edited. No network or new compiler installation is needed for this unit.

## Source and conventions
`sources/h1.px.txt` is the author-hosted Nahar nl hydrogen table, with55 states and1000 energies each. It has SHA2564150287531cc642ecf837fa253b22f5158bd189b3f2c9ce634010b2e4b5ee44c and its header explicitly says '(unpublished)'. `PROVENANCE.json` records the URL and identity. Ry is13.605693122994eV;1Mb=1e-22m^2. Source binding and photoelectron energy define E=chi+K, avoiding independently rounded photon-column mismatch. No high-energy extrapolation or high-n total-rate assumption is used.

The code treats unaligned nl levels, isotropic Maxwellian relative electrons, a nonrelativistic/infinite-nucleus hydrogen convention, and a prescribed local boosted Planck/BE field. The reaction coefficients are microscopic, not effective HYREC coefficients. Read `DERIVATION_SUPPLEMENT.md` and the source-support caveats before using them.

## Commands
```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
d=research/typeii_boundfree_balance_20261116
python3 "$d/test_bridge.py"
python3 "$d/verify_kernels.py"
python3 "$d/source_campaign.py"
python3 "$d/verify_final.py"
```
NumPy and SciPy are required. `verify_final.py` reruns13 unit tests normally and with -O, independent kernel verification normally/-O, and the source/network experiment with -O; it checks byte identities of the seven generated science outputs. It also executes explicit invalid-input and wrong-model tests. A successful process exit is not the only check: source identity, finite support, equilibrium residuals, physical values, positivity and conservation are tested explicitly.

## Outputs and interpretation
- `LEVEL_BOUND_FREE_SOURCE.csv`:2148 forward/reverse records at358 actual parent TypeII states, six low levels.
- `ALL_LEVEL_FINITE_BAND_PROBES.csv`:55-state diagnostics at three source states, finite-band only.
- `NETWORK_*.csv`:three isolated fixed-bath2s/2p/continuum population tests, not cosmological histories.
- `SOURCE_AND_NETWORK_RESULTS.json`:rates, stationary ratios, interpolation sensitivity and independent network solver comparison.
- `KERNEL_VERIFICATION.json`:165 Planck/BE finite-band checks and independent atomic/velocity/angular quadratures.
- `VERIFICATION_AND_HOSTILE.json`:actual execution evidence and wrong-model controls.

The initial4-point cold1s quadrature failure is retained. A RED-to-GREEN regression raised the default to8 points per source interval without modifying the source or tolerance. The final source8/12 comparison is separate from interpolation sensitivity. No native HYREC population/effective coefficient was replaced, and no new cosmological xe or optical-depth history is claimed.

## Preservation and continuation
B1..B4 are separate Git commits with remote readback and ZIP/SHA256+CRC backup on the owner host and external disk. Receipts live outside Git to avoid a self-referential final commit hash:
`/home/cosmosapjw/research_backups/bass_typeii_boundfree_balance_20261116/STAGE_RECEIPTS.tsv`.
Use `NEXT_THREAD_HANDOFF.txt` and read the live HEAD before continuing. Next constructive unit: bound-bound/cascade channels and a conservative effective-rate interface. Upper BASS9/15 scoped/source-mapped and Join/production holds remain unchanged. Do not auto-merge.
