# R118-C2H BASS recovery and live REI
The recovered F08 root and its original CSV are independent from the new cold-IGM live route. Root provenance in ROOT_RECEIPT.json; earlier report and theory in legacy/. The live route uses REC's z20 donor as initial state only, native BASS accepted LRS I geometry, characteristic ionizing packet births, the native REI common AXBI packet stage and live CMB Thomson tracer. It does not consume a prerecorded ionization history. No full coupled Einstein stress solve, active tilt, or z20-to4 characteristic production solve is claimed.

## Reproduction
From the BASS worktree (locked REC and REI git revisions):
```sh
cargo build --release --locked --manifest-path _rustcore/Cargo.toml --example f08_recovered_root --example rei_live_characteristics
mkdir -p /tmp/f08_recovered_inputs
git archive ea19c11ee3412b9fcbc8d3d07ec7c7eefcf7ddbf research/bass_rei_f08_native_root_bridge_20261102/inputs/actual160 | tar -x -C /tmp/f08_recovered_inputs
_rustcore/target/release/examples/f08_recovered_root /tmp/f08_recovered_inputs/research/bass_rei_f08_native_root_bridge_20261102/inputs/actual160 /tmp/f08_root.csv
cmp /tmp/f08_root.csv research/r118c2h_bass_recovery/legacy/ROOT_ALL.csv
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 python research/r118c2h_bass_recovery/run_live.py --binary _rustcore/target/release/examples/rei_live_characteristics --donor ~/Downloads/rec_r118c2g_boundary/normal.json --out /tmp/new_c2h_live
cargo test --release --locked --manifest-path _rustcore/Cargo.toml
cargo test --release --locked --manifest-path _rustcore/Cargo.toml --examples
```
Raw results used for this receipt: ~/Downloads/bass_r118c2h_live_final and ~/Downloads/bass_r118c2h_root. Use verify_results.py --raw to verify those actual outputs and final executable identity. Archived input fixture from exact donor commit, not regenerated.

## Scope and unresolved work
Twelve cases, z20 to 19.98/19.9, time and angle/spectral checks, both shear signs. Packet support maintained with threshold boundary outflow owned at 13.60 eV; no threshold crossing occurred in these short live cases (tested independently by Rust unit test). The apparent first-order convergence of electron fraction in short FLRW interval is not long-term accuracy. Packet count grows linearly with births and per-stage work can grow quadratically over the trajectory; need support-preserving compression and long EoR convergence. Geometry is fixed before this live solve; CMB thermal bath uses isotropic temperature; no source spectral-angle self-consistency or stress-energy feedback. Tau check compares trapezoid integrals on the same accepted state, not an independent cosmology prediction. General Lie/class-B, full REC atomic owner replacement, low-z tail and new production science admission remain HOLD.
