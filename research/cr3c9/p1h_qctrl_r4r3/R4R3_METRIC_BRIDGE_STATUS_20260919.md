# P1H QCTRL R4R3 metric-bridge checkpoint — 2026-09-19

Canonical node:
`WU088_CR3C9P1H_QCTRL_R4R3_TWO_CENTER_COALESCENCE_REPAIR_AND_AOCC_WAVEPACKET_BRIDGE`

## Frozen parent
R4R2:
- Gate A: current single-center L=7 promotion certificate FAIL, exact finite omitted shell lower bound B>=1.439296792862562.
- Gate B: isolated Coulomb wave-packet preprojector PASS.
- physical source remains unpromoted.

## New R4R3 results
- Two-center normalized H(1s) zero-velocity overlap:
  `S0(R)=exp(-R)(1+R+R^2/3)`.
- one-electron two-center metric condition upper bound:
  `kappa <= (1+S0)/(1-S0) ~ 12/R^2`.
- spin-adapted triplet norm lower bound:
  `1-|S_v|^2 >= 1-S0(R)^2 ~ R^2/3`.
- independent cylindrical numerical overlap audit max absolute error:
  `5.161426841482353e-13`.
- exact nonorthogonal packet span projector:
  `P=Phi G^{-1} Phi^dagger`.

Selected W1 geometry E=5 keV, b=1.5 a0, t=.7:
- singlet O: min eig 0.3585263766336233, cond 5.5316883080;
- triplet O: min eig 0.016743834253005102, cond 98.0345122009.

Closest-approach b scan at 5 keV:
- triplet condition rises from ~10 at b=3 to ~2.26e4 at b=0;
- therefore spin-resolved min-eigenvalue/condition monitoring is mandatory.

Moving-basis metric identity:
`Odot=tau+tau^dagger`, `tau=<B|dot B>`,
verified on actual 64-channel W1 basis.
Central finite-difference defect converges at order 2. At delta=2.5e-4:
- singlet relative Frobenius defect 1.3073596596821058e-08;
- triplet relative Frobenius defect 1.2991743990166567e-08.

No physical source, H-, stripping DDCS, P1D/P1B, or He promotion is claimed.

Durable metric checkpoint:
`P1H_QCTRL_R4R3_METRIC_CHECKPOINT_20260919_v1.zip`
SHA-256 `f290b69d30ee595b235e57f1f85a8ca3330e83a0a107cb58a664fbecef72997b`.
Google Drive and Dropbox uploads both completed.
