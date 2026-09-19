# WU088 CR3C9 P1H QCTRL R4 partial close

Date: 2026-09-19

Verdict:
`PARTIAL_CLOSE__OFFAXIS_MRESOLVED_SAE_OPERATOR_CERTIFIED__HIGH_L_PRODUCTION_CONVERGENCE_OPEN__PHYSICAL_SOURCE_NOT_PROMOTED`

## Verified in the active runtime

- R4 unit tests: 12/12 PASS.
- Off-axis full-m SAE operator with analytic nuclear Coulomb multipoles plus smooth neutral-H screening.
- Hermiticity, norm conservation, axial m=0 limit, SO(3) covariance and exact collision-plane cosine-tesseral reduction.
- Sparse Krylov and structured-Krylov propagators cross-checked against the existing Cayley implementation on overlapping fixtures.
- R3 official verify-mode non-regression PASS.
- Parallel `BASS_WU088_BIANCHI_STRIPPING_DEVKIT_v3_20260919.zip` recovered from the durable Dropbox dossier and freshly replayed: manifest PASS, 259/259 tests PASS, physical-component example PASS, v3 validation PASS.
- DEVKIT-v3 loss-side / local gas-tetrad rate is complementary to R4 coherent quantum control. It still does not provide energy-angle gain or a complete event.

## Open

- strict promotion-grade high-l / continuum convergence;
- actual Coulomb continuum scattering amplitudes;
- two-electron spin/exchange/ETF physical B4 reproduction;
- inclusive target(all) stripping;
- same-event proton/electron/recoil gain;
- P1D/P1B deposition replay and complete reionization.

Finite-box positive projectile-energy weight is diagnostic only and is not ionization/TCS/DDCS.

## Durable artifact

`WU088_CR3C9P1H_QCTRL_R4_PARTIAL_CLOSE_20260919_v1.zip`

SHA-256:
`b73eb7a1e8313e2a41255b33d5805adf897bad29836b0d4b6e175ad43988069f`

Size: 99,999 bytes.

Google Drive object:
`external-gdrive:account:112098983264231137819:file:1QXOc4QGsGkpiRYFoV2Fo_tJX6c8GltgM`

Dropbox object:
`id:BSpOijBcT10AAAAAADspSA`

This branch remains a research checkpoint. It does not restore or mutate the missing historical BASS host implementation and does not promote a physical collision source.
