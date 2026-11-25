# R116-B: source-owned H/He/thermal history bridge
Baseline BASS 4c58712012542340155fbb9c813ab898693b3204.
Pinned original REC cb1685271e32223400df0817895952895087ef31 (species_thermal).
This opt-in path derives its opacity, absolute reference anchors and species
initial state from a single REC table. The native cold Thomson cell updates
the host and photon field first; the endpoint material sky, host proper
density, Hubble rate, Lorentz factor and accepted-cell proper-density
expansion then drive the matched BE species solve. The next collision cell
uses its charge offset. Strict linear-segment integration rejects negative
opacity; there is no silent clipping or competing external ionization table.
Thermal/binding energy terms are recorded per H, not applied as active stress
or spectral photon injection. The matched correction is not physical heat.
The discrete expansion ratio is a cell average from mass continuity; the
endpoint tilted expansion is a secant-derivative diagnostic. This is T1
bounded tracer thermochemistry, NOT T2 second-order coupled chemistry.

Run after building with cargo build --release --locked --manifest-path
_rustcore/Cargo.toml --example homogeneous_sky (as one command):
python3 research/r116_species_thermal/smoke.py --binary _rustcore/target/release/examples/homogeneous_sky --rec /path/to/rec_bianchi/research/r116_species_thermal --out /new/output/directory
Optional --legacy takes the actual R116-A smoke output directory to compare
the six numerical TSV files for grid_I and continuum_I.
The committed RESULTS.json contains the executed commands, exact input/binary
hashes, numerical summaries and endpoint comparison. Raw output is on the
workstation at Downloads/bass_r116b_species_final, reproducible from the
compressed REC reference slices and the script. Logs contain 228 regular
and 3 example test passes. The 12 CLI runs passed the explicit finite-state,
charge/nuclei, continuity, energy-ledger and sampled screen checks in smoke.py.
Across these cases, the maximum Gauss residual is 8.1523e-8; the maximum
scaled algebraic residual is 1.8553e-6 (stiff helium FLRW window); neither
is claimed to meet a universal machine-epsilon bound. The density-continuity
check is an identity by construction, not an independent evolution test.
Ray/grid/continuum comparisons concern a short mild-tilt overlap only.
The physical H window endpoint refinement ratios are about 4.24 (xe) and
4.10 (Tm), not evidence of generic second order for lagged chemistry.
No full tilted HeIII non-equilibrium source, HeI spectral transfer, source-phase
handover, active thermal feedback, high-l or long strong-tilt acceptance,
or scientific DAG promotion is asserted.
