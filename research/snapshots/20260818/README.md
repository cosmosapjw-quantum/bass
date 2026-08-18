# BASS durable research snapshot — 2026-08-18

This directory is a durable, claim-scoped checkpoint of the current BASS research/development state. It is intentionally **not** a production merge.

## Read first

- `PROGRESS_LEDGER.md` — complete stage-by-stage M0–M10 and G-* progress ledger.
- `CURRENT_STATE.md` — concise current scientific/numerical/compiler state.
- `ARTIFACT_INDEX.md` — SHA-256 and size ledger for generated bundles and intentionally external large inputs.
- `G_SYMBOLIC_MOVING_MANIFOLD_II_RECEIPT.json` — latest passed moving-equilibrium/Kato reference gate.
- `MOVING_EQUILIBRIUM_CONTINUUM_IR.json` — current Type-II continuum moving-equilibrium authority.
- `WOLFRAM_MTK_PARITY_PLAN.md` — plan to reproduce needed ModelingToolkit-style structural compiler functionality with Wolfram/xAct + Python/SymPy, with Rust as the only production backend.
- `RUSTCORE_INTAKE.json` — lockfile-exact offline RustCore bundle evidence.
- `NAME_REVIEW.md` — naming recommendation.

## Current development boundary

Primary path:

1. WSC-0 Wolfram 15 capability seal.
2. WSC-1 neutral Continuum SymIR v1.
3. WSC-2 structural graph compiler.
4. WSC-3 DAE/index/initialization parity.
5. WSC-4 Jacobian/sparsity/JVP parity.
6. G-SYMBOLIC-LOWERING-II.
7. generated low-rank/matrix-free Rust Type-II Kato kernel.
8. isolated production migration only after generated-vs-reference gates pass.

Parallel research:

- `G-DYN-MANIFOLD-CROSS`: VI0 -> VII0 -> VIII -> class B -> IX/exceptional.

Production migration is currently **BLOCKED**.

## Binary artifact policy

The active environment also produced a deterministic consolidated research ZIP:

- `BASS_RESEARCH_SNAPSHOT_20260818.zip`
- SHA-256 `59df2690804cb38e7a2f9d4c06af05fb0b78e3839a131cd6449e55296bb95210`
- bytes `2700643`

The connected GitHub write API does not accept a local binary file handle, and large third-party/vendor/reference bundles should not be base64-expanded into public Git history. Therefore this GitHub checkpoint preserves the complete textual authority/state package plus exact artifact hashes instead.

## Name recommendation

Keep **BASS**. The acronym is already strong and has continuity value. Prefer the descriptive subtitle:

> **BASS — an exact symbolic–numeric Bianchi–Boltzmann transport system**

Use **BASS-SymIR** for the compiler/IR subsystem and **BASS-Runtime** for generated numerical kernels/runtime. If a rename is ever desired, **BATS — Bianchi Anisotropic Transport System** is the cleanest alternative, but it loses the explicit Boltzmann identity and is a much more generic acronym.
