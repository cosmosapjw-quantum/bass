# Native HYREC-2 mode audit under original BASS Type-II H and conserved proper nH

Parent immutable PR #332 commit `ee298e24a6bac85bb11a81393f37499a8b0ddbe3`. Original BASS main source `9c6506e4e2087129a8b674ff10438e5db1a55c9d`. Original native HYREC installed source in CLASSIER external/HyRec2020 must remain read-only. All mode-specific C builds live in ignored `native_run/`.

## R1/C1 Scope / checkpoint
Question: quantify source-native HYREC hydrogen/helium recombination sensitivity to SWIFT, FULL, and EMLA2s2p approximation on the same BASS gamma-law 1.3 Type-II H(zmean) and conserved class-A nHrest, and distinguish a real radiative-transfer approximation difference from time-step/mode switch.
Acceptance:
- Source inspect exact `MODEL`, timestep, switch and SWIFT fit range before builds.
- Preserve model parameters, TypeII H table, proper Hn factor, and unchanged original atomic rate files.
- FULL must use all original transfer switches and fine DLNA_HYREC. If host storage is inadequate for full radiation histories, do not execute a partial or memory-truncated FULL run; record actual resource blocker and carry out EMLA/SWIFT, fit-domain, and small isolated tests only.
- Use same input H, nHrest factor, cosmology, Tm initial conditions and output redshift grid to compare lanes.
- Include a test of FULL↔EMLA stiff low-z fallback and the SWIFT fit-domain boundaries, not just a final xe comparison.
- No production C files/branch mutation; only research artifact and scratch binaries. The parent worktree must not be modified.
- Stage R1..R10/C1..C10 each separate real commit, pushed branch remote readback, archive SHA if the full bounded experiment has enough space.

## R2/C2 Original source implementation
Original source HYREC-2 model choices: PEEBLES=0, RECFAST=1, EMLA2s2p=2, FULL=3, SWIFT=4. Original source `history.c` gives SWIFT `DLNA_SWIFT=4e-3`, FULL/EMLA `DLNA_HYREC=8.49e-5`; FULL radiation histories allocate memory with `allocate_radiation()`, SWIFT uses `fit_swift.dat`. `rec_dxHIIdlna` selects:
- EMLA2s2p → `rec_HMLA_dxHIIdlna`;
- FULL → detailed `rec_HMLA_2photon_dxHIIdlna` when `Pion>=1e-2`, EMLA otherwise;
- SWIFT → `rec_swift_hyrec_dxHIIdlna` when its scaled-Tr lies in the fit table; EMLA outside it; low-z Pion threshold again takes EMLA.
FULL also selects EMLA2s2p for stiff/Post-Saha source. SWIFT selects EMLA2s2p for stiff when beyond the fit's high temperature boundary. Thus these modes do not run their most distinct approximation over the complete redshift interval.

Original HYREC-2 paper (Lee & Ali-Haïmoud 2020, PRD 102, 083517, arXiv:2007.14114) states HYREC-2 is an effective four-level atom model with excited-state non-equilibrium treated by effective rate tables, while FULL radiative transfer correction data are calculated with original HyRec and tabulated as functions of temperature and derivatives w.r.t relevant cosmological parameters. Reported precision is validated over full 99.7% Planck 2018 cosmological parameter region, not arbitrary anisotropic Bianchi source expansion. Full precision must not be assumed simply by selecting FULL.

## R2 source-backed experimental boundary
Current root filesystem `/` only has 390 MB free (915 GB total, 100% full); available RAM ~17 GiB, but FULL stores radiation evolution arrays at `log(10)/DLNA_HYREC` steps and full compile/run must have free storage for all outputs/temp archives. Do not delete other scratch, user datasets, PR evidence, parent native_run, docker images, caches, or user source to manufacture space. Reassess only when owner explicitly supplies/cleans storage. Current permitted objective continues through source read, EMLA/SWIFT runs and analysis that can fit; FULL large run `NOT_RUN_RESOURCE_BLOCKER`.

## DAG
BASS upper DAG remains 9/15 scoped/source-mapped, newly full production upper nodes 0. StageII historical 11/11, current canonical GateBundle evidence not recovered; J1 0/2 FULL PASS HOLD. Native subagent not exposed; self-hostile review required only once.
## R2/C2 | Exact SWIFT correction source semantics and native fallback range

Original source `hydrogen.c::rec_swift_hyrec_dxHIIdlna` has
`DK_K = DK_K_fid + Sum_i(diff_i * fit_i(TR/kB))`, with
`diff0=(omega_cb-0.14175)*T0fid^3`,
`diff1=(omega_bh2*(1-YHe)-0.02242*(1-0.246738546372))*T0fid^3`,
`diff2=Neff-3.046`,
`T0fid=2.7255/(TR/kB/(1+z))`.
The fitting table's independent axis `TR/kBoltz` is tabulated every 10 K from 1775 K to 4415 K. Column 1 is fiducial correction, columns 2-4 are derivatives for the three cosmology differences above. **The TypeII source Hubble function itself is not a coordinate/parameter of this correction.** The table's ordinary cosmological parameter interpolation is therefore insensitive to a change of H(z) that leaves the present cosmological omega_b, omega_cb, YHe, Neff and Tcmb unchanged.

Exact source hydrogen modes:
- `EMLA2s2p=2` executes `rec_HMLA_dxHIIdlna` using effective 2s/2p atomic rates, no explicit full line transfer.
- `FULL=3` executes `rec_HMLA_2photon_dxHIIdlna` with dynamic radiation transport when `Pion>=1e-2`; when `Pion<1e-2`, original source deliberately uses EMLA. FULL `DLNA=8.49e-5` and allocates radiation arrays of length `log(10)/DLNA≈27,105`.
- `SWIFT=4` executes `rec_swift_hyrec_dxHIIdlna` with `DLNA=4e-3` when the fitting function is within range and `Pion>=1e-2`; below the fit low-temperature endpoint, outside its high endpoint or `Pion<1e-2`, original source uses EMLA. SWIFT uses the high-temperature EMLA source stiff solver too.
Hence SWIFT and FULL intentionally coincide with EMLA in selected fallback regions. A mode comparison restricted to the active SWIFT/FULL two-photon domains is required.

Primary source Lee & Ali-Haïmoud (2020), PRD 102 083517, arXiv:2007.14114: original HyRec computes the redshift/cosmology-dependent radiative transfer correction and the tables for HYREC-2, as functions of radiation temperature and the derivatives w.r.t. relevant cosmological parameters. The reported HYREC-2 accuracy is within Planck 2018 99.7% cosmological parameter region. The current BASS TypeII (H(z_{m mean})) source is a non-standard expansion history, not tested by merely remaining within the SWIFT tabulated temperature axis.

## BASS target cosmological correction deltas
Pinned HYREC TypeII inputs `omega_cb=0.143, omega_b=0.0224, YHe=0.245, Neff=3.046, T0=2.7255 K`, compared with native table's fiducial `omega_cb=0.14175, omega_b*(1-YHe)=0.02242*(1-.246738546372)`, have source SWIFT corrections `diff0 ≈(0.00125)*T0fid^3`, `diff1 ≈(-2.13e-5)*T0fid^3`, `diff2=0`; the second is very small and the first lies within the standard Planck-like range. **The unrepresented TypeII H effect** is not an ordinary cosmological parameter differential; no source evidence proves the fitting correction transports correctly under this change. This is a theoretical/model risk to quantify with EMLA/FULL, not a completed no-go.
