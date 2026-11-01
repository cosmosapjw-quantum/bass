# Continuous source-preserving photon/HHe science reproduction

Owner: original REI-F08 S0 13.7eV photon birth + original 51 Rust source, 12 HHe F08 inputs, 4 photon V1 checkpoint/header. Immutable BASS source PR326 HEAD 4984b42a9ed4025e4b3f20a3a61355a448e522ab. No original worker/main mutation. BASS Draft PR328. The 160-step simulation is a separate RESEARCH IVP, not the official REI paired_runtime interval-certified production solver.

From the BASS repo root with Python3.12, numpy2.4.2 and offline Rust cargo:

1. cd research/bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust
2. CARGO_TARGET_DIR=/tmp/bass_rei_s0_native_target cargo build --release --offline --example bass_s0_continuous_packet_step
3. cd -
4. F=research/bass_rei_f08_s0_continuous_native_20261102
5. python3 "$F/continuous_s0.py" --steps 160 --rust /tmp/bass_rei_s0_native_target/release/examples/bass_s0_continuous_packet_step --out /tmp/rei_s0_continuous_cold160
6. python3 "$F/continuous_s0.py" --steps 64 --rust /tmp/bass_rei_s0_native_target/release/examples/bass_s0_continuous_packet_step --out /tmp/rei_s0_continuous_cold64
7. python3 "$F/audit_continuous.py" --out "$F/results"
8. python3 -m unittest discover -s "$F/tests" -v
9. python3 -O -m unittest discover -s "$F/tests" -v

Outputs: 640 native source-matched gas/photons trajectory rows, 320 actual model difference rows, 256 independent prefix64 controls, 2 physical scientific PNG+SVG figures. Source original 51+12+4 SHA manifest check required. CI recomputes and compares numeric/semantic rows. Keep original scientific owner central REI canonical 28/88 and BASS upper 9/15 scoped; research only.
