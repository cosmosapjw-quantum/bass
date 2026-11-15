# Reproduce the original F08 S0 source-native interval-root compatibility experiment

Branch: research/bass-rei-f08-native-root-bridge-20261102. Parent: immutable BASS PR328 HEAD b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6. Source identity and original owner root/atomic source immutable. Research only: Krawczyk local point-input gas/photons enclosure, NOT an original F08 global interval-propagated certificate.

Required: Python 3.12, NumPy 2.4.2, Rust stable compiler with offline cargo (original crate dependencies are source-scoped). Work from the BASS repo root:

- RUST=research/bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust
- UNIT=research/bass_rei_f08_native_root_bridge_20261102
- (cd "$RUST"; sha256sum -c original_source_sha256.txt)
- (cd research/bass_rei_f08_s0_source_photon_thomson_20261101/source_inputs; sha256sum -c ORIGIN_SHA256SUMS.txt)
- (cd research/bass_rei_f08_s0_remap_support_20261101/source_inputs; sha256sum -c LOCKED_CHECKPOINT_SHA256SUMS.txt)
- (cd "$RUST"; CARGO_TARGET_DIR=/tmp/bass_f08_root_target cargo build --release --offline --example bass_s0_interval_root_probe --example bass_s0_continuous_packet_step)
- python3 "$UNIT/capture_native_source.py" --steps 160 --ticks 1,8,64,160 --exe /tmp/bass_f08_root_target/release/examples/bass_s0_continuous_packet_step --out /tmp/bass_f08_root_cold/inputs/actual160
- /tmp/bass_f08_root_target/release/examples/bass_s0_interval_root_probe /tmp/bass_f08_root_cold/inputs/actual160 /tmp/bass_f08_root_cold/results/ROOT_ALL.csv
- python3 "$UNIT/audit_native_root.py" --inputs /tmp/bass_f08_root_cold/inputs/actual160 --results /tmp/bass_f08_root_cold/results --negative-exe /tmp/bass_f08_root_target/release/examples/bass_s0_interval_root_probe
- python3 -m unittest discover -s "$UNIT/tests" -v
- python3 -O -m unittest discover -s "$UNIT/tests" -v

Original actual source snapshot inputs: UNIT/inputs/actual160/S0_*.txt, with CAPTURE.json SHA256 ledger. Each input carries exact source native HHe gas parent and each original S0 birth-energy photon or fixed-hat node packet; source clock ticks 1,8,64,160. Saved ROOT_ALL.csv is produced by the original Rust primary_stage_root and primary_stage_step_conservative, not a Python reproduction of root. Derived SOURCE_S0_NATIVE_ROOT_PHYSICAL_SUPPORT.csv.gz is standard-library physics readback.

The test evidence proves only a **local** root based on exact f64 input parent boxes; previous gas+photon interval widths, source birth quadrature and energy H/q intervals are not propagated. Original F08 production owner interval-certified paired_runtime MPRK/SDIRK/14-ledger full 16000-step admission HOLD; central 28/88 reported and BASS upper 9/15 scoped.
