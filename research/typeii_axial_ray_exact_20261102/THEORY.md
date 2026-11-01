# Original BASS Type-II axial ray exact physical research

## R1. 계약과 범위

원본 BASS PR #325의 C9 시점 고정 소스(HEAD a3bf54708db1388227b34a313ff3c8e6c250d7f5), original main 9c6506e4e2087129a8b674ff10438e5db1a55c9d 및 원본 9/9 Git blob을 기준으로, Type II 401-state 정상 tetrad의 ±ey 정확 불변광선과 conditional Thomson 단위 고유 opacity를 연구한다. 성공 조건은 정확한 수식, parent CSV의 401×2 원본 ray 및 독립 적분 일치, hostile controls, 재현 코드와 외부 백업이다. Production dispatch/real recombination/observational claims는 범위 밖이다.
## R2. 원전 및 코드 대응

Primary physical context: Pontzen & Challinor, Bianchi model CMB polarization (MNRAS 2007, arXiv:0706.2075), and Davis & Gammie, covariant radiative transfer (ApJ 888 94, DOI:10.3847/1538-4357/ab5950). Numerical authority is original BASS `runtime/rust/typeii/typeii_polarized_liouville.rs`, `generated/rust/typeii/typeii_collision.rs` and `compiler/validation/typeii_fixture_canonical.json`. Previous PR #325 `PHOTON_RAYS_401X26.csv` is the comparison target, not a proof premise for deriving the analytic formula.
## R3. 가정·컨벤션

Metric (-,+,+,+), normal tetrad, dτ_H=Hdt with H>0, fluid gamma-law index 1.3 distinct from electron Lorentz Gamma(v). Source Type II Sigma off-diagonal xz, N=diag(N1,0,0), R_y=√3 Sigma13. Electron 4-velocity is conditionally identified with v2 e_y; the optical depth uses electron-rest proper density, not normal density, and the generated collision owns q=1-vn_y exactly once.
## R4. 독립적인 판별 경로

Build three physically distinct tests: (i) invariant +e_y and -e_y photon rays, (ii) exact normal-frame energy equality but opposite electron-frame Doppler shift, (iii) optical-depth odd/even decomposition. An intentionally off-axis perturbation Sigma_xy≠0 is a counterexample to extending axial invariance to arbitrary shear. No conclusion about general off-axis curvature sign follows from an axial ray.
## R5. 축방향 정리·직접 증명

For n=±e_y, Sigma n=(Sigma_+ +√3 Sigma_-)n, R×n=0, Nn=0, so dn/dτ_H=0 in the original equation: dn=-(Sigma n-Sigma_nn n)+R×n-n×(Nn). Thus ln(E/E0)=-∫(1+Sigma_+ +√3 Sigma_-)dτ_H and ln(I/I0)=4ln(E/E0). With unit electron-rest opacity and v=v2(τ_H), T_±=∫Gamma(1∓v)dτ_H. Therefore T_-−T_+=2∫Gamma v dτ_H, T_-+T_+=2∫Gamma dτ_H, and (T_-−T_+)/(T_-+T_+)=∫Gamma v/∫Gamma. Wolfram independently evaluated the Type-II frame rate as 0 for both directions and simplified the constant-tilt asymmetry to v. This exact identity is valid for the stated tetrad and conditional electron identification, not for arbitrary Bianchi gauges.
## R6. 자기 적대적 검사

The axial invariant hides the Type II curvature sign because Nn=0, so it cannot replace the existing 26-ray off-axis curvature test. A deliberately introduced Sigma_xy=0.02 gives n_x'=-0.02 for +e_y, refuting overly broad axis invariance. q-only opacity and double-q give nonzero numerical discrepancies; in particular a q-only substitution drops the Lorentz density factor. Verify these actual negative controls in `test_axial_negative.py`, without calling it an independent-author review.
## R7. 원본 401-state 수치 판별

Original 401-state × 26-ray CSV is source-locked by SHA-256 9f1400588d39ba3a61020542e14b0e372c8e9be1af130f8c64ed8829b23ad217. Exact Hermite energy integral and independent Gauss-Legendre tau on ±ey agree with the published numerical rays: maximum log normal-energy error 1.67e-16, unit opacity error 2.22e-16, electron-frame log-energy error 2.50e-15. The unit-opacity results are T+=0.19055295929452346 and T-=0.2099155839589957.
## R8. 과학적 주장 판정

Accept exact axis invariance and the conditional unit-proper-opacity asymmetry as DERIVED; accept 401-state comparisons as NUMERICALLY_CHECKED. The gamma-weighted mean tilt is 0.048349926581410956, not a measurement of the real electron velocity or CMB signal. The independent physical density n_e(τ), full Thomson collision redistribution, polarization hierarchy, metric backreaction, and Stage II canonical evidence remain unresolved. BASS upper DAG stays 9/15 scoped, zero newly full-complete nodes.
