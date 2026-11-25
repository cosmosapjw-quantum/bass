# BASS asset recovery (C2H)

## Retain the currently active, already tested implementation
- `_rustcore/src/runtime/{typeii_host,typeii_photon_host}.rs`, `kinetic/{lie_history,lie_hierarchy,radiation_feedback}.rs`: native Type-II/general Lie characteristic, Einstein evolution, angular hierarchy and stress machinery. Keep their current contracts; no imported competing metric solver.
- `homogeneous_sky/{coupled,replay,spectral,frequency_dual}.rs`: partitioned live-stage machinery, LOS replay, spectral diagnostics/mixture and positive frequency machinery. Do not infer that all of their modes are interchangeable.
- `homogeneous_sky/rei_live.rs` calls the current `AxbiSource` and REI `packet_chemistry_stage` APIs; uses existing BASS geometric transport and SDIRK2 Thomson. Background records accepted before the new matter/UV evolution: no self-consistent new matter or photon stress feedback.

## Recovered and actually rerun
- Donor `ea19c11ee3412b9fcbc8d3d07ec7c7eefcf7ddbf` (F08 native root bridge). Exact probe bytes restored as `_rustcore/examples/f08_recovered_root.rs`. Sixteen archived point inputs reproduced against the final direct REI dependency pin. Root CSV byte identical, 70,656 photon records; negative source control rejected. Point-parent local enclosure only; no claim for propagated boxes.
- F08 characteristic representation from continuous-native parent `b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6`. Reimplemented the birth-energy/birth-time representation in `birth_packets.rs` using current BASS native rays rather than reviving old private REI crate copies. Two Rust tests, twelve live cases, independent LRS Killing-momentum oracle. Current closure only expanding non-tilted LRS I; no general class-B spatial divergence closure.
- FT03 hot primary-stage root remains within its original domain. The low-temperature REC donor is handled with AXBI rather than extrapolating the FT03 rates.

## Identified candidates, not newly admitted/retested in this cycle
- PR171 bolometric contract `220c0525e36e817fbe3a4e8932508555e781c1c3`: candidate for stress-energy interface.
- PR173 native SourceLedger `4e2d1fa820d6f7baae1069b615fb82a08d53403b`, `research/bass_sourceledger_20261018/NATIVE_EXECUTION_20261018.md`: historical 58-row source-only native evidence; five invalid-input rejections, not an admitted H/He/opacity/feedback solver.
- AX03 massive Vlasov stress `9e50f936f3289cb0c7c8127772cf9fb8d172d7a8`: candidate for massive-component stress closure.
- Type-II spectral closure `d3ec945c4674d20ae63d4e7f659df24d798630de`: reference/validation candidate; preserve external-HyRec fixtures separately from independent runtime.

No wholesale historical branch merge; old admissions, R78, and unrelated worktrees untouched.
