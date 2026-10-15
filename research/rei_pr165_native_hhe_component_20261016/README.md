# PR165 native H/He component trial

This external Cargo binary calls REI PR150 `rei_microphysics` from the pinned
read-only worktree at `0e25846433170d0f420c4cda44a0bedbf02cd177`.
`export_component_input.py` validates the immutable PR164 BASS CSV and receipt,
then exports the `COLD_FLRW` initial native `BackgroundPoint`, its source hashes,
and the positive proper-time increment through `x=1e-4`. The included
`COLD_FLRW_COMPONENT_INPUT.txt` has SHA-256
`109f30de4ab3f4f3b8c2702cfa66ca6a1d6410cbc33d9dbede8a7619af928eb1`.
The binary reads that input, creates a fresh `Driver::new(DriverConfig::baseline())`
state at `a=1/21`, `b=0`, and injects source photons at the actual BASS initial
native geometry and `zbar=20`. All four photon arrays and the exact returned
source ledger increments enter the public REI chemical stage. The gas,
photons, source and reaction ledgers are checked and emitted as one JSON line.

`state.a` deliberately stays at `1/21`. The current REI `Driver` owns a
concrete `AxbiBackground`; this trial certifies only the fixed initial
geometry component, not evolving BASS geometry, a restart, or a full history.
It reads no checkpoint and writes no scientific state. Numerical execution
belongs on NCP under the controller's resource and timing cap. The absolute
local REI dependency path in `Cargo.toml` must be rewritten to the pinned
read-only NCP crate path when staging there.
