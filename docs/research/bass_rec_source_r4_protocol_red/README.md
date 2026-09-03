# BASS–REC Source Protocol R4 — Repository-Wide Audit and TDD RED

**Date:** 2026-09-03  
**Stage:** `BASS_REC_SOURCE_R4_PROTOCOL_TDD_RED`  
**Disposition:** `EXPECTED_RED / PRODUCTION_UNCHANGED`  
**Authority effect:** `NONE`

## Pinned implementation parent

```text
repository  cosmosapjw-quantum/bass
branch      agent/architecture/rf04-local01-telemetry-20260831-r1
commit      380ce6fe6aebe0c76c59c0d2a0f8707aac0ce14c
tree        0062a719173dc0c40dcc1202ab0d305f8fe2e2bb
PR          #70 (OPEN / DRAFT)
```

This is the actual code-bearing RF-04 runtime lineage. `main` is not used as the implementation authority. The formula/compiler lineages and the REC repository are read as separately pinned authorities and are not silently merged.

## What was audited

The audit performed a repository-wide tree census over the Python package, Rust core, standalone Type-II runtime, compiler/IR areas, workflows, tests, audits, benchmarks, and observables. It then deeply read the load-bearing execution paths for:

- family routing and orthogonal/globally tilted backgrounds;
- Python/Rust backend policy and public route admission;
- direct angular and full spectral distribution grids;
- dense-tensor and coefficient-space PSTF hierarchies;
- exact scalar and polarized Thomson kernels;
- finite-electron-velocity, electron-trajectory, and validity layers;
- recombination-history collision-rate wiring;
- observables and output readiness;
- formula/compiler versus production-runtime boundaries.

This is an exhaustive **code-path census plus load-bearing source audit**, not a claim that every repository byte was dynamically executed. The current ChatGPT runtime did not expose a working local container, so no local `pytest`, Cargo, binary, benchmark, or plot result is claimed in this stage.

## Corrected architecture

BASS does not have one undifferentiated “Boltzmann representation.” It has three materially different numerical state lanes:

1. `FULL_SPECTRAL_GRID`: the distribution itself, such as Q Mode B `f(q_hat,q)`;
2. `RADIAL_INTEGRATED_ANGULAR_GRID`: an energy-weighted angular density, such as Q Mode A `G_hat(q_hat)`;
3. `FINITE_PSTF_WORKSPACE`: a finite numerical multipole workspace, while the formula SSOT defines the all-rank hierarchy.

The first and third can receive the same spectral REC source by pointwise evaluation and exact projection. The second cannot receive a generic frequency-dependent REC source from its stored state alone. For

```text
G(e) = integral dnu nu^3 f(nu,e)
C_REC[f] = eta(nu,e) - chi_affine(nu,e) f(nu,e)
```

the integrated absorption term depends on spectral information not contained in `G(e)` unless a grey/source-integrated theorem or additional spectral witness is supplied. R4 therefore forbids treating Mode A as source-equivalent to Mode B by default.

## PSTF qualification

The repository has an exact all-rank distribution/PSTF/Wigner formula authority and generic coefficient algebra, but the inspected numerical implementations remain finite workspaces:

- dense Rust PSTF projection is generated only through rank 5;
- coefficient-space tables admit a finite kernel wall (`L_KERNEL_MAX=10`);
- the Lewis–Challinor numerical hierarchy carries explicit `l_max`, `i_max`, an upper-`i` extrapolation closure, and zeroes unavailable `l+2` sectors at the boundary.

Accordingly:

```text
all-rank formula authority                    YES
finite numerical PSTF evolution               YES
numerical PSTF evolution without truncation    NO
full-distribution grid without moment closure  YES
all-family all-source dual-representation parity NOT YET
```

## Source protocol required by the RED test

The missing BASS-owned protocol must eventually provide one immutable REC source authority bundle with:

- positive primary pair `(eta_s_inv, kappa_s_inv)` and derived signed `chi_affine_s_inv`;
- exact SI physical-time to Q-time conversion
  `eta_per_tau=eta_s_inv/H_s_inv`, `kappa_per_tau=kappa_s_inv/H_s_inv`;
- distinct admission rules for full spectral grid, radial-integrated angular grid, and finite PSTF workspace;
- work-rank guard `L_work >= L_out + L_source` for polynomial angular products;
- pointwise/adaptive-tail treatment of anisotropic exponential jump maps;
- frame, frequency, channel, state-parent, background-parent, source, and convention identities;
- no mutation of the BASS state by TEFF diagnostics;
- no dependence on the still-blocked RF-04 v2 public route.

## RED status

The test imports `bianchi.source_authority`. That module does not exist at the pinned parent. The intended first failure is therefore:

```text
ModuleNotFoundError: No module named 'bianchi.source_authority'
```

No production module has been added. The failure is intentional and is the only admitted result of this stage.

## Next node

```text
BASS_REC_SOURCE_R5_PROTOCOL_GREEN
```

R5 may implement only the minimal protocol required by the RED test. It must not yet wire physical REC data, virtual-spike tails, provider output, fitting, or the blocked RF-04 polarized-v2 route.

## Claim boundary

```text
PASS_REPOSITORY_WIDE_STATIC_CODE_AUDIT
PASS_WOLFRAM_UNIT_RANK_AND_NONIDENTIFIABILITY_ORACLES
EXPECTED_RED_PROTOCOL_ABSENT
NO_LOCAL_RUNTIME_REPLAY
NO_GRID_PSTF_NUMERICAL_PARITY
NO_GENERIC_REC_SOURCE_ON_MODE_A
NO_SOURCE_COMPLETE_TWO_PHOTON_RAMAN_DEPOSITION
NO_DYNAMIC_ELECTRON_TRAJECTORY_PRODUCTION_WIRING
NO_SOURCE_IDENTICAL_PHYSICAL_FACE
NO_PROVIDER_EXPORT
NO_STATISTICS_PROMOTION
NO_PASS_RF04
```
