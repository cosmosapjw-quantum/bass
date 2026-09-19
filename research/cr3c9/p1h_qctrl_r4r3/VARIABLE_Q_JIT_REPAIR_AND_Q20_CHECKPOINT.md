# R4R3 variable-q ERI repair and q20 checkpoint — 2026-09-19

## Implementation bug found and quarantined
The exploratory variable-quadrature Numba modules originally changed
`leggauss(4)` to `leggauss(N)` but inherited the hard-coded
`for iq in range(4)` loop. Therefore q28/q36/q48/q64 exploratory full-G
outputs from that adapter used only the first four nodes of the larger rule
and are scientifically invalid.

They are classified:
`IMPLEMENTATION_ERROR_INVALID_VARIABLE_QUADRATURE_ADAPTER`.

Independent exact ssss witness:
- spectator `K0011[0,0]` analytic value = 4.582121677365901;
- Python correctness backend q32..q384 matches to ~1e-15.

## Corrected variable-q backend
Both the Gauss nodes and the loop bound are changed consistently.
Corrected q20/q28 JIT versus the Python correctness backend:
- max selected-sample relative difference = 2.3291660716233074e-14;
- corrected spectator K0011[0,0] agrees with analytic reference to <8e-16.

## One-body selected point
E=5 keV, b=1.5 a0, t=.7:
- nq12 vs nq20 contracted one-body h relative Frobenius difference
  = 1.8448914627393404e-6;
- h Hermiticity defects are <=4.1e-15.

## Corrected q20 full electron-electron candidate
All 8 direct/exchange spectator blocks were computed durably.
Full 64-channel matrices:
- singlet G Hermiticity relative defect = 6.24e-15;
- triplet G Hermiticity relative defect = 1.26e-14;
- full H Hermiticity defects <=3.86e-15;
- V=H-i tau continues to satisfy V-V^dag=-i Odot to the existing
  finite-difference error ~1.3e-8.

q20 is CANDIDATE only. Full corrected q28 audit is required before
selected-point H can be promoted even as a bridge component.

Durable checkpoint:
`P1H_QCTRL_R4R3_Q20_CHECKPOINT_20260919_v1.zip`
SHA-256 `8541c8c2117084981324607c8a8f25ac127dc7f3de79a143d68e9bdd18a71fd9`.
Google Drive and Dropbox uploads completed.

No physical source, DDCS, P1D/P1B, or He promotion is claimed.
