# P1H QCTRL R4 partial close — 2026-09-19

Canonical node:
`WU088_CR3C9P1H_QCTRL_R4_OFFAXIS_MRESOLVED_SAE_AND_CHANNEL_PREPROJECTOR_RUNTIME_CERTIFICATION`

Verdict:
`PARTIAL_CLOSE__BODY_FIXED_MRESOLVED_SAE_ARCHITECTURE_PASS__ANALYTIC_COULOMB_PLUS_SMOOTH_SCREENING_SPLIT_PASS__SO3_STATIC_AND_DYNAMIC_COVARIANCE_PASS__AXIAL_R3_REGRESSION_CONVERGENT__COARSE_12_CELL_RUNTIME_PASS__PARENT_R3_VERIFY_PASS__DT_AND_SCREENING_QUADRATURE_STABLE__RADIAL_ANGULAR_COUPLED_DISCRETIZATION_OPEN__LMAX_TRUNCATION_FIRST_NUMERICAL_BLOCKER__FROZEN_TARGET_BOUND_SUBSPACE_EMPTY__NO_HMINUS_IN_SAE__COULOMB_WAVEPACKET_CONTINUUM_ROUTE_SELECTED__PHYSICAL_SOURCE_NOT_PROMOTED__P1D_P1B_NOT_RUN__HE_BLOCKED`

Key evidence:
- fresh combined pytest: 33/33 PASS;
- parent `run_all.py --mode verify`: rc=0;
- static SO(3) covariance: relative operator defects about 1.3e-13 against independent 2D sphere quadrature;
- dynamic body-fixed vs direct lab-frame witness: overlap 0.9999999890876 at the refined audit quadrature;
- 12/12 coarse `E={10,30,100} keV`, `b={0,.5,1,2} a0` cells completed with durable receipts;
- coupled refinement at 30 keV, b=1 a0:
  - nr=120: L=5,6,7 -> 0.7582740992, 0.7516003474, 0.7472021735;
  - nr=180: L=5,6,7 -> 0.7631825558, 0.7568278218, 0.7526766278.
  Radial and angular errors are therefore still coupled and non-negligible.

Runtime finding:
- concurrent cell processes plus threaded BLAS/OpenMP caused a real >45 s wrapper interruption;
- the same nr=120,L=5 cell completed with TDSE runtime 2.58968 s after setting OMP/OPENBLAS/MKL/NUMEXPR threads to 1;
- COMPLETE + receipt sentinels successfully preserved four completed cells through a later wrapper interruption, so only the unfinished cell was rerun.

Scientific ceiling:
- one-active-electron frozen-neutral control only;
- finite-box complement is not ionization/TCS/DDCS;
- frozen target one-electron direct potential has no tested negative-energy bound subspace, so no H- promotion;
- physical source remains unpromoted;
- P1D/P1B deposition and He remain disabled.

Current source SHA-256:
- qctrl_r4.py: `71252db37e2b01dc11409f977a59b8b3f62cecf3a9bb1ba0a2d01f561a76cd62`
- test_qctrl_r4.py: `3ab686be986ea77730a847edc5faad236c328f81997574612fbc42dab7018f09`
- run_qctrl_r4_cell.py: `178da4a933694a28babd1281142e57d4025343eefb992ef9e8774328a1500e81`

Next local node:
`WU088_CR3C9P1H_QCTRL_R4R2_ANGULAR_TAIL_CERTIFICATE_AND_COULOMB_WAVEPACKET_PREPROJECTOR`.

Do not merge this checkpoint to production based on the structural PASSes alone.
