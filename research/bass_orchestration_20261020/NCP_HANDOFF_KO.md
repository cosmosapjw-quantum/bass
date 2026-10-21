# NCP/local Codex: BASS continuation contract

Read this file together with THEORY_SHARED_Q.md, INTAKE_KO.md, shared_q_bridge/TEST_RECEIPT.json and the parent orchestration index. This package is an additive source contract. Preserve existing working trees and never move an active external run to a different revision.

## Pinned inputs and reuse

- BASS PR174 source/result closeout head a85605302bb0317022eb06b498eb05b9d621de6a, branch research/bass-isotropy-checkpoint-recovery-20261018.
- S9 executed source4b30957cb008aad8019bb1a673937fc67bd017e8, result a40311796f9aac5ea5e0e58c630bee2a78443353.
- S10 executed source d5a173644f5c7c0dbe9eb8757dfc4ccad6c4f4c8, result26e9e1ba8f39788d98ec33c60f6e9fd2605f8b8a, independent review0771f0610987eb9f900674e83063912150733255.
- Original immutable source dependencies: VigilODEa21d573980f66fe02891bd216153443b5352f921 and REI0e25846433170d0f420c4cda44a0bedbf02cd177.
- Current REI MD14 source identity and full RUN19 revision are in the companion REI handoff; required sourceID is MD14_Z002_FESC_BB50K_13P6_100_V1, source blob36d24eb13db3fc42321cb0ddb165e003c0a086c7.

S9 and S10 are complete. Reuse their receipts, including failure/regression records; do not replay the8 histories,496 timing repetitions or allocation matrix. Do not run historical NOT_RUN entries already superseded by PR173/S9/S10.

## Checkout and compile-only readiness

The parent publication supplies the immutable package commit. From a disposable checkout of that commit, locate this handoff; its directory is PACKAGE. Record git rev-parse HEAD and git status --porcelain before any change. If a user repository exists, make an isolated worktree rather than modifying its active branch. Fetch the fixed BASS revision only if it is absent:
~~~sh
git fetch origin a85605302bb0317022eb06b498eb05b9d621de6a
~~~
Run from this package directory:
~~~sh
gcc -std=c99 -O2 -Wall -Wextra -Werror -fPIC -shared shared_q_bridge/shared_q_bridge.c -lm -o /tmp/libbass_shared_q_bridge.so
~~~
The sandbox already ran all eleven focused tests successfully. An NCP ABI/compiler check may execute the test command once only if compiler/platform wiring changed:
~~~sh
python3 shared_q_bridge/test_shared_q_bridge.py
~~~
No Rust dependency or new crate download is needed for this pure adapter. Rust FFI must use #[repr(C)] and the header's exact fields and enum integer values; Fortran may use ISO_C_BINDING. Keep round-to-nearest binary64, gradual underflow and no fast-math. Native activation is not part of this compile check.

## New physical experiment, only when its exact inputs exist

The next scientific experiment is a genuinely shared energy-source event on the same signed BASS geometry and REI spectral deposition. It is distinct from the completed manufactured exponential-donor histories.

Require one source-owner record with:
1. immutable source/binary/input hashes, sourceID, spectral band and f_esc already applied;
2. t,x,a,b,H,s and explicit geometry orientation/normal frame;
3. proper n_H in m^-3, source q_H energy in eV/(H nucleus s) or eV/(H nucleus ln a), explicit clock;
4. actual deposited radiation ΔU in J/m³ and nominal source integral separately;
5. donor reservoir U_d and its physical pressure/closure/initial conditions, plus authority identifying the owner;
6. exact event interval and frozen-volume versus expansion-work ordering.

Call bass_q_normalize once per common rate and use its returned opposite source components in both sectors. At frozen events call bass_q_transfer_event with the *same measured* ΔU used by radiation. Save the compensated balance defect. If the donor instead supplies nominal energy, save δQ and evaluate Cdot+2HC=−kδQ; do not erase the difference by rescaling source bins. Preserve existing nominal/deposited tags and measured scalar source-deposition residual.

If the physical donor closure or actual radiation-event input is absent, mark only PHYSICAL_SHARED_Q_HISTORY INPUT_DEPENDENT. Continue artifact intake, module compilation and source-only normalization using existing owner data. Do not invent a dust reservoir, reuse the S9 manufactured donor as an astrophysical model, or manufacture a new all-lane stopping rule. Write an input_missing record naming the exact absent fields. Further native implementation should be limited to small wiring of this already provided adapter; any genuinely larger missing source exporter must be returned as a concrete implementation dependency, not disguised as an executed calculation.

## Budget, acceptance and return

Use existing stricter project limits: at most16 additional workers,16GiB RAM,4GiB new disk,1,800s per individual job. The pure adapter needs one core and negligible memory. Do not fill64 cores for algebra; S10's measured four-history recommendation is two workers. Record prior cumulative budget if continuing an existing run; no new deadline resets.

For an eligible new paired pilot:
- fixed source/geometry/clock identities must match both sectors;
- all rate/event values finite and donor nonnegative;
- common source signs cancel exactly by construction;
- report ΔC+kδE and source forcing with dimensioned raw values, original solver tolerances and stated floating-point scale;
- retain signed angular P2/isotropy and actual scalar spectral differences;
- accepting this local energy exchange does not close angular, basis, donor-model or full-trajectory convergence.

Save source manifest, compiler/version, exact command, exit code, stdout/stderr, start/stop time, peakRSS, actual processed step count, input owner record and output hashes. Stop on the original wall budget without deleting partial results. Return receipt.json and the smallest restartable actual checkpoint. Update the DAG only with completed outputs or exact input-dependent status. Parent orchestration publishes and backs up after each stage; raw private data stay in their configured providers.

## Existing backup recovery

The fixed S10 Dropbox final archive is id:BSpOijBcT10AAAAAAD_SRg, /BASS_BACKUPS/BASS_S10_C10_20261020_a8560530.zip,130271bytes,SHA2563d4b2a6737eb69e05e06bde492e4b20b5c493855132d403f4db2e372b56f66d2. The latest recovery receipt is id:BSpOijBcT10AAAAAAD_SSA. Source-only recovery also exists as PR172 archive646321bytes,SHA256022af5cf56958c371e4d4154c785780952ccd9a5e0d38b390f603c96e67f13de, Drive1uA1WWfIrFsHr-LCfgTyQXN2mOURTVJQl or Dropboxid:BSpOijBcT10AAAAAAD_JjA. Use existing verified local bytes first; no user download is required. Drive S10 delivery was still pending in the fetched receipt and must not be marked complete without a new acknowledgement.

