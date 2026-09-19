# WU088 / CR3C9 / P1H QCTRL R4 WIP checkpoint

Date: 2026-09-19
Branch: `agent/p1h-qctrl-r4-20260919`
Production mutation: NO
Physical source promoted: NO

## Parent

- R3 quantum-control package preserved as immutable regression input.
- P1G Dataverse H+H stripping source-coherence contradiction remains open and is not repaired by this branch.
- Current BASS `main` is only the recovery bootstrap. This branch is a research checkpoint, not restored host implementation authority.

## Implemented in this checkpoint

1. Off-axis full complex `(l,m)` SAE basis.
2. Neutral-H moving potential split into analytic nuclear Coulomb multipoles and smooth screening Legendre multipoles.
3. Stable `V_scr(s)` evaluation with exact finite limit `V_scr(0)=1`.
4. Gaunt/3j angular assembly and Hermitian Hamiltonian construction.
5. Exact axial `b=0` `m`-decoupling test.
6. SO(3) rotation covariance through Wigner-D blocks.
7. Projectile-bound and translated-target-1s MODEL subspace diagnostics with Gram/union projector accounting.
8. Collision-plane reflection-even cosine-tesseral invariant sector.
9. Fast integer Racah formula for Wigner 3j generation.

## Current gates

- Unit tests: 9/9 PASS.
- Operator rotation-covariance defect: ~5.6e-17 on tested rotations.
- Norm conservation in bounded runs: ~1e-14 or better.
- Original fixed-quadrature axial comparison to R3 `nangle=40`: FAIL retained as evidence.
- Diagnosis: inherited R3 direct quadrature under-resolves the moving Coulomb singularity. R3 `nangle=96` agrees with the split solver within the original 2e-5 dynamic tolerance.
- Screening quadrature is converged on tested fixtures.
- Radial ground-survival trend is stabilizing, while finite-box positive-energy population remains box-sensitive and therefore diagnostic only.
- Partial-wave convergence is still OPEN. `lmax=4,5,6` continues to move materially; collision-plane reduction reaches `lmax=9`, but `lmax>=10` is currently runtime-expensive with global Cayley factorization.

## Hard firewalls retained

- No finite-box positive-energy population is labeled ionization/TCS/DDCS.
- No target-localized SAE model state is labeled physical H-.
- No fitting to inconsistent Cariatore-Schultz Table-7 `E_loss(theta_proj)`.
- No P1D/P1B deposition replay yet.
- No two-electron physical-source promotion.

## Online checkpoint

Midpoint immutable ZIP SHA-256:
`2407867dfc043cedfb35c83c876ba18bf8f130b733430a330faae2bcd76fe702`

Backed up to both Google Drive and Dropbox under `BASS_DERIVATION_DOSSIERS_20260912`.
